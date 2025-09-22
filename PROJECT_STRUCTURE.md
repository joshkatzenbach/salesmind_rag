# Project Structure Overview

This document provides a quick overview of the organized folder structure for the SalesMind RAG API.

## 📁 Directory Organization

### Root Level
- `main.py` - FastAPI application entry point
- `requirements.txt` - Python dependencies
- `alembic.ini` - Alembic database migration configuration
- `init_db.py` - Direct database initialization utility

### 📂 Core Directories

#### `models/` - Database Models
- `__init__.py` - Package initialization and exports
- `base.py` - SQLAlchemy declarative base
- `transcript.py` - Transcript ORM model
- `chunk.py` - Chunk ORM model for embeddings

#### `services/` - Business Logic
- `__init__.py` - Package initialization
- `chunking_service.py` - Text chunking and embedding generation
- `file_processor.py` - File processing utilities (PDF, DOC, DOCX, TXT)
- `query_service.py` - Query processing and AI response generation

#### `config/` - Configuration Files
- `__init__.py` - Package initialization
- `db_config.py` - Database connection configuration
- `env.local` - Local development environment variables
- `env.production` - Production environment variables (Supabase)
- `env.example` - Environment variables template

#### `scripts/` - Utility Scripts
- `__init__.py` - Package initialization
- `migrate_local.py` - Run migrations on local database
- `migrate_production.py` - Run migrations on production database
- `migrate_both.py` - Run migrations on both databases
- `run_local.py` - Start server in local development mode
- `run_production.py` - Start server in production mode

#### `docs/` - Documentation
- `README.md` - Complete project documentation

#### `alembic/` - Database Migrations
- `env.py` - Alembic environment configuration
- `versions/` - Migration files directory

## 🚀 Quick Commands

### Development
```bash
# Start local development server
python scripts/run_local.py

# Run local migrations
python scripts/migrate_local.py
```

### Production
```bash
# Start production server
python scripts/run_production.py

# Run production migrations
python scripts/migrate_production.py
```

### Both Environments
```bash
# Migrate both databases
python scripts/migrate_both.py
```

## 🔧 Import Structure

The project uses relative imports within packages and absolute imports from the root:

```python
# In main.py
from services.query_service import QueryService
from services.chunking_service import ChunkingService
from config.db_config import get_db
from models import Transcript

# In services/query_service.py
from .chunking_service import ChunkingService
from models.chunk import Chunk
```

## 📋 Benefits of This Structure

1. **Separation of Concerns** - Each directory has a specific purpose
2. **Scalability** - Easy to add new services, models, or scripts
3. **Maintainability** - Clear organization makes code easier to find and modify
4. **Environment Management** - Separate configs for different environments
5. **Documentation** - Centralized docs with clear project overview
