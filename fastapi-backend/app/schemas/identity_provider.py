from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

class IdentityProviderBase(BaseModel):
    alias: str = Field(..., description="Unique identifier for the identity provider")
    displayName: Optional[str] = Field(None, description="Display name for the identity provider")
    providerId: str = Field(..., description="Type of provider (e.g., 'google', 'github', 'saml')")
    enabled: bool = Field(True, description="Whether the identity provider is enabled")
    config: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific configuration")

class IdentityProvider(IdentityProviderBase):
    internalId: Optional[str] = Field(None, description="Internal Keycloak ID")
    addReadTokenRoleOnCreate: bool = Field(False, description="Add default role to new users")
    trustEmail: bool = Field(False, description="Trust email from provider")
    storeToken: bool = Field(False, description="Store provider tokens")
    firstBrokerLoginFlowAlias: str = Field("first broker login", description="Authentication flow for first login")

    class Config:
        orm_mode = True

class IdentityProviderCreate(IdentityProviderBase):
    """Schema for creating a new identity provider"""
    pass

class IdentityProviderUpdate(BaseModel):
    """Schema for updating an identity provider's state"""
    enabled: bool = Field(..., description="New enabled state for the provider")

class IdentityProviderResponse(IdentityProvider):
    """Schema for identity provider responses"""
    pass

class IdentityProviderListResponse(BaseModel):
    """Schema for list of identity providers"""
    providers: list[IdentityProviderResponse]
