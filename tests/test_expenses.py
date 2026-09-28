def test_add_and_list_expense(client, auth_headers):
    r = client.post("/api/expenses", json={
        "expense_date": "2026-09-01", "amount": 250, "category": "Food", "note": "Test lunch",
    }, headers=auth_headers)
    assert r.status_code == 201

    r2 = client.get("/api/expenses", headers=auth_headers)
    assert r2.status_code == 200
    assert len(r2.json()) == 1
    assert r2.json()[0]["note"] == "Test lunch"


def test_negative_amount_rejected(client, auth_headers):
    r = client.post("/api/expenses", json={
        "expense_date": "2026-09-01", "amount": -50, "category": "Food",
    }, headers=auth_headers)
    assert r.status_code == 422


def test_invalid_category_rejected(client, auth_headers):
    r = client.post("/api/expenses", json={
        "expense_date": "2026-09-01", "amount": 50, "category": "NotACategory",
    }, headers=auth_headers)
    assert r.status_code == 422


def test_update_expense(client, auth_headers):
    add = client.post("/api/expenses", json={
        "expense_date": "2026-09-01", "amount": 100, "category": "Food",
    }, headers=auth_headers)
    expense_id = add.json()["id"]

    update = client.put(f"/api/expenses/{expense_id}", json={"amount": 150}, headers=auth_headers)
    assert update.status_code == 200
    assert float(update.json()["amount"]) == 150.0


def test_delete_expense(client, auth_headers):
    add = client.post("/api/expenses", json={
        "expense_date": "2026-09-01", "amount": 75, "category": "Travel",
    }, headers=auth_headers)
    expense_id = add.json()["id"]

    delete = client.delete(f"/api/expenses/{expense_id}", headers=auth_headers)
    assert delete.status_code == 204

    get_after = client.get(f"/api/expenses/{expense_id}", headers=auth_headers)
    assert get_after.status_code == 404


def test_users_cannot_see_each_others_expenses(client, auth_headers):
    client.post("/api/expenses", json={
        "expense_date": "2026-09-01", "amount": 100, "category": "Food", "note": "A's expense",
    }, headers=auth_headers)

    client.post("/api/auth/register", json={
        "full_name": "Isolation Test", "email": "isolation_test_user@example.com", "password": "isopass123",
    })
    login2 = client.post("/api/auth/login", json={
        "email": "isolation_test_user@example.com", "password": "isopass123",
    })
    headers_b = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    r = client.get("/api/expenses", headers=headers_b)
    assert r.status_code == 200
    assert len(r.json()) == 0


def test_cannot_delete_another_users_expense(client, auth_headers):
    add = client.post("/api/expenses", json={
        "expense_date": "2026-09-01", "amount": 500, "category": "Shopping",
    }, headers=auth_headers)
    expense_id = add.json()["id"]

    client.post("/api/auth/register", json={
        "full_name": "Attacker", "email": "attacker_test@example.com", "password": "attackpass123",
    })
    login2 = client.post("/api/auth/login", json={
        "email": "attacker_test@example.com", "password": "attackpass123",
    })
    headers_attacker = {"Authorization": f"Bearer {login2.json()['access_token']}"}

    r = client.delete(f"/api/expenses/{expense_id}", headers=headers_attacker)
    assert r.status_code == 404
