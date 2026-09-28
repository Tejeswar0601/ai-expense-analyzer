from datetime import date
import pandas as pd
from backend.services.forecast_service import compute_forecast


def test_forecast_math():
    df = pd.DataFrame([
        {"amount": 300.0, "display_category": "Food"},
        {"amount": 400.0, "display_category": "Bills"},
    ])
    result = compute_forecast(df, 2026, 9, today=date(2026, 9, 10))
    assert result["available"] is True
    assert result["spent_so_far"] == 700.0
    assert result["daily_average_rate"] == 70.0
    assert result["projected_month_end_total"] == 2100.0  # 700 + 70*20


def test_forecast_unavailable_for_past_month():
    df = pd.DataFrame(columns=["amount", "display_category"])
    result = compute_forecast(df, 2026, 8, today=date(2026, 9, 10))
    assert result["available"] is False


def test_forecast_unavailable_for_future_month():
    df = pd.DataFrame(columns=["amount", "display_category"])
    result = compute_forecast(df, 2026, 12, today=date(2026, 9, 10))
    assert result["available"] is False


def test_forecast_confidence_levels():
    df = pd.DataFrame([{"amount": 100.0, "display_category": "Food"}])
    assert compute_forecast(df, 2026, 9, today=date(2026, 9, 2))["confidence"] == "low"
    assert compute_forecast(df, 2026, 9, today=date(2026, 9, 8))["confidence"] == "medium"
    assert compute_forecast(df, 2026, 9, today=date(2026, 9, 20))["confidence"] == "high"
