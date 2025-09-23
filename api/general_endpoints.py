"""
General API endpoints (health, root, etc.).
"""

from fastapi import APIRouter

router = APIRouter(tags=["general"])


@router.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Hello World"}


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
