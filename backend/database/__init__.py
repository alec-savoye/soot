from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Use bind mount path for persistent data
DB_DIR = "/app/backend/data"
DB_PATH = os.path.join(DB_DIR, "heat_map.db")

# Create data directory if it doesn't exist
os.makedirs(DB_DIR, exist_ok=True)

# Create database engine
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def init_db():
    """Initialize database tables"""
    from . import schema
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {DB_PATH}")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Export schema models
from .schema import Submission
