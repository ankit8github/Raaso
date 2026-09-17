import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    display_name: Mapped[str] = mapped_column(String(100))
    age_bracket: Mapped[str | None] = mapped_column(String(30), nullable=True)
    city: Mapped[str] = mapped_column(String(100))
    instagram_handle: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    attendances: Mapped[list["Attendance"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100))
    venue: Mapped[str] = mapped_column(String(200))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    ticket_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=datetime.utcnow,
    )

    attendances: Mapped[list["Attendance"]] = relationship(
        back_populates="event",
    )


class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
    )

    intent: Mapped[str] = mapped_column(String(50))
    dance_level: Mapped[str] = mapped_column(String(50))
    vibes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    group_size_preference: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user: Mapped["User"] = relationship(
        back_populates="attendances",
    )

    event: Mapped["Event"] = relationship(
        back_populates="attendances",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "event_id",
            name="uq_attendance_user_event",
        ),
    )


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    attendance_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("attendances.id", ondelete="CASCADE"),
    )

    matched_attendance_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("attendances.id", ondelete="CASCADE"),
    )

    score: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    attendance: Mapped["Attendance"] = relationship(
        "Attendance",
        foreign_keys=[attendance_id],
    )
    matched_attendance: Mapped["Attendance"] = relationship(
        "Attendance",
        foreign_keys=[matched_attendance_id],
    )

    __table_args__ = (
        UniqueConstraint(
            "attendance_id",
            "matched_attendance_id",
            name="uq_match_attendance_pair",
        ),
    )


class Squad(Base):
    __tablename__ = "squads"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"),
    )

    name: Mapped[str] = mapped_column(String(100))
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    max_members: Mapped[int] = mapped_column(
        Integer,
        default=6,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    event: Mapped["Event"] = relationship("Event")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])

    members: Mapped[list["SquadMember"]] = relationship(
        back_populates="squad",
        cascade="all, delete-orphan",
    )


class SquadMember(Base):
    __tablename__ = "squad_members"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    squad_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("squads.id", ondelete="CASCADE"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    squad: Mapped["Squad"] = relationship(
        back_populates="members",
    )
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        UniqueConstraint(
            "squad_id",
            "user_id",
            name="uq_squad_user",
        ),
    )


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    reporter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    reported_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    reason: Mapped[str] = mapped_column(String(100))
    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="open",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
    )

    reporter: Mapped["User"] = relationship("User", foreign_keys=[reporter_id])
    reported_user: Mapped["User"] = relationship("User", foreign_keys=[reported_user_id])
