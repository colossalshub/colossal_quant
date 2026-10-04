"""Equity, drawdown, and verification extraction from ``BacktestResult``.

Rebuilds the equity curve from ``portfolio_returns`` (§4.3) and verifies it.

Two verification modes:

* ``source="account_report"`` — the reconstructed equity curve (built purely
  from ``portfolio_returns``) is compared against
  ``independent_ending_balance``, an ending equity figure computed
  independently from Nautilus's authoritative account report (USDT cash +
  base-currency qty × last bar close). This is a genuine, independent check.
* ``source="self_consistent"`` — used when ``independent_ending_balance`` is
  missing or zero (e.g. older runs that predate the account-report wiring).
  The reconstruction is compared against ``ending_balance``, which is itself
  derived from the same snapshot series used to build the reconstruction.
  This proves internal coherence only, not agreement with Nautilus.

Callers supply ``first_bar_ts`` so bar 1 is included at ``starting_balance``.
"""

from __future__ import annotations

import bisect
import logging
import math
from dataclasses import dataclass
from typing import NoReturn

from quant.engine.runner import BacktestResult
from quant.engine.temporal import ResearchInterval

_VERIFICATION_THRESHOLD = 0.005
_LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class EquityPoint:
    ts: int
    equity: float
    benchmark: float | None


@dataclass(frozen=True)
class DrawdownPoint:
    ts: int
    dd: float  # in [-1, 0]


@dataclass(frozen=True)
class Verification:
    verified: bool
    discrepancy_pct: float
    source: str


@dataclass(frozen=True)
class EquityExtraction:
    equity: list[EquityPoint]
    drawdown: list[DrawdownPoint]
    verification: Verification


def _build_equity_series(
    result: BacktestResult,
    first_bar_ts: int,
    benchmark_bars: list[tuple[int, float]] | None,
) -> list[EquityPoint]:
    if result.starting_balance == 0:
        msg = "cannot build equity series: starting_balance is zero"
        raise ValueError(msg)
    if not result.portfolio_returns:
        msg = "cannot build equity series: no returns"
        raise ValueError(msg)

    bench_ts: list[int] = []
    bench_equity: list[float] = []
    if benchmark_bars is not None:
        if len(benchmark_bars) < 2:
            msg = "benchmark_bars must contain at least two bars"
            raise ValueError(msg)
        first_close = benchmark_bars[0][1]
        if first_close == 0:
            msg = "benchmark first close must be non-zero"
            raise ValueError(msg)
        for ts, close in benchmark_bars:
            bench_ts.append(ts)
            bench_equity.append(result.starting_balance * close / first_close)

        equity_last_ts = result.portfolio_returns[-1][0]
        if benchmark_bars[0][0] > first_bar_ts:
            msg = "benchmark bars do not cover equity time range"
            raise ValueError(msg)
        if benchmark_bars[-1][0] < equity_last_ts:
            msg = "benchmark bars do not cover equity time range"
            raise ValueError(msg)

    def benchmark_at(ts: int) -> float | None:
        if benchmark_bars is None:
            return None
        idx = bisect.bisect_right(bench_ts, ts) - 1
        return bench_equity[idx]

    points: list[EquityPoint] = [
        EquityPoint(
            ts=first_bar_ts,
            equity=result.starting_balance,
            benchmark=benchmark_at(first_bar_ts),
        ),
    ]
    prev_equity = result.starting_balance
    for ts, ret in result.portfolio_returns:
        prev_equity *= 1.0 + ret
        points.append(
            EquityPoint(
                ts=ts,
                equity=prev_equity,
                benchmark=benchmark_at(ts),
            ),
        )
    return points


def _verify_ending_balance(result: BacktestResult) -> Verification:
    reconstructed_final = result.starting_balance
    for _, ret in result.portfolio_returns:
        reconstructed_final *= 1.0 + ret

    independent = result.independent_ending_balance
    if independent is None or independent == 0:
        # Fall back to self-consistency (old behavior). This keeps older
        # runs that predate the account-report wiring working.
        ending = result.ending_balance
        if ending == 0:
            return Verification(
                verified=True,
                discrepancy_pct=0.0,
                source="self_consistent",
            )
        discrepancy = abs(reconstructed_final - ending) / ending
        return Verification(
            verified=discrepancy < _VERIFICATION_THRESHOLD,
            discrepancy_pct=discrepancy * 100.0,
            source="self_consistent",
        )

    # Independent verification against Nautilus's authoritative account state.
    discrepancy = abs(reconstructed_final - independent) / independent
    return Verification(
        verified=discrepancy < _VERIFICATION_THRESHOLD,
        discrepancy_pct=discrepancy * 100.0,
        source="account_report",
    )


def _compute_drawdown(
    equity_points: list[EquityPoint], *, initial_peak: float | None = None
) -> list[DrawdownPoint]:
    peak = equity_points[0].equity if initial_peak is None else initial_peak
    drawdown_points: list[DrawdownPoint] = []
    for point in equity_points:
        if point.equity > peak:
            peak = point.equity
        if peak > 0:
            dd = (point.equity / peak) - 1.0
        else:
            dd = 0.0
        dd = min(0.0, max(-1.0, dd))
        drawdown_points.append(DrawdownPoint(ts=point.ts, dd=dd))
    return drawdown_points


def extract_equity(
    result: BacktestResult,
    *,
    first_bar_ts: int,
    benchmark_bars: list[tuple[int, float]] | None = None,
) -> EquityExtraction:
    equity_points = _build_equity_series(result, first_bar_ts, benchmark_bars)
    verification = _verify_ending_balance(result)
    drawdown_points = _compute_drawdown(equity_points)
    return EquityExtraction(
        equity=equity_points,
        drawdown=drawdown_points,
        verification=verification,
    )


def _research_error(message: str) -> NoReturn:
    _LOG.error(message)
    raise ValueError(message)


def extract_research_equity(
    result: BacktestResult, *, active: ResearchInterval
) -> EquityExtraction:
    """Extract scored active clocks without the ordinary artifact cash baseline.

    Cash remains metadata and the compounding/drawdown basis. Only positive
    equity and positive account verification are supported; total-loss and
    negative account paths reject. Supplied clocks are checked, not actual
    coverage or source provenance. The independent account figure is supplied
    evidence, whose origin this pure extractor cannot authenticate. A finite
    verification mismatch is reported, not an eligibility decision.
    """
    if not isinstance(active, ResearchInterval):
        _research_error("active must be a ResearchInterval")
    if not isinstance(active.start_ts, int) or isinstance(active.start_ts, bool):
        _research_error("active.start_ts must be an integer excluding bool")
    if not isinstance(active.end_ts, int) or isinstance(active.end_ts, bool):
        _research_error("active.end_ts must be an integer excluding bool")
    if active.start_ts >= active.end_ts:
        _research_error("active.start_ts must be less than active.end_ts")
    cash = result.starting_balance
    if type(cash) is not float or not math.isfinite(cash) or cash <= 0:
        _research_error("research starting_balance must be a finite positive float")
    returns = result.portfolio_returns
    if type(returns) is not list or not returns:
        _research_error("research portfolio_returns must be a nonempty list")
    previous_ts: int | None = None
    for item in returns:
        if type(item) is not tuple or len(item) != 2:
            _research_error("research return item must be a two-element tuple")
        ts, ret = item
        if not isinstance(ts, int) or isinstance(ts, bool):
            _research_error(
                "research return timestamp must be an integer excluding bool"
            )
        if type(ret) is not float or not math.isfinite(ret):
            _research_error("research return value must be a finite float")
        if not active.start_ts <= ts < active.end_ts:
            _research_error(
                "research return timestamp must lie inside the active interval"
            )
        if previous_ts is not None and ts <= previous_ts:
            _research_error("research return timestamps must be strictly increasing")
        if previous_ts is None and ts != active.start_ts:
            _research_error(
                "research first return timestamp must equal active.start_ts"
            )
        previous_ts = ts

    points: list[EquityPoint] = []
    equity = cash
    for ts, ret in returns:
        equity *= 1.0 + ret
        if not math.isfinite(equity) or equity <= 0:
            _research_error("research reconstructed equity must be finite and positive")
        points.append(EquityPoint(ts=ts, equity=equity, benchmark=None))
    independent = result.independent_ending_balance
    if (
        type(independent) is not float
        or not math.isfinite(independent)
        or independent <= 0
    ):
        _research_error(
            "research independent_ending_balance must be a finite positive float"
        )
    verification = _verify_ending_balance(result)
    if not math.isfinite(verification.discrepancy_pct):
        _research_error("research account discrepancy must be finite")
    return EquityExtraction(
        equity=points,
        drawdown=_compute_drawdown(points, initial_peak=cash),
        verification=verification,
    )
