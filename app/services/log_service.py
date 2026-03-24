import json
from typing import Optional
from datetime import datetime

from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.models.log_entry import LogEntry, LogLevel
from app.schemas.log_schema import (
    LogEntryCreate,
    LogEntryBatch,
    LogQueryParams,
    PaginatedResponse,
    LogEntryResponse,
)


def create_log_entry(db: Session, log_data: LogEntryCreate, owner_id: int) -> LogEntry:
    """Create a single log entry."""
    entry = LogEntry(
        level=log_data.level,
        message=log_data.message,
        source=log_data.source,
        service_name=log_data.service_name,
        environment=log_data.environment,
        trace_id=log_data.trace_id,
        metadata_json=json.dumps(log_data.metadata) if log_data.metadata else None,
        owner_id=owner_id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def create_log_entries_batch(db: Session, batch: LogEntryBatch, owner_id: int) -> int:
    """Create multiple log entries in a single transaction.

    Returns the number of entries created.
    """
    entries = [
        LogEntry(
            level=log_data.level,
            message=log_data.message,
            source=log_data.source,
            service_name=log_data.service_name,
            environment=log_data.environment,
            trace_id=log_data.trace_id,
            metadata_json=json.dumps(log_data.metadata) if log_data.metadata else None,
            owner_id=owner_id,
        )
        for log_data in batch.entries
    ]

    db.add_all(entries)
    db.commit()
    return len(entries)


def query_log_entries(
    db: Session,
    owner_id: int,
    params: LogQueryParams,
) -> PaginatedResponse:
    """Query log entries with filtering, search, and pagination."""
    query = db.query(LogEntry).filter(LogEntry.owner_id == owner_id)

    # Apply filters
    if params.level:
        query = query.filter(LogEntry.level == params.level)
    if params.service_name:
        query = query.filter(LogEntry.service_name == params.service_name)
    if params.source:
        query = query.filter(LogEntry.source.ilike(f"%{params.source}%"))
    if params.environment:
        query = query.filter(LogEntry.environment == params.environment)
    if params.trace_id:
        query = query.filter(LogEntry.trace_id == params.trace_id)
    if params.start_date:
        query = query.filter(LogEntry.timestamp >= params.start_date)
    if params.end_date:
        query = query.filter(LogEntry.timestamp <= params.end_date)
    if params.search:
        query = query.filter(LogEntry.message.ilike(f"%{params.search}%"))

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (params.page - 1) * params.page_size
    entries = (
        query.order_by(desc(LogEntry.timestamp))
        .offset(offset)
        .limit(params.page_size)
        .all()
    )

    total_pages = (total + params.page_size - 1) // params.page_size

    return PaginatedResponse(
        items=[LogEntryResponse.model_validate(e) for e in entries],
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
    )


def get_log_entry_by_id(
    db: Session, entry_id: int, owner_id: int
) -> Optional[LogEntry]:
    """Retrieve a specific log entry by ID."""
    return (
        db.query(LogEntry)
        .filter(LogEntry.id == entry_id, LogEntry.owner_id == owner_id)
        .first()
    )


def delete_log_entry(db: Session, entry_id: int, owner_id: int) -> bool:
    """Delete a log entry. Returns True if deleted, False if not found."""
    entry = get_log_entry_by_id(db, entry_id, owner_id)
    if not entry:
        return False
    db.delete(entry)
    db.commit()
    return True
