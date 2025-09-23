"""
Authentication API endpoints.
"""

import traceback
from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from config.db_config import get_db
from models.user import User, AccessLevel
from services.auth_service import AuthService
from api.schemas import (
    UserRegister, 
    UserLogin, 
    UserResponse, 
    LoginResponse, 
    LogoutResponse
)
from api.auth_dependencies import (
    get_current_user, 
    set_session_cookie, 
    clear_session_cookie
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.options("/{path:path}")
def options_handler(path: str):
    """Handle preflight OPTIONS requests for CORS."""
    return {"message": "OK"}


@router.post("/register", response_model=UserResponse)
def register_user(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If user already exists or validation fails
    """
    try:
        # Create new user
        user = AuthService.create_user(
            db=db,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            password=user_data.password,
            access_level=AccessLevel.USER,  # Default to USER
            query_permission=False  # Default to False
        )
        
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
        
    except ValueError as e:
        print(f"ValueError in register_user: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error in register_user: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")


@router.post("/login", response_model=LoginResponse)
def login_user(
    login_data: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and create session.
    
    Args:
        login_data: User login credentials
        response: FastAPI response object for setting cookies
        db: Database session
        
    Returns:
        Login response with user info and session details
        
    Raises:
        HTTPException: If authentication fails
    """
    try:
        # Authenticate user
        user = AuthService.authenticate_user(
            db=db,
            email=login_data.email,
            password=login_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        # Login user and get session info
        session_key, session_expires_at = AuthService.login_user(db, user)
        
        # Set secure HTTP-only cookie
        set_session_cookie(response, session_key)
        
        return LoginResponse(
            message="Login successful",
            user=UserResponse(
                id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                full_name=user.full_name,
                access_level=user.access_level,
                query_permission=user.query_permission,
                created_at=user.created_at,
                last_login=user.last_login
            ),
            session_expires_at=session_expires_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in login_user: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")


@router.post("/logout", response_model=LogoutResponse)
def logout_user(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Log out current user and clear session.
    
    Args:
        response: FastAPI response object for clearing cookies
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Logout confirmation message
    """
    try:
        # Clear user session in database
        AuthService.logout_user(db, current_user)
        
        # Clear session cookie
        clear_session_cookie(response)
        
        return LogoutResponse(message="Logout successful")
        
    except Exception as e:
        print(f"Unexpected error in logout_user: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error during logout: {str(e)}")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user information
    """
    return UserResponse(
        id=current_user.id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        full_name=current_user.full_name,
        access_level=current_user.access_level,
        query_permission=current_user.query_permission,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )
