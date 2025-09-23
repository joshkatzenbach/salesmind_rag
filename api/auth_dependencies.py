"""
Authentication dependencies for FastAPI endpoints.
"""

import traceback
import os
from fastapi import HTTPException, Depends, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config.db_config import get_db
from models.user import User, AccessLevel
from services.auth_service import AuthService

# Security scheme for API documentation
security = HTTPBearer(auto_error=False)

# Environment-based cookie security
def get_cookie_security_settings():
    """Get cookie security settings based on environment."""
    env = os.getenv("ENVIRONMENT", "local")
    is_production = env == "production"
    print(f"🍪 Cookie settings - Environment: {env}, Secure: {is_production}")
    return {
        "secure": is_production,  # Only secure in production (HTTPS)
        "httponly": True,
        "samesite": "lax",
        "max_age": 24 * 60 * 60  # 24 hours
    }


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from session cookie.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If user is not authenticated
    """
    # Get session key from cookies
    session_key = request.cookies.get("session_key")
    
    if not session_key:
        print("🔍 DEBUG: No session cookie found in request")
        print("🔍 DEBUG: Available cookies:", list(request.cookies.keys()))
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Cookie"}
        )
    
    print(f"🔍 DEBUG: Session cookie found: {session_key[:10]}...")
    print(f"🔍 DEBUG: Full session key: {session_key}")
    
    # Get user by session key
    user = AuthService.get_user_by_session(db, session_key)
    
    if not user:
        print(f"🔍 DEBUG: Authentication failed: Invalid or expired session for key: {session_key[:10]}...")
        traceback.print_exc()
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session. Please log in again.",
            headers={"WWW-Authenticate": "Cookie"}
        )
    
    print(f"🔍 DEBUG: User authenticated: {user.email} (access_level: {user.access_level})")
    return user


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> User | None:
    """
    Get the current authenticated user from session cookie (optional).
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Current authenticated user or None if not authenticated
    """
    session_key = request.cookies.get("session_key")
    
    if not session_key:
        return None
    
    return AuthService.get_user_by_session(db, session_key)


def require_access_level(required_level: AccessLevel):
    """
    Create a dependency that requires a specific access level.
    
    Args:
        required_level: Required access level
        
    Returns:
        Dependency function
    """
    def access_level_dependency(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if not AuthService.require_access_level(current_user, required_level):
            print(f"Access denied: User {current_user.email} (level: {current_user.access_level}) attempted to access {required_level.value} endpoint")
            traceback.print_exc()
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required access level: {required_level.value}"
            )
        return current_user
    
    return access_level_dependency


def require_admin_access(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require admin or super admin access.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if admin access
        
    Raises:
        HTTPException: If user doesn't have admin access
    """
    print(f"🔍 DEBUG: Checking admin access for user: {current_user.email} (level: {current_user.access_level})")
    if not current_user.is_admin():
        print(f"🚫 DEBUG: Access denied: User {current_user.email} (level: {current_user.access_level}) attempted to access admin endpoint")
        traceback.print_exc()
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin privileges required."
        )
    print(f"✅ DEBUG: Admin access granted for user: {current_user.email}")
    return current_user


def require_super_admin_access(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require super admin access.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if super admin access
        
    Raises:
        HTTPException: If user doesn't have super admin access
    """
    if not current_user.is_super_admin():
        print(f"Access denied: User {current_user.email} (level: {current_user.access_level}) attempted to access super admin endpoint")
        traceback.print_exc()
        raise HTTPException(
            status_code=403,
            detail="Access denied. Super admin privileges required."
        )
    return current_user


def require_query_permission(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Require query permission.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user if has query permission
        
    Raises:
        HTTPException: If user doesn't have query permission
    """
    if not current_user.query_permission:
        print(f"Access denied: User {current_user.email} (query_permission: {current_user.query_permission}) attempted to access query endpoint")
        traceback.print_exc()
        raise HTTPException(
            status_code=403,
            detail="Access denied. Query permission required."
        )
    return current_user


def set_session_cookie(response: Response, session_key: str) -> None:
    """
    Set secure HTTP-only session cookie.
    
    Args:
        response: FastAPI response object
        session_key: Session key to set
    """
    settings = get_cookie_security_settings()
    response.set_cookie(
        key="session_key",
        value=session_key,
        **settings
    )


def clear_session_cookie(response: Response) -> None:
    """
    Clear session cookie.
    
    Args:
        response: FastAPI response object
    """
    settings = get_cookie_security_settings()
    response.delete_cookie(
        key="session_key",
        **settings
    )
