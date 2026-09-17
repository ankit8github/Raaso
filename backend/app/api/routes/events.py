import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.models import Event
from app.db.session import get_db
from app.schemas.event import EventCreate, EventResponse

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=list[EventResponse])
def list_events(
    city: str | None = Query(None, description="Filter events by city"),
    active_only: bool = Query(True, description="Only return active events"),
    db: Session = Depends(get_db),
) -> list[Event]:
    stmt = select(Event)
    if active_only:
        stmt = stmt.where(Event.is_active.is_(True))
    if city:
        stmt = stmt.where(Event.city.ilike(f"%{city.strip()}%"))
    stmt = stmt.order_by(Event.starts_at.asc())
    return list(db.scalars(stmt).all())


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
) -> Event:
    event = Event(**event_in.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Event:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event

