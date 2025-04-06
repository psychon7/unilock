from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.domain import Domain
from app.schemas.domain import DomainCreate, DomainResponse
from app.services.keycloak_service import KeycloakService
from app.core.database import get_db

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
