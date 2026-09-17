import uuid
from datetime import datetime, timezone
from app.db.models.models import Attendance
from app.services.matching import MatchingConfig, MatchingEngine


def test_matching_engine_hard_constraints():
    engine = MatchingEngine()
    event1 = uuid.uuid4()
    event2 = uuid.uuid4()
    user1 = uuid.uuid4()
    user2 = uuid.uuid4()

    att1 = Attendance(
        id=uuid.uuid4(),
        user_id=user1,
        event_id=event1,
        intent="hardcore_garba",
        dance_level="intermediate",
        vibes="energetic, traditional",
        group_size_preference=5,
    )
    att2_diff_event = Attendance(
        id=uuid.uuid4(),
        user_id=user2,
        event_id=event2,
        intent="hardcore_garba",
        dance_level="intermediate",
        vibes="energetic, traditional",
        group_size_preference=5,
    )
    score, reasons = engine.calculate_match_score(att1, att2_diff_event)
    assert score == 0
    assert "Different events" in reasons

    att3_same_user = Attendance(
        id=uuid.uuid4(),
        user_id=user1,
        event_id=event1,
        intent="hardcore_garba",
        dance_level="intermediate",
        vibes="energetic, traditional",
        group_size_preference=5,
    )
    score, reasons = engine.calculate_match_score(att1, att3_same_user)
    assert score == 0
    assert "Same user" in reasons


def test_matching_engine_scoring_behavior():
    engine = MatchingEngine()
    event_id = uuid.uuid4()

    user_a = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="hardcore_garba",
        dance_level="pro",
        vibes="energetic, fast_paced, late_night",
        group_size_preference=6,
    )
    user_b_identical = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="hardcore_garba",
        dance_level="pro",
        vibes="energetic, fast_paced, late_night",
        group_size_preference=6,
    )
    score_identical, reasons_identical = engine.calculate_match_score(user_a, user_b_identical)
    assert score_identical >= 95
    assert any("Both share" in r for r in reasons_identical)
    assert any("Exact dance level match" in r for r in reasons_identical)

    user_c_distant = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="chilling_food",
        dance_level="beginner",
        vibes="relaxed, photography",
        group_size_preference=2,
    )
    score_distant, reasons_distant = engine.calculate_match_score(user_a, user_c_distant)
    assert score_distant < score_identical
    assert score_distant > 0


def test_matching_with_empty_vibes_and_configurable_weights():
    custom_config = MatchingConfig(
        max_intent_score=50,
        max_dance_score=20,
        max_vibes_score=20,
        max_group_size_score=10,
    )
    engine = MatchingEngine(config=custom_config)
    event_id = uuid.uuid4()

    att1 = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="learning",
        dance_level="beginner",
        vibes=None,
        group_size_preference=None,
    )
    att2 = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="learning",
        dance_level="beginner",
        vibes=None,
        group_size_preference=None,
    )
    score, reasons = engine.calculate_match_score(att1, att2)
    assert score > 0
    assert any("Open to all event vibes" in r for r in reasons)


def test_matches_api_endpoint(client):
    # Setup event
    event_res = client.post(
        "/api/events",
        json={
            "name": "Navratri Night 2026",
            "city": "Vadodara",
            "venue": "Navlakhi Ground",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        },
    )
    event_id = event_res.json()["id"]

    # Attendee 1
    u1 = client.post(
        "/api/users",
        json={"display_name": "Kinjal", "city": "Vadodara"},
    ).json()
    att1 = client.post(
        "/api/attendances",
        json={
            "user_id": u1["id"],
            "event_id": event_id,
            "intent": "hardcore_garba",
            "dance_level": "intermediate",
            "vibes": "energetic, traditional",
            "group_size_preference": 5,
        },
    ).json()

    # Attendee 2 (High match)
    u2 = client.post(
        "/api/users",
        json={"display_name": "Meet", "city": "Vadodara"},
    ).json()
    client.post(
        "/api/attendances",
        json={
            "user_id": u2["id"],
            "event_id": event_id,
            "intent": "hardcore_garba",
            "dance_level": "intermediate",
            "vibes": "energetic, traditional",
            "group_size_preference": 5,
        },
    )

    # Attendee 3 (Lower match)
    u3 = client.post(
        "/api/users",
        json={"display_name": "Dev", "city": "Vadodara"},
    ).json()
    client.post(
        "/api/attendances",
        json={
            "user_id": u3["id"],
            "event_id": event_id,
            "intent": "chilling_food",
            "dance_level": "beginner",
            "vibes": "photography",
            "group_size_preference": 2,
        },
    )

    # Request matches for attendee 1
    res = client.get(f"/api/attendances/{att1['id']}/matches")
    assert res.status_code == 200
    matches = res.json()
    assert len(matches) == 2
    # Verify ranked descending order
    assert matches[0]["score"] >= matches[1]["score"]
    assert matches[0]["matched_user"]["display_name"] == "Meet"
    assert "https://wa.me/?text=" in matches[0]["whatsapp_link"]
    assert len(matches[0]["reasons"]) > 0

def test_matching_score_is_bounded_between_zero_and_hundred():
    engine = MatchingEngine()
    event_id = uuid.uuid4()

    att1 = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="hardcore_garba",
        dance_level="pro",
        vibes="energetic, traditional, fast_paced",
        group_size_preference=6,
    )

    att2 = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="hardcore_garba",
        dance_level="pro",
        vibes="energetic, traditional, fast_paced",
        group_size_preference=6,
    )

    score, _ = engine.calculate_match_score(att1, att2)

    assert 0 <= score <= 100


def test_vibe_parser_handles_commas_semicolons_and_case():
    engine = MatchingEngine()

    result = engine.parse_vibes("Energetic, Traditional; late_night, energetic")

    assert result == {
        "energetic",
        "traditional",
        "late_night",
    }


def test_matching_engine_handles_missing_vibes():
    engine = MatchingEngine()
    event_id = uuid.uuid4()

    att1 = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="social_casual",
        dance_level="beginner",
        vibes=None,
        group_size_preference=4,
    )

    att2 = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="social_casual",
        dance_level="beginner",
        vibes="energetic",
        group_size_preference=4,
    )

    score, reasons = engine.calculate_match_score(att1, att2)

    assert score > 0
    assert "Open to all event vibes" in reasons


def test_matching_engine_handles_different_group_preferences():
    engine = MatchingEngine()
    event_id = uuid.uuid4()

    att1 = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="social_casual",
        dance_level="intermediate",
        vibes="energetic",
        group_size_preference=2,
    )

    att2 = Attendance(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        event_id=event_id,
        intent="social_casual",
        dance_level="intermediate",
        vibes="energetic",
        group_size_preference=10,
    )

    score, reasons = engine.calculate_match_score(att1, att2)

    assert score > 0
    assert "Different squad size preferences" in reasons


def test_matches_api_respects_limit(client):
    event = client.post(
        "/api/events",
        json={
            "name": "Limit Test Garba",
            "city": "Ahmedabad",
            "venue": "Test Venue",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        },
    ).json()

    users = []
    for i in range(4):
        user = client.post(
            "/api/users",
            json={
                "display_name": f"Dancer {i}",
                "city": "Ahmedabad",
            },
        ).json()
        users.append(user)

        client.post(
            "/api/attendances",
            json={
                "user_id": user["id"],
                "event_id": event["id"],
                "intent": "social_casual",
                "dance_level": "intermediate",
                "vibes": "energetic",
                "group_size_preference": 4,
            },
        )

    first_attendance = client.get(
        f"/api/attendances/user/{users[0]['id']}"
    ).json()[0]

    response = client.get(
        f"/api/attendances/{first_attendance['id']}/matches?limit=2"
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_matches_api_with_nonexistent_attendance_returns_404(client):
    response = client.get(
        f"/api/attendances/{uuid.uuid4()}/matches"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Attendance not found"