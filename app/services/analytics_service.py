from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.models.log_entry import LogEntry, LogLevel


def get_log_stats(db: Session, owner_id: int, hours: int = 24) -> dict:
    """Get aggregated log statistics for the last N hours."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    # Count by level
    level_counts = (
        db.query(LogEntry.level, func.count(LogEntry.id))
        .filter(LogEntry.owner_id == owner_id, LogEntry.timestamp >= since)
        .group_by(LogEntry.level)
        .all()
    )

    level_map = {level.value: count for level, count in level_counts}
    total = sum(level_map.values())

    return {
        "period_hours": hours,
        "total_entries": total,
        "by_level": {
            "debug": level_map.get("DEBUG", 0),
            "info": level_map.get("INFO", 0),
            "warning": level_map.get("WARNING", 0),
            "error": level_map.get("ERROR", 0),
            "critical": level_map.get("CRITICAL", 0),
        },
        "error_rate": round(
            (level_map.get("ERROR", 0) + level_map.get("CRITICAL", 0)) / max(total, 1) * 100, 2
        ),
    }


def get_top_error_sources(
    db: Session, owner_id: int, limit: int = 10, hours: int = 24
) -> list:
    """Get the sources with the most errors and critical logs."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    results = (
        db.query(LogEntry.source, func.count(LogEntry.id).label("count"))
        .filter(
            LogEntry.owner_id == owner_id,
            LogEntry.timestamp >= since,
            LogEntry.level.in_([LogLevel.ERROR, LogLevel.CRITICAL]),
        )
        .group_by(LogEntry.source)
        .order_by(func.count(LogEntry.id).desc())
        .limit(limit)
        .all()
    )

    return [{"source": source, "error_count": count} for source, count in results]


def get_service_breakdown(
    db: Session, owner_id: int, hours: int = 24
) -> list:
    """Get log count breakdown by service name."""
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    results = (
        db.query(
            LogEntry.service_name,
            func.count(LogEntry.id).label("total"),
            func.sum(case((LogEntry.level == LogLevel.ERROR, 1), else_=0)).label("errors"),
            func.sum(case((LogEntry.level == LogLevel.CRITICAL, 1), else_=0)).label("critical"),
        )
        .filter(LogEntry.owner_id == owner_id, LogEntry.timestamp >= since)
        .group_by(LogEntry.service_name)
        .order_by(func.count(LogEntry.id).desc())
        .all()
    )

    return [
        {
            "service_name": name,
            "total_logs": total,
            "errors": errors or 0,
            "critical": critical or 0,
        }
        for name, total, errors, critical in results
    ]
