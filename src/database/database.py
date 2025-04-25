"""
Database connection and session management for the Property Investment Analysis App
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment variables, fallback to SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./investment_analysis.db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Import models to ensure they're registered with the Base metadata
from .models import Base, User, Property, RentalUnit, Financing, Expense, Analysis, MarketData, AgentTask

# Create all tables in the database
def create_tables():
    Base.metadata.create_all(bind=engine)

# Initialize database with default data
def init_db():
    db = SessionLocal()
    try:
        # Check if there are any users
        user_count = db.query(User).count()
        if user_count == 0:
            # Create a default admin user
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
                first_name="Admin",
                last_name="User"
            )
            db.add(admin_user)
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()

# Initialize database if running this file directly
if __name__ == "__main__":
    create_tables()
    init_db()
    print("Database initialized successfully.")