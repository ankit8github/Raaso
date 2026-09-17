from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models.models import Report, User
from app.db.session import get_db
from app.schemas.report import ReportCreate, ReportResponse

router = APIRouter(prefix="/reports", tags=["Safety Reports"])


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def submit_report(
    report_in: ReportCreate,
    db: Session = Depends(get_db),
) -> Report:
    if report_in.reporter_id == report_in.reported_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot report yourself",
        )

    reporter = db.get(User, report_in.reporter_id)
    if not reporter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporter user not found",
        )

    reported_user = db.get(User, report_in.reported_user_id)
    if not reported_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reported user not found",
        )

    report = Report(**report_in.model_dump(), status="open")
    db.add(report)
    db.commit()
    db.refresh(report)
    return report

