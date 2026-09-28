from backend.services.ai_insight_service import compute_confidence, save_insights, get_saved_insights


def test_confidence_scales_with_transaction_count():
    assert compute_confidence(0) == 0.0
    assert compute_confidence(15) == 1.0
    assert compute_confidence(100) == 1.0  # capped, never exceeds 1.0


def test_save_and_retrieve_insights(db_session):
    fake_insights = {
        "spending_summary": "s", "spending_patterns": "p", "main_expense_categories": "m",
        "recommendations": ["r1", "r2"], "monthly_summary": "sum",
    }
    save_insights(db_session, user_id=999001, month_year="2026-09", ai_insights=fake_insights, transaction_count=10)

    saved = get_saved_insights(db_session, user_id=999001, month_year="2026-09")
    assert saved["spending_summary"] == "s"
    assert len(saved["recommendations"]) == 2


def test_regenerating_replaces_not_accumulates(db_session):
    first = {
        "spending_summary": "old", "spending_patterns": "old", "main_expense_categories": "old",
        "recommendations": ["a", "b", "c"], "monthly_summary": "old",
    }
    save_insights(db_session, user_id=999002, month_year="2026-09", ai_insights=first, transaction_count=5)

    second = {
        "spending_summary": "new", "spending_patterns": "new", "main_expense_categories": "new",
        "recommendations": ["x"], "monthly_summary": "new",
    }
    save_insights(db_session, user_id=999002, month_year="2026-09", ai_insights=second, transaction_count=20)

    saved = get_saved_insights(db_session, user_id=999002, month_year="2026-09")
    assert saved["spending_summary"] == "new"
    assert len(saved["recommendations"]) == 1  # replaced, not appended to the old 3
