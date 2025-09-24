"""
Prompt history API endpoints.
"""

import traceback
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from config.db_config import get_db
from models.user import User, AccessLevel
from models.query import Query as QueryModel
from api.auth_dependencies import require_access_level
from api.schemas import UserResponse

router = APIRouter(prefix="/prompt-history", tags=["prompt history"])


@router.options("/{path:path}")
def options_handler(path: str):
    """Handle preflight OPTIONS requests for CORS."""
    return {"message": "OK"}


@router.get("/")
def get_prompt_history(
    user_id: int = Query(None, description="Filter by user ID"),
    days: int = Query(30, description="Number of days to look back (default: 30)"),
    limit: int = Query(100, description="Maximum number of results (default: 100)"),
    current_user: User = Depends(require_access_level(AccessLevel.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get prompt history with filtering options (admin and super admin only).
    
    Args:
        user_id: Optional user ID to filter by
        days: Number of days to look back (default: 30)
        limit: Maximum number of results (default: 100)
        current_user: Current authenticated user (must be admin or super admin)
        db: Database session
        
    Returns:
        List of queries with user information
    """
    try:
        # Calculate the date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)
        
        # Build the query
        query = db.query(QueryModel).join(User).filter(
            QueryModel.created_at >= date_threshold
        )
        
        # Filter by user if specified
        if user_id is not None:
            query = query.filter(QueryModel.user_id == user_id)
        
        # Order by most recent first and limit results
        queries = query.order_by(desc(QueryModel.created_at)).limit(limit).all()
        
        # Format the response
        result = []
        for query_record in queries:
            result.append({
                "id": query_record.id,
                "user_id": query_record.user_id,
                "user_name": query_record.user.full_name,
                "user_email": query_record.user.email,
                "query": query_record.query,
                "created_at": query_record.created_at.isoformat()
            })
        
        return {
            "queries": result,
            "total": len(result),
            "filters": {
                "user_id": user_id,
                "days": days,
                "limit": limit
            }
        }
        
    except Exception as e:
        print(f"Error getting prompt history: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving prompt history: {str(e)}")


@router.get("/users")
def get_users_for_filtering(
    current_user: User = Depends(require_access_level(AccessLevel.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get list of users for filtering prompt history (admin and super admin only).
    
    Args:
        current_user: Current authenticated user (must be admin or super admin)
        db: Database session
        
    Returns:
        List of users who have made queries
    """
    try:
        # Get users who have made queries, ordered by name
        users = db.query(User).join(QueryModel).distinct().order_by(User.first_name, User.last_name).all()
        
        result = []
        for user in users:
            result.append({
                "id": user.id,
                "name": user.full_name,
                "email": user.email,
                "access_level": user.access_level.value
            })
        
        return {"users": result}
        
    except Exception as e:
        print(f"Error getting users for filtering: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")


@router.get("/stats")
def get_prompt_history_stats(
    days: int = Query(30, description="Number of days to look back (default: 30)"),
    current_user: User = Depends(require_access_level(AccessLevel.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get prompt history statistics (admin and super admin only).
    
    Args:
        days: Number of days to look back (default: 30)
        current_user: Current authenticated user (must be admin or super admin)
        db: Database session
        
    Returns:
        Statistics about prompt history
    """
    try:
        # Calculate the date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)
        
        # Get total queries in the time period
        total_queries = db.query(QueryModel).filter(QueryModel.created_at >= date_threshold).count()
        
        # Get unique users who made queries
        unique_users = db.query(QueryModel.user_id).filter(
            QueryModel.created_at >= date_threshold
        ).distinct().count()
        
        # Get queries per day (last 7 days)
        daily_stats = []
        for i in range(7):
            day_start = datetime.utcnow() - timedelta(days=i+1)
            day_end = datetime.utcnow() - timedelta(days=i)
            day_queries = db.query(QueryModel).filter(
                and_(QueryModel.created_at >= day_start, QueryModel.created_at < day_end)
            ).count()
            daily_stats.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "queries": day_queries
            })
        
        return {
            "total_queries": total_queries,
            "unique_users": unique_users,
            "period_days": days,
            "daily_stats": daily_stats
        }
        
    except Exception as e:
        print(f"Error getting prompt history stats: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving statistics: {str(e)}")
