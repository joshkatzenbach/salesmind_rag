"""
Transcript-related API endpoints.
"""

import traceback
import json
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db_config import get_db
from models import Transcript
from services.chunking_service import ChunkingService
from services.file_processor import FileProcessor
from api.schemas import DocumentMetadata, ToggleActiveRequest
from api.auth_dependencies import (
    get_current_user, 
    require_admin_access, 
    require_query_permission
)
from models.user import User

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.get("/metadata")
def get_transcript_metadata(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_access)
):
    """
    Get metadata for all transcripts.
    
    Returns:
        List of transcript metadata (excluding transcript_text)
    """
    try:
        # Query only the metadata fields, excluding transcript_text
        transcripts = db.query(
            Transcript.id,
            Transcript.created_at,
            Transcript.updated_at,
            Transcript.trainer_name,
            Transcript.media_type,
            Transcript.source_url,
            Transcript.provide_link_to_searcher,
            Transcript.title,
            Transcript.active
        ).all()
        
        # Convert to list of dictionaries
        metadata = []
        for transcript in transcripts:
            metadata.append({
                "id": transcript.id,
                "created_at": transcript.created_at.isoformat() if transcript.created_at else None,
                "updated_at": transcript.updated_at.isoformat() if transcript.updated_at else None,
                "trainer_name": transcript.trainer_name,
                "media_type": transcript.media_type,
                "source_url": transcript.source_url,
                "provide_link_to_searcher": transcript.provide_link_to_searcher,
                "title": transcript.title,
                "active": transcript.active
            })
        
        return {
            "transcripts": metadata,
            "count": len(metadata),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching transcript metadata: {str(e)}"
        )


@router.patch("/{transcript_id}/active")
def toggle_transcript_active(
    transcript_id: int, 
    request: ToggleActiveRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_access)
):
    """
    Toggle the active status of a transcript.
    
    Args:
        transcript_id: ID of the transcript to update
        request: ToggleActiveRequest containing the new active status
        db: Database session
        
    Returns:
        Updated transcript metadata
    """
    try:
        # Find the transcript
        transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
        
        if not transcript:
            raise HTTPException(
                status_code=404,
                detail=f"Transcript with ID {transcript_id} not found"
            )
        
        # Update the active status
        transcript.active = request.active
        db.commit()
        db.refresh(transcript)
        
        return {
            "id": transcript.id,
            "active": transcript.active,
            "title": transcript.title,
            "trainer_name": transcript.trainer_name,
            "message": f"Transcript {'activated' if request.active else 'deactivated'} successfully",
            "status": "success"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating transcript status: {str(e)}"
        )


@router.delete("/{transcript_id}")
def delete_transcript(
    transcript_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_access)
):
    """
    Delete a transcript and all its associated chunks.
    
    Args:
        transcript_id: ID of the transcript to delete
        db: Database session
        
    Returns:
        Success message with deleted transcript info
    """
    try:
        # Find the transcript
        transcript = db.query(Transcript).filter(Transcript.id == transcript_id).first()
        
        if not transcript:
            raise HTTPException(
                status_code=404,
                detail=f"Transcript with ID {transcript_id} not found"
            )
        
        # Store transcript info before deletion for response
        transcript_info = {
            "id": transcript.id,
            "title": transcript.title,
            "trainer_name": transcript.trainer_name,
            "media_type": transcript.media_type,
            "created_at": transcript.created_at.isoformat() if transcript.created_at else None
        }
        
        # Count chunks before deletion
        chunk_count = len(transcript.chunks)
        
        # Delete the transcript (chunks will be automatically deleted due to cascade)
        db.delete(transcript)
        db.commit()
        
        return {
            "message": f"Transcript and {chunk_count} associated chunks deleted successfully",
            "deleted_transcript": transcript_info,
            "chunks_deleted": chunk_count,
            "status": "success"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 404)
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting transcript: {str(e)}"
        )


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    metadata: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_access)
):
    """
    Upload a document with metadata and store in database.
    Supports PDF, DOC, DOCX, and TXT files.
    
    Args:
        file: The uploaded file (PDF, DOC, DOCX, or TXT)
        metadata: JSON string containing DocumentMetadata
        db: Database session
        
    Returns:
        Upload confirmation with transcript details
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

        ChunkingService.run_chunk_pipeline(transcript, db)
        
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
        print(e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
