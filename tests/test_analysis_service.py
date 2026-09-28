import pandas as pd
from backend.services.analysis_service import generate_monthly_report_from_df


def test_category_percentages_and_totals():
    data = [
        {"id": 1, "expense_date": "2026-09-01", "amount": 600, "category": "Food", "custom_category": None, "note": None},
        {"id": 2, "expense_date": "2026-09-02", "amount": 400, "category": "Bills", "custom_category": None, "note": None},
    ]
    df = pd.DataFrame(data)
    report = generate_monthly_report_from_df(df, None, 2026, 9)

    assert report["overall_summary"]["total_spending"] == 1000.0
    assert report["trends"]["highest_spending_category"] == "Food"

    total_pct = sum(c["percentage"] for c in report["category_analysis"])
    assert 99.0 <= total_pct <= 100.0


def test_empty_month_does_not_crash():
    empty_df = pd.DataFrame(columns=["id", "expense_date", "amount", "category", "custom_category", "note"])
    report = generate_monthly_report_from_df(empty_df, None, 2026, 9)
    assert report["overall_summary"]["total_spending"] == 0.0
    assert report["previous_month_comparison"]["available"] is False


def test_month_comparison_never_fabricated_without_previous_data():
    data = [{"id": 1, "expense_date": "2026-09-01", "amount": 100, "category": "Food", "custom_category": None, "note": None}]
    df = pd.DataFrame(data)
    report = generate_monthly_report_from_df(df, None, 2026, 9)
    assert report["previous_month_comparison"]["available"] is False
    assert "not available" in report["previous_month_comparison"]["message"].lower()


def test_outlier_detection_flags_unusually_high_transaction():
    rows = [
        {"id": i, "expense_date": "2026-09-01", "amount": 100, "category": "Food", "custom_category": None, "note": None}
        for i in range(1, 6)
    ]
    rows.append({"id": 6, "expense_date": "2026-09-02", "amount": 5000, "category": "Food", "custom_category": None, "note": "Big spend"})
    df = pd.DataFrame(rows)
    report = generate_monthly_report_from_df(df, None, 2026, 9)
    unusual_ids = [t["id"] for t in report["unusual_transactions"]]
    assert 6 in unusual_ids
