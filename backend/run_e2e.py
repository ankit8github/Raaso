import os
import sys
from datetime import datetime, timezone
from uuid import UUID

os.environ["DATABASE_URL"] = "sqlite:///./e2e.db"

from app.db.models.models import Base, Event
from app.db.session import SessionLocal, engine
import uvicorn


E2E_EVENT_ID = UUID("10d01270-d650-442c-b80a-4adad80be594")


def reset_e2e_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        db.add(
            Event(
                id=E2E_EVENT_ID,
                name="Raaso E2E Garba Night",
                city="Chandigarh",
                venue="E2E Test Venue",
                starts_at=datetime(2026, 10, 18, 19, 0, tzinfo=timezone.utc),
                ends_at=datetime(2026, 10, 18, 23, 0, tzinfo=timezone.utc),
                ticket_url=None,
                is_active=True,
            )
        )
        db.commit()


if __name__ == "__main__":
    if "--reset" in sys.argv:
        reset_e2e_database()
        print("E2E database reset")
    else:
        reset_e2e_database()

        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8001,
        )