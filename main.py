from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
from sqlalchemy.orm import Session
from db_config import get_db
from models import Transcript
from file_processor import FileProcessor

# FastAPI app
app = FastAPI(title="SalesMind RAG API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for request validation
class DocumentMetadata(BaseModel):
    sourceUrl: Optional[str] = None
    trainerName: Optional[str] = None
    mediaType: Optional[str] = None
    provideLinkToSearcher: bool = False

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    metadata: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document with metadata and store in database.
    Supports PDF, DOC, DOCX, and TXT files.
    
    Args:
        file: The uploaded file (PDF, DOC, DOCX, or TXT)
        metadata: JSON string containing DocumentMetadata
        db: Database session
    """
    try:
        # Validate file type
        if not FileProcessor.is_supported_file(file):
            supported_types = ", ".join(FileProcessor.get_supported_extensions())
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Supported types: {supported_types}"
            )
        
        # Parse metadata JSON
        metadata_dict = json.loads(metadata)
        document_metadata = DocumentMetadata(**metadata_dict)
        
        # Process file and extract text content
        transcript_text = await FileProcessor.process_file(file)
        
        # Create new transcript record
        transcript = Transcript(
            transcript_text=transcript_text,
            trainer_name=document_metadata.trainerName,
            media_type=document_metadata.mediaType,
            source_url=document_metadata.sourceUrl,
            provide_link_to_searcher=document_metadata.provideLinkToSearcher
        )
        
        # Add to database
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        
        return {
            "message": "File uploaded and processed successfully",
            "transcript_id": transcript.id,
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(transcript_text),
            "extracted_text_length": len(transcript_text),
            "metadata": document_metadata.dict()
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in metadata")
    except HTTPException:
        # Re-raise HTTP exceptions from file processor
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
