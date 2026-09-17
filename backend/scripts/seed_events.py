import uuid
from datetime import datetime, timezone, timedelta
from app.db.session import SessionLocal
from app.db.models.models import Event, User, Attendance, Squad, SquadMember


def seed_data():
    db = SessionLocal()
    try:
        if db.query(Event).count() > 0:
            print("Database already contains events. Skipping seeding.")
            return

        now = datetime.now(timezone.utc)
        events_data = [
            {
                "name": "United Way of Baroda Garba Mahotsav",
                "city": "Vadodara",
                "venue": "Alembic Ground, Gorwa",
                "starts_at": now + timedelta(days=5, hours=19),
                "ends_at": now + timedelta(days=5, hours=24),
                "ticket_url": "https://unitedwaybaroda.org",
                "is_active": True,
            },
            {
                "name": "Karnavati Club Navratri Utsav",
                "city": "Ahmedabad",
                "venue": "SG Highway, Karnavati Club Lawn",
                "starts_at": now + timedelta(days=6, hours=20),
                "ends_at": now + timedelta(days=6, hours=25),
                "ticket_url": "https://karnavaticlub.com",
                "is_active": True,
            },
            {
                "name": "Dome Dandiya Nites with Ta-Dhom",
                "city": "Mumbai",
                "venue": "Dome SVP Stadium, Worli",
                "starts_at": now + timedelta(days=7, hours=19, minutes=30),
                "ends_at": now + timedelta(days=7, hours=24),
                "ticket_url": "https://insider.in",
                "is_active": True,
            },
            {
                "name": "Surat Rasotsav Grand Dandiya",
                "city": "Surat",
                "venue": "Indoor Stadium, Athwa Lines",
                "starts_at": now + timedelta(days=8, hours=20),
                "ends_at": now + timedelta(days=8, hours=25),
                "ticket_url": "https://bookmyshow.com",
                "is_active": True,
            },
        ]

        created_events = []
        for ed in events_data:
            ev = Event(**ed)
            db.add(ev)
            created_events.append(ev)
        db.flush()

        # Seed 3 initial users and attendances for the first event so match discovery has real profiles to match with
        first_event = created_events[0]

        u1 = User(
            display_name="Devang Mehta",
            age_bracket="21-25",
            city="Vadodara",
            instagram_handle="@devang_moves",
        )
        u2 = User(
            display_name="Pooja Trivedi",
            age_bracket="21-25",
            city="Vadodara",
            instagram_handle="@pooja_garba",
        )
        u3 = User(
            display_name="Aniket Joshi",
            age_bracket="26-30",
            city="Vadodara",
            instagram_handle="@aniket_steps",
        )
        db.add_all([u1, u2, u3])
        db.flush()

        att1 = Attendance(
            user_id=u1.id,
            event_id=first_event.id,
            intent="hardcore_garba",
            dance_level="pro",
            vibes="fast_paced, late_night, energetic",
            group_size_preference=6,
        )
        att2 = Attendance(
            user_id=u2.id,
            event_id=first_event.id,
            intent="hardcore_garba",
            dance_level="intermediate",
            vibes="energetic, traditional, fast_paced",
            group_size_preference=6,
        )
        att3 = Attendance(
            user_id=u3.id,
            event_id=first_event.id,
            intent="social_casual",
            dance_level="beginner",
            vibes="relaxed, photography, food",
            group_size_preference=4,
        )
        db.add_all([att1, att2, att3])
        db.flush()

        # Seed an initial squad
        squad = Squad(
            event_id=first_event.id,
            name="Baroda Raas Kings",
            created_by=u1.id,
            max_members=6,
            status="active",
        )
        db.add(squad)
        db.flush()

        member1 = SquadMember(
            squad_id=squad.id,
            user_id=u1.id,
            status="active",
        )
        member2 = SquadMember(
            squad_id=squad.id,
            user_id=u2.id,
            status="active",
        )
        db.add_all([member1, member2])

        db.commit()
        print("Database successfully seeded with initial events, attendees, and squads!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()

