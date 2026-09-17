from datetime import datetime, timezone


def test_squad_lifecycle_and_capacity_limits(client):
    # Setup event
    event = client.post(
        "/api/events",
        json={
            "name": "Karnavati Club Garba",
            "city": "Ahmedabad",
            "venue": "SG Highway",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        },
    ).json()

    # Create users
    creator = client.post(
        "/api/users",
        json={"display_name": "Rohan", "city": "Ahmedabad"},
    ).json()

    user2 = client.post(
        "/api/users",
        json={"display_name": "Pooja", "city": "Ahmedabad"},
    ).json()

    user3 = client.post(
        "/api/users",
        json={"display_name": "Yash", "city": "Ahmedabad"},
    ).json()

    # 1. Create squad with capacity of 2
    squad_payload = {
        "event_id": event["id"],
        "name": "Dandiya Warriors",
        "created_by": creator["id"],
        "max_members": 2,
    }
    squad_res = client.post("/api/squads", json=squad_payload)
    assert squad_res.status_code == 201
    squad = squad_res.json()
    assert squad["name"] == "Dandiya Warriors"
    assert squad["member_count"] == 1
    assert squad["members"][0]["user_id"] == creator["id"]
    assert "https://wa.me/?text=" in squad["whatsapp_link"]

    # 2. List squads for event
    list_res = client.get(f"/api/squads/event/{event['id']}")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1
    assert list_res.json()[0]["member_count"] == 1

    # 3. Creator tries to join again -> 400
    dup_join = client.post(
        f"/api/squads/{squad['id']}/join",
        json={"user_id": creator["id"]},
    )
    assert dup_join.status_code == 400
    assert "already an active member" in dup_join.json()["detail"].lower()

    # 4. User 2 joins (reaches max capacity 2)
    join_res = client.post(
        f"/api/squads/{squad['id']}/join",
        json={"user_id": user2["id"]},
    )
    assert join_res.status_code == 200
    assert join_res.json()["member_count"] == 2

    # 5. User 3 tries to join full squad -> 400
    full_join = client.post(
        f"/api/squads/{squad['id']}/join",
        json={"user_id": user3["id"]},
    )
    assert full_join.status_code == 400
    assert "maximum capacity" in full_join.json()["detail"].lower()

    # 6. User 2 leaves squad
    leave_res = client.post(
        f"/api/squads/{squad['id']}/leave",
        json={"user_id": user2["id"]},
    )
    assert leave_res.status_code == 200
    assert leave_res.json()["status"] == "left"

    # Member count should now be 1
    squad_after_leave = client.get(f"/api/squads/{squad['id']}").json()
    assert squad_after_leave["member_count"] == 1

    # 7. Now User 3 can join
    user3_join = client.post(
        f"/api/squads/{squad['id']}/join",
        json={"user_id": user3["id"]},
    )
    assert user3_join.status_code == 200
    assert user3_join.json()["member_count"] == 2

def test_create_squad_with_nonexistent_event_returns_404(client):
    user_res = client.post(
        "/api/users",
        json={"display_name": "Creator", "city": "Ahmedabad"},
    )
    assert user_res.status_code == 201

    response = client.post(
        "/api/squads",
        json={
            "event_id": "00000000-0000-0000-0000-000000000000",
            "name": "Test Squad",
            "created_by": user_res.json()["id"],
            "max_members": 4,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_create_squad_with_nonexistent_creator_returns_404(client):
    event_res = client.post(
        "/api/events",
        json={
            "name": "Test Garba",
            "city": "Ahmedabad",
            "venue": "Test Venue",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        },
    )
    assert event_res.status_code == 201

    response = client.post(
        "/api/squads",
        json={
            "event_id": event_res.json()["id"],
            "name": "Test Squad",
            "created_by": "00000000-0000-0000-0000-000000000000",
            "max_members": 4,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Creator user not found"


def test_join_squad_with_nonexistent_user_returns_404(client):
    event = client.post(
        "/api/events",
        json={
            "name": "Test Garba",
            "city": "Ahmedabad",
            "venue": "Test Venue",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        },
    ).json()

    creator = client.post(
        "/api/users",
        json={"display_name": "Creator", "city": "Ahmedabad"},
    ).json()

    squad = client.post(
        "/api/squads",
        json={
            "event_id": event["id"],
            "name": "Test Squad",
            "created_by": creator["id"],
            "max_members": 4,
        },
    ).json()

    response = client.post(
        f"/api/squads/{squad['id']}/join",
        json={
            "user_id": "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_join_nonexistent_squad_returns_404(client):
    response = client.post(
        "/api/squads/00000000-0000-0000-0000-000000000000/join",
        json={
            "user_id": "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Active squad not found"


def test_leave_squad_when_not_a_member_returns_404(client):
    event = client.post(
        "/api/events",
        json={
            "name": "Test Garba",
            "city": "Ahmedabad",
            "venue": "Test Venue",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        },
    ).json()

    creator = client.post(
        "/api/users",
        json={"display_name": "Creator", "city": "Ahmedabad"},
    ).json()

    other_user = client.post(
        "/api/users",
        json={"display_name": "Other User", "city": "Ahmedabad"},
    ).json()

    squad = client.post(
        "/api/squads",
        json={
            "event_id": event["id"],
            "name": "Test Squad",
            "created_by": creator["id"],
            "max_members": 4,
        },
    ).json()

    response = client.post(
        f"/api/squads/{squad['id']}/leave",
        json={"user_id": other_user["id"]},
    )

    assert response.status_code == 404
    assert "membership not found" in response.json()["detail"].lower()