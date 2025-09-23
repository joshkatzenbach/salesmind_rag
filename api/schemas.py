"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models.user import AccessLevel


class DocumentMetadata(BaseModel):
    sourceUrl: Optional[str] = None
    trainerName: Optional[str] = None
    mediaType: Optional[str] = None
    provideLinkToSearcher: bool = False


class QueryRequest(BaseModel):
    question: str


class ToggleActiveRequest(BaseModel):
    active: bool


# Authentication schemas
class UserRegister(BaseModel):
    first_name: str
    last_name: str
    password: str
    access_level: Optional[AccessLevel] = AccessLevel.USER
    query_permission: Optional[bool] = False


class UserLogin(BaseModel):
    first_name: str
    last_name: str
    password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    access_level: AccessLevel
    query_permission: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    message: str
    user: UserResponse
    session_expires_at: datetime


class LogoutResponse(BaseModel):
    message: str
