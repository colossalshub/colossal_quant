"""Actual SQLite durability, replay, ordering and contender regressions."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from pathlib import Path
from threading import Barrier
from typing import Literal, cast

import pytest

from quant.data import research_store as store
from quant.engine.research_fixture import create_controlled_fixture

DAY = 86_400_000


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()


def wire(recipe: dict[str, object]) -> dict[str, object]:
    """Independent raw recipe expansion with separately constructed provenance."""
    typed = {
        key: {"kind": "int", "value": hex(value)} if isinstance(value, int) else value
        for key, value in recipe.items()
    }
    revision = "sha256:" + hashlib.sha256(canonical(typed)).hexdigest()
    rows = []
    for index in range(cast(int, recipe["observation_count"])):
        ts = cast(int, recipe["start_open_ts"]) + index * DAY
        price = cast(int, recipe["price_start"]) + index * cast(
            int, recipe["price_step"]
        )
        rows.append(
            {
                "ts": ts,
                "close_ts": ts + DAY,
                "available_ts": ts + DAY,
                "open": price,
                "high": price,
                "low": price,
                "close": price,
                "volume": recipe["volume"],
                "source_id": "controlled-fixture:controlled-daily-linear-v1",
                "revision_id": revision,
                "provenance": {
                    "kind": "controlled_fixture",
                    "reference": revision,
                    "declared_by": None,
                },
            }
        )
    return {
        "contract_version": "research-input-v1",
        "rule_id": "phase18-temporal-v1",
        "venue": "binance",
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "calendar": "continuous_utc_fixed",
        "anchor_ts": recipe["anchor_ts"],
        "observations": rows,
    }


@pytest.fixture
def recipe() -> dict[str, object]:
    return {
        "recipe_version": "controlled-daily-linear-v1",
        "rule_id": "phase18-temporal-v1",
        "anchor_ts": 0,
        "start_open_ts": 0,
        "observation_count": 4,
        "price_start": 100,
        "price_step": 10,
        "volume": 2,
    }


@pytest.fixture
def db(tmp_path: Path) -> Path:
    return tmp_path / "nested" / "metadata.sqlite"


def capture(db: Path, recipe: dict[str, object]) -> store.StoredResearchEvent:
    return store.capture_fixture_input(db, recipe=recipe, document=wire(recipe))


def candidate(input_id: str) -> dict[str, object]:
    return {
        "contract_version": "research-candidate-v1",
        "rule_id": "phase18-temporal-v1",
        "experiment_id": "experiment",
        "hypothesis_id": "hypothesis",
        "candidate_revision": "r1",
        "parent_candidate_id": None,
        "strategy_version": "v1",
        "strategy": "buy_hold",
        "parameters": {
            "starting_balance_usdt": 100000.0,
            "trade_size": "1.0000000",
            "deploy_pct": "0",
            "maker_fee": "0.001",
            "taker_fee": "0.001",
        },
        "code_id": "a" * 40,
        "seed": None,
        "fitted_artifacts": (),
        "in_sample_input_id": input_id,
        "in_sample_start_ts": DAY,
        "in_sample_end_ts": 3 * DAY,
        "trial_index": 1,
        "trial_count": 3,
    }


def count(db: Path) -> int:
    with sqlite3.connect(db) as connection:
        return cast(
            int,
            connection.execute("SELECT count(*) FROM research_events_v1").fetchone()[0],
        )


def test_roundtrip_exact_identity_durable_and_idempotent(
    db: Path, recipe: dict[str, object]
) -> None:
    event = capture(db, recipe)
    expected_input = canonical(
        {
            "contract_version": "research-store-input-v1",
            "recipe": {
                key: {"kind": "int", "value": hex(value)}
                if isinstance(value, int)
                else value
                for key, value in recipe.items()
            },
            "snapshot": json.loads(create_controlled_fixture(recipe).canonical_bytes),
        }
    )
    assert event.canonical_bytes == expected_input
    assert event.event_id == "sha256:" + hashlib.sha256(expected_input).hexdigest()
    document = candidate(event.event_id)
    frozen = store.freeze_research_candidate(db, document=document)
    expected = {**document, "fitted_artifacts": []}
    for field in (
        "in_sample_start_ts",
        "in_sample_end_ts",
        "trial_index",
        "trial_count",
    ):
        expected[field] = {"kind": "int", "value": hex(cast(int, document[field]))}
    params = cast(dict[str, object], document["parameters"]).copy()
    params["starting_balance_usdt"] = {"kind": "float", "value": (100000.0).hex()}
    expected["parameters"] = params
    assert frozen.canonical_bytes == canonical(expected)
    assert (
        frozen.event_id == "sha256:" + hashlib.sha256(canonical(expected)).hexdigest()
    )
    assert event.seq == 1 and frozen.seq == 2
    store.init_research_schema(db)
    assert store._read_research_event(db, event_id=frozen.event_id) == frozen
    assert capture(db, recipe) == event
    assert store.freeze_research_candidate(db, document=document) == frozen
    assert count(db) == 2
    assert not hasattr(frozen, "eligible")
    with pytest.raises(FrozenInstanceError):
        frozen.__setattr__("seq", 10)
    assert store._read_research_event(db, event_id="missing") is None


@pytest.mark.parametrize("field", ["code_id", "parameters", "in_sample_input_id"])
def test_changed_content_same_revision_rejects_new_revision_preserved(
    db: Path,
    recipe: dict[str, object],
    field: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = capture(db, recipe)
    original = store.freeze_research_candidate(db, document=candidate(source.event_id))
    revised = candidate(source.event_id)
    if field == "code_id":
        revised[field] = "b" * 40
    elif field == "parameters":
        revised[field] = {**cast(dict[str, object], revised[field]), "trade_size": "2"}
    else:
        revised[field] = capture(db, {**recipe, "price_start": 200}).event_id
    caplog.clear()
    with pytest.raises(
        ValueError, match="^candidate revision already has different frozen content$"
    ):
        store.freeze_research_candidate(db, document=revised)
    assert [(record.name, record.message) for record in caplog.records] == [
        (
            "quant.data.research_store",
            "candidate revision already has different frozen content",
        )
    ]
    revised["candidate_revision"] = "r2"
    revised["parent_candidate_id"] = original.event_id
    second = store.freeze_research_candidate(db, document=revised)
    assert second.event_id != original.event_id
    assert store._read_research_event(db, event_id=original.event_id) == original
    assert store._read_research_event(db, event_id=second.event_id) == second


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"trial_index": True}, "trial_index must be an integer excluding bool"),
        ({"trial_count": 0}, "trial_count must be positive"),
        ({"trial_index": 4}, "trial_index must be between one and trial_count"),
        (
            {"seed": 1},
            "seed and fitted_artifacts must be explicitly absent for buy_hold",
        ),
        (
            {"fitted_artifacts": ["model"]},
            "seed and fitted_artifacts must be explicitly absent for buy_hold",
        ),
        (
            {"in_sample_start_ts": DAY + 1},
            "in_sample_start_ts must align with the declared daily grid",
        ),
        (
            {"in_sample_end_ts": 7 * DAY},
            "observations do not provide complete expected bar coverage",
        ),
        (
            {"in_sample_start_ts": 6 * DAY, "in_sample_end_ts": 7 * DAY},
            "observations must contain at least one stage observation",
        ),
        ({"in_sample_input_id": "missing"}, "candidate input event does not exist"),
        ({"parent_candidate_id": "missing"}, "parent candidate event does not exist"),
    ],
)
def test_candidate_rejection_has_no_insert(
    db: Path,
    recipe: dict[str, object],
    changes: dict[str, object],
    message: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = capture(db, recipe)
    caplog.clear()
    with pytest.raises(ValueError) as error:
        store.freeze_research_candidate(
            db, document={**candidate(source.event_id), **changes}
        )
    assert str(error.value) == message
    assert len(caplog.records) == 1 and caplog.records[0].message == message
    assert count(db) == 1


def test_parent_group_and_wrong_kinds(db: Path, recipe: dict[str, object]) -> None:
    source = capture(db, recipe)
    parent = store.freeze_research_candidate(db, document=candidate(source.event_id))
    data = {
        **candidate(source.event_id),
        "candidate_revision": "r2",
        "parent_candidate_id": parent.event_id,
        "hypothesis_id": "other",
    }
    with pytest.raises(
        ValueError, match="parent candidate does not match experiment and hypothesis"
    ):
        store.freeze_research_candidate(db, document=data)
    data["parent_candidate_id"] = source.event_id
    with pytest.raises(ValueError, match="parent candidate event does not exist"):
        store.freeze_research_candidate(db, document=data)
    data["in_sample_input_id"] = parent.event_id
    with pytest.raises(ValueError, match="candidate input event does not exist"):
        store.freeze_research_candidate(db, document=data)
    assert count(db) == 2


@pytest.mark.parametrize(
    "size", ["1", "1.0", "1.000000000000000000000", "1.234567000", "10e-7"]
)
def test_runner_equivalent_decimal_precision(
    db: Path, recipe: dict[str, object], size: str
) -> None:
    data = candidate(capture(db, recipe).event_id)
    cast(dict[str, object], data["parameters"])["trade_size"] = size
    frozen = store.freeze_research_candidate(db, document=data)
    assert json.loads(frozen.canonical_bytes)["parameters"]["trade_size"] == size
    assert store._read_research_event(db, event_id=frozen.event_id) == frozen


def test_validation_precedence_and_precision(
    db: Path, recipe: dict[str, object]
) -> None:
    data = candidate(capture(db, recipe).event_id)
    data.update(contract_version="wrong", rule_id="wrong", seed=1)
    with pytest.raises(
        ValueError, match="contract_version must be research-candidate-v1"
    ):
        store.freeze_research_candidate(db, document=data)
    data = candidate(capture(db, recipe).event_id)
    params = cast(dict[str, object], data["parameters"])
    params.update(trade_size="0.0000001", maker_fee=-1)
    with pytest.raises(
        ValueError, match="positive and exactly representable at 6 decimal places"
    ):
        store.freeze_research_candidate(db, document=data)
    params.update(trade_size="1", maker_fee=0)
    with pytest.raises(
        ValueError, match="parameters.maker_fee must be a finite decimal string"
    ):
        store.freeze_research_candidate(db, document=data)
    assert count(db) == 1


def test_huge_hex_and_tampered_source_binder(
    db: Path, recipe: dict[str, object], caplog: pytest.LogCaptureFixture
) -> None:
    huge = 1 << 16000
    recipe.update(anchor_ts=-huge, start_open_ts=-huge, price_start=huge, volume=huge)
    event = capture(db, recipe)
    assert store._read_research_event(db, event_id=event.event_id) == event
    assert json.loads(event.canonical_bytes)["recipe"]["anchor_ts"]["value"] == hex(
        -huge
    )
    document = wire(recipe)
    rows = cast(list[dict[str, object]], document["observations"])
    rows[0]["volume"] = huge + 1
    caplog.clear()
    with pytest.raises(
        ValueError, match="document does not match the reproduced controlled fixture"
    ):
        store.capture_fixture_input(db, recipe=recipe, document=document)
    assert len(caplog.records) == 1
    assert caplog.records[0].name == "quant.engine.research_fixture"
    assert count(db) == 1


def test_close_float_kind_cannot_collide(db: Path, recipe: dict[str, object]) -> None:
    document = wire(recipe)
    row = cast(list[dict[str, object]], document["observations"])[0]
    row["close"] = 100.000000001
    row["high"] = 100.000000001
    with pytest.raises(
        ValueError, match="document does not match the reproduced controlled fixture"
    ):
        store.capture_fixture_input(db, recipe=recipe, document=document)
    assert capture(db, recipe).seq == 1


def test_triggers_block_update_delete(db: Path, recipe: dict[str, object]) -> None:
    capture(db, recipe)
    with sqlite3.connect(db) as connection:
        for sql in (
            "UPDATE research_events_v1 SET recorded_at_ts=0",
            "DELETE FROM research_events_v1",
        ):
            with pytest.raises(
                sqlite3.IntegrityError, match="research events are append-only"
            ):
                connection.execute(sql)
    assert count(db) == 1


def corrupt(
    db: Path,
    event_id: str,
    *,
    payload: bytes | None = None,
    assignment: str | None = None,
) -> str:
    """Simulate a direct SQLite owner bypassing append-only application triggers."""
    with sqlite3.connect(db) as connection:
        connection.execute("DROP TRIGGER research_no_update")
        if payload is not None:
            new_id = "sha256:" + hashlib.sha256(payload).hexdigest()
            connection.execute(
                "UPDATE research_events_v1 SET event_id=?,payload=? WHERE event_id=?",
                (new_id, payload, event_id),
            )
            return new_id
        assert assignment is not None
        connection.execute(
            f"UPDATE research_events_v1 SET {assignment} WHERE event_id=?", (event_id,)
        )
    return event_id


@pytest.mark.parametrize(
    "change",
    [
        "digest",
        "kind",
        "input_index",
        "candidate_index",
        "whitespace",
        "duplicate",
        "hex",
        "tag",
    ],
)
def test_corruption_integrity_replay(
    db: Path, recipe: dict[str, object], change: str, caplog: pytest.LogCaptureFixture
) -> None:
    source = capture(db, recipe)
    frozen = store.freeze_research_candidate(db, document=candidate(source.event_id))
    event = frozen if change == "candidate_index" else source
    if change == "digest":
        identity = corrupt(db, event.event_id, assignment="payload=X'7B7D'")
    elif change == "kind":
        identity = corrupt(db, event.event_id, assignment="kind='candidate'")
    elif change in ("input_index", "candidate_index"):
        identity = corrupt(db, event.event_id, assignment="experiment_id='tampered'")
    else:
        payload = event.canonical_bytes
        if change == "whitespace":
            payload += b"\n"
        elif change == "duplicate":
            payload = b'{"contract_version":"research-store-input-v1",' + payload[1:]
        elif change == "hex":
            payload = payload.replace(b'"0x0"', b'"0X0"')
        else:
            payload = payload.replace(b'"kind":"int"', b'"kind":"unknown"', 1)
        identity = corrupt(db, event.event_id, payload=payload)
    caplog.clear()
    with pytest.raises(
        ValueError, match="^stored research event failed integrity validation$"
    ):
        store._read_research_event(db, event_id=identity)
    assert len(caplog.records) == 1
    assert count(db) == 2


def test_valid_encoding_binder_failure_propagates_once(
    db: Path, recipe: dict[str, object], caplog: pytest.LogCaptureFixture
) -> None:
    source = capture(db, recipe)
    payload = json.loads(source.canonical_bytes)
    payload["snapshot"]["observations"][0]["volume"]["value"] = "0x3"
    identity = corrupt(db, source.event_id, payload=canonical(payload))
    caplog.clear()
    with pytest.raises(
        ValueError, match="document does not match the reproduced controlled fixture"
    ):
        store._read_research_event(db, event_id=identity)
    assert [(record.name, record.message) for record in caplog.records] == [
        (
            "quant.engine.research_fixture",
            "document does not match the reproduced controlled fixture",
        )
    ]


def test_server_seq_and_original_timestamp(
    db: Path, recipe: dict[str, object], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(store.time, "time_ns", lambda: 900_000_000)
    source = capture(db, recipe)
    monkeypatch.setattr(store.time, "time_ns", lambda: 100_000_000)
    frozen = store.freeze_research_candidate(db, document=candidate(source.event_id))
    assert frozen.seq > source.seq and frozen.recorded_at_ts < source.recorded_at_ts
    assert capture(db, recipe) == source
    assert (
        store.freeze_research_candidate(db, document=candidate(source.event_id))
        == frozen
    )


@pytest.mark.parametrize("conflict", [False, True])
def test_concurrent_contenders(
    db: Path, recipe: dict[str, object], conflict: bool
) -> None:
    source = capture(db, recipe)
    barrier = Barrier(2)

    def contend(code: str) -> store.StoredResearchEvent | str:
        data = {**candidate(source.event_id), "code_id": code}
        barrier.wait()
        try:
            return store.freeze_research_candidate(db, document=data)
        except ValueError as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(contend, "a" * 40),
            pool.submit(contend, ("b" if conflict else "a") * 40),
        ]
        results = [future.result() for future in futures]
    if conflict:
        assert (
            sum(isinstance(result, store.StoredResearchEvent) for result in results)
            == 1
        )
        assert "candidate revision already has different frozen content" in results
    else:
        assert results[0] == results[1]
    assert count(db) == 2


def test_sqlite_failure_rolls_back_and_surfaces(
    db: Path, recipe: dict[str, object], caplog: pytest.LogCaptureFixture
) -> None:
    source = capture(db, recipe)
    with sqlite3.connect(db) as connection:
        connection.execute("""CREATE TRIGGER fail_candidate
            BEFORE INSERT ON research_events_v1
            WHEN NEW.kind='candidate' BEGIN
            SELECT RAISE(ABORT,'injected insert failure'); END""")
    caplog.clear()
    with pytest.raises(sqlite3.IntegrityError, match="injected insert failure"):
        store.freeze_research_candidate(db, document=candidate(source.event_id))
    assert not caplog.records
    assert count(db) == 1
    with sqlite3.connect(db) as connection:
        connection.execute("DROP TRIGGER fail_candidate")
    assert (
        store.freeze_research_candidate(db, document=candidate(source.event_id)).seq
        == 2
    )


@pytest.mark.parametrize("raw", [b"NaN", b"Infinity", b"1.0", b"1" * 5000])
def test_bare_json_numbers_are_redacted_integrity_failures(
    db: Path,
    recipe: dict[str, object],
    caplog: pytest.LogCaptureFixture,
    raw: bytes,
) -> None:
    source = capture(db, recipe)
    payload = source.canonical_bytes.replace(
        b'"anchor_ts":{"kind":"int","value":"0x0"}', b'"anchor_ts":' + raw, 1
    )
    identity = corrupt(db, source.event_id, payload=payload)
    caplog.clear()
    with pytest.raises(
        ValueError, match="^stored research event failed integrity validation$"
    ):
        store._read_research_event(db, event_id=identity)
    assert len(caplog.records) == 1
    assert (
        caplog.records[0].message == "stored research event failed integrity validation"
    )


def test_commit_failure_rolls_back_original_exception(
    db: Path,
    recipe: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = capture(db, recipe)
    original_connect = sqlite3.connect
    failure = sqlite3.OperationalError("injected commit failure")

    class FailCommit(sqlite3.Connection):
        def commit(self) -> None:
            raise failure

    def connect(path: Path, *, isolation_level: None) -> sqlite3.Connection:
        return original_connect(
            path, isolation_level=isolation_level, factory=FailCommit
        )

    monkeypatch.setattr(store.sqlite3, "connect", connect)
    caplog.clear()
    with pytest.raises(sqlite3.OperationalError) as error:
        store.freeze_research_candidate(db, document=candidate(source.event_id))
    assert error.value is failure
    assert not caplog.records
    monkeypatch.setattr(store.sqlite3, "connect", original_connect)
    assert count(db) == 1
    assert (
        store.freeze_research_candidate(db, document=candidate(source.event_id)).seq
        == 2
    )


def test_failed_reference_revalidation_rolls_back(
    db: Path,
    recipe: dict[str, object],
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = capture(db, recipe)
    payload = json.loads(source.canonical_bytes)
    payload["snapshot"]["observations"][0]["volume"]["value"] = "0x3"
    identity = corrupt(db, source.event_id, payload=canonical(payload))
    caplog.clear()
    with pytest.raises(
        ValueError, match="document does not match the reproduced controlled fixture"
    ):
        store.freeze_research_candidate(db, document=candidate(identity))
    assert count(db) == 1
    assert len(caplog.records) == 1


def test_replay_requires_earlier_committed_parent(
    db: Path, recipe: dict[str, object]
) -> None:
    source = capture(db, recipe)
    parent = store.freeze_research_candidate(db, document=candidate(source.event_id))
    child = store.freeze_research_candidate(
        db,
        document={
            **candidate(source.event_id),
            "candidate_revision": "r2",
            "parent_candidate_id": parent.event_id,
        },
    )
    corrupt(db, parent.event_id, assignment="seq=100")
    with pytest.raises(
        ValueError, match="^stored research event failed integrity validation$"
    ):
        store._read_research_event(db, event_id=child.event_id)


def test_read_initializes_missing_schema(db: Path) -> None:
    assert store._read_research_event(db, event_id="missing") is None
    assert count(db) == 0


@pytest.fixture
def ledger(db: Path, recipe: dict[str, object]) -> tuple[str, str]:
    source = capture(db, {**recipe, "observation_count": 12})
    frozen = store.freeze_research_candidate(
        db, document={**candidate(source.event_id), "trial_count": 1}
    )
    return source.event_id, frozen.event_id


def selection(source: str, frozen: str, **changes: object) -> dict[str, object]:
    return {
        "contract_version": "research-selection-v1",
        "rule_id": "phase18-temporal-v1",
        "experiment_id": "experiment",
        "hypothesis_id": "hypothesis",
        "selection_revision": "s1",
        "selected_candidate_id": frozen,
        "considered_candidate_ids": [frozen],
        "selection_criteria": "declared criterion α",
        "validation": None,
        "input_id": source,
        "oos_start_ts": 5 * DAY,
        "oos_end_ts": 7 * DAY,
        **changes,
    }


def lifecycle_count(db: Path) -> int:
    with sqlite3.connect(db) as connection:
        return cast(
            int,
            connection.execute("SELECT count(*) FROM research_lifecycle_v1").fetchone()[
                0
            ],
        )


def external(
    db: Path, source: str, start: int = 5 * DAY, end: int = 7 * DAY
) -> store.ResearchLifecycleEvent:
    return store.record_external_inspection(
        db,
        input_id=source,
        start_ts=start,
        end_ts=end,
        actor="manual researcher",
        declared_at_ts=-100,
        note="outside inspection claim",
    )


def validation_access(
    db: Path, source: str, frozen: str
) -> store.ResearchObservationAccess:
    return store.access_validation_observations(
        db,
        candidate_id=frozen,
        input_id=source,
        start_ts=3 * DAY,
        end_ts=5 * DAY,
        actor="developer",
    )


def member(ts: int) -> list[object]:
    return [
        "binance",
        "BTC/USDT",
        "1d",
        "controlled-fixture:controlled-daily-linear-v1",
        {"kind": "int", "value": hex(ts - DAY)},
        {"kind": "int", "value": hex(ts)},
    ]


def test_selection_canonical_binding_access_and_historic_idempotence(
    db: Path,
    ledger: tuple[str, str],
) -> None:
    source, frozen = ledger
    data = selection(source, frozen)
    event = store.freeze_final_selection(db, document=data)
    with sqlite3.connect(db) as connection:
        candidate_payload = json.loads(
            connection.execute(
                "SELECT payload FROM research_events_v1 WHERE event_id=?", (frozen,)
            ).fetchone()[0]
        )
    expected_document = {
        **data,
        "oos_start_ts": {"kind": "int", "value": hex(5 * DAY)},
        "oos_end_ts": {"kind": "int", "value": hex(7 * DAY)},
    }
    expected = {
        "contract_version": "research-selection-v1",
        "rule_id": "phase18-temporal-v1",
        "document": expected_document,
        "candidate_bindings": [
            {"candidate_id": frozen, "candidate_payload": candidate_payload}
        ],
        "selection_memberships": [
            {
                "role": "is",
                "candidate_id": frozen,
                "input_id": source,
                "start_ts": {"kind": "int", "value": hex(DAY)},
                "end_ts": {"kind": "int", "value": hex(3 * DAY)},
                "members": [member(DAY), member(2 * DAY)],
            }
        ],
        "holdout_membership": {
            "input_id": source,
            "start_ts": {"kind": "int", "value": hex(5 * DAY)},
            "end_ts": {"kind": "int", "value": hex(7 * DAY)},
            "members": [member(5 * DAY), member(6 * DAY)],
        },
    }
    assert event.canonical_bytes == canonical(expected)
    assert event.event_id == "sha256:" + hashlib.sha256(canonical(expected)).hexdigest()
    first = store.access_oos_observations(db, selection_id=event.event_id, actor="one")
    second = store.access_oos_observations(
        db, selection_id=event.event_id, actor="another"
    )
    assert [row.close_ts for row in first.observations] == [5 * DAY, 6 * DAY]
    assert [row.ts for row in first.observations] == [4 * DAY, 5 * DAY]
    assert first.observations == second.observations
    assert first.event.event_id != second.event.event_id
    assert [
        json.loads(access.event.canonical_bytes)["access_status"]
        for access in (first, second)
    ] == ["first_access", "repeat_access"]
    payload = json.loads(first.event.canonical_bytes)
    assert payload == {
        "contract_version": "research-inspection-v1",
        "rule_id": "phase18-temporal-v1",
        "access_id": payload["access_id"],
        "action": "oos",
        "access_status": "first_access",
        "actor": "one",
        "declared_at_ts": None,
        "note": None,
        "input_id": source,
        "start_ts": {"kind": "int", "value": hex(5 * DAY)},
        "end_ts": {"kind": "int", "value": hex(7 * DAY)},
        "source_watermark": {"kind": "int", "value": "0x2"},
        "members": [member(5 * DAY), member(6 * DAY)],
        "candidate_id": None,
        "selection_id": event.event_id,
    }
    assert first.event.canonical_bytes == canonical(payload)
    assert (
        first.event.event_id
        == "sha256:" + hashlib.sha256(canonical(payload)).hexdigest()
    )
    assert (
        store.freeze_final_selection(
            db, document={**data, "considered_candidate_ids": (frozen,)}
        )
        == event
    )
    with pytest.raises(
        ValueError, match="selection revision already has different frozen content"
    ):
        store.freeze_final_selection(
            db, document={**data, "selection_criteria": "changed"}
        )
    with pytest.raises(
        ValueError, match="final holdout observations were already inspected"
    ):
        store.freeze_final_selection(db, document={**data, "selection_revision": "s2"})
    assert lifecycle_count(db) == 3
    assert not hasattr(first, "eligible")
    with pytest.raises(FrozenInstanceError):
        event.__setattr__("seq", 20)


def test_common_validation_each_trial_proof_and_explicit_absence(
    db: Path,
    recipe: dict[str, object],
) -> None:
    source = capture(db, {**recipe, "observation_count": 8}).event_id
    candidates = [
        store.freeze_research_candidate(
            db,
            document={
                **candidate(source),
                "candidate_revision": f"r{index}",
                "trial_index": index,
                "trial_count": 2,
            },
        ).event_id
        for index in (1, 2)
    ]
    data = selection(
        source,
        candidates[0],
        considered_candidate_ids=candidates,
        validation={"input_id": source, "start_ts": 3 * DAY, "end_ts": 5 * DAY},
    )
    validation_access(db, source, candidates[0])
    with pytest.raises(
        ValueError,
        match="validation access must precede final selection "
        "for every considered candidate",
    ):
        store.freeze_final_selection(db, document=data)
    validation_access(db, source, candidates[1])
    repeated = validation_access(db, source, candidates[1])
    assert (
        json.loads(repeated.event.canonical_bytes)["access_status"] == "repeat_access"
    )
    assert [row.close_ts for row in repeated.observations] == [3 * DAY, 4 * DAY]
    with pytest.raises(
        ValueError, match="validation absence conflicts with recorded validation access"
    ):
        store.freeze_final_selection(db, document={**data, "validation": None})
    frozen = store.freeze_final_selection(db, document=data)
    payload = json.loads(frozen.canonical_bytes)
    assert [
        binding["candidate_id"] for binding in payload["candidate_bindings"]
    ] == candidates
    assert payload["selection_memberships"][-1]["members"] == [
        member(3 * DAY),
        member(4 * DAY),
    ]
    store.access_oos_observations(db, selection_id=frozen.event_id, actor="reviewer")
    assert store.freeze_final_selection(db, document=data) == frozen


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"unexpected": 1}, "selection must contain exactly the declared fields"),
        (
            {"contract_version": "wrong", "rule_id": "wrong"},
            "contract_version must be research-selection-v1",
        ),
        (
            {"selection_criteria": ""},
            "selection_criteria must be a nonempty UTF-8 string without NUL",
        ),
        (
            {"considered_candidate_ids": []},
            "considered_candidate_ids must be a nonempty list or tuple "
            "of unique candidate IDs",
        ),
        (
            {"validation": {}},
            "validation must be null or contain exactly input_id, start_ts, and end_ts",
        ),
        ({"oos_start_ts": True}, "oos_start_ts must be an integer excluding bool"),
        ({"oos_end_ts": 5 * DAY}, "oos.start_ts must be less than oos.end_ts"),
        (
            {"oos_start_ts": 5 * DAY + 1},
            "oos_start_ts must align with the declared daily grid",
        ),
        ({"selected_candidate_id": "missing"}, "selected candidate must be considered"),
        (
            {"considered_candidate_ids": ["missing"]},
            "research candidate event does not exist",
        ),
        ({"input_id": "missing"}, "research input event does not exist"),
        (
            {"experiment_id": "other"},
            "considered candidates must match experiment and hypothesis",
        ),
        (
            {"oos_start_ts": 2 * DAY},
            "research ranges must be chronological and nonoverlapping",
        ),
    ],
)
def test_selection_errors_are_redacted_single_log_and_rollback(
    db: Path,
    ledger: tuple[str, str],
    change: dict[str, object],
    message: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.clear()
    with pytest.raises(ValueError) as error:
        store.freeze_final_selection(db, document=selection(*ledger, **change))
    assert str(error.value) == message
    assert [(record.name, record.message) for record in caplog.records] == [
        ("quant.data.research_store", message)
    ]
    assert lifecycle_count(db) == 0


def test_trial_budget_and_duplicate_considered_are_rejected(
    db: Path, ledger: tuple[str, str]
) -> None:
    source, frozen = ledger
    extra = store.freeze_research_candidate(
        db,
        document={**candidate(source), "candidate_revision": "extra", "trial_count": 1},
    ).event_id
    with pytest.raises(
        ValueError,
        match="considered candidates must enumerate the declared trial budget",
    ):
        store.freeze_final_selection(
            db,
            document=selection(
                source, frozen, considered_candidate_ids=[frozen, extra]
            ),
        )
    with pytest.raises(
        ValueError,
        match="considered_candidate_ids must be a nonempty list or tuple "
        "of unique candidate IDs",
    ):
        store.freeze_final_selection(
            db,
            document=selection(
                source, frozen, considered_candidate_ids=[frozen, frozen]
            ),
        )


@pytest.mark.parametrize("replacement", ["same", "unrelated", "linked"])
def test_changed_criteria_requires_new_selected_candidate_lineage(
    db: Path,
    ledger: tuple[str, str],
    replacement: str,
) -> None:
    source, frozen = ledger
    data = selection(source, frozen)
    original = store.freeze_final_selection(db, document=data)
    store.access_oos_observations(db, selection_id=original.event_id, actor="reader")
    selected = frozen
    if replacement != "same":
        selected = store.freeze_research_candidate(
            db,
            document={
                **candidate(source),
                "candidate_revision": "new",
                "trial_count": 1,
                "parent_candidate_id": frozen if replacement == "linked" else None,
            },
        ).event_id
    revised = selection(
        source,
        selected,
        selection_revision="s2",
        selection_criteria="new criterion",
        oos_start_ts=8 * DAY,
        oos_end_ts=10 * DAY,
    )
    if replacement == "linked":
        newer = store.freeze_final_selection(db, document=revised)
        assert newer.event_id != original.event_id
        store.access_oos_observations(db, selection_id=newer.event_id, actor="reader")
    else:
        with pytest.raises(
            ValueError,
            match="^changed selection criteria require a new candidate revision "
            "with prior selection lineage$",
        ):
            store.freeze_final_selection(db, document=revised)
    assert store.freeze_final_selection(db, document=data) == original


def test_sc15_explicit_new_is_reuses_inspected_old_holdout_with_unseen_final(
    db: Path,
    ledger: tuple[str, str],
) -> None:
    source, frozen = ledger
    old = store.freeze_final_selection(db, document=selection(source, frozen))
    old_access = store.access_oos_observations(
        db, selection_id=old.event_id, actor="researcher"
    )
    revised = store.freeze_research_candidate(
        db,
        document={
            **candidate(source),
            "candidate_revision": "development-r2",
            "parent_candidate_id": frozen,
            "trial_count": 1,
            "in_sample_start_ts": 5 * DAY,
            "in_sample_end_ts": 7 * DAY,
        },
    )
    new = store.freeze_final_selection(
        db,
        document=selection(
            source,
            revised.event_id,
            selection_revision="new",
            selection_criteria="revised on development data",
            oos_start_ts=8 * DAY,
            oos_end_ts=10 * DAY,
        ),
    )
    assert [
        row.close_ts
        for row in store.access_oos_observations(
            db, selection_id=new.event_id, actor="researcher"
        ).observations
    ] == [8 * DAY, 9 * DAY]
    assert store.freeze_final_selection(db, document=selection(source, frozen)) == old
    assert (
        store.access_oos_observations(
            db, selection_id=old.event_id, actor="reproducer"
        ).observations
        == old_access.observations
    )


@pytest.mark.parametrize(
    "variant",
    [
        "new_revision",
        "new_candidate",
        "new_experiment",
        "changed_recipe",
        "partial_overlap",
    ],
)
def test_inspection_contamination_cannot_be_reset_by_identity(
    db: Path,
    ledger: tuple[str, str],
    recipe: dict[str, object],
    variant: str,
) -> None:
    source, frozen = ledger
    external(db, source)
    changes: dict[str, object] = {"selection_revision": "later"}
    if variant == "changed_recipe":
        source = capture(
            db,
            {**recipe, "observation_count": 12, "price_start": 400, "anchor_ts": DAY},
        ).event_id
    if variant in ("new_candidate", "new_experiment"):
        changes["experiment_id"] = (
            "other" if variant == "new_experiment" else "experiment"
        )
        frozen = store.freeze_research_candidate(
            db,
            document={
                **candidate(source),
                "trial_count": 1,
                "candidate_revision": "r2",
                "experiment_id": changes["experiment_id"],
            },
        ).event_id
    if variant == "partial_overlap":
        changes.update(oos_start_ts=6 * DAY, oos_end_ts=8 * DAY)
    with pytest.raises(
        ValueError, match="final holdout observations were already inspected"
    ):
        store.freeze_final_selection(db, document=selection(source, frozen, **changes))
    allowed = store.freeze_final_selection(
        db,
        document=selection(
            source,
            frozen,
            **{**changes, "oos_start_ts": 8 * DAY, "oos_end_ts": 10 * DAY},
        ),
    )
    assert allowed.kind == "selection"


def test_wall_clock_and_manual_claim_cannot_change_commit_order(
    db: Path,
    ledger: tuple[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source, frozen = ledger
    monkeypatch.setattr(store.time, "time_ns", lambda: -1000000)
    event = external(db, source)
    payload = json.loads(event.canonical_bytes)
    assert event.recorded_at_ts == -1
    assert payload["declared_at_ts"] == {"kind": "int", "value": hex(-100)}
    assert payload["source_watermark"] == {"kind": "int", "value": "0x2"}
    assert payload["access_status"] == "external_declaration"
    monkeypatch.setattr(store.time, "time_ns", lambda: -2000000)
    with pytest.raises(
        ValueError, match="final holdout observations were already inspected"
    ):
        store.freeze_final_selection(db, document=selection(source, frozen))
    later = external(db, source)
    assert later.seq > event.seq and later.recorded_at_ts < event.recorded_at_ts


def test_validation_blocks_oos_and_external_even_for_existing_candidate(
    db: Path,
    ledger: tuple[str, str],
) -> None:
    source, frozen = ledger
    registered = store.freeze_final_selection(db, document=selection(source, frozen))
    for start, end in ((5 * DAY, 7 * DAY), (6 * DAY, 8 * DAY)):
        with pytest.raises(
            ValueError,
            match="validation observations overlap a final holdout or OOS inspection",
        ):
            store.access_validation_observations(
                db,
                candidate_id=frozen,
                input_id=source,
                start_ts=start,
                end_ts=end,
                actor="developer",
            )
    external(db, source, 8 * DAY, 10 * DAY)
    with pytest.raises(
        ValueError,
        match="validation observations overlap a final holdout or OOS inspection",
    ):
        store.access_validation_observations(
            db,
            candidate_id=frozen,
            input_id=source,
            start_ts=8 * DAY,
            end_ts=10 * DAY,
            actor="developer",
        )
    store.access_oos_observations(
        db, selection_id=registered.event_id, actor="reviewer"
    )
    assert [
        row.close_ts for row in validation_access(db, source, frozen).observations
    ] == [3 * DAY, 4 * DAY]


def test_candidate_after_validation_inspection_cannot_manufacture_proof(
    db: Path,
    ledger: tuple[str, str],
) -> None:
    source, frozen = ledger
    validation_access(db, source, frozen)
    newer = store.freeze_research_candidate(
        db,
        document={
            **candidate(source),
            "candidate_revision": "after-access",
            "trial_count": 1,
        },
    ).event_id
    with pytest.raises(
        ValueError, match="validation was inspected before candidate freeze"
    ):
        validation_access(db, source, newer)
    old_selection = store.freeze_final_selection(
        db,
        document=selection(
            source,
            frozen,
            validation={"input_id": source, "start_ts": 3 * DAY, "end_ts": 5 * DAY},
        ),
    )
    assert old_selection.kind == "selection"


def test_access_missing_records_and_coverage_propagate_once(
    db: Path,
    ledger: tuple[str, str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    source, frozen = ledger
    with pytest.raises(ValueError, match="research selection event does not exist"):
        store.access_oos_observations(db, selection_id="missing", actor="reader")
    with pytest.raises(ValueError, match="research candidate event does not exist"):
        validation_access(db, source, "missing")
    caplog.clear()
    with pytest.raises(
        ValueError, match="observations do not provide complete expected bar coverage"
    ):
        store.record_external_inspection(
            db,
            input_id=source,
            start_ts=11 * DAY,
            end_ts=15 * DAY,
            actor="reader",
            declared_at_ts=None,
            note="report",
        )
    assert (
        len(caplog.records) == 1
        and caplog.records[0].name == "quant.engine.bar_coverage"
    )
    assert lifecycle_count(db) == 0


def corrupt_lifecycle(
    db: Path,
    event: store.ResearchLifecycleEvent,
    *,
    payload: bytes | None = None,
    assignment: str | None = None,
) -> str:
    with sqlite3.connect(db) as connection:
        connection.execute("DROP TRIGGER research_lifecycle_no_update")
        if payload is not None:
            identity = "sha256:" + hashlib.sha256(payload).hexdigest()
            connection.execute(
                "UPDATE research_lifecycle_v1 SET event_id=?,payload=? "
                "WHERE event_id=?",
                (identity, payload, event.event_id),
            )
            return identity
        assert assignment is not None
        connection.execute(
            f"UPDATE research_lifecycle_v1 SET {assignment} WHERE event_id=?",
            (event.event_id,),
        )
    return event.event_id


@pytest.mark.parametrize(
    "change",
    [
        "digest",
        "index",
        "kind",
        "extra",
        "version",
        "document",
        "membership",
        "binding",
        "hex",
        "duplicate",
        "whitespace",
        "criteria",
    ],
)
def test_selection_replay_reproduces_payload_before_release(
    db: Path,
    ledger: tuple[str, str],
    change: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = store.freeze_final_selection(db, document=selection(*ledger))
    payload = json.loads(event.canonical_bytes)
    if change in ("digest", "index", "kind"):
        assignment = {
            "digest": "payload=X'7B7D'",
            "index": "selection_revision='tampered'",
            "kind": "kind='inspection'",
        }[change]
        identity = corrupt_lifecycle(db, event, assignment=assignment)
    else:
        if change == "extra":
            payload["extra"] = None
        elif change == "version":
            payload["contract_version"] = "wrong"
        elif change == "document":
            payload["document"]["considered_candidate_ids"] = {}
        elif change == "membership":
            payload["holdout_membership"]["members"][0][3] = "unknown family"
        elif change == "binding":
            payload["candidate_bindings"][0]["candidate_payload"]["code_id"] = "b" * 40
        elif change == "hex":
            payload["document"]["oos_start_ts"]["value"] = "0X19BFCC00"
        elif change == "criteria":
            payload["document"]["selection_criteria"] = ""
        raw = canonical(payload)
        if change == "duplicate":
            raw = b'{"rule_id":"phase18-temporal-v1",' + raw[1:]
        elif change == "whitespace":
            raw += b"\n"
        identity = corrupt_lifecycle(db, event, payload=raw)
    caplog.clear()
    with pytest.raises(
        ValueError, match="^stored research event failed integrity validation$"
    ):
        store.access_oos_observations(db, selection_id=identity, actor="reader")
    assert [(record.name, record.message) for record in caplog.records] == [
        (
            "quant.data.research_store",
            "stored research event failed integrity validation",
        )
    ]
    assert lifecycle_count(db) == 1
    # Replay's private error context must reset even when an exception escapes.
    caplog.clear()
    with pytest.raises(
        ValueError, match="^actor must be a nonempty UTF-8 string without NUL$"
    ):
        store.access_oos_observations(db, selection_id=identity, actor="")
    assert len(caplog.records) == 1


@pytest.mark.parametrize(
    "change",
    [
        "uuid",
        "status",
        "action",
        "null",
        "actor",
        "watermark",
        "member",
        "index",
        "bound_kind",
        "extra",
    ],
)
def test_inspection_replay_validates_exact_shapes_status_and_source_watermark(
    db: Path,
    ledger: tuple[str, str],
    change: str,
    caplog: pytest.LogCaptureFixture,
) -> None:
    event = external(db, ledger[0])
    payload = json.loads(event.canonical_bytes)
    if change == "index":
        corrupt_lifecycle(db, event, assignment="experiment_id='forged'")
    else:
        if change == "uuid":
            payload["access_id"] = "A" * 32
        elif change == "status":
            payload["access_status"] = "first_access"
        elif change == "action":
            payload["action"] = "result"
        elif change == "null":
            payload["candidate_id"] = ledger[1]
        elif change == "actor":
            payload["actor"] = ""
        elif change == "watermark":
            payload["source_watermark"] = {"kind": "int", "value": "0x0"}
        elif change == "member":
            payload["members"] = [member(9 * DAY)]
        elif change == "bound_kind":
            payload["start_ts"]["kind"] = "float"
        elif change == "extra":
            payload["raw_observations"] = []
        corrupt_lifecycle(db, event, payload=canonical(payload))
    caplog.clear()
    with pytest.raises(
        ValueError, match="^stored research event failed integrity validation$"
    ):
        store.freeze_final_selection(db, document=selection(*ledger))
    assert (
        len(caplog.records) == 1
        and caplog.records[0].message
        == "stored research event failed integrity validation"
    )
    assert lifecycle_count(db) == 1


def test_repeat_status_and_later_selection_reference_cannot_be_fabricated(
    db: Path,
    ledger: tuple[str, str],
) -> None:
    data = selection(*ledger)
    frozen = store.freeze_final_selection(db, document=data)
    first = store.access_oos_observations(
        db, selection_id=frozen.event_id, actor="reader"
    )
    second = store.access_oos_observations(
        db, selection_id=frozen.event_id, actor="reader"
    )
    payload = json.loads(second.event.canonical_bytes)
    payload["access_status"] = "first_access"
    corrupt_lifecycle(db, second.event, payload=canonical(payload))
    with pytest.raises(
        ValueError, match="^stored research event failed integrity validation$"
    ):
        store.freeze_final_selection(db, document=data)
    assert first.event.seq < second.event.seq


def test_oos_replay_rejects_nonhistorical_selection_reference(
    db: Path,
    ledger: tuple[str, str],
) -> None:
    frozen = store.freeze_final_selection(db, document=selection(*ledger))
    store.access_oos_observations(db, selection_id=frozen.event_id, actor="reader")
    corrupt_lifecycle(db, frozen, assignment="seq=100")
    with pytest.raises(
        ValueError, match="^stored research event failed integrity validation$"
    ):
        external(db, ledger[0])


def test_source_corruption_fails_before_observation_release_with_original_error(
    db: Path,
    ledger: tuple[str, str],
    caplog: pytest.LogCaptureFixture,
) -> None:
    source, frozen = ledger
    event = store.freeze_final_selection(db, document=selection(source, frozen))
    stored = store._read_research_event(db, event_id=source)
    assert stored is not None
    payload = json.loads(stored.canonical_bytes)
    payload["snapshot"]["observations"][0]["volume"]["value"] = "0x3"
    corrupt(db, source, payload=canonical(payload))
    caplog.clear()
    with pytest.raises(
        ValueError, match="document does not match the reproduced controlled fixture"
    ):
        store.access_oos_observations(db, selection_id=event.event_id, actor="reader")
    assert (
        len(caplog.records) == 1
        and caplog.records[0].name == "quant.engine.research_fixture"
    )
    assert lifecycle_count(db) == 1


def test_lifecycle_triggers_block_update_delete(
    db: Path, ledger: tuple[str, str]
) -> None:
    store.freeze_final_selection(db, document=selection(*ledger))
    with sqlite3.connect(db) as connection:
        for sql in (
            "UPDATE research_lifecycle_v1 SET recorded_at_ts=0",
            "DELETE FROM research_lifecycle_v1",
        ):
            with pytest.raises(
                sqlite3.IntegrityError, match="research events are append-only"
            ):
                connection.execute(sql)
        source_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE name='research_events_v1'"
        ).fetchone()[0]
        assert "CHECK(kind IN ('input','candidate'))" in source_sql
    assert lifecycle_count(db) == 1


@pytest.mark.parametrize("action", ["validation", "oos", "external", "selection"])
@pytest.mark.parametrize("failure_kind", ["insert", "commit"])
def test_failed_lifecycle_mutation_never_releases_or_leaves_orphan(
    db: Path,
    ledger: tuple[str, str],
    action: str,
    failure_kind: str,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source, frozen = ledger
    selected = (
        store.freeze_final_selection(db, document=selection(source, frozen))
        if action == "oos"
        else None
    )
    before = lifecycle_count(db)
    original_connect = sqlite3.connect
    failure = sqlite3.OperationalError("injected lifecycle commit failure")
    if failure_kind == "insert":
        with sqlite3.connect(db) as connection:
            connection.execute(
                """CREATE TRIGGER fail_lifecycle
                    BEFORE INSERT ON research_lifecycle_v1 BEGIN
                    SELECT RAISE(ABORT,'injected lifecycle insert failure'); END"""
            )
    else:

        class FailCommit(sqlite3.Connection):
            def commit(self) -> None:
                raise failure

        def connect(path: Path, *, isolation_level: None) -> sqlite3.Connection:
            return original_connect(
                path, isolation_level=isolation_level, factory=FailCommit
            )

        monkeypatch.setattr(store.sqlite3, "connect", connect)
    caplog.clear()
    returned: list[object] = []
    with pytest.raises(sqlite3.Error) as error:
        if action == "validation":
            returned.append(validation_access(db, source, frozen))
        elif action == "oos":
            assert selected is not None
            returned.append(
                store.access_oos_observations(
                    db, selection_id=selected.event_id, actor="reader"
                )
            )
        elif action == "external":
            returned.append(external(db, source))
        else:
            returned.append(
                store.freeze_final_selection(db, document=selection(source, frozen))
            )
    if failure_kind == "commit":
        assert error.value is failure
    else:
        assert str(error.value) == "injected lifecycle insert failure"
    assert returned == [] and not caplog.records
    monkeypatch.setattr(store.sqlite3, "connect", original_connect)
    assert lifecycle_count(db) == before and count(db) == 2


@pytest.mark.parametrize("first_action", ["selection", "inspection"])
def test_actual_sqlite_contenders_serialize_freeze_against_inspection(
    db: Path,
    ledger: tuple[str, str],
    first_action: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from threading import Event, get_ident

    source, frozen = ledger
    locked = Event()
    contender_started = Event()
    owner: list[int] = []
    original_append = store._append_lifecycle
    original_connect = sqlite3.connect

    class ObserveBegin(sqlite3.Connection):
        def execute(self, sql: str, parameters: object = (), /) -> sqlite3.Cursor:
            if sql == "BEGIN IMMEDIATE" and owner and get_ident() != owner[0]:
                contender_started.set()
            return super().execute(sql, parameters)

    def connect(path: Path, *, isolation_level: None) -> sqlite3.Connection:
        return original_connect(
            path, isolation_level=isolation_level, factory=ObserveBegin
        )

    def append(
        connection: sqlite3.Connection,
        kind: str,
        payload: dict[str, object],
        data: dict[str, object] | None = None,
    ) -> store.ResearchLifecycleEvent:
        if not owner:
            owner.append(get_ident())
            locked.set()
            assert contender_started.wait(5), (
                "contender failed to enter BEGIN IMMEDIATE"
            )
        return original_append(
            connection,
            cast(Literal["selection", "inspection"], kind),
            payload,
            data,
        )

    def run(action: str) -> store.ResearchLifecycleEvent | str:
        try:
            return (
                store.freeze_final_selection(db, document=selection(source, frozen))
                if action == "selection"
                else external(db, source)
            )
        except ValueError as error:
            return str(error)

    monkeypatch.setattr(store.sqlite3, "connect", connect)
    monkeypatch.setattr(store, "_append_lifecycle", append)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(run, first_action)
        assert locked.wait(5)
        second = pool.submit(
            run, "inspection" if first_action == "selection" else "selection"
        )
        results = [first.result(), second.result()]
    monkeypatch.setattr(store.sqlite3, "connect", original_connect)
    if first_action == "selection":
        assert all(
            isinstance(result, store.ResearchLifecycleEvent) for result in results
        )
        assert [
            cast(store.ResearchLifecycleEvent, result).seq for result in results
        ] == [1, 2]
    else:
        assert isinstance(results[0], store.ResearchLifecycleEvent)
        assert results[1] == "final holdout observations were already inspected"
        assert lifecycle_count(db) == 1


def test_typed_large_lifecycle_clocks_remain_exact(
    db: Path,
    recipe: dict[str, object],
) -> None:
    huge = 1 << 16000
    source = capture(
        db,
        {**recipe, "anchor_ts": -huge, "start_open_ts": -huge, "observation_count": 12},
    ).event_id
    frozen = store.freeze_research_candidate(
        db,
        document={
            **candidate(source),
            "trial_count": 1,
            "in_sample_start_ts": -huge + DAY,
            "in_sample_end_ts": -huge + 3 * DAY,
        },
    ).event_id
    event = store.freeze_final_selection(
        db,
        document=selection(
            source, frozen, oos_start_ts=-huge + 5 * DAY, oos_end_ts=-huge + 7 * DAY
        ),
    )
    access = store.access_oos_observations(
        db, selection_id=event.event_id, actor="reader"
    )
    assert [row.close_ts for row in access.observations] == [
        -huge + 5 * DAY,
        -huge + 6 * DAY,
    ]
    assert json.loads(event.canonical_bytes)["document"]["oos_start_ts"] == {
        "kind": "int",
        "value": hex(-huge + 5 * DAY),
    }
    assert (
        store.freeze_final_selection(
            db,
            document=selection(
                source, frozen, oos_start_ts=-huge + 5 * DAY, oos_end_ts=-huge + 7 * DAY
            ),
        )
        == event
    )


def test_private_integrity_context_isolated_between_concurrent_calls(
    db: Path,
    ledger: tuple[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from threading import Event

    event = store.freeze_final_selection(db, document=selection(*ledger))
    payload = json.loads(event.canonical_bytes)
    payload["document"]["selection_criteria"] = ""
    identity = corrupt_lifecycle(db, event, payload=canonical(payload))
    replaying = Event()
    public_failed = Event()
    original_decode = store._decode_selection

    def decode(value: dict[str, object]) -> dict[str, object]:
        replaying.set()
        assert public_failed.wait(5)
        return original_decode(value)

    def malformed_replay() -> str:
        try:
            store.access_oos_observations(db, selection_id=identity, actor="reader")
        except ValueError as error:
            return str(error)
        raise AssertionError("malformed replay released data")

    def public_validation() -> str:
        assert replaying.wait(5)
        try:
            store.access_oos_observations(db, selection_id=identity, actor="")
        except ValueError as error:
            return str(error)
        finally:
            public_failed.set()
        raise AssertionError("invalid actor admitted")

    monkeypatch.setattr(store, "_decode_selection", decode)
    with ThreadPoolExecutor(max_workers=2) as pool:
        replay = pool.submit(malformed_replay)
        public = pool.submit(public_validation)
        assert public.result() == "actor must be a nonempty UTF-8 string without NUL"
        assert replay.result() == "stored research event failed integrity validation"
