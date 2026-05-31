"""EMA trend strategy for 5-minute bars."""

from __future__ import annotations

from dataclasses import dataclass

from supamarkt.analytics.indicators import BarSeries, ema


@dataclass(frozen=True, slots=True)
class StrategyResult:
    action: str
    confidence: float
    bar_ts: str
    reasons: list[str]


def analyze(
    *,
    bar_ts_list: list[str],
    closes: list[float],
    min_bars: int = 25,
) -> StrategyResult | None:
    if len(closes) < min_bars:
        return None

    series = BarSeries(closes=closes, highs=[], lows=[], volumes=[])
    ema9 = ema(series.closes, 9)
    ema21 = ema(series.closes, 21)

    close = series.closes[-1]
    e9 = ema9[-1]
    e21 = ema21[-1]
    if e9 is None or e21 is None:
        return None

    reasons = [
        f"close={close:.4f}",
        f"EMA9={e9:.4f}",
        f"EMA21={e21:.4f}",
    ]

    if close > e21 and e9 > e21:
        action = "BUY"
        spread = (e9 - e21) / e21 if e21 else 0
        confidence = min(0.95, 0.55 + spread * 10)
        reasons.append("Price above EMA21 with EMA9 > EMA21 (uptrend)")
    elif close < e21 and e9 < e21:
        action = "SELL"
        spread = (e21 - e9) / e21 if e21 else 0
        confidence = min(0.95, 0.55 + spread * 10)
        reasons.append("Price below EMA21 with EMA9 < EMA21 (downtrend)")
    else:
        action = "HOLD"
        confidence = 0.5
        reasons.append("Trend mixed — no clear EMA alignment")

    return StrategyResult(
        action=action,
        confidence=round(confidence, 2),
        bar_ts=bar_ts_list[-1],
        reasons=reasons,
    )
