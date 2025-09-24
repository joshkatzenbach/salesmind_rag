"""
Query model for storing user query history.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Query(Base):
    """Query model for storing user query history."""
    
    __tablename__ = "queries"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to user who made the query
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Query information
    query = Column(String(5000), nullable=False)  # Store the actual query text
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationship to user
    user = relationship("User", back_populates="queries")
    
    def __repr__(self) -> str:
        return f"<Query(id={self.id}, user_id={self.user_id}, query='{self.query[:50]}...', created_at='{self.created_at}')>"
