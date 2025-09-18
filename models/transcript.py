from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from .base import Base

class Transcript(Base):
    """Transcript model for storing sales call transcripts."""
    
    __tablename__ = "transcripts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Transcript content
    transcript_text = Column(Text, nullable=False)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Trainer/Salesperson information
    trainer_name = Column(String(255), nullable=True)  # maps to trainerName
    
    # Source information
    media_type = Column(String(50), nullable=True)  # maps to mediaType (video, document, etc)
    source_url = Column(String(500), nullable=True)  # maps to sourceUrl
    provide_link_to_searcher = Column(Boolean, default=False, nullable=False)  # maps to provideLinkToSearcher
    
    def __repr__(self) -> str:
        return f"<Transcript(id={self.id}, trainer_name='{self.trainer_name}', media_type='{self.media_type}', created_at='{self.created_at}')>"
