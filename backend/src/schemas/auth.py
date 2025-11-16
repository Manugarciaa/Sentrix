"""
Authentication schemas for Sentrix API
Esquemas de autenticación para la API Sentrix
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from sentrix_shared.data_models import UserRoleEnum


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    display_name: Optional[str] = None
    organization: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(min_length=8, description="Password must be at least 8 characters")


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    display_name: Optional[str] = None
    organization: Optional[str] = None


class UserInDB(UserBase):
    """User schema with database fields"""
    id: UUID
    role: UserRoleEnum
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    """Public user model without sensitive data"""
    pass


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: User


class RefreshRequest(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str


class RefreshResponse(BaseModel):
    """Schema for token refresh response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class PasswordChangeRequest(BaseModel):
    """Schema for password change request"""
    current_password: str
    new_password: str = Field(min_length=8)


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(min_length=8)


class Token(BaseModel):
    """Basic token schema"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data schema"""
    user_id: Optional[UUID] = None
    email: Optional[str] = None
    role: Optional[UserRoleEnum] = None