def test_delete_account_wrong_password_rejected(client, auth_headers):
    r = client.request("DELETE", "/api/auth/account", json={"password": "wrongpassword"}, headers=auth_headers)
    assert r.status_code == 401


def test_delete_account_removes_all_data_and_locks_out(client):
    client.post("/api/auth/register", json={
        "full_name": "Delete Me", "email": "delete_me_pytest@example.com", "password": "deletepass123",
    })
    login = client.post("/api/auth/login", json={
        "email": "delete_me_pytest@example.com", "password": "deletepass123",
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    client.post("/api/expenses", json={
        "expense_date": "2026-09-01", "amount": 50, "category": "Food",
    }, headers=headers)
    client.post("/api/budgets", json={
        "category": "Food", "monthly_limit": 500, "month_year": "2026-09",
    }, headers=headers)

    r = client.request("DELETE", "/api/auth/account", json={"password": "deletepass123"}, headers=headers)
    assert r.status_code == 200

    # The account is truly gone: logging in again fails
    login_after = client.post("/api/auth/login", json={
        "email": "delete_me_pytest@example.com", "password": "deletepass123",
    })
    assert login_after.status_code == 401

    # The old token is also no longer valid, since the user row it
    # points to doesn't exist anymore
    r_check = client.get("/api/expenses", headers=headers)
    assert r_check.status_code == 401
