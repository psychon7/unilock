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
    theme_config = Column(JSONB, nullable=True, default={
        "primaryColor": "#3b82f6",
        "secondaryColor": "#6b7280",
        "logoUrl": None,
        "loginTheme": None
    })  # Stores theme preferences as JSON
    default_client_redirect = Column(String(500), nullable=True)  # Default redirect URI

    def __repr__(self):
        return f"<Domain {self.name} ({self.display_name})>"

    @property
    def theme(self):
        """Get theme configuration with defaults"""
        default_theme = {
            "primaryColor": "#3b82f6",
            "secondaryColor": "#6b7280",
            "logoUrl": None,
            "loginTheme": None
        }
        if not self.theme_config:
            return default_theme
        return {**default_theme, **self.theme_config}
