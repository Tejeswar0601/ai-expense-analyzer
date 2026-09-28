"""
Predictive month-end spending forecast: projects total spend by
month-end based on the daily average rate so far this month.

Only meaningful for the CURRENT, in-progress month - projecting a
month that's already fully over doesn't make sense, so this returns
available=False for any other month. `today` is a parameter (not
hardcoded to date.today() internally) specifically so this stays
testable with a fixed date, independent of the real wall-clock.
"""

import calendar
from datetime import date
from typing import Optional

import pandas as pd

LOW_CONFIDENCE_MAX_DAYS = 3
MEDIUM_CONFIDENCE_MAX_DAYS = 10


def compute_forecast(df: pd.DataFrame, year: int, month: int, today: Optional[date] = None) -> dict:
    today = today or date.today()

    if (year, month) != (today.year, today.month):
        return {
            "available": False,
            "message": "Forecast is only available for the current, in-progress month.",
        }

    days_in_month = calendar.monthrange(year, month)[1]
    days_elapsed = today.day  # counts today as an elapsed day
    days_remaining = days_in_month - days_elapsed

    total_so_far = float(df["amount"].sum()) if not df.empty else 0.0
    daily_rate = total_so_far / days_elapsed if days_elapsed else 0.0
    projected_total = round(total_so_far + daily_rate * days_remaining, 2)

    if days_elapsed <= LOW_CONFIDENCE_MAX_DAYS:
        confidence = "low"
    elif days_elapsed <= MEDIUM_CONFIDENCE_MAX_DAYS:
        confidence = "medium"
    else:
        confidence = "high"

    category_forecast = []
    if not df.empty:
        grouped = df.groupby("display_category")["amount"].sum()
        for category, cat_total_so_far in grouped.items():
            cat_total_so_far = float(cat_total_so_far)
            cat_daily_rate = cat_total_so_far / days_elapsed if days_elapsed else 0.0
            cat_projected = round(cat_total_so_far + cat_daily_rate * days_remaining, 2)
            category_forecast.append({
                "category": category,
                "spent_so_far": round(cat_total_so_far, 2),
                "projected_total": cat_projected,
            })
        category_forecast.sort(key=lambda c: c["projected_total"], reverse=True)

    return {
        "available": True,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "days_in_month": days_in_month,
        "spent_so_far": round(total_so_far, 2),
        "daily_average_rate": round(daily_rate, 2),
        "projected_month_end_total": projected_total,
        "confidence": confidence,
        "category_forecast": category_forecast,
    }
