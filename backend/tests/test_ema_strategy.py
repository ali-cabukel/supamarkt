"""Tests for EMA trend strategy."""

from supamarkt.analytics.strategies.ema_trend_5m import analyze


def _closes_uptrend(n: int = 30) -> list[float]:
    return [100.0 + i * 0.5 for i in range(n)]


def _closes_downtrend(n: int = 30) -> list[float]:
    return [200.0 - i * 0.5 for i in range(n)]


def test_ema_trend_buy_on_uptrend():
    closes = _closes_uptrend()
    bar_ts = [f"2026-05-31 10:{i:02d}:00" for i in range(len(closes))]
    result = analyze(bar_ts_list=bar_ts, closes=closes)
    assert result is not None
    assert result.action == "BUY"
    assert result.confidence > 0.5
    assert any("EMA" in reason for reason in result.reasons)


def test_ema_trend_sell_on_downtrend():
    closes = _closes_downtrend()
    bar_ts = [f"2026-05-31 11:{i:02d}:00" for i in range(len(closes))]
    result = analyze(bar_ts_list=bar_ts, closes=closes)
    assert result is not None
    assert result.action == "SELL"


def test_ema_trend_insufficient_bars():
    assert analyze(bar_ts_list=["t1"], closes=[1.0, 2.0]) is None
