from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.log_entry import LogLevel


class LogEntryCreate(BaseModel):
    """Schema for creating a new log entry."""
    level: LogLevel
    message: str = Field(..., min_length=1, max_length=10000)
    source: str = Field(..., min_length=1, max_length=200, examples=["app.auth.login"])
    service_name: str = Field(..., min_length=1, max_length=100, examples=["user-service"])
    environment: str = Field(default="production", max_length=50)
    trace_id: Optional[str] = Field(None, max_length=64)
    metadata: Optional[Dict[str, Any]] = None


class LogEntryBatch(BaseModel):
    """Schema for batch log ingestion."""
    entries: List[LogEntryCreate] = Field(..., min_length=1, max_length=100)


class LogEntryResponse(BaseModel):
    """Schema for log entry response."""
    id: int
    level: LogLevel
    message: str
    source: str
    service_name: str
    environment: str
    trace_id: Optional[str]
    metadata_json: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class LogQueryParams(BaseModel):
    """Query parameters for filtering log entries."""
    level: Optional[LogLevel] = None
    service_name: Optional[str] = None
    source: Optional[str] = None
    environment: Optional[str] = None
    trace_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""
    items: List[LogEntryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
