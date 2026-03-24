import secrets
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class ApiKey(Base):
    """API keys for programmatic log ingestion."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="api_keys")

    @staticmethod
    def generate_key() -> str:
        """Generate a secure random API key."""
        return f"ls_{secrets.token_hex(24)}"

    def __repr__(self):
        return f"<ApiKey(id={self.id}, name='{self.name}')>"
