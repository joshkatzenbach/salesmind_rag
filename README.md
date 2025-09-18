# SalesMind RAG API

A FastAPI-based document processing API for handling sales call transcripts and documents.

## Features

- **File Upload & Processing**: Supports PDF, DOC, DOCX, and TXT files
- **Text Extraction**: Automatically extracts text content from uploaded documents
- **Database Storage**: Stores processed documents in PostgreSQL with metadata
- **CORS Support**: Configured to accept requests from any origin
- **RESTful API**: Clean API endpoints with automatic documentation

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

### Health Check
```
GET /health
```

### Root
```
GET /
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your PostgreSQL credentials
   ```

3. **Initialize database:**
   ```bash
   # Option 1: Using Alembic (recommended)
   alembic upgrade head
   
   # Option 2: Direct initialization
   python init_db.py
   ```

4. **Start the server:**
   ```bash
   python run.py
   # or
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
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

## Development

- **API Documentation**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Database Migrations**: Use `alembic revision --autogenerate -m "description"` to create new migrations
