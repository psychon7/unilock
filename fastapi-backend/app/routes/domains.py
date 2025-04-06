from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import aiofiles

from app.models.domain import Domain
from app.schemas.domain import DomainCreate, DomainResponse, DomainListResponse
from app.schemas.client import Client, ClientListResponse
from app.schemas.identity_provider import (
    IdentityProvider,
    IdentityProviderUpdate,
    IdentityProviderListResponse,
)
from app.schemas.theme import (
    ThemeConfig,
    ThemeConfigResponse,
    ThemeConfigUpdate,
    LogoUploadResponse,
)
from app.services.keycloak_service import KeycloakService
from app.core.dependencies import get_db, get_keycloak_service # Use dependencies module

router = APIRouter(
    prefix="/api/v1/domains",
    tags=["Domain Management"],
    responses={
        401: {"description": "Unauthorized - Requires authentication"},
        403: {"description": "Forbidden - Requires admin privileges"},
        404: {"description": "Not Found - Domain doesn't exist"}
    }
)

"""Domain Management API

Provides CRUD operations for managing Keycloak realms through a simplified interface.
Each domain corresponds to a Keycloak realm with additional metadata.
"""

@router.post(
    "/", 
    response_model=DomainResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new domain",
    response_description="The created domain details"
)
async def create_domain(
    domain: DomainCreate,
    db: Session = Depends(get_db),
    keycloak: KeycloakService = Depends(KeycloakService)
) -> DomainResponse:
    """Create a new domain (Keycloak realm) with metadata.
    
    Creates both:
    - A Keycloak realm
    - A domain record in local database
    
    Args:
        domain: Domain creation parameters
        
    Returns:
        DomainResponse: Created domain with metadata
        
    Raises:
        HTTPException 400: If domain name already exists
        HTTPException 500: If Keycloak realm creation fails
        
    Example:
        POST /api/v1/domains
        {
            "name": "example-domain",
            "display_name": "Example Domain",
            "description": "Example description",
            "default_client_redirect": "https://example.com"
        }
    """
    # Check if domain name already exists in our database
    existing_domain = db.query(Domain).filter(Domain.name == domain.name).first()
    if existing_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Domain with name {domain.name} already exists"
        )

    # Create the realm in Keycloak
    try:
        await keycloak.create_realm(domain.name, domain.display_name)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Keycloak realm: {str(e)}"
        )

    # Create the domain in our database
    db_domain = Domain(
        name=domain.name,
        display_name=domain.display_name,
        description=domain.description,
        default_client_redirect=domain.default_client_redirect
    )
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)

    return db_domain

@router.get(
    "/",
    response_model=List[DomainResponse],
    summary="List all domains",
    response_description="Paginated list of domains"
)
def list_domains(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[DomainResponse]:
    """Retrieve a paginated list of domains.
    
    Args:
        skip: Number of items to skip (pagination offset)
        limit: Maximum number of items to return (pagination limit)

    Returns:
        List of domain objects with metadata

    Example:
        GET /api/v1/domains?skip=0&limit=10
    """
    domains = db.query(Domain).offset(skip).limit(limit).all()
    return domains

@router.get(
    "/{domain_name}",
    response_model=DomainResponse,
    summary="Get domain details",
    response_description="Domain details including Keycloak realm info"
)
async def get_domain(
    domain_name: str,
    db: Session = Depends(get_db),
    keycloak: KeycloakService = Depends(KeycloakService)
) -> DomainResponse:
    """Retrieve comprehensive details for a specific domain.

    Combines:
    - Local domain metadata from database
    - Keycloak realm information (when available)

    Args:
        domain_name: Unique name of the domain to retrieve

    Returns:
        Combined domain metadata and Keycloak realm details

    Raises:
        HTTPException 404: If domain doesn't exist
        
    Example:
        GET /api/v1/domains/example-domain
    """
    domain = db.query(Domain).filter(Domain.name == domain_name).first()
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain {domain_name} not found"
        )

    # Get additional info from Keycloak
    try:
        realm_info = await keycloak.get_realm_info(domain_name)
        return {
            **domain.__dict__,
            "keycloak_info": realm_info
        }
    except HTTPException:
        # If we can't get Keycloak info, just return the basic domain info
        return domain


@router.get(
    "/{domain_name}/clients",
    response_model=ClientListResponse, # Use the new schema
    summary="List clients (applications) for a domain",
    response_description="List of clients configured in the specified domain"
)
async def list_domain_clients(
    domain_name: str,
    keycloak: KeycloakService = Depends(get_keycloak_service) # Use dependency injection
) -> ClientListResponse:
    """Retrieve all clients (applications) associated with a specific domain (realm).

    Args:
        domain_name: The name of the domain (realm) to query.

    Returns:
        A list of client details.

    Raises:
        HTTPException 400: If Keycloak encounters an error listing clients.
        HTTPException 404: If the domain itself is not found (implicitly handled by KeycloakService).
        
    Example:
        GET /api/v1/domains/example-domain/clients
    """
    try:
        # The KeycloakService already handles potential 404s if the realm doesn't exist
        keycloak_clients = await keycloak.list_clients(realm=domain_name)
        
        # Map the raw Keycloak client data to our Pydantic schema
        # Note: Keycloak client data structure might need inspection to ensure fields match Client schema
        # We need to handle potential missing fields gracefully
        clients_response = []
        for client_data in keycloak_clients:
             # Map fields carefully, providing defaults or handling missing keys
             client_dict = {
                 "id": client_data.get("id"),
                 "clientId": client_data.get("clientId"),
                 "name": client_data.get("name"),
                 "description": client_data.get("description"),
                 "enabled": client_data.get("enabled", True),
                 "publicClient": client_data.get("publicClient", True),
                 "redirectUris": client_data.get("redirectUris", []),
                 "rootUrl": client_data.get("rootUrl"),
                 "baseUrl": client_data.get("baseUrl"),
                 "adminUrl": client_data.get("adminUrl"),
             }
             # Filter out None values if the Pydantic model doesn't expect them for required fields
             # (id and clientId are required by our schema)
             if client_dict["id"] and client_dict["clientId"]:
                 clients_response.append(Client(**client_dict))
             else:
                 # Log or handle clients missing essential IDs if necessary
                 pass 
                 
        return ClientListResponse(clients=clients_response)
    except HTTPException as e:
        # Re-raise HTTPExceptions from the service layer
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while listing clients: {str(e)}"
        )


@router.get(
    "/{domain_name}/identity-providers",
    response_model=IdentityProviderListResponse,
    summary="List identity providers for a domain",
    response_description="List of identity providers configured in the specified domain"
)
async def list_domain_identity_providers(
    domain_name: str,
    keycloak: KeycloakService = Depends(get_keycloak_service)
) -> IdentityProviderListResponse:
    """Retrieve all identity providers associated with a specific domain (realm).

    Args:
        domain_name: The name of the domain (realm) to query.

    Returns:
        A list of identity provider details.

    Raises:
        HTTPException 400: If Keycloak encounters an error listing providers.
        HTTPException 404: If the domain itself is not found.
        
    Example:
        GET /api/v1/domains/example-domain/identity-providers
    """
    try:
        idps = await keycloak.list_identity_providers(realm=domain_name)
        return IdentityProviderListResponse(providers=[IdentityProvider(**idp) for idp in idps])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while listing identity providers: {str(e)}"
        )


@router.get(
    "/{domain_name}/identity-providers/{provider_alias}",
    response_model=IdentityProvider,
    summary="Get identity provider details",
    response_description="Detailed configuration for the specified identity provider"
)
async def get_domain_identity_provider(
    domain_name: str,
    provider_alias: str,
    keycloak: KeycloakService = Depends(get_keycloak_service)
) -> IdentityProvider:
    """Get detailed information about a specific identity provider.

    Args:
        domain_name: The name of the domain (realm).
        provider_alias: The alias/ID of the identity provider.

    Returns:
        Detailed identity provider configuration.

    Raises:
        HTTPException 404: If the domain or provider is not found.
        
    Example:
        GET /api/v1/domains/example-domain/identity-providers/google
    """
    try:
        idp = await keycloak.get_identity_provider(realm=domain_name, alias=provider_alias)
        return IdentityProvider(**idp)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching identity provider: {str(e)}"
        )


@router.patch(
    "/{domain_name}/identity-providers/{provider_alias}/state",
    response_model=dict,
    summary="Update identity provider state",
    response_description="Result of the state update operation"
)
async def update_domain_identity_provider_state(
    domain_name: str,
    provider_alias: str,
    state: IdentityProviderUpdate,
    keycloak: KeycloakService = Depends(get_keycloak_service)
) -> dict:
    """Enable or disable an identity provider.

    Args:
        domain_name: The name of the domain (realm).
        provider_alias: The alias/ID of the identity provider.
        state: The new state (enabled/disabled).

    Returns:
        Status of the update operation.

    Raises:
        HTTPException 404: If the domain or provider is not found.
        HTTPException 400: If the update operation fails.
        
    Example:
        PATCH /api/v1/domains/example-domain/identity-providers/google/state
        {
            "enabled": true
        }
    """
    try:
        result = await keycloak.update_identity_provider_state(
            realm=domain_name,
            alias=provider_alias,
            enabled=state.enabled
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while updating identity provider state: {str(e)}"
        )


@router.get(
    "/{domain_name}/theme",
    response_model=ThemeConfigResponse,
    summary="Get theme configuration",
    response_description="Current theme configuration for the domain"
)
async def get_domain_theme(
    domain_name: str,
    keycloak: KeycloakService = Depends(get_keycloak_service)
) -> ThemeConfigResponse:
    """Get the current theme configuration for a domain.

    Args:
        domain_name: The name of the domain (realm).

    Returns:
        Current theme configuration including colors and logo URL.

    Raises:
        HTTPException 404: If the domain is not found.
        
    Example:
        GET /api/v1/domains/example-domain/theme
    """
    try:
        theme_config = await keycloak.get_theme(realm=domain_name)
        return ThemeConfigResponse(**theme_config)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while fetching theme configuration: {str(e)}"
        )


@router.put(
    "/{domain_name}/theme",
    response_model=ThemeConfigResponse,
    summary="Update theme configuration",
    response_description="Updated theme configuration"
)
async def update_domain_theme(
    domain_name: str,
    theme_config: ThemeConfigUpdate,
    keycloak: KeycloakService = Depends(get_keycloak_service)
) -> ThemeConfigResponse:
    """Update the theme configuration for a domain.

    Args:
        domain_name: The name of the domain (realm).
        theme_config: New theme configuration.

    Returns:
        Updated theme configuration.

    Raises:
        HTTPException 404: If the domain is not found.
        HTTPException 400: If the theme update fails.
        
    Example:
        PUT /api/v1/domains/example-domain/theme
        {
            "primaryColor": "#3b82f6",
            "secondaryColor": "#6b7280"
        }
    """
    try:
        updated_config = await keycloak.update_theme(
            realm=domain_name,
            theme_config=theme_config.model_dump(exclude_unset=True)
        )
        return ThemeConfigResponse(**updated_config)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while updating theme configuration: {str(e)}"
        )


@router.post(
    "/{domain_name}/theme/logo",
    response_model=LogoUploadResponse,
    summary="Upload domain logo",
    response_description="URL of the uploaded logo"
)
async def upload_domain_logo(
    domain_name: str,
    logo: UploadFile = File(...),
    keycloak: KeycloakService = Depends(get_keycloak_service)
) -> LogoUploadResponse:
    """Upload a logo for a domain.

    Args:
        domain_name: The name of the domain (realm).
        logo: The logo file to upload (image file).

    Returns:
        URL of the uploaded logo.

    Raises:
        HTTPException 404: If the domain is not found.
        HTTPException 400: If the logo upload fails.
        
    Example:
        POST /api/v1/domains/example-domain/theme/logo
        Content-Type: multipart/form-data
        
        logo: [binary file data]
    """
    try:
        # Read the file content
        content = await logo.read()
        
        # Upload the logo and get its URL
        logo_url = await keycloak.upload_logo(
            realm=domain_name,
            logo_file=content,
            filename=logo.filename
        )
        
        return LogoUploadResponse(url=logo_url)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred while uploading logo: {str(e)}"
        )
