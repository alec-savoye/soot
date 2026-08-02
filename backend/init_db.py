#!/usr/bin/env python
"""
Database initialization script for the heat map application.
Creates database tables and directories.
"""
import os
import sys
from sqlalchemy import create_engine, text

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.schema import Base

# Set the database path
DB_DIR = "/app/backend/data"
DB_PATH = os.path.join(DB_DIR, "heat_map.db")

# Create data directory if it doesn't exist
os.makedirs(DB_DIR, exist_ok=True)

# Create database engine
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

print(f"Creating data directory: {DB_DIR}")
print(f"Database path: {DB_PATH}")

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
