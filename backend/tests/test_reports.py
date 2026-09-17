import uuid


def test_safety_report_submission(client):
    u1 = client.post(
        "/api/users",
        json={"display_name": "Reporter User", "city": "Mumbai"},
    ).json()

    u2 = client.post(
        "/api/users",
        json={"display_name": "Offender User", "city": "Mumbai"},
    ).json()

    # 1. Valid report
    report_res = client.post(
        "/api/reports",
        json={
            "reporter_id": u1["id"],
            "reported_user_id": u2["id"],
            "reason": "Harassment / inappropriate behavior",
            "details": "User was sending unsolicited messages.",
        },
    )
    assert report_res.status_code == 201
    report = report_res.json()
    assert report["reason"] == "Harassment / inappropriate behavior"
    assert report["status"] == "open"

    # 2. Self-reporting prohibited
    self_report = client.post(
        "/api/reports",
        json={
            "reporter_id": u1["id"],
            "reported_user_id": u1["id"],
            "reason": "Self test",
        },
    )
    assert self_report.status_code == 400
    assert "cannot report yourself" in self_report.json()["detail"].lower()

    # 3. Nonexistent user
    nonexistent = client.post(
        "/api/reports",
        json={
            "reporter_id": u1["id"],
            "reported_user_id": str(uuid.uuid4()),
            "reason": "Unknown",
        },
    )
    assert nonexistent.status_code == 404

def test_report_with_nonexistent_reporter_returns_404(client):
    reported_user = client.post(
        "/api/users",
        json={"display_name": "Reported User", "city": "Mumbai"},
    ).json()

    response = client.post(
        "/api/reports",
        json={
            "reporter_id": str(uuid.uuid4()),
            "reported_user_id": reported_user["id"],
            "reason": "Harassment",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Reporter user not found"


def test_report_without_optional_details_succeeds(client):
    reporter = client.post(
        "/api/users",
        json={"display_name": "Reporter", "city": "Mumbai"},
    ).json()

    reported = client.post(
        "/api/users",
        json={"display_name": "Reported", "city": "Mumbai"},
    ).json()

    response = client.post(
        "/api/reports",
        json={
            "reporter_id": reporter["id"],
            "reported_user_id": reported["id"],
            "reason": "Harassment",
        },
    )

    assert response.status_code == 201

    report = response.json()
    assert report["details"] is None
    assert report["status"] == "open"


def test_report_with_empty_reason_returns_422(client):
    reporter = client.post(
        "/api/users",
        json={"display_name": "Reporter", "city": "Mumbai"},
    ).json()

    reported = client.post(
        "/api/users",
        json={"display_name": "Reported", "city": "Mumbai"},
    ).json()

    response = client.post(
        "/api/reports",
        json={
            "reporter_id": reporter["id"],
            "reported_user_id": reported["id"],
            "reason": "",
        },
    )

    assert response.status_code == 422


def test_report_with_missing_required_field_returns_422(client):
    reporter = client.post(
        "/api/users",
        json={"display_name": "Reporter", "city": "Mumbai"},
    ).json()

    response = client.post(
        "/api/reports",
        json={
            "reporter_id": reporter["id"],
            "reason": "Harassment",
        },
    )

    assert response.status_code == 422