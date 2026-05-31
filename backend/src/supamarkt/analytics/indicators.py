"""Technical indicators for intraday bars."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BarSeries:
    closes: list[float]
    highs: list[float]
    lows: list[float]
    volumes: list[float]


def ema(values: list[float], period: int) -> list[float | None]:
    if period < 1 or not values:
        return []
    out: list[float | None] = [None] * len(values)
    multiplier = 2 / (period + 1)
    ema_value: float | None = None
    for i, value in enumerate(values):
        if ema_value is None:
            if i + 1 < period:
                continue
            ema_value = sum(values[i + 1 - period : i + 1]) / period
        else:
            ema_value = (value - ema_value) * multiplier + ema_value
        out[i] = ema_value
    return out


def rsi(closes: list[float], period: int = 14) -> list[float | None]:
    if len(closes) < period + 1:
        return [None] * len(closes)

    out: list[float | None] = [None] * len(closes)
    gains: list[float] = []
    losses: list[float] = []

    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    def _rsi(ag: float, al: float) -> float:
        if al == 0:
            return 100.0
        rs = ag / al
        return 100 - (100 / (1 + rs))

    out[period] = _rsi(avg_gain, avg_loss)

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        out[i + 1] = _rsi(avg_gain, avg_loss)

    return out


def vwap(
    highs: list[float],
    lows: list[float],
    closes: list[float],
    volumes: list[float],
) -> list[float | None]:
    if not closes:
        return []
    out: list[float | None] = []
    cumulative_pv = 0.0
    cumulative_vol = 0.0
    for high, low, close, volume in zip(highs, lows, closes, volumes, strict=True):
        typical = (high + low + close) / 3
        cumulative_pv += typical * volume
        cumulative_vol += volume
        if cumulative_vol == 0:
            out.append(None)
        else:
            out.append(cumulative_pv / cumulative_vol)
    return out
