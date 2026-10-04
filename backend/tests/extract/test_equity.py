from __future__ import annotations

import copy
import logging
from dataclasses import replace
from types import SimpleNamespace
from typing import Any

import pandas as pd
import pytest

from quant.engine import research_runner
from quant.engine.bar_coverage import BarClock
from quant.engine.runner import BacktestResult
from quant.engine.temporal import ResearchInterval
from quant.extract.equity import extract_equity, extract_research_equity

_EMPTY_REPORTS: dict[str, object] = {}
_EMPTY_LIST: list[dict[str, object]] = []


def _result(
    *,
    starting_balance: float,
    ending_balance: float,
    portfolio_returns: list[tuple[int, float]],
    independent_ending_balance: float | None = None,
) -> BacktestResult:
    return BacktestResult(
        portfolio_returns=portfolio_returns,
        starting_balance=starting_balance,
        ending_balance=ending_balance,
        independent_ending_balance=independent_ending_balance,
        position_report=_EMPTY_LIST,
        fills_report=_EMPTY_LIST,
        account_report=_EMPTY_REPORTS,
    )


def test_basic_equity_series() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert len(extraction.equity) == 3
    assert extraction.equity[0].ts == 1000
    assert extraction.equity[0].equity == 1000.0
    assert extraction.equity[1].ts == 2000
    assert extraction.equity[1].equity == pytest.approx(1050.0)
    assert extraction.equity[2].equity == pytest.approx(1100.0)


def test_verification_exact_reconstruction() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.verified is True
    assert extraction.verification.discrepancy_pct < 0.001
    assert extraction.verification.source == "self_consistent"


def test_verification_drifted_ending_balance() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1050.0,
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.verified is False
    assert extraction.verification.discrepancy_pct == pytest.approx(
        4.761904761904762,
        rel=1e-4,
    )


def test_verification_against_account_report_agrees() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1050.0,  # deliberately different from independent
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
        independent_ending_balance=1100.0,
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.source == "account_report"
    assert extraction.verification.verified is True
    assert extraction.verification.discrepancy_pct < 0.001


def test_verification_against_account_report_flags_discrepancy() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1050.0,
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
        independent_ending_balance=1050.0,
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.verified is False
    assert extraction.verification.source == "account_report"
    assert extraction.verification.discrepancy_pct > 0.5


def test_verification_falls_back_to_self_consistent_when_independent_none() -> None:
    second_return = 50.0 / 1050.0
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, second_return)],
        independent_ending_balance=None,
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.source == "self_consistent"


def test_verification_zero_ending_balance() -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=0.0,
        portfolio_returns=[(2000, -1.0)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.verification.verified is True
    assert extraction.verification.discrepancy_pct == 0.0


def test_drawdown_rising_equity_all_zero() -> None:
    result = _result(
        starting_balance=100.0,
        ending_balance=121.0,
        portfolio_returns=[(2000, 0.1), (3000, 0.1)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert all(p.dd == 0.0 for p in extraction.drawdown)


def test_drawdown_peak_then_drop() -> None:
    # Equity path: 100 -> 110 -> 105 -> 90 -> 95
    r1 = 0.1
    r2 = 105.0 / 110.0 - 1.0
    r3 = 90.0 / 105.0 - 1.0
    r4 = 95.0 / 90.0 - 1.0
    result = _result(
        starting_balance=100.0,
        ending_balance=95.0,
        portfolio_returns=[(2000, r1), (3000, r2), (4000, r3), (5000, r4)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    dds = [p.dd for p in extraction.drawdown]
    expected = [
        0.0,
        0.0,
        -0.045454545454545456,
        -0.18181818181818182,
        -0.13636363636363635,
    ]
    assert dds == pytest.approx(expected)


def test_drawdown_recovery_to_new_high() -> None:
    r1 = 0.1
    r2 = 105.0 / 110.0 - 1.0
    r3 = 120.0 / 105.0 - 1.0
    result = _result(
        starting_balance=100.0,
        ending_balance=120.0,
        portfolio_returns=[(2000, r1), (3000, r2), (4000, r3)],
    )
    extraction = extract_equity(result, first_bar_ts=1000)
    assert extraction.drawdown[-1].dd == 0.0


def test_benchmark_none() -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, 50.0 / 1050.0)],
    )
    extraction = extract_equity(result, first_bar_ts=1000, benchmark_bars=None)
    assert all(p.benchmark is None for p in extraction.equity)


def test_benchmark_normalized_values() -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=900.0,
        portfolio_returns=[(2000, 0.1), (3000, -0.18181818181818182)],
    )
    bars = [(1000, 100.0), (2000, 110.0), (3000, 90.0)]
    extraction = extract_equity(result, first_bar_ts=1000, benchmark_bars=bars)
    benchmarks = [p.benchmark for p in extraction.equity]
    assert benchmarks == pytest.approx([1000.0, 1100.0, 900.0])


def test_benchmark_forward_fill_sparse_bars() -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, 50.0 / 1050.0)],
    )
    bars = [(1000, 100.0), (3000, 110.0)]
    extraction = extract_equity(result, first_bar_ts=1000, benchmark_bars=bars)
    assert extraction.equity[1].benchmark == pytest.approx(1000.0)


@pytest.mark.parametrize(
    ("benchmark_bars", "first_bar_ts"),
    [
        ([], 1000),
        ([(1000, 100.0)], 1000),
        ([(2000, 100.0), (3000, 110.0)], 1000),
        ([(1000, 100.0), (2000, 110.0)], 1000),
    ],
)
def test_benchmark_raises_when_invalid(
    benchmark_bars: list[tuple[int, float]],
    first_bar_ts: int,
) -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=1100.0,
        portfolio_returns=[(2000, 0.05), (3000, 50.0 / 1050.0)],
    )
    with pytest.raises(ValueError):
        extract_equity(result, first_bar_ts=first_bar_ts, benchmark_bars=benchmark_bars)


def test_empty_portfolio_returns_raises() -> None:
    result = _result(
        starting_balance=1000.0,
        ending_balance=1000.0,
        portfolio_returns=[],
    )
    with pytest.raises(ValueError, match="no returns"):
        extract_equity(result, first_bar_ts=1000)


def test_zero_starting_balance_raises() -> None:
    result = _result(
        starting_balance=0.0,
        ending_balance=0.0,
        portfolio_returns=[(2000, 0.0)],
    )
    with pytest.raises(ValueError, match="starting_balance"):
        extract_equity(result, first_bar_ts=1000)


def _research_result() -> BacktestResult:
    return _result(
        starting_balance=100.0,
        ending_balance=90.0,
        portfolio_returns=[(10, -0.1)],
        independent_ending_balance=90.0,
    )


@pytest.mark.parametrize("start", [-10, 10, 2**100])
def test_research_cash_peak_exact_clocks_and_no_mutation(start: int) -> None:
    result = _research_result()
    result = replace(
        result,
        portfolio_returns=[(start, -0.1), (start + 1, 0.0), (start + 2, 0.5)],
        independent_ending_balance=135.0,
    )
    before = copy.deepcopy(result)
    active = ResearchInterval(start, start + 3)
    extraction = extract_research_equity(result, active=active)
    assert [p.ts for p in extraction.equity] == [start, start + 1, start + 2]
    assert [p.equity for p in extraction.equity] == pytest.approx([90, 90, 135])
    assert [p.dd for p in extraction.drawdown] == pytest.approx([-0.1, -0.1, 0])
    assert [p.ts for p in extraction.drawdown] == [start, start + 1, start + 2]
    assert all(p.benchmark is None for p in extraction.equity)
    assert extraction.verification.verified
    assert extraction.verification.source == "account_report"
    assert result == before


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("active", None, "active must be a ResearchInterval"),
        (
            "active",
            ResearchInterval(True, 20),
            "active.start_ts must be an integer excluding bool",
        ),
        (
            "active",
            ResearchInterval("secret", 20),
            "active.start_ts must be an integer excluding bool",
        ),
        (
            "active",
            ResearchInterval(10, False),
            "active.end_ts must be an integer excluding bool",
        ),
        (
            "active",
            ResearchInterval(10, 20.0),
            "active.end_ts must be an integer excluding bool",
        ),
        (
            "active",
            ResearchInterval(20, 10),
            "active.start_ts must be less than active.end_ts",
        ),
        (
            "active",
            ResearchInterval(10, 10),
            "active.start_ts must be less than active.end_ts",
        ),
        *[
            (
                "starting_balance",
                v,
                "research starting_balance must be a finite positive float",
            )
            for v in (100, True, "secret", 0.0, -1.0, float("nan"), float("inf"))
        ],
        *[
            (
                "portfolio_returns",
                v,
                "research portfolio_returns must be a nonempty list",
            )
            for v in ([], None, ((10, 0.0),))
        ],
        *[
            (
                "portfolio_returns",
                [v],
                "research return item must be a two-element tuple",
            )
            for v in ([10, 0.0], (10,), (10, 0.0, "secret"))
        ],
        *[
            (
                "portfolio_returns",
                [(v, 0.0)],
                "research return timestamp must be an integer excluding bool",
            )
            for v in (True, "secret", 10.0)
        ],
        *[
            (
                "portfolio_returns",
                [(10, v)],
                "research return value must be a finite float",
            )
            for v in (0, False, "secret", float("nan"), float("inf"), -float("inf"))
        ],
        *[
            (
                "portfolio_returns",
                [(v, 0.0)],
                "research return timestamp must lie inside the active interval",
            )
            for v in (9, 20)
        ],
        (
            "portfolio_returns",
            [(10, 0.0), (10, 0.0)],
            "research return timestamps must be strictly increasing",
        ),
        (
            "portfolio_returns",
            [(10, 0.0), (12, 0.0), (11, 0.0)],
            "research return timestamps must be strictly increasing",
        ),
        (
            "portfolio_returns",
            [(11, 0.0)],
            "research first return timestamp must equal active.start_ts",
        ),
        *[
            (
                "portfolio_returns",
                [(10, v)],
                "research reconstructed equity must be finite and positive",
            )
            for v in (-1.0, -2.0, 1e308)
        ],
        *[
            (
                "independent_ending_balance",
                v,
                "research independent_ending_balance must be a finite positive float",
            )
            for v in (None, 0.0, -1.0, 90, True, "secret", float("nan"), float("inf"))
        ],
        (
            "independent_ending_balance",
            5e-324,
            "research account discrepancy must be finite",
        ),
    ],
)
def test_research_rejections_are_single_redacted_errors(
    caplog: pytest.LogCaptureFixture, field: str, value: Any, message: str
) -> None:
    result = _research_result()
    active = ResearchInterval(10, 20)
    if field == "active":
        active = value
    else:
        result = replace(result, **{field: value})
    before = copy.deepcopy(result)
    with caplog.at_level(logging.ERROR), pytest.raises(ValueError) as exc:
        extract_research_equity(result, active=active)
    assert str(exc.value) == message
    assert [(r.name, r.levelno, r.getMessage()) for r in caplog.records] == [
        ("quant.extract.equity", logging.ERROR, message)
    ]
    # deepcopy preserves NaN objects; containers/reports are never replaced.
    assert result.portfolio_returns == before.portfolio_returns
    assert result.account_report == before.account_report


@pytest.mark.parametrize(
    ("returns", "independent", "message"),
    [
        (
            [(10, -1.0), (11, "secret")],
            None,
            "research return value must be a finite float",
        ),
        (
            [(10, -1.0)],
            None,
            "research reconstructed equity must be finite and positive",
        ),
        ([(11, "secret")], None, "research return value must be a finite float"),
        (
            [(20, 0.0)],
            None,
            "research return timestamp must lie inside the active interval",
        ),
    ],
)
def test_research_validation_order(
    returns: Any, independent: Any, message: str
) -> None:
    result = _research_result()
    result = replace(
        result, portfolio_returns=returns, independent_ending_balance=independent
    )
    with pytest.raises(ValueError) as exc:
        extract_research_equity(result, active=ResearchInterval(10, 20))
    assert str(exc.value) == message


@pytest.mark.parametrize("independent", [90.0, 80.0])
def test_research_uses_account_figure_not_snapshot(independent: float) -> None:
    result = _research_result()
    result = replace(result, independent_ending_balance=independent)
    verification = extract_research_equity(
        result, active=ResearchInterval(10, 20)
    ).verification
    assert verification.source == "account_report"
    assert verification.discrepancy_pct == pytest.approx(
        abs(90 - independent) / independent * 100
    )
    assert verification.verified is (independent == 90)


def test_research_real_engine_warmup_fee_and_last_eligible_account_valuation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    day = 86_400_000
    anchor = 1_735_689_600_000 + 12_345
    active = ResearchInterval(anchor + 2 * day, anchor + 4 * day)
    account_frames: list[Any] = []
    real_factory = research_runner.BacktestEngine

    class EngineObserver:
        def __init__(self, **kwargs: Any) -> None:
            self.real = real_factory(**kwargs)

        def __getattr__(self, name: str) -> Any:
            return getattr(self.real, name)

        @property
        def trader(self) -> Any:
            real_trader = self.real.trader

            def account(venue: Any) -> Any:
                frame = real_trader.generate_account_report(venue)
                account_frames.append(frame.copy())
                return frame

            return SimpleNamespace(
                generate_account_report=account,
                generate_positions_report=real_trader.generate_positions_report,
                generate_fills_report=real_trader.generate_fills_report,
            )

    monkeypatch.setattr(research_runner, "BacktestEngine", EngineObserver)
    rows = [
        dict(ts=anchor + i * day, open=p, high=p + 1, low=p - 1, close=p, volume=1000.0)
        for i, p in enumerate((50.0, 100.0, 120.0, 9000.0, 8000.0))
    ]
    result = research_runner.run_research_buy_hold(
        active=active,
        warmup=ResearchInterval(anchor + day, active.start_ts),
        required_warmup_observations=1,
        timeframe="1d",
        calendar="continuous_utc_fixed",
        anchor_ts=anchor,
        clocks=tuple(
            BarClock(anchor + i * day, anchor + (i + 1) * day, anchor + (i + 1) * day)
            for i in range(5)
        ),
        rows=rows,
        starting_balance_usdt=100_000.0,
        trade_size="1.0000000",
        deploy_pct="0",
        maker_fee="0.001",
        taker_fee="0.001",
    )
    extraction = extract_research_equity(result, active=active)
    assert [p.ts for p in extraction.equity] == [active.start_ts, anchor + 3 * day]
    assert [p.ts for p in extraction.drawdown] == [p.ts for p in extraction.equity]
    (fill,) = result.fills_report
    commission = float(str(fill["commission"]).split()[0])
    qty, fill_price = float(fill["last_qty"]), float(fill["last_px"])
    assert commission == pytest.approx(0.1)
    assert fill["ts_event"].value == active.start_ts * 1_000_000
    assert qty == 1.0 and fill_price == 100.0
    (frame,) = account_frames
    cash = float(frame[frame["currency"] == "USDT"].iloc[-1]["total"])
    btc = float(frame[frame["currency"] == "BTC"].iloc[-1]["total"])
    assert cash == pytest.approx(100_000 - qty * fill_price - commission)
    assert btc == qty
    assert extraction.equity[0].equity == pytest.approx(cash + btc * fill_price)
    assert extraction.equity[0].equity < result.starting_balance
    assert extraction.drawdown[0].dd == pytest.approx(-commission / 100_000)
    assert extraction.drawdown[0].dd < 0
    last_eligible_price = 120.0  # row at anchor+2d closes at anchor+3d
    assert rows[2]["close"] == last_eligible_price
    expected_final = cash + btc * last_eligible_price
    assert result.independent_ending_balance == pytest.approx(expected_final)
    assert extraction.equity[-1].equity == pytest.approx(expected_final)
    (position,) = result.position_report
    assert pd.isna(position["ts_closed"])
    assert position["side"] == "LONG"
    assert extraction.verification.source == "account_report"
    assert extraction.verification.verified
