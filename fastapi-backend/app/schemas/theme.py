from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

class ThemeConfig(BaseModel):
    """Theme configuration for a domain/realm"""
    primaryColor: str = Field(
        ...,
        description="Primary color in hex format (e.g., #3b82f6)",
        pattern="^#[0-9a-fA-F]{6}$"
    )
    secondaryColor: str = Field(
        ...,
        description="Secondary color in hex format (e.g., #6b7280)",
        pattern="^#[0-9a-fA-F]{6}$"
    )
    logoUrl: Optional[HttpUrl] = Field(
        None,
        description="URL to the logo image"
    )
    loginTheme: Optional[str] = Field(
        None,
        description="Name of the Keycloak login theme to use"
    )

class ThemeConfigResponse(ThemeConfig):
    """Response model for theme configuration"""
    pass

class ThemeConfigUpdate(ThemeConfig):
    """Update model for theme configuration"""
    pass

class LogoUploadResponse(BaseModel):
    """Response model for logo upload"""
    url: HttpUrl = Field(..., description="URL of the uploaded logo")
