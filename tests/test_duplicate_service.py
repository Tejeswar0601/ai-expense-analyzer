import pandas as pd
from backend.services.duplicate_service import detect_duplicate_charges


def test_double_entry_detected():
    data = [
        {"id": 1, "expense_date": pd.Timestamp("2026-09-05"), "amount": 250.0, "display_category": "Food", "note": "Lunch", "created_at": pd.Timestamp("2026-09-05 12:00:00")},
        {"id": 2, "expense_date": pd.Timestamp("2026-09-05"), "amount": 250.0, "display_category": "Food", "note": "Lunch", "created_at": pd.Timestamp("2026-09-05 12:02:00")},
    ]
    df = pd.DataFrame(data)
    results = detect_duplicate_charges(df)
    assert len(results) == 1
    assert results[0]["likely_double_entry"] is True


def test_same_day_different_time_flagged_but_not_confident():
    data = [
        {"id": 1, "expense_date": pd.Timestamp("2026-09-10"), "amount": 150.0, "display_category": "Food", "note": "Coffee AM", "created_at": pd.Timestamp("2026-09-10 08:00:00")},
        {"id": 2, "expense_date": pd.Timestamp("2026-09-10"), "amount": 150.0, "display_category": "Food", "note": "Coffee PM", "created_at": pd.Timestamp("2026-09-10 17:30:00")},
    ]
    df = pd.DataFrame(data)
    results = detect_duplicate_charges(df)
    assert len(results) == 1
    assert results[0]["likely_double_entry"] is False


def test_different_categories_not_flagged():
    data = [
        {"id": 1, "expense_date": pd.Timestamp("2026-09-05"), "amount": 500.0, "display_category": "Shopping", "note": None, "created_at": pd.Timestamp("2026-09-05 10:00:00")},
        {"id": 2, "expense_date": pd.Timestamp("2026-09-05"), "amount": 500.0, "display_category": "Bills", "note": None, "created_at": pd.Timestamp("2026-09-05 10:01:00")},
    ]
    df = pd.DataFrame(data)
    assert detect_duplicate_charges(df) == []
