"""
User service for managing user operations
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.schemas.auth import UserCreate, UserUpdate
from app.utils.auth import AuthService
from src.database.models.models import UserProfile


class UserService:
    """Service for managing user operations"""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserProfile:
        """Create a new user"""
        try:
            # Hash the password
            hashed_password = AuthService.hash_password(user_data.password)

            # Create user instance
            db_user = UserProfile(
                email=user_data.email,
                hashed_password=hashed_password,
                display_name=user_data.display_name,
                organization=user_data.organization,
                is_active=True,
                is_verified=False  # Require email verification
            )

            db.add(db_user)
            db.commit()
            # Skip refresh to avoid enum issues for now
            return db_user

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists"
            )

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[UserProfile]:
        """Get user by email"""
        return db.query(UserProfile).filter(UserProfile.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[UserProfile]:
        """Get user by ID"""
        return db.query(UserProfile).filter(UserProfile.id == user_id).first()

    @staticmethod
    def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> Optional[UserProfile]:
        """Update user information"""
        user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not user:
            return None

        # Update fields
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)

        user.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_last_login(db: Session, user_id: UUID) -> None:
        """Update user's last login timestamp"""
        user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if user:
            user.last_login = datetime.utcnow()
            db.commit()

    @staticmethod
    def deactivate_user(db: Session, user_id: UUID) -> bool:
        """Deactivate a user account"""
        user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not user:
            return False

        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def activate_user(db: Session, user_id: UUID) -> bool:
        """Activate a user account"""
        user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not user:
            return False

        user.is_active = True
        user.updated_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def verify_user(db: Session, user_id: UUID) -> bool:
        """Mark user as verified"""
        user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not user:
            return False

        user.is_verified = True
        user.updated_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def change_password(db: Session, user_id: UUID, current_password: str, new_password: str) -> bool:
        """Change user password"""
        user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not user:
            return False

        # Verify current password
        if not AuthService.verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        user.hashed_password = AuthService.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[UserProfile]:
        """Get list of users (admin only)"""
        return db.query(UserProfile).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_count(db: Session) -> int:
        """Get total number of users"""
        return db.query(UserProfile).count()