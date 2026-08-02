from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.schema import Base

# SQLite file-based database (bind mounted)
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
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at: {DB_PATH}")

if __name__ == "__main__":
    init_db()
