"""
User model for authentication and authorization.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from .base import Base
import enum


class AccessLevel(enum.Enum):
    """User access levels."""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    """User model for storing user authentication and authorization data."""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User information
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)  # Salted, hashed password
    session_key = Column(String(255), nullable=True, unique=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Authorization
    access_level = Column(Enum(AccessLevel), default=AccessLevel.USER, nullable=False)
    query_permission = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, first_name='{self.first_name}', last_name='{self.last_name}', access_level='{self.access_level}')>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.access_level in [AccessLevel.ADMIN, AccessLevel.SUPER_ADMIN]
    
    def is_super_admin(self) -> bool:
        """Check if user has super admin privileges."""
        return self.access_level == AccessLevel.SUPER_ADMIN
    
    # Relationship to queries
    queries = relationship("Query", back_populates="user")