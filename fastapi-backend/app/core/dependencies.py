from fastapi import Depends, HTTPException, status
from app.services.security_service import SecurityService, TokenData
from typing import List, Optional

security_service = SecurityService()

"""Role-Based Access Control (RBAC) dependencies for FastAPI routes.

Provides decorators and dependency functions to:
- Validate JWT tokens
- Enforce scope requirements
- Simplify common role checks
"""

async def get_current_user(token: str = Depends(security_service.verify_token)):
    return token

async def has_required_scopes(required_scopes: Optional[List[str]] = None):
    """Dependency factory for checking required scopes.
    
    Args:
        required_scopes: List of scopes to check against token
        
    Returns:
        Dependency function that enforces scope requirements
        
    Raises:
        HTTPException 403: If any required scope is missing
        
    Example:
        @app.get("/protected")
        async def protected_route(user = Depends(has_required_scopes(["admin"]))):
            # Only accessible with admin scope
    """
    async def dependency(current_user: TokenData = Depends(get_current_user)):
        if required_scopes:
            for scope in required_scopes:
                if scope not in current_user.scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not enough permissions"
                    )
        return current_user
    return dependency

# Common role dependencies
async def admin_required(current_user: TokenData = Depends(has_required_scopes(["admin"]))) -> TokenData:
    """Convenience dependency that enforces admin privileges.
    
    Returns:
        TokenData for authenticated admin users
        
    Raises:
        HTTPException 403: For non-admin users
        
    Usage:
        @app.get("/admin-only")
        async def admin_route(user: TokenData = Depends(admin_required)):
            # Admin-only functionality
    """
    return current_user

async def user_required(current_user: TokenData = Depends(has_required_scopes(["user"]))) -> TokenData:
    """Convenience dependency that enforces basic user privileges.
    
    Returns:
        TokenData for authenticated users
        
    Raises:
        HTTPException 403: For unauthenticated requests
        
    Usage:
        @app.get("/user-area")
        async def user_route(user: TokenData = Depends(user_required)):
            # User-only functionality
    """
    return current_user
