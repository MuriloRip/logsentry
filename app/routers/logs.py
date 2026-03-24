from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.log_entry import LogLevel
from app.routers.auth import get_current_user
from app.schemas.log_schema import (
    LogEntryCreate,
    LogEntryBatch,
    LogEntryResponse,
    LogQueryParams,
    PaginatedResponse,
)
from app.services.log_service import (
    create_log_entry,
    create_log_entries_batch,
    query_log_entries,
    get_log_entry_by_id,
    delete_log_entry,
)

router = APIRouter(prefix="/logs", tags=["Logs"])


@router.post("/", response_model=LogEntryResponse, status_code=status.HTTP_201_CREATED)
def ingest_log(
    log_data: LogEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ingest a single log entry."""
    entry = create_log_entry(db, log_data, current_user.id)
    return entry


@router.post("/batch", status_code=status.HTTP_201_CREATED)
def ingest_batch(
    batch: LogEntryBatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ingest multiple log entries in a single request (max 100)."""
    count = create_log_entries_batch(db, batch, current_user.id)
    return {"message": f"Successfully ingested {count} log entries"}


@router.get("/", response_model=PaginatedResponse)
def list_logs(
    level: Optional[LogLevel] = None,
    service_name: Optional[str] = None,
    source: Optional[str] = None,
    environment: Optional[str] = None,
    trace_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Query log entries with optional filtering and pagination."""
    params = LogQueryParams(
        level=level,
        service_name=service_name,
        source=source,
        environment=environment,
        trace_id=trace_id,
        start_date=start_date,
        end_date=end_date,
        search=search,
        page=page,
        page_size=page_size,
    )
    return query_log_entries(db, current_user.id, params)


@router.get("/{entry_id}", response_model=LogEntryResponse)
def get_log(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific log entry by ID."""
    entry = get_log_entry_by_id(db, entry_id, current_user.id)
    if not entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    return entry


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_log(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a log entry."""
    deleted = delete_log_entry(db, entry_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Log entry not found")
