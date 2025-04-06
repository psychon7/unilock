from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from app.core.settings import settings

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "admin": "Admin operations",
        "user": "Regular user operations"
    }
)

class SecurityService:
    """Main service handling JWT authentication and authorization.
    
    Provides methods for:
    - Creating JWT access tokens
    - Verifying tokens and checking scopes
    - Managing token expiration

    Configuration is pulled from app settings.
    """
    def __init__(self):
        self.SECRET_KEY = settings.SECRET_KEY
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = 30

    async def create_access_token(
        self, 
        data: dict, 
        expires_delta: Optional[timedelta] = None
    ):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def verify_token(
        self, 
        token: str = Depends(oauth2_scheme),
        required_scopes: Optional[list[str]] = None
    ) -> TokenData:
        """Verify and decode a JWT token, optionally checking required scopes.
        
        Args:
            token: JWT token fromAuthorization header
            required_scopes: List of scopes required for access
            
        Returns:
            TokenData containing username and scopes
            
        Raises:
            HTTPException 401: If token is invalid
            HTTPException 403: If required scopes are missing
            
        Example:
            # In route dependency
            token_data = await verify_token(token, required_scopes=["admin"])
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_scopes = payload.get("scopes", [])
            token_data = TokenData(username=username, scopes=token_scopes)
        except JWTError:
            raise credentials_exception

        if required_scopes:
            for scope in required_scopes:
                if scope not in token_data.scopes:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Not enough permissions",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
        return token_data
