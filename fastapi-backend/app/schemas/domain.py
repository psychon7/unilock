from pydantic import BaseModel, Field
from typing import Optional

class DomainBase(BaseModel):
    """Base schema for domain operations"""
    name: str = Field(..., min_length=3, max_length=255, regex=r'^[a-z0-9-]+$',
                    description="Keycloak realm name (lowercase, numbers, hyphens only)")
    display_name: str = Field(..., min_length=3, max_length=255,
                            description="User-friendly display name")

class DomainCreate(DomainBase):
    """Schema for creating a new domain"""
    description: Optional[str] = Field(None, max_length=500)
    default_client_redirect: Optional[str] = Field(None, max_length=500)

class DomainResponse(DomainBase):
    """Schema for returning domain information"""
    id: int
    description: Optional[str]
    is_active: bool
    default_client_redirect: Optional[str]

    class Config:
        orm_mode = True
