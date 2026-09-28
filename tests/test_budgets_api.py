def test_set_budget_upserts_instead_of_duplicating(client, auth_headers):
    r1 = client.post("/api/budgets", json={
        "category": "Food", "monthly_limit": 5000, "month_year": "2026-09",
    }, headers=auth_headers)
    assert r1.status_code == 201
    budget_id = r1.json()["id"]

    r2 = client.post("/api/budgets", json={
        "category": "Food", "monthly_limit": 6000, "month_year": "2026-09",
    }, headers=auth_headers)
    assert r2.status_code == 201
    assert r2.json()["id"] == budget_id
    assert r2.json()["monthly_limit"] == 6000.0


def test_invalid_budget_category_rejected(client, auth_headers):
    r = client.post("/api/budgets", json={
        "category": "NotReal", "monthly_limit": 100, "month_year": "2026-09",
    }, headers=auth_headers)
    assert r.status_code == 422


def test_invalid_month_year_format_rejected(client, auth_headers):
    r = client.post("/api/budgets", json={
        "category": "Food", "monthly_limit": 100, "month_year": "Sept-2026",
    }, headers=auth_headers)
    assert r.status_code == 422


def test_cannot_delete_another_users_budget(client, auth_headers):
    r1 = client.post("/api/budgets", json={
        "category": "Bills", "monthly_limit": 2000, "month_year": "2026-09",
    }, headers=auth_headers)
    budget_id = r1.json()["id"]

    client.post("/api/auth/register", json={
        "full_name": "Budget Attacker", "email": "budget_attacker@example.com", "password": "attackpass123",
    })
    login2 = client.post("/api/auth/login", json={
        "email": "budget_attacker@example.com", "password": "attackpass123",
    })
    headers_attacker = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    r = client.delete(f"/api/budgets/{budget_id}", headers=headers_attacker)
    assert r.status_code == 404
