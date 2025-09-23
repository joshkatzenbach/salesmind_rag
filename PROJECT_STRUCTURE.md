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
- `user.py` - User ORM model for authentication

#### `services/` - Business Logic
- `__init__.py` - Package initialization
- `chunking_service.py` - Text chunking and embedding generation
- `file_processor.py` - File processing utilities (PDF, DOC, DOCX, TXT)
- `query_service.py` - Query processing and AI response generation
- `auth_service.py` - User authentication and session management

#### `api/` - API Endpoints
- `__init__.py` - Package initialization
- `schemas.py` - Pydantic models for request/response validation
- `general_endpoints.py` - General endpoints (health, root)
- `auth_endpoints.py` - Authentication endpoints (register, login, logout, me)
- `transcript_endpoints.py` - Transcript management endpoints
- `query_endpoints.py` - Query endpoints
- `auth_dependencies.py` - Authentication dependencies and middleware

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
from api import general_endpoints, auth_endpoints, transcript_endpoints, query_endpoints

# In api/auth_endpoints.py
from api.schemas import UserRegister, UserLogin, UserResponse
from api.auth_dependencies import get_current_user, set_session_cookie
from services.auth_service import AuthService

# In services/auth_service.py
from models.user import User, AccessLevel
from passlib.context import CryptContext
```

## 🔐 Authentication System

The project includes a comprehensive authentication system:

### User Management
- **Registration**: `POST /auth/register` - Create new users
- **Login**: `POST /auth/login` - Authenticate and create session
- **Logout**: `POST /auth/logout` - Clear session
- **Profile**: `GET /auth/me` - Get current user info

### Access Control
- **Role-Based**: Admin/Super Admin access for transcript management
- **Permission-Based**: Query permission required for document queries
- **Session Management**: 24-hour secure session cookies

### Security Features
- **Password Hashing**: bcrypt with salts
- **Session Keys**: Cryptographically secure random tokens
- **HTTP-Only Cookies**: Secure session storage
- **Access Levels**: USER, ADMIN, SUPER_ADMIN hierarchy

## 📋 Benefits of This Structure

1. **Separation of Concerns** - Each directory has a specific purpose
2. **Scalability** - Easy to add new services, models, or scripts
3. **Maintainability** - Clear organization makes code easier to find and modify
4. **Environment Management** - Separate configs for different environments
5. **Documentation** - Centralized docs with clear project overview
