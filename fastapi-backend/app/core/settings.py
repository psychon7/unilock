from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl
from typing import Optional

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: PostgresDsn = "postgresql://identity:identity@localhost:5433/identity_db"
    
    # Keycloak configuration
    KEYCLOAK_URL: AnyHttpUrl = "http://localhost:8081"
    KEYCLOAK_ADMIN_USERNAME: str = "admin"
    KEYCLOAK_ADMIN_PASSWORD: str = "admin"
    KEYCLOAK_REALM: str = "master"  # Default realm for admin operations
    
    # Security configuration
    SECRET_KEY: str = "your-secret-key-here"  # Change this to a secure random value
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application settings
    APP_ENV: str = "development"  # or "production"
    LOG_LEVEL: str = "DEBUG"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"  # Frontend URLs
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
