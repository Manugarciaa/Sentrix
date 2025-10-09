"""
Authentication utilities for Sentrix API
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Union
from uuid import UUID

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..schemas.auth import TokenData, User
from ..database.models.models import UserProfile


# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()


class AuthService:
    """Authentication service for handling JWT tokens and password hashing"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check token type
            if payload.get("type") != token_type:
                return None

            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")

            if user_id is None or email is None:
                return None

            token_data = TokenData(
                user_id=UUID(user_id),
                email=email,
                role=role
            )
            return token_data
        except JWTError:
            return None

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[UserProfile]:
        """Authenticate a user by email and password"""
        user = db.query(UserProfile).filter(UserProfile.email == email).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserProfile:
    """Dependency to get the current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        token_data = AuthService.verify_token(token, "access")
        if token_data is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(UserProfile).filter(UserProfile.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user


async def get_current_active_user(
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """Dependency to get the current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_admin_user(
    current_user: UserProfile = Depends(get_current_active_user)
) -> UserProfile:
    """Dependency to get the current user if they are an admin"""
    if current_user.role not in ["ADMIN", "EXPERT"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def create_user_tokens(user: UserProfile) -> tuple[str, str]:
    """Create access and refresh tokens for a user"""
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }

    access_token = AuthService.create_access_token(token_data)
    refresh_token = AuthService.create_refresh_token(token_data)

    return access_token, refresh_token