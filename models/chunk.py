"""
Chunk model for storing text chunks and their embeddings.
"""

from sqlalchemy import Column, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import Base

class Chunk(Base):
    """Chunk model for storing text chunks and their embeddings."""
    
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)  
    
    # Relationship to transcript
    transcript = relationship("Transcript", back_populates="chunks")
    
    # Create index on transcript_id and chunk_index for efficient queries
    __table_args__ = (
        Index('ix_chunks_transcript_chunk', 'transcript_id', 'chunk_index'),
    )
    
    def __repr__(self) -> str:
        return f"<Chunk(id={self.id}, transcript_id={self.transcript_id}, chunk_index={self.chunk_index}, text_length={len(self.chunk_text) if self.chunk_text else 0})>"
