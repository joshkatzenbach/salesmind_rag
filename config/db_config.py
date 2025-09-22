import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from appropriate .env file
import os
from pathlib import Path

# Get the project root directory
project_root = Path(__file__).parent.parent
env = os.getenv("ENVIRONMENT", "local")
env_file = project_root / f"config/env.{env}"

if env_file.exists():
    load_dotenv(env_file)
else:
    # Fallback to .env in project root
    fallback_env = project_root / ".env"
    if fallback_env.exists():
        load_dotenv(fallback_env)

# Database configuration from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "salesmind_rag")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Construct database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Initialize pgvector extension
def init_pgvector():
    """Initialize pgvector extension in the database."""
    try:
        with engine.begin() as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        print("✅ pgvector extension initialized successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize pgvector extension: {e}")

# Initialize pgvector
init_pgvector()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
