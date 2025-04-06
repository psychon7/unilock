from pydantic import BaseModel, Field
from typing import List, Optional

class ClientBase(BaseModel):
    clientId: str = Field(..., description="The client ID used for authentication flows")
    name: Optional[str] = Field(None, description="Display name for the client")
    description: Optional[str] = Field(None, description="Description of the client")
    enabled: bool = Field(True, description="Whether the client is enabled")
    publicClient: bool = Field(True, description="Whether the client is public (no secret)")
    redirectUris: List[str] = Field([], description="Allowed redirect URIs after login")
    rootUrl: Optional[str] = Field(None, description="Default root URL for the application")
    baseUrl: Optional[str] = Field(None, description="Default base URL for relative application links")
    adminUrl: Optional[str] = Field(None, description="URL for the client's administration console")

class Client(ClientBase):
    id: str = Field(..., description="Internal Keycloak ID for the client")

    class Config:
        orm_mode = True # Kept for potential future DB integration, though Keycloak is the source here

class ClientListResponse(BaseModel):
    clients: List[Client]
