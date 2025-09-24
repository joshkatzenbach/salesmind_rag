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
    title: Optional[str] = None


class QueryRequest(BaseModel):
    question: str


class ToggleActiveRequest(BaseModel):
    active: bool


# Authentication schemas
class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
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


# User management schemas
class UserUpdateRequest(BaseModel):
    access_level: Optional[AccessLevel] = None
    query_permission: Optional[bool] = None


class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int


class UserUpdateResponse(BaseModel):
    message: str
    user: UserResponse
