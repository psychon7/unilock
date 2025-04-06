from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import PostgresDsn
from loguru import logger

# Database configuration
SQLALCHEMY_DATABASE_URL = "postgresql://identity:identity@localhost:5433/identity_db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Checks connection health before using
    pool_size=5,         # Number of connections to keep open
    max_overflow=10      # Number of connections allowed beyond pool_size
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
