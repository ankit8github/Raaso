import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.db.models.models import Attendance, Event, User
from app.db.session import get_db
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
    AttendanceWithUserResponse,
)

router = APIRouter(prefix="/attendances", tags=["Attendances"])


@router.post(
    "",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_attendance(
    attendance_in: AttendanceCreate,
    db: Session = Depends(get_db),
) -> Attendance:
    user = db.get(User, attendance_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    event = db.get(Event, attendance_in.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    if not event.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is no longer active",
        )

    stmt = select(Attendance).where(
        Attendance.user_id == attendance_in.user_id,
        Attendance.event_id == attendance_in.event_id,
    )
    existing = db.scalar(stmt)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance profile already exists for this event",
        )

    attendance = Attendance(**attendance_in.model_dump())
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.get("/event/{event_id}", response_model=list[AttendanceWithUserResponse])
def get_event_attendances(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[Attendance]:
    stmt = (
        select(Attendance)
        .options(joinedload(Attendance.user))
        .where(Attendance.event_id == event_id)
        .order_by(Attendance.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.get("/user/{user_id}", response_model=list[AttendanceResponse])
def get_user_attendances(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[Attendance]:
    stmt = (
        select(Attendance)
        .where(Attendance.user_id == user_id)
        .order_by(Attendance.created_at.desc())
    )
    return list(db.scalars(stmt).all())


@router.get("/{attendance_id}", response_model=AttendanceWithUserResponse)
def get_attendance(
    attendance_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> Attendance:
    stmt = (
        select(Attendance)
        .options(joinedload(Attendance.user))
        .where(Attendance.id == attendance_id)
    )
    attendance = db.scalar(stmt)

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance not found",
        )

    return attendance


@router.patch("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: uuid.UUID,
    attendance_in: AttendanceUpdate,
    db: Session = Depends(get_db),
) -> Attendance:
    attendance = db.get(Attendance, attendance_id)

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance not found",
        )

    update_data = attendance_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(attendance, field, value)

    db.commit()
    db.refresh(attendance)

    return attendance