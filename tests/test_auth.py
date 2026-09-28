def test_register_success(client):
    r = client.post("/api/auth/register", json={
        "full_name": "Alice", "email": "alice_auth_test@example.com", "password": "alicepass123",
    })
    assert r.status_code == 201
    assert r.json()["email"] == "alice_auth_test@example.com"


def test_register_duplicate_email_rejected(client):
    payload = {"full_name": "Dup", "email": "dup_test@example.com", "password": "duppass123"}
    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code == 201
    r2 = client.post("/api/auth/register", json=payload)
    assert r2.status_code == 400


def test_password_too_short_rejected(client):
    r = client.post("/api/auth/register", json={
        "full_name": "Shorty", "email": "shorty@example.com", "password": "short",
    })
    assert r.status_code == 422


def test_login_wrong_password_rejected(client):
    client.post("/api/auth/register", json={
        "full_name": "Bob", "email": "bob_auth_test@example.com", "password": "bobpass123",
    })
    r = client.post("/api/auth/login", json={"email": "bob_auth_test@example.com", "password": "wrongpass"})
    assert r.status_code == 401


def test_login_unknown_email_rejected(client):
    r = client.post("/api/auth/login", json={"email": "nobody_here@example.com", "password": "whatever123"})
    assert r.status_code == 401


def test_unauthenticated_request_rejected(client):
    r = client.get("/api/expenses")
    assert r.status_code in (401, 403)


def test_email_casing_is_normalized(client):
    """Regression test: found via QA sweep - email comparison used to
    be case-sensitive, allowing duplicate accounts that differed only
    by casing, and breaking login if casing didn't match exactly."""
    r1 = client.post("/api/auth/register", json={
        "full_name": "Casing Test", "email": "CasingTest@Example.com", "password": "casingpass123",
    })
    assert r1.status_code == 201
    assert r1.json()["email"] == "casingtest@example.com"

    r2 = client.post("/api/auth/register", json={
        "full_name": "Casing Test 2", "email": "casingtest@example.com", "password": "otherpass123",
    })
    assert r2.status_code == 400  # same account, different casing - rejected as duplicate

    login = client.post("/api/auth/login", json={
        "email": "CASINGTEST@EXAMPLE.COM", "password": "casingpass123",
    })
    assert login.status_code == 200
