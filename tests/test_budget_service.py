from backend.services.budget_service import _compute_utilization_rows


def test_over_budget_detected():
    budgets = [{"id": 1, "category": "Food", "monthly_limit": 5000.0}]
    spent = {"Food": 7050.0}
    results = _compute_utilization_rows(budgets, spent)
    assert results[0]["status"] == "over_budget"
    assert results[0]["remaining"] == -2050.0


def test_near_limit_detected():
    budgets = [{"id": 1, "category": "Bills", "monthly_limit": 3000.0}]
    spent = {"Bills": 2800.0}
    results = _compute_utilization_rows(budgets, spent)
    assert results[0]["status"] == "near_limit"


def test_on_track_and_zero_spending():
    budgets = [
        {"id": 1, "category": "Entertainment", "monthly_limit": 1000.0},
        {"id": 2, "category": "Travel", "monthly_limit": 500.0},
    ]
    spent = {"Entertainment": 400.0}  # Travel has no spending at all
    results = _compute_utilization_rows(budgets, spent)
    by_cat = {r["category"]: r for r in results}
    assert by_cat["Entertainment"]["status"] == "on_track"
    assert by_cat["Travel"]["spent"] == 0.0
    assert by_cat["Travel"]["status"] == "on_track"


def test_results_sorted_by_percent_used_descending():
    budgets = [
        {"id": 1, "category": "A", "monthly_limit": 100.0},
        {"id": 2, "category": "B", "monthly_limit": 100.0},
    ]
    spent = {"A": 50.0, "B": 150.0}
    results = _compute_utilization_rows(budgets, spent)
    assert results[0]["category"] == "B"  # 150% comes before 50%
