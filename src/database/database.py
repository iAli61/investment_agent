"""
Database connection and session management for the application
"""
import os
import logging
from typing import Generator, Optional
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from .models import Base

logger = logging.getLogger(__name__)

# Get database URL from environment or use default
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "sqlite:///./investment_analysis.db"
)

# Azure SQL Database connection string format if needed
# "mssql+pyodbc://username:password@server.database.windows.net:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    echo=False
)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get DB session
    
    Yields:
        Session: SQLAlchemy session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Initialize the database, creating tables if they don't exist
    """
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

def get_engine():
    """
    Get the SQLAlchemy engine
    
    Returns:
        Engine: SQLAlchemy engine instance
    """
    return engine

def create_test_db() -> None:
    """
    Create a test database for unit testing
    """
    # Create test database in memory
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=test_engine)
    return test_engine

def migrate_db() -> None:
    """
    Migrate database schema (placeholder for Alembic integration)
    """
    # This will be implemented with Alembic for schema migrations
    # For now, just ensures tables exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema updated")