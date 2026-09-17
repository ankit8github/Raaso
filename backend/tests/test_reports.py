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

