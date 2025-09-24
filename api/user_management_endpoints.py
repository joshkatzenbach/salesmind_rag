"""
User management API endpoints.
"""

import traceback
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.db_config import get_db
from models.user import User, AccessLevel
from services.auth_service import AuthService
from api.schemas import (
    UserListResponse,
    UserUpdateRequest,
    UserUpdateResponse,
    UserResponse
)
from api.auth_dependencies import (
    get_current_user,
    require_access_level
)

router = APIRouter(prefix="/users", tags=["user management"])


@router.options("/{path:path}")
def options_handler(path: str):
    """Handle preflight OPTIONS requests for CORS."""
    return {"message": "OK"}


@router.get("/", response_model=UserListResponse)
def get_all_users(
    current_user: User = Depends(require_access_level(AccessLevel.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get all users (admin and super admin only).
    
    Args:
        current_user: Current authenticated user (must be admin or super admin)
        db: Database session
        
    Returns:
        List of all users
    """
    try:
        users = db.query(User).all()
        
        user_responses = [
            UserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                full_name=user.full_name,
                access_level=user.access_level,
                query_permission=user.query_permission,
                created_at=user.created_at,
                last_login=user.last_login
            )
            for user in users
        ]
        
        return UserListResponse(
            users=user_responses,
            total=len(user_responses)
        )
        
    except Exception as e:
        print(f"Error getting users: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving users: {str(e)}")


@router.put("/{user_id}/permissions", response_model=UserUpdateResponse)
def update_user_permissions(
    user_id: int,
    update_data: UserUpdateRequest,
    current_user: User = Depends(require_access_level(AccessLevel.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Update user permissions (admin and super admin only).
    
    Args:
        user_id: ID of user to update
        update_data: Permission update data
        current_user: Current authenticated user (must be admin or super admin)
        db: Database session
        
    Returns:
        Updated user information
    """
    try:
        # Get the user to update
        user_to_update = db.query(User).filter(User.id == user_id).first()
        
        if not user_to_update:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if current user can modify this user
        # Super admins can modify anyone, admins can only modify users (not other admins/super admins)
        if current_user.access_level == AccessLevel.ADMIN:
            if user_to_update.access_level in [AccessLevel.ADMIN, AccessLevel.SUPER_ADMIN]:
                raise HTTPException(
                    status_code=403, 
                    detail="Admins can only modify user-level accounts"
                )
        
        # Update query permission (both admin and super admin can do this)
        # But admins/super admins always have query permission, so don't allow changing it
        if update_data.query_permission is not None:
            if user_to_update.is_admin():
                raise HTTPException(
                    status_code=400,
                    detail="Cannot modify query permission for admins or super admins - they always have query permission"
                )
            user_to_update.query_permission = update_data.query_permission
        
        # Update access level (only super admin can do this)
        if update_data.access_level is not None:
            if current_user.access_level != AccessLevel.SUPER_ADMIN:
                raise HTTPException(
                    status_code=403,
                    detail="Only super admins can change access levels"
                )
            
            # Prevent super admin from demoting themselves
            if user_to_update.id == current_user.id and update_data.access_level != AccessLevel.SUPER_ADMIN:
                raise HTTPException(
                    status_code=400,
                    detail="Cannot demote yourself from super admin"
                )
            
            user_to_update.access_level = update_data.access_level
        
        db.commit()
        db.refresh(user_to_update)
        
        return UserUpdateResponse(
            message="User permissions updated successfully",
            user=UserResponse(
                id=user_to_update.id,
                first_name=user_to_update.first_name,
                last_name=user_to_update.last_name,
                email=user_to_update.email,
                full_name=user_to_update.full_name,
                access_level=user_to_update.access_level,
                query_permission=user_to_update.query_permission,
                created_at=user_to_update.created_at,
                last_login=user_to_update.last_login
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating user permissions: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error updating user permissions: {str(e)}")


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(require_access_level(AccessLevel.ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (admin and super admin only).
    
    Args:
        user_id: ID of user to retrieve
        current_user: Current authenticated user (must be admin or super admin)
        db: Database session
        
    Returns:
        User information
    """
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            full_name=user.full_name,
            access_level=user.access_level,
            query_permission=user.query_permission,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting user: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")
