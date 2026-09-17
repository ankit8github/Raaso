from datetime import datetime, timezone


def test_create_and_list_events(client):
    event_payload = {
        "name": "United Way Garba 2026",
        "city": "Vadodara",
        "venue": "Alembic Ground",
        "starts_at": datetime.now(timezone.utc).isoformat(),
        "ticket_url": "https://example.com/tickets",
        "is_active": True,
    }
    create_res = client.post("/api/events", json=event_payload)
    assert create_res.status_code == 201
    created_event = create_res.json()
    assert created_event["name"] == "United Way Garba 2026"
    assert created_event["city"] == "Vadodara"

    # List events
    list_res = client.get("/api/events")
    assert list_res.status_code == 200
    events = list_res.json()
    assert len(events) == 1
    assert events[0]["id"] == created_event["id"]

    # Filter by city
    vadodara_res = client.get("/api/events?city=Vadodara")
    assert len(vadodara_res.json()) == 1

    mumbai_res = client.get("/api/events?city=Mumbai")
    assert len(mumbai_res.json()) == 0

    # Get single event
    single_res = client.get(f"/api/events/{created_event['id']}")
    assert single_res.status_code == 200
    assert single_res.json()["name"] == "United Way Garba 2026"


def test_get_nonexistent_event(client):
    res = client.get("/api/events/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404

