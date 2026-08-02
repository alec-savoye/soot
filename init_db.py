#!/usr/bin/env python
"""
Database initialization script for the heat map application.
Creates database tables and directories.
"""
import os
import sys
from sqlalchemy import create_engine, text

# Set the database path
DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "heat_map.db")

# Create data directory if it doesn't exist
os.makedirs(DB_DIR, exist_ok=True)

# Create database engine
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

# Import and create tables
from database.schema import Base

print(f"Creating data directory: {DB_DIR}")
print(f"Database path: {DB_PATH}")

# Create all tables
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")

if __name__ == "__main__":
    init_database()
