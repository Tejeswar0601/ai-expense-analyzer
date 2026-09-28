"""
Analysis service: all monthly-report calculations, done in Pandas.

Design note: the calculation logic (generate_monthly_report_from_df) is
kept separate from the database query (get_month_dataframe) so the math
can be unit-tested with plain DataFrames, independent of MySQL.

The AI (Phase 8) is only ever given the OUTPUT of this file - it never
calculates numbers itself, per the project spec.
"""

import calendar
from datetime import date
from typing import Optional

import pandas as pd
from sqlalchemy import text

from backend.database.connection import engine
from backend.services.duplicate_service import detect_duplicate_charges

OUTLIER_STD_MULTIPLIER = 1.5
MIN_TRANSACTIONS_FOR_OUTLIER_CHECK = 5


# ---------------------------------------------------------------------
# Database access
# ---------------------------------------------------------------------

def get_month_dataframe(year: int, month: int, user_id: int) -> pd.DataFrame:
    """Fetch all expenses for a given user, year/month as a DataFrame."""
    query = text(
        """
        SELECT id, expense_date, amount, category, custom_category, note, created_at
        FROM expenses
        WHERE user_id = :user_id
          AND YEAR(expense_date) = :year AND MONTH(expense_date) = :month
        """
    )
    df = pd.read_sql(query, engine, params={"user_id": user_id, "year": year, "month": month})
    return _prepare_dataframe(df)


def _prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize types and add a 'display_category' column."""
    if df.empty:
        return df
    df = df.copy()
    df["amount"] = df["amount"].astype(float)
    df["expense_date"] = pd.to_datetime(df["expense_date"])
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
    df["display_category"] = df.apply(
        lambda r: r["custom_category"]
        if r["category"] == "Others" and pd.notna(r.get("custom_category")) and r["custom_category"]
        else r["category"],
        axis=1,
    )
    return df


# ---------------------------------------------------------------------
# Individual calculations (pure functions, easy to test)
# ---------------------------------------------------------------------

def compute_overall_summary(df: pd.DataFrame, year: int, month: int) -> dict:
    days_in_month = calendar.monthrange(year, month)[1]

    if df.empty:
        return {
            "total_spending": 0.0,
            "transaction_count": 0,
            "average_transaction": 0.0,
            "average_daily_spending": 0.0,
        }

    total = round(float(df["amount"].sum()), 2)
    count = int(len(df))
    return {
        "total_spending": total,
        "transaction_count": count,
        "average_transaction": round(total / count, 2) if count else 0.0,
        "average_daily_spending": round(total / days_in_month, 2),
    }


def compute_category_analysis(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []

    total = df["amount"].sum()
    grouped = (
        df.groupby("display_category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )
    return [
        {
            "category": category,
            "total": round(float(amount), 2),
            "percentage": round(float(amount) / float(total) * 100, 1) if total else 0.0,
        }
        for category, amount in grouped.items()
    ]


def compute_daily_totals(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    grouped = df.groupby(df["expense_date"].dt.date)["amount"].sum().sort_index()
    return [
        {"date": str(d), "total": round(float(total), 2)}
        for d, total in grouped.items()
    ]


def compute_weekly_totals(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    df = df.copy()
    df["week_of_month"] = ((df["expense_date"].dt.day - 1) // 7) + 1
    grouped = df.groupby("week_of_month")["amount"].sum().sort_index()
    return [
        {"week": f"Week {int(week)}", "total": round(float(total), 2)}
        for week, total in grouped.items()
    ]


def compute_trends(df: pd.DataFrame, category_analysis: list[dict], daily_totals: list[dict], weekly_totals: list[dict]) -> dict:
    if df.empty:
        return {
            "highest_spending_day": None,
            "lowest_spending_day": None,
            "highest_spending_category": None,
            "most_frequent_category": None,
            "highest_spending_week": None,
        }

    highest_day = max(daily_totals, key=lambda d: d["total"])
    lowest_day = min(daily_totals, key=lambda d: d["total"])
    highest_category = category_analysis[0]["category"] if category_analysis else None
    most_frequent_category = df["display_category"].value_counts().idxmax()
    highest_week = max(weekly_totals, key=lambda w: w["total"])["week"] if weekly_totals else None

    return {
        "highest_spending_day": highest_day,
        "lowest_spending_day": lowest_day,
        "highest_spending_category": highest_category,
        "most_frequent_category": most_frequent_category,
        "highest_spending_week": highest_week,
    }


def detect_unusual_transactions(df: pd.DataFrame) -> list[dict]:
    """
    Flag transactions more than (mean + 1.5 * std_dev) above the month's
    average. Skipped entirely if there are too few transactions for the
    statistics to mean anything.
    """
    if len(df) < MIN_TRANSACTIONS_FOR_OUTLIER_CHECK:
        return []

    mean = df["amount"].mean()
    std = df["amount"].std()

    if pd.isna(std) or std == 0:
        return []

    threshold = mean + OUTLIER_STD_MULTIPLIER * std
    unusual = df[df["amount"] > threshold].sort_values("amount", ascending=False)

    return [
        {
            "id": int(row["id"]),
            "date": str(row["expense_date"].date()),
            "amount": round(float(row["amount"]), 2),
            "category": row["display_category"],
            "note": row["note"] if pd.notna(row["note"]) else None,
            "times_above_average": round(float(row["amount"]) / float(mean), 1),
        }
        for _, row in unusual.iterrows()
    ]


def compute_month_comparison(current_df: pd.DataFrame, previous_df: Optional[pd.DataFrame]) -> dict:
    if previous_df is None or previous_df.empty:
        return {
            "available": False,
            "message": "Previous month data is not available.",
        }

    current_total = float(current_df["amount"].sum()) if not current_df.empty else 0.0
    previous_total = float(previous_df["amount"].sum())

    change_amount = round(current_total - previous_total, 2)
    change_percent = (
        round((change_amount / previous_total) * 100, 1) if previous_total else None
    )

    # Which categories contributed most to the change
    current_by_cat = current_df.groupby("display_category")["amount"].sum() if not current_df.empty else pd.Series(dtype=float)
    previous_by_cat = previous_df.groupby("display_category")["amount"].sum()
    all_categories = set(current_by_cat.index) | set(previous_by_cat.index)

    deltas = []
    for cat in all_categories:
        cur = float(current_by_cat.get(cat, 0.0))
        prev = float(previous_by_cat.get(cat, 0.0))
        deltas.append({
            "category": cat,
            "current": round(cur, 2),
            "previous": round(prev, 2),
            "change": round(cur - prev, 2),
        })
    deltas.sort(key=lambda d: abs(d["change"]), reverse=True)

    return {
        "available": True,
        "previous_total": round(previous_total, 2),
        "current_total": round(current_total, 2),
        "change_amount": change_amount,
        "change_percent": change_percent,
        "top_contributing_categories": deltas[:3],
    }


# ---------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------

def generate_monthly_report_from_df(
    df: pd.DataFrame, previous_df: Optional[pd.DataFrame], year: int, month: int
) -> dict:
    """Pure function: given DataFrames, produce the full report dict.
    No database access here - this is what gets unit-tested."""

    df = _prepare_dataframe(df)
    if previous_df is not None:
        previous_df = _prepare_dataframe(previous_df)

    category_analysis = compute_category_analysis(df)
    daily_totals = compute_daily_totals(df)
    weekly_totals = compute_weekly_totals(df)

    return {
        "year": year,
        "month": month,
        "month_name": date(year, month, 1).strftime("%B %Y"),
        "overall_summary": compute_overall_summary(df, year, month),
        "category_analysis": category_analysis,
        "daily_totals": daily_totals,
        "weekly_totals": weekly_totals,
        "trends": compute_trends(df, category_analysis, daily_totals, weekly_totals),
        "unusual_transactions": detect_unusual_transactions(df),
        "potential_duplicates": detect_duplicate_charges(df),
        "previous_month_comparison": compute_month_comparison(df, previous_df),
    }


def generate_monthly_report(year: int, month: int, user_id: int) -> dict:
    """Queries MySQL for the given user's expenses in the given month
    and the previous month, then builds the full report."""

    current_df = get_month_dataframe(year, month, user_id)

    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year = year - 1

    previous_df = get_month_dataframe(prev_year, prev_month, user_id)

    return generate_monthly_report_from_df(current_df, previous_df, year, month)
