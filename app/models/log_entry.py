from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class LogLevel(str, enum.Enum):
    """Severity levels for log entries."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(Base):
    """Model representing a single log entry from an application."""

    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Enum(LogLevel), nullable=False, index=True)
    message = Column(Text, nullable=False)
    source = Column(String(200), nullable=False, index=True)
    service_name = Column(String(100), nullable=False, index=True)
    environment = Column(String(50), default="production")
    trace_id = Column(String(64), nullable=True, index=True)
    metadata_json = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="log_entries")

    # Composite indexes for common query patterns
    __table_args__ = (
        Index("ix_log_entries_service_level", "service_name", "level"),
        Index("ix_log_entries_owner_timestamp", "owner_id", "timestamp"),
    )

    def __repr__(self):
        return f"<LogEntry(id={self.id}, level='{self.level}', source='{self.source}')>"
