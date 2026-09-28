from datetime import date
from backend.models.expense import Expense
from backend.services import ml_service


def test_suggest_category_with_enough_history(db_session):
    d = date(2026, 9, 1)
    rows = [
        ("Uber ride", "Travel"), ("Taxi to office", "Travel"), ("Cab ride", "Travel"),
        ("Flight ticket", "Travel"), ("Metro pass", "Travel"),
        ("Lunch", "Food"), ("Dinner", "Food"), ("Groceries", "Food"), ("Snacks", "Food"),
    ]
    for note, cat in rows:
        db_session.add(Expense(user_id=999101, expense_date=d, amount=100, category=cat, note=note))
    db_session.commit()

    result = ml_service.suggest_category(db_session, user_id=999101, note="cab to the airport")
    assert result["available"] is True
    assert result["suggested_category"] == "Travel"
    assert isinstance(result["suggested_category"], str)  # not a numpy type


def test_not_enough_history_is_honest_not_a_guess(db_session):
    result = ml_service.suggest_category(db_session, user_id=999102, note="anything")
    assert result["available"] is False


def test_empty_note_rejected(db_session):
    result = ml_service.suggest_category(db_session, user_id=999103, note="   ")
    assert result["available"] is False
