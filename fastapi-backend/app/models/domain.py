from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

class Domain(Base):
    """Represents a domain/realm in our system with user-friendly metadata"""
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)  # Keycloak realm name
    display_name = Column(String(255))  # User-friendly display name
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    theme_config = Column(JSONB, nullable=True)  # Stores theme preferences as JSON
    default_client_redirect = Column(String(500), nullable=True)  # Default redirect URI

    def __repr__(self):
        return f"<Domain {self.name} ({self.display_name})>"
