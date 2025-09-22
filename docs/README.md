# SalesMind RAG API

A FastAPI-based document processing API for handling sales call transcripts and documents with intelligent chunking and embedding generation.

## Features

- **File Upload & Processing**: Supports PDF, DOC, DOCX, and TXT files
- **Text Extraction**: Automatically extracts text content from uploaded documents
- **Intelligent Chunking**: Splits documents into optimal chunks using configurable parameters
- **Embedding Generation**: Creates vector embeddings using OpenAI's text-embedding-3-small model
- **Vector Storage**: Stores chunks and embeddings in PostgreSQL with pgvector support
- **Database Storage**: Stores processed documents in PostgreSQL with metadata
- **CORS Support**: Configured to accept requests from any origin
- **RESTful API**: Clean API endpoints with automatic documentation
- **Multi-Environment Support**: Separate configurations for local and production databases

## Supported File Types

- **TXT**: Plain text files (UTF-8, Latin-1, CP1252, ISO-8859-1)
- **PDF**: PDF documents using PyPDF2
- **DOCX**: Microsoft Word documents using python-docx
- **DOC**: Legacy Microsoft Word documents (basic support)

## API Endpoints

### Upload Document
```
POST /upload
```

**Request:**
- `file`: Uploaded file (PDF, DOC, DOCX, or TXT)
- `metadata`: JSON string containing:
  ```json
  {
    "sourceUrl": "string (optional)",
    "trainerName": "string (optional)", 
    "mediaType": "string (optional)",
    "provideLinkToSearcher": "boolean"
  }
  ```

**Response:**
```json
{
  "message": "File uploaded and processed successfully",
  "transcript_id": 1,
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "file_size": 12345,
  "extracted_text_length": 5678,
  "metadata": { ... }
}
```

### Query Documents
```
POST /query
```

**Request:**
```json
{
  "question": "your search question here"
}
```

**Response:**
```json
{
  "question": "your search question here",
  "answer": "AI-generated answer based on your documents",
  "status": "success"
}
```

### Get Transcript Metadata
```
GET /transcripts/metadata
```

**Response:**
```json
{
  "transcripts": [
    {
      "id": 1,
      "created_at": "2025-09-19T17:34:07.338248",
      "updated_at": "2025-09-19T17:34:07.338248",
      "trainer_name": "John Doe",
      "media_type": "video",
      "source_url": "https://example.com/video",
      "provide_link_to_searcher": true,
      "title": "Sales Call - Q3 Review",
      "active": true
    }
  ],
  "count": 1,
  "status": "success"
}
```

### Toggle Transcript Active Status
```
PATCH /transcripts/{transcript_id}/active
```

**Request:**
```json
{
  "active": true
}
```

**Response:**
```json
{
  "id": 1,
  "active": true,
  "title": "Sales Call - Q3 Review",
  "trainer_name": "John Doe",
  "message": "Transcript activated successfully",
  "status": "success"
}
```

### Health Check
```
GET /health
```

### Root
```
GET /
```

## Environment Configuration

The application supports separate configurations for local development and production:

### Environment Files
- **`config/env.local`** - Local development database (PostgreSQL)
- **`config/env.production`** - Production database (Render)
- **`config/env.local.template`** - Template for local environment
- **`config/env.production.template`** - Template for production environment

### Setup Environment Files

1. **Configure local environment:**
   ```bash
   # Edit config/env.local
   nano config/env.local
   ```
   ```env
   # Local Development Environment
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=salesmind_rag_local
   DB_USER=postgres
   DB_PASSWORD=your_local_password
   OPENAI_API_KEY=your_openai_api_key
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   MAX_BATCH_SIZE=7000
   ```

2. **Configure production environment:**
   ```bash
   # Edit config/env.production
   nano config/env.production
   ```
   ```env
   # Production Environment (Supabase)
   DB_HOST=aws-1-us-west-1.pooler.supabase.com
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres.aevnayrfokvawccrmhno
   DB_PASSWORD=your_supabase_password
   OPENAI_API_KEY=your_openai_api_key
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   MAX_BATCH_SIZE=7000
   ```

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up local database:**
   ```bash
   # Create local PostgreSQL database
   createdb salesmind_rag_local
   
   # Run migrations on local database
   python scripts/migrate_local.py
   ```

3. **Set up production database:**
   ```bash
   # Run migrations on production database (Supabase)
   python scripts/migrate_production.py
   ```

4. **Run migrations on both databases:**
   ```bash
   # Migrate both local and production at once
   python scripts/migrate_both.py
   ```

## Running the Server

### Local Development
```bash
# Run server with local database
python scripts/run_local.py
```
- Server: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Uses `config/env.local` configuration

### Production Mode
```bash
# Run server with production database (Supabase)
python scripts/run_production.py
```
- Server: http://0.0.0.0:8000
- Uses `config/env.production` configuration

### Manual Server Start
```bash
# Set environment and run manually
ENVIRONMENT=local python main.py
ENVIRONMENT=production python main.py
```

## Database Migrations

### Individual Database Migrations
```bash
# Migrate local database only
python scripts/migrate_local.py

# Migrate production database only
python scripts/migrate_production.py
```

### Migrate Both Databases
```bash
# Migrate both local and production databases
python scripts/migrate_both.py
```

### Manual Migration Commands
```bash
# Local database
ENVIRONMENT=local alembic upgrade head

# Production database
ENVIRONMENT=production alembic upgrade head
```

### Create New Migrations
```bash
# Create a new migration (run from project root)
alembic revision --autogenerate -m "Description of changes"
```

## File Processing

The API automatically:
- Validates file types before processing
- Extracts text content using appropriate libraries
- Handles encoding issues for text files
- Stores both original metadata and extracted text
- Provides detailed error messages for unsupported files

## Database Schema

The `transcripts` table includes:
- `id`: Primary key
- `transcript_text`: Extracted text content
- `created_at`: Timestamp
- `updated_at`: Timestamp
- `trainer_name`: Optional trainer/salesperson name
- `media_type`: Optional media type (video, document, etc.)
- `source_url`: Optional source URL
- `provide_link_to_searcher`: Boolean flag

## Deployment

### Render Deployment

1. **Set Environment Variables in Render:**
   ```
   ENVIRONMENT=production
   DB_HOST=aws-1-us-west-1.pooler.supabase.com
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres.aevnayrfokvawccrmhno
   DB_PASSWORD=your_supabase_password
   OPENAI_API_KEY=your_openai_api_key
   CHUNK_SIZE=1000
   CHUNK_OVERLAP=200
   MAX_BATCH_SIZE=7000
   ```

2. **Deploy:**
   - Connect your GitHub repository to Render
   - Render will automatically build and deploy
   - The app will use the production environment variables

### Other Platforms

For other deployment platforms, ensure you set the `ENVIRONMENT=production` variable and provide all required environment variables.

## Development

- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Database Migrations**: Use `alembic revision --autogenerate -m "description"` to create new migrations

## Project Structure

```
salesmind_rag/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── alembic.ini            # Alembic configuration
├── init_db.py             # Direct database initialization
├── models/                # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── base.py           # Declarative base
│   ├── transcript.py     # Transcript model
│   └── chunk.py          # Chunk model
├── services/              # Business logic services
│   ├── __init__.py
│   ├── chunking_service.py    # Text chunking and embedding
│   ├── file_processor.py      # File processing utilities
│   └── query_service.py       # Query processing logic
├── config/                # Configuration files
│   ├── __init__.py
│   ├── db_config.py      # Database configuration
│   ├── env.local         # Local environment variables
│   ├── env.production    # Production environment variables
│   └── env.example       # Environment template
├── scripts/               # Utility scripts
│   ├── __init__.py
│   ├── migrate_local.py      # Local database migrations
│   ├── migrate_production.py # Production database migrations
│   ├── migrate_both.py       # Migrate both databases
│   ├── run_local.py          # Run local server
│   └── run_production.py     # Run production server
├── docs/                  # Documentation
│   └── README.md         # This file
└── alembic/              # Database migrations
    ├── env.py
    └── versions/         # Migration files
```

## Quick Reference

### Server Commands
```bash
python scripts/run_local.py      # Local development
python scripts/run_production.py # Production mode
```

### Migration Commands
```bash
python scripts/migrate_local.py     # Local database only
python scripts/migrate_production.py # Production database only
python scripts/migrate_both.py      # Both databases
```

### Environment Files
- `config/env.local` - Local development settings
- `config/env.production` - Production settings (Supabase)
