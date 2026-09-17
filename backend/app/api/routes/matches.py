import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.models import Attendance, Event, Match, User
from app.db.session import get_db
from app.schemas.attendance import AttendanceResponse
from app.schemas.match import MatchDetailResponse
from app.schemas.user import UserResponse
from app.services.matching import matching_service
from app.services.whatsapp import generate_attendee_connect_link

router = APIRouter(prefix="/attendances", tags=["Matches"])


@router.get("/{attendance_id}/matches", response_model=list[MatchDetailResponse])
def get_attendance_matches(
    attendance_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[MatchDetailResponse]:
    attendance = db.get(Attendance, attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance not found",
        )

    event = db.get(Event, attendance.event_id)
    event_name = event.name if event else "Garba Night"

    # Compute matches via deterministic matching service
    matched_data = matching_service.find_matches_for_attendance(
        db, attendance, limit=limit
    )

    results: list[MatchDetailResponse] = []
    for item in matched_data:
        matched_user: User = item["matched_user"]
        matched_attendance: Attendance = item["matched_attendance"]
        score: int = item["score"]
        reasons: list[str] = item["reasons"]

        # Persist or update match record in DB
        match_stmt = select(Match).where(
            Match.attendance_id == attendance.id,
            Match.matched_attendance_id == matched_attendance.id,
        )
        existing_match = db.scalar(match_stmt)
        if existing_match:
            existing_match.score = score
            match_id = existing_match.id
        else:
            new_match = Match(
                attendance_id=attendance.id,
                matched_attendance_id=matched_attendance.id,
                score=score,
                status="active",
            )
            db.add(new_match)
            db.flush()
            match_id = new_match.id

        wa_link = generate_attendee_connect_link(
            event_name=event_name,
            matched_display_name=matched_user.display_name,
        )

        results.append(
            MatchDetailResponse(
                id=match_id,
                attendance_id=attendance.id,
                matched_attendance_id=matched_attendance.id,
                score=score,
                status="active",
                matched_user=UserResponse.model_validate(matched_user),
                matched_attendance=AttendanceResponse.model_validate(matched_attendance),
                reasons=reasons,
                whatsapp_link=wa_link,
            )
        )

    db.commit()
    return results

