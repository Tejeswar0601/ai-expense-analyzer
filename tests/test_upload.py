import io


def test_upload_valid_and_invalid_rows(client, auth_headers):
    csv_content = (
        "Date,Amount,Category,Note\n"
        "2026-09-01,250,Food,Lunch\n"
        "2026-09-02,-50,Food,Bad amount\n"
        "2026-09-03,100,Groceries,Unknown category mapped to Others\n"
    )
    files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}

    r = client.post(
        "/api/expenses/upload", files=files, params={"dry_run": True}, headers=auth_headers
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid_count"] == 2
    assert body["error_count"] == 1

    # Unknown category should be mapped to Others with a custom_category
    mapped = [row for row in body["valid_preview"] if row["category"] == "Others"]
    assert len(mapped) == 1
    assert mapped[0]["custom_category"] == "Groceries"


def test_upload_missing_required_column_rejected(client, auth_headers):
    csv_content = "Date,Amount\n2026-09-01,250\n"
    files = {"file": ("bad.csv", io.BytesIO(csv_content.encode()), "text/csv")}

    r = client.post(
        "/api/expenses/upload", files=files, params={"dry_run": True}, headers=auth_headers
    )
    assert r.status_code == 400


def test_upload_confirm_actually_inserts(client, auth_headers):
    csv_content = "Date,Amount,Category,Note\n2026-09-05,300,Bills,Electricity\n"
    files = {"file": ("confirm.csv", io.BytesIO(csv_content.encode()), "text/csv")}

    r = client.post(
        "/api/expenses/upload", files=files, params={"dry_run": False}, headers=auth_headers
    )
    assert r.status_code == 200
    assert r.json()["inserted_count"] == 1

    listing = client.get("/api/expenses", headers=auth_headers)
    notes = [e["note"] for e in listing.json()]
    assert "Electricity" in notes
