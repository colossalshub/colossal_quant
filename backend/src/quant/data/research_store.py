"""Append-only synthetic source and immutable BuyHold candidate capture.

Identity uses sorted compact UTF-8 JSON and exact typed hexadecimal numbers.
Server sequence records application commit order; wall time may go backwards.
Code/source identities are assertions, not authentication. Direct record
construction is unvalidated. This is internal persistence replay: no public raw
observation read path is integrated. Capture records must not become unlogged
API dumps. The transactional inspection gateway below logs requested access;
runtime/API/CLI integration and evaluation results remain separate work.
Frozen capture does not authorize selection, validation or OOS access, certify
an unseen holdout, outside inspection, historical data or research eligibility.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import re
import sqlite3
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Literal, NoReturn, cast
from uuid import uuid4

from quant.engine.bar_coverage import validate_bar_coverage
from quant.engine.research_fixture import bind_controlled_fixture
from quant.engine.research_input import ResearchInputSnapshot, ResearchObservation
from quant.engine.temporal import ResearchInterval

logger = logging.getLogger(__name__)
_DAY = 86_400_000
_INTS = ("in_sample_start_ts", "in_sample_end_ts", "trial_index", "trial_count")
_RECIPE_INTS = (
    "anchor_ts",
    "start_open_ts",
    "observation_count",
    "price_start",
    "price_step",
    "volume",
)
_INDEX = ("experiment_id", "hypothesis_id", "candidate_revision")
_FIELDS = frozenset(
    (
        "contract_version",
        "rule_id",
        *_INDEX,
        "parent_candidate_id",
        "strategy_version",
        "strategy",
        "parameters",
        "code_id",
        "seed",
        "fitted_artifacts",
        "in_sample_input_id",
        *_INTS,
    )
)
_PARAMS = frozenset(
    ("starting_balance_usdt", "trade_size", "deploy_pct", "maker_fee", "taker_fee")
)
_INTEGRITY = "stored research event failed integrity validation"
_LIFECYCLE_REPLAY: ContextVar[bool] = ContextVar(
    "research_lifecycle_replay", default=False
)


@dataclass(frozen=True, slots=True)
class StoredResearchEvent:
    """Internal immutable persistence record, without an eligibility flag."""

    seq: int
    event_id: str
    kind: Literal["input", "candidate"]
    recorded_at_ts: int
    canonical_bytes: bytes


def _fail(message: str) -> NoReturn:
    if _LIFECYCLE_REPLAY.get():
        message = _INTEGRITY
    logger.error(message)
    raise ValueError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _identity(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _typed(value: int | float) -> dict[str, str]:
    return (
        {"kind": "int", "value": hex(value)}
        if isinstance(value, int)
        else {"kind": "float", "value": value.hex()}
    )


def _decode_number(value: object, kinds: tuple[str, ...]) -> int | float:
    if not isinstance(value, dict) or value.keys() != {"kind", "value"}:
        _fail(_INTEGRITY)
    kind, spelling = value["kind"], value["value"]
    if kind not in kinds or not isinstance(spelling, str):
        _fail(_INTEGRITY)
    try:
        number = int(spelling, 16) if kind == "int" else float.fromhex(spelling)
    except (ValueError, OverflowError):
        _fail(_INTEGRITY)
    if _typed(number) != value:
        _fail(_INTEGRITY)
    return number


def _pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            _fail(_INTEGRITY)
        result[key] = value
    return result


def _reject_json_number(value: str) -> NoReturn:
    _fail(_INTEGRITY)


def _parse(payload: bytes) -> dict[str, object]:
    try:
        value: object = json.loads(
            payload,
            object_pairs_hook=_pairs,
            parse_int=_reject_json_number,
            parse_float=_reject_json_number,
            parse_constant=_reject_json_number,
        )
        if not isinstance(value, dict) or _canonical(value) != payload:
            _fail(_INTEGRITY)
    except (UnicodeError, json.JSONDecodeError, OverflowError):
        _fail(_INTEGRITY)
    return cast(dict[str, object], value)


def _mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        _fail(_INTEGRITY)
    return cast(dict[str, object], value).copy()


def _decode_input(
    value: dict[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    if (
        value.keys() != {"contract_version", "recipe", "snapshot"}
        or value.get("contract_version") != "research-store-input-v1"
    ):
        _fail(_INTEGRITY)
    recipe = _mapping(value["recipe"])
    snapshot = _mapping(value["snapshot"])
    try:
        for field in _RECIPE_INTS:
            recipe[field] = _decode_number(recipe[field], ("int",))
        snapshot["anchor_ts"] = _decode_number(snapshot["anchor_ts"], ("int",))
        rows = snapshot["observations"]
        if not isinstance(rows, list):
            _fail(_INTEGRITY)
        decoded: list[dict[str, object]] = []
        for raw in rows:
            row = _mapping(raw)
            for field in (
                "ts",
                "close_ts",
                "available_ts",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ):
                if field == "available_ts" and row[field] is None:
                    continue
                kinds = ("int",) if field.endswith("ts") else ("int", "float")
                row[field] = _decode_number(row[field], kinds)
            decoded.append(row)
        snapshot["observations"] = decoded
    except KeyError:
        _fail(_INTEGRITY)
    return recipe, snapshot


def _input_payload(
    recipe: Mapping[str, object], snapshot: ResearchInputSnapshot
) -> bytes:
    encoded_recipe = {
        key: _typed(cast(int, val)) if key in _RECIPE_INTS else val
        for key, val in recipe.items()
    }
    return _canonical(
        {
            "contract_version": "research-store-input-v1",
            "recipe": encoded_recipe,
            "snapshot": json.loads(snapshot.canonical_bytes),
        }
    )


def _text(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and "\x00" not in value
        and not any(0xD800 <= ord(char) <= 0xDFFF for char in value)
    )


def _integer(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        _fail(f"{field} must be an integer excluding bool")
    return value


def _candidate(document: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(document, Mapping) or document.keys() != _FIELDS:
        _fail("candidate must contain exactly the declared fields")
    data = dict(document)
    for field, token in (
        ("contract_version", "research-candidate-v1"),
        ("rule_id", "phase18-temporal-v1"),
        ("strategy", "buy_hold"),
    ):
        if not isinstance(data[field], str) or data[field] != token:
            _fail(f"{field} must be {token}")
    for field in (*_INDEX, "strategy_version", "in_sample_input_id"):
        if not _text(data[field]):
            _fail(f"{field} must be a nonempty UTF-8 string without NUL")
    if data["parent_candidate_id"] is not None and not _text(
        data["parent_candidate_id"]
    ):
        _fail("parent_candidate_id must be null or a nonempty UTF-8 string without NUL")
    code = data["code_id"]
    if not isinstance(code, str) or re.fullmatch("[0-9a-f]{40}", code) is None:
        _fail("code_id must be a 40-character lowercase hexadecimal git commit ID")
    params = data["parameters"]
    if not isinstance(params, Mapping) or params.keys() != _PARAMS:
        _fail("parameters must contain exactly the declared fields")
    cash = params["starting_balance_usdt"]
    if (
        not isinstance(cash, float)
        or not math.isfinite(cash)
        or cash <= 0
        or not cash.is_integer()
    ):
        _fail(
            "parameters.starting_balance_usdt must be a finite positive "
            "whole-USDT float"
        )
    for field in ("trade_size", "deploy_pct", "maker_fee", "taker_fee"):
        raw = params[field]
        if not isinstance(raw, str):
            _fail(f"parameters.{field} must be a finite decimal string")
        try:
            number = Decimal(raw)
        except InvalidOperation:
            _fail(f"parameters.{field} must be a finite decimal string")
        if not number.is_finite():
            _fail(f"parameters.{field} must be a finite decimal string")
        if field == "trade_size":
            _, digits, exponent = number.as_tuple()
            assert isinstance(exponent, int)
            trailing = 0
            for digit in reversed(digits):
                if digit:
                    break
                trailing += 1
            if number <= 0 or exponent + trailing < -6:
                _fail(
                    "parameters.trade_size must be positive and exactly representable "
                    "at 6 decimal places"
                )
        elif field == "deploy_pct" and not 0 <= number <= 1:
            _fail("parameters.deploy_pct must be between zero and one")
        elif field in ("maker_fee", "taker_fee") and number < 0:
            _fail(f"parameters.{field} must be nonnegative")
    if (
        data["seed"] is not None
        or not isinstance(data["fitted_artifacts"], list | tuple)
        or data["fitted_artifacts"]
    ):
        _fail("seed and fitted_artifacts must be explicitly absent for buy_hold")
    data["fitted_artifacts"] = []
    start = _integer(data["in_sample_start_ts"], "in_sample_start_ts")
    end = _integer(data["in_sample_end_ts"], "in_sample_end_ts")
    if start >= end:
        _fail("in_sample_start_ts must be less than in_sample_end_ts")
    index = _integer(data["trial_index"], "trial_index")
    count = _integer(data["trial_count"], "trial_count")
    if count <= 0:
        _fail("trial_count must be positive")
    if not 1 <= index <= count:
        _fail("trial_index must be between one and trial_count")
    data["parameters"] = dict(params)
    return data


def _candidate_payload(data: dict[str, object]) -> bytes:
    encoded = data.copy()
    for field in _INTS:
        encoded[field] = _typed(cast(int, data[field]))
    params = cast(dict[str, object], data["parameters"]).copy()
    params["starting_balance_usdt"] = _typed(
        cast(float, params["starting_balance_usdt"])
    )
    encoded["parameters"] = params
    return _canonical(encoded)


@contextmanager
def _connection(db_path: Path) -> Iterator[sqlite3.Connection]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path, isolation_level=None)
    try:
        connection.execute("PRAGMA busy_timeout=5000")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("""CREATE TABLE IF NOT EXISTS research_events_v1 (
            seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE,
            kind TEXT NOT NULL CHECK(kind IN ('input','candidate')),
            recorded_at_ts INTEGER NOT NULL, payload BLOB NOT NULL,
            experiment_id TEXT, hypothesis_id TEXT, candidate_revision TEXT,
            UNIQUE(experiment_id,hypothesis_id,candidate_revision))""")
        for operation in ("UPDATE", "DELETE"):
            connection.execute(f"""CREATE TRIGGER IF NOT EXISTS
                research_no_{operation.lower()}
                BEFORE {operation} ON research_events_v1 BEGIN
                SELECT RAISE(ABORT, 'research events are append-only'); END""")
        connection.execute("""CREATE TABLE IF NOT EXISTS research_lifecycle_v1 (
            seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT UNIQUE NOT NULL,
            kind TEXT NOT NULL CHECK(kind IN ('selection','inspection')),
            recorded_at_ts INTEGER NOT NULL, payload BLOB NOT NULL,
            selection_revision TEXT, experiment_id TEXT, hypothesis_id TEXT,
            UNIQUE(experiment_id,hypothesis_id,selection_revision))""")
        for operation in ("UPDATE", "DELETE"):
            connection.execute(f"""CREATE TRIGGER IF NOT EXISTS
                research_lifecycle_no_{operation.lower()}
                BEFORE {operation} ON research_lifecycle_v1 BEGIN
                SELECT RAISE(ABORT, 'research events are append-only'); END""")
        yield connection
    finally:
        connection.close()


def init_research_schema(db_path: Path) -> None:
    """Idempotently initialize the supplied metadata database."""
    with _connection(db_path):
        pass


def _references(
    connection: sqlite3.Connection,
    data: dict[str, object],
    seen: frozenset[str],
    seq: int | None = None,
) -> None:
    source = _replay(connection, cast(str, data["in_sample_input_id"]), seen)
    if source is None or source.kind != "input":
        _fail("candidate input event does not exist")
    recipe, document = _decode_input(_parse(source.canonical_bytes))
    snapshot = bind_controlled_fixture(recipe=recipe, document=document)
    start, end = (cast(int, data[field]) for field in _INTS[:2])
    for field, number in zip(_INTS[:2], (start, end), strict=True):
        if (number - snapshot.anchor_ts) % _DAY:
            _fail(f"{field} must align with the declared daily grid")
    validate_bar_coverage(
        ResearchInterval(start, end),
        timeframe=snapshot.timeframe,
        calendar=snapshot.calendar,
        anchor_ts=snapshot.anchor_ts,
        observations=[
            {"ts": row.ts, "close_ts": row.close_ts, "available_ts": row.available_ts}
            for row in snapshot.observations
            if start <= row.close_ts < end
        ],
    )
    parent_id = data["parent_candidate_id"]
    if parent_id is not None:
        parent = _replay(connection, cast(str, parent_id), seen)
        if parent is None or parent.kind != "candidate":
            _fail("parent candidate event does not exist")
        parent_data = _parse(parent.canonical_bytes)
        if any(parent_data[field] != data[field] for field in _INDEX[:2]):
            _fail("parent candidate does not match experiment and hypothesis")
        if seq is not None and parent.seq >= seq:
            _fail(_INTEGRITY)
    if seq is not None and source.seq >= seq:
        _fail(_INTEGRITY)


def _replay(
    connection: sqlite3.Connection, event_id: str, seen: frozenset[str] = frozenset()
) -> StoredResearchEvent | None:
    if event_id in seen:
        _fail(_INTEGRITY)
    row = connection.execute(
        """SELECT seq,event_id,kind,recorded_at_ts,payload,
        experiment_id,hypothesis_id,candidate_revision FROM research_events_v1
        WHERE event_id=?""",
        (event_id,),
    ).fetchone()
    if row is None:
        return None
    seq, identity, kind, timestamp, payload, *indexed = row
    if (
        not isinstance(payload, bytes)
        or _identity(payload) != identity
        or kind not in ("input", "candidate")
    ):
        _fail(_INTEGRITY)
    data = _parse(payload)
    if kind == "input":
        if indexed != [None, None, None]:
            _fail(_INTEGRITY)
        recipe, document = _decode_input(data)
        snapshot = bind_controlled_fixture(recipe=recipe, document=document)
        if _input_payload(recipe, snapshot) != payload:
            _fail(_INTEGRITY)
    else:
        if data.keys() != _FIELDS or indexed != [data[field] for field in _INDEX]:
            _fail(_INTEGRITY)
        try:
            for field in _INTS:
                data[field] = _decode_number(data[field], ("int",))
            params = _mapping(data["parameters"])
            params["starting_balance_usdt"] = _decode_number(
                params["starting_balance_usdt"], ("float",)
            )
            data["parameters"] = params
        except KeyError:
            _fail(_INTEGRITY)
        data = _candidate(data)
        if _candidate_payload(data) != payload:
            _fail(_INTEGRITY)
        _references(connection, data, seen | {event_id}, seq)
    return StoredResearchEvent(seq, identity, kind, timestamp, payload)


def _read_research_event(db_path: Path, *, event_id: str) -> StoredResearchEvent | None:
    """Private integrity replay only; future researcher access must be guarded."""
    with _connection(db_path) as connection:
        connection.execute("BEGIN")
        return _replay(connection, event_id)


def _capture(
    db_path: Path,
    kind: Literal["input", "candidate"],
    payload: bytes,
    data: dict[str, object] | None,
) -> StoredResearchEvent:
    identity = _identity(payload)
    with _connection(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            if data is not None:
                _references(connection, data, frozenset())
                prior = connection.execute(
                    """SELECT event_id FROM research_events_v1
                    WHERE experiment_id=? AND hypothesis_id=?
                    AND candidate_revision=?""",
                    tuple(data[field] for field in _INDEX),
                ).fetchone()
                if prior is not None:
                    original = _replay(connection, prior[0])
                    if original is None or original.event_id != identity:
                        _fail("candidate revision already has different frozen content")
                    connection.commit()
                    return original
            original = _replay(connection, identity)
            if original is not None:
                if original.kind != kind or original.canonical_bytes != payload:
                    _fail(_INTEGRITY)
                connection.commit()
                return original
            timestamp = time.time_ns() // 1_000_000
            cursor = connection.execute(
                """INSERT INTO research_events_v1
                (event_id,kind,recorded_at_ts,payload,experiment_id,hypothesis_id,
                 candidate_revision) VALUES (?,?,?,?,?,?,?)""",
                (
                    identity,
                    kind,
                    timestamp,
                    payload,
                    *(data[field] if data is not None else None for field in _INDEX),
                ),
            )
            assert cursor.lastrowid is not None
            result = StoredResearchEvent(
                cursor.lastrowid, identity, kind, timestamp, payload
            )
            connection.commit()
            return result
        except BaseException:
            connection.rollback()
            raise


def capture_fixture_input(
    db_path: Path, *, recipe: Mapping[str, object], document: Mapping[str, object]
) -> StoredResearchEvent:
    """Reproduce raw synthetic evidence before persisting full immutable content."""
    snapshot = bind_controlled_fixture(recipe=recipe, document=document)
    return _capture(db_path, "input", _input_payload(recipe, snapshot), None)


def freeze_research_candidate(
    db_path: Path, *, document: Mapping[str, object]
) -> StoredResearchEvent:
    """Freeze exact declared BuyHold inputs; this grants no selection authorization."""
    data = _candidate(document)
    return _capture(db_path, "candidate", _candidate_payload(data), data)


@dataclass(frozen=True, slots=True)
class ResearchLifecycleEvent:
    """Immutable logged selection or access, without an evaluation claim."""

    seq: int
    event_id: str
    kind: Literal["selection", "inspection"]
    recorded_at_ts: int
    canonical_bytes: bytes


@dataclass(frozen=True, slots=True)
class ResearchObservationAccess:
    """Only requested observations, released after the inspection commits."""

    event: ResearchLifecycleEvent
    observations: tuple[ResearchObservation, ...]


_SELECTION_FIELDS = frozenset(
    (
        "contract_version",
        "rule_id",
        "experiment_id",
        "hypothesis_id",
        "selection_revision",
        "selected_candidate_id",
        "considered_candidate_ids",
        "selection_criteria",
        "validation",
        "input_id",
        "oos_start_ts",
        "oos_end_ts",
    )
)
_SELECTION_INDEX = ("experiment_id", "hypothesis_id", "selection_revision")
_INSPECTION_FIELDS = frozenset(
    (
        "contract_version",
        "rule_id",
        "access_id",
        "action",
        "access_status",
        "actor",
        "declared_at_ts",
        "note",
        "input_id",
        "start_ts",
        "end_ts",
        "source_watermark",
        "members",
        "candidate_id",
        "selection_id",
    )
)
_History = list[tuple[ResearchLifecycleEvent, dict[str, object]]]


def _require_text(value: object, field: str) -> str:
    if not _text(value):
        _fail(f"{field} must be a nonempty UTF-8 string without NUL")
    return cast(str, value)


def _bounds(start: object, end: object, prefix: str) -> tuple[int, int]:
    first = _integer(start, f"{prefix}.start_ts")
    last = _integer(end, f"{prefix}.end_ts")
    if first >= last:
        _fail(f"{prefix}.start_ts must be less than {prefix}.end_ts")
    return first, last


def _selection(document: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(document, Mapping) or document.keys() != _SELECTION_FIELDS:
        _fail("selection must contain exactly the declared fields")
    data = dict(document)
    for field, token in (
        ("contract_version", "research-selection-v1"),
        ("rule_id", "phase18-temporal-v1"),
    ):
        if not isinstance(data[field], str) or data[field] != token:
            _fail(f"{field} must be {token}")
    for field in (
        *_SELECTION_INDEX,
        "selected_candidate_id",
        "input_id",
        "selection_criteria",
    ):
        _require_text(data[field], field)
    ids = data["considered_candidate_ids"]
    if (
        not isinstance(ids, list | tuple)
        or not ids
        or any(not _text(item) for item in ids)
        or len(set(ids)) != len(ids)
    ):
        _fail(
            "considered_candidate_ids must be a nonempty list or tuple "
            "of unique candidate IDs"
        )
    data["considered_candidate_ids"] = list(ids)
    validation = data["validation"]
    if validation is not None:
        if not isinstance(validation, Mapping) or validation.keys() != {
            "input_id",
            "start_ts",
            "end_ts",
        }:
            _fail(
                "validation must be null or contain exactly "
                "input_id, start_ts, and end_ts"
            )
        _require_text(validation["input_id"], "validation.input_id")
        _bounds(validation["start_ts"], validation["end_ts"], "validation")
        data["validation"] = dict(validation)
    start = _integer(data["oos_start_ts"], "oos_start_ts")
    end = _integer(data["oos_end_ts"], "oos_end_ts")
    if start >= end:
        _fail("oos.start_ts must be less than oos.end_ts")
    return data


def _candidate_data(event: StoredResearchEvent) -> dict[str, object]:
    data = _parse(event.canonical_bytes)
    for field in _INTS:
        data[field] = _decode_number(data[field], ("int",))
    return data


def _source(
    connection: sqlite3.Connection, identity: str, kind: str
) -> StoredResearchEvent:
    event = _replay(connection, identity)
    if event is None or event.kind != kind:
        _fail(f"research {kind} event does not exist")
    return event


def _membership(
    connection: sqlite3.Connection,
    identity: str,
    start: int,
    end: int,
    fields: tuple[str, str] = ("start_ts", "end_ts"),
) -> tuple[dict[str, object], tuple[ResearchObservation, ...], StoredResearchEvent]:
    event = _source(connection, identity, "input")
    recipe, document = _decode_input(_parse(event.canonical_bytes))
    snapshot = bind_controlled_fixture(recipe=recipe, document=document)
    for field, number in zip(fields, (start, end), strict=True):
        if (number - snapshot.anchor_ts) % _DAY:
            _fail(f"{field} must align with the declared daily grid")
    rows = tuple(row for row in snapshot.observations if start <= row.close_ts < end)
    validate_bar_coverage(
        ResearchInterval(start, end),
        timeframe=snapshot.timeframe,
        calendar=snapshot.calendar,
        anchor_ts=snapshot.anchor_ts,
        observations=[
            {"ts": row.ts, "close_ts": row.close_ts, "available_ts": row.available_ts}
            for row in rows
        ],
    )
    members = [
        [
            snapshot.venue,
            snapshot.symbol,
            snapshot.timeframe,
            "controlled-fixture:controlled-daily-linear-v1",
            _typed(row.ts),
            _typed(row.close_ts),
        ]
        for row in rows
    ]
    return (
        {
            "input_id": identity,
            "start_ts": _typed(start),
            "end_ts": _typed(end),
            "members": members,
        },
        rows,
        event,
    )


def _keys(membership: dict[str, object]) -> set[bytes]:
    return {_canonical(member) for member in cast(list[object], membership["members"])}


def _selection_payload(
    connection: sqlite3.Connection, data: dict[str, object]
) -> tuple[dict[str, object], list[StoredResearchEvent]]:
    candidates = [
        _source(connection, identity, "candidate")
        for identity in cast(list[str], data["considered_candidate_ids"])
    ]
    documents = [_candidate_data(event) for event in candidates]
    if any(
        any(item[field] != data[field] for field in _INDEX[:2]) for item in documents
    ):
        _fail("considered candidates must match experiment and hypothesis")
    if any(item["trial_count"] != len(candidates) for item in documents) or {
        item["trial_index"] for item in documents
    } != set(range(1, len(candidates) + 1)):
        _fail("considered candidates must enumerate the declared trial budget")
    if data["selected_candidate_id"] not in cast(
        list[str], data["considered_candidate_ids"]
    ):
        _fail("selected candidate must be considered")
    memberships: list[dict[str, object]] = []
    for event, item in zip(candidates, documents, strict=True):
        membership, _, _ = _membership(
            connection,
            cast(str, item["in_sample_input_id"]),
            cast(int, item["in_sample_start_ts"]),
            cast(int, item["in_sample_end_ts"]),
            _INTS[:2],
        )
        memberships.append({"role": "is", "candidate_id": event.event_id, **membership})
    encoded = data.copy()
    validation = cast(dict[str, object] | None, data["validation"])
    if validation is not None:
        membership, _, _ = _membership(
            connection,
            cast(str, validation["input_id"]),
            cast(int, validation["start_ts"]),
            cast(int, validation["end_ts"]),
            ("validation.start_ts", "validation.end_ts"),
        )
        memberships.append({"role": "validation", "candidate_id": None, **membership})
        encoded["validation"] = {
            key: _typed(cast(int, value)) if key != "input_id" else value
            for key, value in validation.items()
        }
    holdout, _, _ = _membership(
        connection,
        cast(str, data["input_id"]),
        cast(int, data["oos_start_ts"]),
        cast(int, data["oos_end_ts"]),
        ("oos_start_ts", "oos_end_ts"),
    )
    for field in ("oos_start_ts", "oos_end_ts"):
        encoded[field] = _typed(cast(int, data[field]))
    return {
        "contract_version": "research-selection-v1",
        "rule_id": "phase18-temporal-v1",
        "document": encoded,
        "candidate_bindings": [
            {
                "candidate_id": event.event_id,
                "candidate_payload": _parse(event.canonical_bytes),
            }
            for event in candidates
        ],
        "selection_memberships": memberships,
        "holdout_membership": holdout,
    }, candidates


def _selection_gate(
    connection: sqlite3.Connection,
    data: dict[str, object],
    payload: dict[str, object],
    candidates: list[StoredResearchEvent],
    history: _History,
) -> None:
    validation = cast(dict[str, object] | None, data["validation"])
    oos_start = cast(int, data["oos_start_ts"])
    documents = [_candidate_data(event) for event in candidates]
    if any(
        cast(int, item["in_sample_end_ts"])
        > (cast(int, validation["start_ts"]) if validation else oos_start)
        for item in documents
    ) or (validation is not None and cast(int, validation["end_ts"]) > oos_start):
        _fail("research ranges must be chronological and nonoverlapping")
    earlier = [
        item
        for event, item in history
        if event.kind == "selection"
        and all(
            cast(dict[str, object], item["document"])[field] == data[field]
            for field in _INDEX[:2]
        )
    ]
    if earlier:
        previous = cast(dict[str, object], earlier[-1]["document"])
        if previous["selection_criteria"] != data["selection_criteria"]:
            target = previous["selected_candidate_id"]
            current = data["selected_candidate_id"]
            linked = False
            while current != target:
                event = _source(connection, cast(str, current), "candidate")
                current = _candidate_data(event)["parent_candidate_id"]
                if current is None:
                    break
                if current == target:
                    linked = True
            if not linked:
                _fail(
                    "changed selection criteria require a new candidate revision "
                    "with prior selection lineage"
                )
    inspections = [item for event, item in history if event.kind == "inspection"]
    if validation is None:
        if any(
            item["action"] == "validation"
            and item["candidate_id"]
            in cast(list[str], data["considered_candidate_ids"])
            for item in inspections
        ):
            _fail("validation absence conflicts with recorded validation access")
    else:
        validation_members = cast(
            list[dict[str, object]], payload["selection_memberships"]
        )[-1]
        keys = _keys(validation_members)
        for candidate in candidates:
            if not any(
                item["action"] == "validation"
                and item["candidate_id"] == candidate.event_id
                and all(
                    item[field] == validation_members[field]
                    for field in ("input_id", "start_ts", "end_ts")
                )
                for item in inspections
            ):
                _fail(
                    "validation access must precede final selection "
                    "for every considered candidate"
                )
        if any(
            candidate.seq
            > cast(int, _decode_number(item["source_watermark"], ("int",)))
            for candidate in candidates
            for item in inspections
            if keys & _keys(item)
        ):
            _fail("validation was inspected before candidate freeze")
    holdout = _keys(cast(dict[str, object], payload["holdout_membership"]))
    if any(
        holdout & _keys(item)
        for item in cast(list[dict[str, object]], payload["selection_memberships"])
    ):
        _fail("selection data must not overlap final holdout observations")
    if any(holdout & _keys(item) for item in inspections):
        _fail("final holdout observations were already inspected")


def _validation_gate(
    connection: sqlite3.Connection,
    candidate: StoredResearchEvent,
    membership: dict[str, object],
    start: int,
    history: _History,
) -> None:
    if cast(int, _candidate_data(candidate)["in_sample_end_ts"]) > start:
        _fail("research ranges must be chronological and nonoverlapping")
    keys = _keys(membership)
    if any(
        keys
        & (
            _keys(cast(dict[str, object], item["holdout_membership"]))
            if event.kind == "selection"
            else _keys(item)
        )
        for event, item in history
        if event.kind == "selection" or item["action"] in ("oos", "external")
    ):
        _fail("validation observations overlap a final holdout or OOS inspection")
    if any(
        candidate.seq > cast(int, _decode_number(item["source_watermark"], ("int",)))
        for event, item in history
        if event.kind == "inspection" and keys & _keys(item)
    ):
        _fail("validation was inspected before candidate freeze")


def _inspection_payload(
    connection: sqlite3.Connection,
    *,
    action: str,
    actor: str,
    input_id: str,
    start: int,
    end: int,
    candidate_id: str | None,
    selection_id: str | None,
    declared_at: int | None,
    note: str | None,
    access_id: str,
    watermark: int,
    history: _History,
) -> tuple[dict[str, object], tuple[ResearchObservation, ...]]:
    membership, observations, source = _membership(connection, input_id, start, end)
    if source.seq > watermark:
        _fail(_INTEGRITY)
    if action == "validation":
        candidate = _source(connection, cast(str, candidate_id), "candidate")
        if candidate.seq > watermark:
            _fail(_INTEGRITY)
        _validation_gate(connection, candidate, membership, start, history)
    elif action == "oos":
        selections = [
            (event, item)
            for event, item in history
            if event.event_id == selection_id and event.kind == "selection"
        ]
        if not selections:
            _fail("research selection event does not exist")
        holdout = selections[0][1]["holdout_membership"]
        if membership != holdout:
            _fail(_INTEGRITY)
        for item in cast(
            list[dict[str, object]], selections[0][1]["selection_memberships"]
        ):
            if (
                _source(connection, cast(str, item["input_id"]), "input").seq
                > watermark
            ):
                _fail(_INTEGRITY)
        # Reproduction replays every bound source; all must predate this access.
        for binding in cast(
            list[dict[str, object]], selections[0][1]["candidate_bindings"]
        ):
            candidate = _source(
                connection, cast(str, binding["candidate_id"]), "candidate"
            )
            if candidate.seq > watermark:
                _fail(_INTEGRITY)
    repeat = any(
        event.kind == "inspection"
        and item["action"] == action
        and (
            (action == "oos" and item["selection_id"] == selection_id)
            or (
                action == "validation"
                and item["candidate_id"] == candidate_id
                and all(
                    item[field] == membership[field]
                    for field in ("input_id", "start_ts", "end_ts")
                )
            )
        )
        for event, item in history
    )
    return {
        "contract_version": "research-inspection-v1",
        "rule_id": "phase18-temporal-v1",
        "access_id": access_id,
        "action": action,
        "access_status": "external_declaration"
        if action == "external"
        else "repeat_access"
        if repeat
        else "first_access",
        "actor": actor,
        "declared_at_ts": None if declared_at is None else _typed(declared_at),
        "note": note,
        **membership,
        "source_watermark": _typed(watermark),
        "candidate_id": candidate_id,
        "selection_id": selection_id,
    }, observations


def _decode_selection(payload: dict[str, object]) -> dict[str, object]:
    if payload.keys() != {
        "contract_version",
        "rule_id",
        "document",
        "candidate_bindings",
        "selection_memberships",
        "holdout_membership",
    }:
        _fail(_INTEGRITY)
    data = _mapping(payload["document"])
    try:
        for field in ("oos_start_ts", "oos_end_ts"):
            data[field] = _decode_number(data[field], ("int",))
        if data["validation"] is not None:
            validation = _mapping(data["validation"])
            for field in ("start_ts", "end_ts"):
                validation[field] = _decode_number(validation[field], ("int",))
            data["validation"] = validation
    except KeyError:
        _fail(_INTEGRITY)
    return _selection(data)


def _history(connection: sqlite3.Connection) -> _History:
    # Replay the source ledger as well, before permitting any lifecycle release.
    for (identity,) in connection.execute(
        "SELECT event_id FROM research_events_v1 ORDER BY seq"
    ):
        _replay(connection, identity)
    token = _LIFECYCLE_REPLAY.set(True)
    try:
        return _replay_lifecycle(connection)
    except (KeyError, TypeError, AttributeError):
        _fail(_INTEGRITY)
    finally:
        _LIFECYCLE_REPLAY.reset(token)


def _replay_lifecycle(connection: sqlite3.Connection) -> _History:
    history: _History = []
    for row in connection.execute("""SELECT seq,event_id,kind,recorded_at_ts,payload,
             experiment_id,hypothesis_id,selection_revision
             FROM research_lifecycle_v1 ORDER BY seq"""):
        seq, identity, kind, timestamp, raw, *indexed = row
        if (
            not isinstance(raw, bytes)
            or _identity(raw) != identity
            or kind not in ("selection", "inspection")
        ):
            _fail(_INTEGRITY)
        payload = _parse(raw)
        if kind == "selection":
            data = _decode_selection(payload)
            if indexed != [data[field] for field in _SELECTION_INDEX]:
                _fail(_INTEGRITY)
            expected, candidates = _selection_payload(connection, data)
            _selection_gate(connection, data, expected, candidates, history)
        else:
            if indexed != [None, None, None] or payload.keys() != _INSPECTION_FIELDS:
                _fail(_INTEGRITY)
            try:
                action = payload["action"]
                if action not in ("validation", "oos", "external"):
                    _fail(_INTEGRITY)
                access_id = payload["access_id"]
                if (
                    not isinstance(access_id, str)
                    or re.fullmatch("[0-9a-f]{32}", access_id) is None
                ):
                    _fail(_INTEGRITY)
                if not _text(payload["actor"]) or not _text(payload["input_id"]):
                    _fail(_INTEGRITY)
                start = cast(int, _decode_number(payload["start_ts"], ("int",)))
                end = cast(int, _decode_number(payload["end_ts"], ("int",)))
                watermark = cast(
                    int, _decode_number(payload["source_watermark"], ("int",))
                )
                maximum = connection.execute(
                    "SELECT COALESCE(MAX(seq),0) FROM research_events_v1"
                ).fetchone()[0]
                if start >= end or not 0 <= watermark <= maximum:
                    _fail(_INTEGRITY)
                declared = payload["declared_at_ts"]
                declared_at = (
                    None
                    if declared is None
                    else cast(int, _decode_number(declared, ("int",)))
                )
                if action == "external":
                    if (
                        not _text(payload["note"])
                        or payload["candidate_id"] is not None
                        or payload["selection_id"] is not None
                    ):
                        _fail(_INTEGRITY)
                elif (
                    declared is not None
                    or payload["note"] is not None
                    or (
                        action == "validation"
                        and (
                            not _text(payload["candidate_id"])
                            or payload["selection_id"] is not None
                        )
                    )
                    or (
                        action == "oos"
                        and (
                            not _text(payload["selection_id"])
                            or payload["candidate_id"] is not None
                        )
                    )
                ):
                    _fail(_INTEGRITY)
                expected, _ = _inspection_payload(
                    connection,
                    action=action,
                    actor=cast(str, payload["actor"]),
                    input_id=cast(str, payload["input_id"]),
                    start=start,
                    end=end,
                    candidate_id=cast(str | None, payload["candidate_id"]),
                    selection_id=cast(str | None, payload["selection_id"]),
                    declared_at=declared_at,
                    note=cast(str | None, payload["note"]),
                    access_id=access_id,
                    watermark=watermark,
                    history=history,
                )
            except KeyError:
                _fail(_INTEGRITY)
        if _canonical(expected) != raw:
            _fail(_INTEGRITY)
        history.append(
            (ResearchLifecycleEvent(seq, identity, kind, timestamp, raw), payload)
        )
    return history


def _append_lifecycle(
    connection: sqlite3.Connection,
    kind: Literal["selection", "inspection"],
    payload: dict[str, object],
    data: dict[str, object] | None = None,
) -> ResearchLifecycleEvent:
    raw = _canonical(payload)
    identity = _identity(raw)
    timestamp = time.time_ns() // 1_000_000
    cursor = connection.execute(
        """INSERT INTO research_lifecycle_v1
        (event_id,kind,recorded_at_ts,payload,experiment_id,hypothesis_id,selection_revision)
        VALUES (?,?,?,?,?,?,?)""",
        (
            identity,
            kind,
            timestamp,
            raw,
            *(data[field] if data is not None else None for field in _SELECTION_INDEX),
        ),
    )
    assert cursor.lastrowid is not None
    return ResearchLifecycleEvent(cursor.lastrowid, identity, kind, timestamp, raw)


@contextmanager
def _lifecycle_transaction(
    db_path: Path,
) -> Iterator[tuple[sqlite3.Connection, _History]]:
    with _connection(db_path) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            yield connection, _history(connection)
            connection.commit()
        except BaseException:
            connection.rollback()
            raise


def freeze_final_selection(
    db_path: Path, *, document: Mapping[str, object]
) -> ResearchLifecycleEvent:
    """Freeze the declared trial budget and holdout before any logged inspection.

    Criteria and trial counts are declarations, not proof of all human trials.
    Synthetic truth and unreported outside inspection remain unverified.
    """
    data = _selection(document)
    with _lifecycle_transaction(db_path) as (connection, history):
        payload, candidates = _selection_payload(connection, data)
        original = next(
            (
                (event, item)
                for event, item in history
                if event.kind == "selection"
                and all(
                    cast(dict[str, object], item["document"])[field] == data[field]
                    for field in _SELECTION_INDEX
                )
            ),
            None,
        )
        if original is not None:
            if original[0].canonical_bytes != _canonical(payload):
                _fail("selection revision already has different frozen content")
            result = original[0]
        else:
            _selection_gate(connection, data, payload, candidates, history)
            result = _append_lifecycle(connection, "selection", payload, data)
    return result


def _access(
    connection: sqlite3.Connection,
    history: _History,
    *,
    action: str,
    input_id: str,
    start: int,
    end: int,
    actor: str,
    candidate_id: str | None = None,
    selection_id: str | None = None,
    declared_at: int | None = None,
    note: str | None = None,
) -> ResearchObservationAccess:
    watermark = connection.execute(
        "SELECT COALESCE(MAX(seq),0) FROM research_events_v1"
    ).fetchone()[0]
    payload, observations = _inspection_payload(
        connection,
        action=action,
        actor=actor,
        input_id=input_id,
        start=start,
        end=end,
        candidate_id=candidate_id,
        selection_id=selection_id,
        declared_at=declared_at,
        note=note,
        access_id=uuid4().hex,
        watermark=watermark,
        history=history,
    )
    return ResearchObservationAccess(
        _append_lifecycle(connection, "inspection", payload), observations
    )


def access_validation_observations(
    db_path: Path,
    *,
    candidate_id: str,
    input_id: str,
    start_ts: int,
    end_ts: int,
    actor: str,
) -> ResearchObservationAccess:
    """Log each development access to this frozen candidate's explicit range."""
    for field, value in (
        ("candidate_id", candidate_id),
        ("input_id", input_id),
        ("actor", actor),
    ):
        _require_text(value, field)
    start, end = _bounds(start_ts, end_ts, "validation")
    with _lifecycle_transaction(db_path) as (connection, history):
        _source(connection, candidate_id, "candidate")
        result = _access(
            connection,
            history,
            action="validation",
            input_id=input_id,
            start=start,
            end=end,
            actor=actor,
            candidate_id=candidate_id,
        )
    return result


def access_oos_observations(
    db_path: Path, *, selection_id: str, actor: str
) -> ResearchObservationAccess:
    """Commit distinct first/repeat inspection before releasing only the holdout.

    Logged access is neither an independent trial nor a completed evaluation.
    """
    _require_text(selection_id, "selection_id")
    _require_text(actor, "actor")
    with _lifecycle_transaction(db_path) as (connection, history):
        selection = next(
            (
                item
                for event, item in history
                if event.event_id == selection_id and event.kind == "selection"
            ),
            None,
        )
        if selection is None:
            _fail("research selection event does not exist")
        membership = cast(dict[str, object], selection["holdout_membership"])
        result = _access(
            connection,
            history,
            action="oos",
            input_id=cast(str, membership["input_id"]),
            start=cast(int, _decode_number(membership["start_ts"], ("int",))),
            end=cast(int, _decode_number(membership["end_ts"], ("int",))),
            actor=actor,
            selection_id=selection_id,
        )
    return result


def record_external_inspection(
    db_path: Path,
    *,
    input_id: str,
    start_ts: int,
    end_ts: int,
    actor: str,
    declared_at_ts: int | None,
    note: str,
) -> ResearchLifecycleEvent:
    """Append an attributed outside-inspection claim; claimed time cannot undo it."""
    for field, value in (("input_id", input_id), ("actor", actor), ("note", note)):
        _require_text(value, field)
    start = _integer(start_ts, "start_ts")
    end = _integer(end_ts, "end_ts")
    if declared_at_ts is not None:
        _integer(declared_at_ts, "declared_at_ts")
    if start >= end:
        _fail("inspection.start_ts must be less than inspection.end_ts")
    with _lifecycle_transaction(db_path) as (connection, history):
        result = _access(
            connection,
            history,
            action="external",
            input_id=input_id,
            start=start,
            end=end,
            actor=actor,
            declared_at=declared_at_ts,
            note=note,
        ).event
    return result
