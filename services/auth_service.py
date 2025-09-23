"""
Authentication service for user management, password hashing, and session management.
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from models.user import User, AccessLevel
from passlib.context import CryptContext

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Session key length and expiration
SESSION_KEY_LENGTH = 32
SESSION_EXPIRATION_HOURS = 24


class AuthService:
    """Service for handling user authentication and authorization."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt with salt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_session_key() -> str:
        """
        Generate a cryptographically secure random session key.
        
        Returns:
            Random session key string
        """
        return secrets.token_urlsafe(SESSION_KEY_LENGTH)
    
    @staticmethod
    def is_session_expired(session_created_at: datetime) -> bool:
        """
        Check if a session has expired.
        
        Args:
            session_created_at: When the session was created
            
        Returns:
            True if session is expired, False otherwise
        """
        if not session_created_at:
            return True
        
        expiration_time = session_created_at + timedelta(hours=SESSION_EXPIRATION_HOURS)
        return datetime.utcnow() > expiration_time
    
    @staticmethod
    def create_user(
        db: Session,
        first_name: str,
        last_name: str,
        password: str,
        access_level: AccessLevel = AccessLevel.USER,
        query_permission: bool = False
    ) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            db: Database session
            first_name: User's first name
            last_name: User's last name
            password: Plain text password
            access_level: User's access level
            query_permission: Whether user can query documents
            
        Returns:
            Created User object
        """
        # Check if user already exists
        existing_user = db.query(User).filter(
            User.first_name == first_name,
            User.last_name == last_name
        ).first()
        
        if existing_user:
            raise ValueError("User with this name already exists")
        
        # Hash the password
        password_hash = AuthService.hash_password(password)
        
        # Create new user
        user = User(
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            access_level=access_level,
            query_permission=query_permission
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def authenticate_user(
        db: Session,
        first_name: str,
        last_name: str,
        password: str
    ) -> Optional[User]:
        """
        Authenticate a user by name and password.
        
        Args:
            db: Database session
            first_name: User's first name
            last_name: User's last name
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = db.query(User).filter(
            User.first_name == first_name,
            User.last_name == last_name
        ).first()
        
        if not user:
            return None
        
        if not AuthService.verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def login_user(db: Session, user: User) -> Tuple[str, datetime]:
        """
        Log in a user and generate/update session key.
        
        Args:
            db: Database session
            user: User object to log in
            
        Returns:
            Tuple of (session_key, session_expires_at)
        """
        # Check if existing session is still valid
        if (user.session_key and 
            user.updated_at and 
            not AuthService.is_session_expired(user.updated_at)):
            # Use existing session key
            session_key = user.session_key
            session_expires_at = user.updated_at + timedelta(hours=SESSION_EXPIRATION_HOURS)
        else:
            # Generate new session key
            session_key = AuthService.generate_session_key()
            session_expires_at = datetime.utcnow() + timedelta(hours=SESSION_EXPIRATION_HOURS)
        
        # Update user with new session info
        user.session_key = session_key
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return session_key, session_expires_at
    
    @staticmethod
    def logout_user(db: Session, user: User) -> None:
        """
        Log out a user by clearing their session key.
        
        Args:
            db: Database session
            user: User object to log out
        """
        user.session_key = None
        user.updated_at = datetime.utcnow()
        db.commit()
    
    @staticmethod
    def get_user_by_session(db: Session, session_key: str) -> Optional[User]:
        """
        Get user by session key and check if session is valid.
        
        Args:
            db: Database session
            session_key: Session key from cookie
            
        Returns:
            User object if session is valid, None otherwise
        """
        if not session_key:
            return None
        
        user = db.query(User).filter(User.session_key == session_key).first()
        
        if not user:
            return None
        
        # Check if session is expired
        if AuthService.is_session_expired(user.updated_at):
            # Clear expired session
            user.session_key = None
            user.updated_at = datetime.utcnow()
            db.commit()
            return None
        
        return user
    
    @staticmethod
    def require_access_level(user: User, required_level: AccessLevel) -> bool:
        """
        Check if user has required access level.
        
        Args:
            user: User object
            required_level: Required access level
            
        Returns:
            True if user has required access level, False otherwise
        """
        level_hierarchy = {
            AccessLevel.USER: 1,
            AccessLevel.ADMIN: 2,
            AccessLevel.SUPER_ADMIN: 3
        }
        
        user_level = level_hierarchy.get(user.access_level, 0)
        required_level_value = level_hierarchy.get(required_level, 0)
        
        return user_level >= required_level_value
