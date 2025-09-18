#!/usr/bin/env python3
"""
Database initialization script.
This creates the database tables directly using SQLAlchemy.
"""
from db_config import engine
from models import Base

def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
