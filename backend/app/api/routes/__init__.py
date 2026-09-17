from fastapi import APIRouter

from app.api.routes.attendances import router as attendances_router
from app.api.routes.events import router as events_router
from app.api.routes.matches import router as matches_router
from app.api.routes.reports import router as reports_router
from app.api.routes.squads import router as squads_router
from app.api.routes.users import router as users_router

api_router = APIRouter(prefix="/api")

api_router.include_router(events_router)
api_router.include_router(users_router)
api_router.include_router(attendances_router)
api_router.include_router(matches_router)
api_router.include_router(squads_router)
api_router.include_router(reports_router)

__all__ = ["api_router"]

