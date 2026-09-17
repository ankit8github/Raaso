import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.db.models.models import Event, Squad, SquadMember, User
from app.db.session import get_db
from app.schemas.squad import (
    SquadCreate,
    SquadDetailResponse,
    SquadJoinRequest,
    SquadLeaveRequest,
    SquadMemberResponse,
    SquadResponse,
)
from app.services.whatsapp import generate_squad_invite_link

router = APIRouter(prefix="/squads", tags=["Squads"])


def _get_active_member_count(db: Session, squad_id: uuid.UUID) -> int:
    return db.scalar(
        select(func.count(SquadMember.id)).where(
            SquadMember.squad_id == squad_id,
            SquadMember.status == "active",
        )
    ) or 0


@router.post("", response_model=SquadDetailResponse, status_code=status.HTTP_201_CREATED)
def create_squad(
    squad_in: SquadCreate,
    db: Session = Depends(get_db),
) -> SquadDetailResponse:
    event = db.get(Event, squad_in.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    creator = db.get(User, squad_in.created_by)
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Creator user not found",
        )

    squad = Squad(
        event_id=squad_in.event_id,
        name=squad_in.name,
        created_by=squad_in.created_by,
        max_members=squad_in.max_members,
        status="active",
    )
    db.add(squad)
    db.flush()

    # Automatically add creator as first squad member
    creator_member = SquadMember(
        squad_id=squad.id,
        user_id=squad_in.created_by,
        status="active",
    )
    db.add(creator_member)
    db.commit()
    db.refresh(squad)

    wa_link = generate_squad_invite_link(squad.name, event.name)

    return SquadDetailResponse(
        id=squad.id,
        event_id=squad.event_id,
        name=squad.name,
        created_by=squad.created_by,
        max_members=squad.max_members,
        status=squad.status,
        created_at=squad.created_at,
        member_count=1,
        whatsapp_link=wa_link,
        creator=creator,
        members=[
            SquadMemberResponse(
                id=creator_member.id,
                squad_id=creator_member.squad_id,
                user_id=creator_member.user_id,
                status=creator_member.status,
                joined_at=creator_member.joined_at,
                user=creator,
            )
        ],
    )


@router.get("/event/{event_id}", response_model=list[SquadResponse])
def get_event_squads(
    event_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> list[SquadResponse]:
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    stmt = (
        select(Squad)
        .where(
            Squad.event_id == event_id,
            Squad.status == "active",
        )
        .order_by(Squad.created_at.desc())
    )
    squads = list(db.scalars(stmt).all())

    results = []
    for squad in squads:
        active_count = _get_active_member_count(db, squad.id)
        wa_link = generate_squad_invite_link(squad.name, event.name)
        results.append(
            SquadResponse(
                id=squad.id,
                event_id=squad.event_id,
                name=squad.name,
                created_by=squad.created_by,
                max_members=squad.max_members,
                status=squad.status,
                created_at=squad.created_at,
                member_count=active_count,
                whatsapp_link=wa_link,
            )
        )
    return results


@router.get("/{squad_id}", response_model=SquadDetailResponse)
def get_squad(
    squad_id: uuid.UUID,
    db: Session = Depends(get_db),
) -> SquadDetailResponse:
    stmt = (
        select(Squad)
        .options(
            joinedload(Squad.creator),
            joinedload(Squad.event),
            joinedload(Squad.members).joinedload(SquadMember.user),
        )
        .where(Squad.id == squad_id)
    )
    squad = db.scalar(stmt)
    if not squad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Squad not found",
        )

    active_members = [m for m in squad.members if m.status == "active"]
    wa_link = generate_squad_invite_link(squad.name, squad.event.name if squad.event else "Garba")

    return SquadDetailResponse(
        id=squad.id,
        event_id=squad.event_id,
        name=squad.name,
        created_by=squad.created_by,
        max_members=squad.max_members,
        status=squad.status,
        created_at=squad.created_at,
        member_count=len(active_members),
        whatsapp_link=wa_link,
        creator=squad.creator,
        members=[
            SquadMemberResponse(
                id=m.id,
                squad_id=m.squad_id,
                user_id=m.user_id,
                status=m.status,
                joined_at=m.joined_at,
                user=m.user,
            )
            for m in active_members
        ],
    )


@router.post("/{squad_id}/join", response_model=SquadDetailResponse)
def join_squad(
    squad_id: uuid.UUID,
    join_in: SquadJoinRequest,
    db: Session = Depends(get_db),
) -> SquadDetailResponse:
    squad = db.get(Squad, squad_id)
    if not squad or squad.status != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active squad not found",
        )

    user = db.get(User, join_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Check capacity
    active_count = _get_active_member_count(db, squad.id)
    if active_count >= squad.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Squad is already at maximum capacity",
        )

    # Check existing membership
    mem_stmt = select(SquadMember).where(
        SquadMember.squad_id == squad.id,
        SquadMember.user_id == user.id,
    )
    existing_member = db.scalar(mem_stmt)
    if existing_member:
        if existing_member.status == "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already an active member of this squad",
            )
        else:
            # Reactivate membership
            existing_member.status = "active"
            db.commit()
    else:
        new_member = SquadMember(
            squad_id=squad.id,
            user_id=user.id,
            status="active",
        )
        db.add(new_member)
        db.commit()

    return get_squad(squad.id, db)


@router.post("/{squad_id}/leave", response_model=dict[str, str])
def leave_squad(
    squad_id: uuid.UUID,
    leave_in: SquadLeaveRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    mem_stmt = select(SquadMember).where(
        SquadMember.squad_id == squad_id,
        SquadMember.user_id == leave_in.user_id,
        SquadMember.status == "active",
    )
    member = db.scalar(mem_stmt)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active squad membership not found",
        )

    member.status = "left"
    db.commit()

    return {"status": "left", "message": "Successfully left the squad"}

