from datetime import datetime, timezone


def test_user_creation_and_retrieval(client):
    user_payload = {
        "display_name": "Aarav Patel",
        "age_bracket": "21-25",
        "city": "Ahmedabad",
        "instagram_handle": "@aarav_garba",
    }
    create_res = client.post("/api/users", json=user_payload)
    assert create_res.status_code == 201
    user = create_res.json()
    assert user["display_name"] == "Aarav Patel"

    get_res = client.get(f"/api/users/{user['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["city"] == "Ahmedabad"


def test_attendance_creation_and_duplicate_prevention(client):
    # 1. Create user
    user_res = client.post(
        "/api/users",
        json={
            "display_name": "Diya Shah",
            "age_bracket": "21-25",
            "city": "Surat",
            "instagram_handle": "@diya_steps",
        },
    )
    user_id = user_res.json()["id"]

    # 2. Create event
    event_res = client.post(
        "/api/events",
        json={
            "name": "Surat Garba Mahotsav",
            "city": "Surat",
            "venue": "Indoor Stadium",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        },
    )
    event_id = event_res.json()["id"]

    # 3. Create attendance
    attendance_payload = {
        "user_id": user_id,
        "event_id": event_id,
        "intent": "hardcore_garba",
        "dance_level": "intermediate",
        "vibes": "energetic, late_night, fast_paced",
        "group_size_preference": 4,
    }
    res1 = client.post("/api/attendances", json=attendance_payload)
    assert res1.status_code == 201
    attendance_data = res1.json()
    assert attendance_data["intent"] == "hardcore_garba"

    # 4. Attempt duplicate attendance creation for same user & event -> 409 CONFLICT
    res2 = client.post("/api/attendances", json=attendance_payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"].lower()

    # 5. Fetch single attendance with user
    get_res = client.get(f"/api/attendances/{attendance_data['id']}")
    assert get_res.status_code == 200
    assert get_res.json()["user"]["display_name"] == "Diya Shah"

    # 6. Fetch by event
    event_attendees = client.get(f"/api/attendances/event/{event_id}").json()
    assert len(event_attendees) == 1

    # 7. Fetch by user
    user_attendances = client.get(f"/api/attendances/user/{user_id}").json()
    assert len(user_attendances) == 1

def test_attendance_partial_update(client):
    # Create user
    user_res = client.post(
        "/api/users",
        json={
            "display_name": "Riya Mehta",
            "city": "Ahmedabad",
        },
    )
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    # Create event
    event_res = client.post(
        "/api/events",
        json={
            "name": "Ahmedabad Garba Night",
            "city": "Ahmedabad",
            "venue": "GMDC Ground",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        },
    )
    assert event_res.status_code == 201
    event_id = event_res.json()["id"]

    # Create attendance
    attendance_res = client.post(
        "/api/attendances",
        json={
            "user_id": user_id,
            "event_id": event_id,
            "intent": "hardcore_garba",
            "dance_level": "beginner",
            "vibes": "energetic",
            "group_size_preference": 4,
        },
    )
    assert attendance_res.status_code == 201
    attendance = attendance_res.json()

    # Partially update only dance level and vibes
    update_res = client.patch(
        f"/api/attendances/{attendance['id']}",
        json={
            "dance_level": "advanced",
            "vibes": "traditional, energetic",
        },
    )

    assert update_res.status_code == 200

    updated = update_res.json()

    assert updated["id"] == attendance["id"]
    assert updated["intent"] == "hardcore_garba"
    assert updated["dance_level"] == "advanced"
    assert updated["vibes"] == "traditional, energetic"
    assert updated["group_size_preference"] == 4
    assert updated["updated_at"] is not None


def test_update_nonexistent_attendance_returns_404(client):
    import uuid

    response = client.patch(
        f"/api/attendances/{uuid.uuid4()}",
        json={"dance_level": "advanced"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Attendance not found"
def test_create_attendance_with_nonexistent_user_returns_404(client):
    event_res = client.post(
        "/api/events",
        json={
            "name": "Test Garba Event",
            "city": "Ahmedabad",
            "venue": "Test Venue",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        },
    )
    assert event_res.status_code == 201
    event_id = event_res.json()["id"]

    response = client.post(
        "/api/attendances",
        json={
            "user_id": "00000000-0000-0000-0000-000000000000",
            "event_id": event_id,
            "intent": "hardcore_garba",
            "dance_level": "beginner",
        },
    )

    assert response.status_code == 404
    assert "user" in response.json()["detail"].lower()


def test_create_attendance_with_nonexistent_event_returns_404(client):
    user_res = client.post(
        "/api/users",
        json={
            "display_name": "Test User",
            "city": "Ahmedabad",
        },
    )
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    response = client.post(
        "/api/attendances",
        json={
            "user_id": user_id,
            "event_id": "00000000-0000-0000-0000-000000000000",
            "intent": "hardcore_garba",
            "dance_level": "beginner",
        },
    )

    assert response.status_code == 404
    assert "event" in response.json()["detail"].lower()


def test_create_attendance_for_inactive_event_returns_400(client):
    user_res = client.post(
        "/api/users",
        json={
            "display_name": "Test User",
            "city": "Ahmedabad",
        },
    )
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    event_res = client.post(
        "/api/events",
        json={
            "name": "Inactive Garba Event",
            "city": "Ahmedabad",
            "venue": "Test Venue",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": False,
        },
    )
    assert event_res.status_code == 201
    event_id = event_res.json()["id"]

    response = client.post(
        "/api/attendances",
        json={
            "user_id": user_id,
            "event_id": event_id,
            "intent": "hardcore_garba",
            "dance_level": "beginner",
        },
    )

    assert response.status_code == 400
    assert "no longer active" in response.json()["detail"].lower()


def test_create_attendance_with_invalid_group_size_returns_422(client):
    user_res = client.post(
        "/api/users",
        json={
            "display_name": "Test User",
            "city": "Ahmedabad",
        },
    )
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    event_res = client.post(
        "/api/events",
        json={
            "name": "Test Garba Event",
            "city": "Ahmedabad",
            "venue": "Test Venue",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        },
    )
    assert event_res.status_code == 201
    event_id = event_res.json()["id"]

    response = client.post(
        "/api/attendances",
        json={
            "user_id": user_id,
            "event_id": event_id,
            "intent": "hardcore_garba",
            "dance_level": "beginner",
            "group_size_preference": 0,
        },
    )

    assert response.status_code == 422