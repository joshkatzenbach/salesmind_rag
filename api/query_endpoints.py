"""
Query-related API endpoints.
"""

import traceback
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db_config import get_db
from services.query_service import QueryService
from api.schemas import QueryRequest
from api.auth_dependencies import require_query_permission
from models.user import User

router = APIRouter(tags=["query"])


@router.post("/query")
def query_documents(
    request: QueryRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_query_permission)
):
    """
    Query documents using semantic search.
    
    Args:
        request: QueryRequest containing the search question
        db: Database session
        
    Returns:
        Query response with answer
    """
    try:
        answer = QueryService.process_query(request.question, db)
        return {
            "question": request.question,
            "answer": answer,
            "message": "Query endpoint ready - logic to be implemented",
            "status": "success"
        }
    except Exception as e:
        print(f"Unexpected error in query_documents: {str(e)}")
        traceback.print_exc()
        # Handle query processing errors
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )
