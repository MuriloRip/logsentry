from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.analytics_service import (
    get_log_stats,
    get_top_error_sources,
    get_service_breakdown,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/stats")
def log_statistics(
    hours: int = Query(default=24, ge=1, le=720, description="Period in hours"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get aggregated log statistics for the specified time period."""
    return get_log_stats(db, current_user.id, hours)


@router.get("/top-errors")
def top_error_sources(
    hours: int = Query(default=24, ge=1, le=720),
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get sources with the highest error counts."""
    return get_top_error_sources(db, current_user.id, limit, hours)


@router.get("/services")
def service_breakdown(
    hours: int = Query(default=24, ge=1, le=720),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get log count breakdown by service."""
    return get_service_breakdown(db, current_user.id, hours)
