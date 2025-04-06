from fastapi import APIRouter, Depends, HTTPException, status
from app.services.security_service import SecurityService
from app.core.dependencies import admin_required, user_required
from datetime import timedelta

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"}
    }
)
security_service = SecurityService()

"""Authentication API endpoints.

Provides routes for:
- Token generation (mock implementation)
- Role-based access testing
"""

@router.post("/token", response_model=dict, status_code=status.HTTP_200_OK)
async def login_for_access_token() -> dict:
    """Mock endpoint to generate an access token (for testing purposes).
    
    In production, this would validate credentials against Keycloak.
    
    Returns:
        dict: Contains access_token and token_type
        
    Example Response:
        {
            "access_token": "eyJhbGciOi...",
            "token_type": "bearer"
        }
    """
    access_token = await security_service.create_access_token(
        data={"sub": "admin@example.com", "scopes": ["admin"]},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/test-admin", dependencies=[Depends(admin_required)])
async def test_admin_access() -> dict:
    """Validate admin-only access.
    
    Requires:
        Valid JWT with admin scope
        
    Returns:
        dict: Success message if authorized
        
    Raises:
        HTTPException 403: If user lacks admin privileges
    """
    return {"message": "Admin access successful"}

@router.get("/test-user", dependencies=[Depends(user_required)])
async def test_user_access() -> dict:
    """Validate basic user access.
    
    Requires:
        Valid JWT with user scope
        
    Returns:
        dict: Success message if authorized
        
    Raises:
        HTTPException 403: If unauthorized
    """
    return {"message": "User access successful"}
