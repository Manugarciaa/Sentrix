"""
Authentication endpoints for Sentrix API
"""

from datetime import timedelta
from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

from ...database.connection import get_db
from ...schemas.auth import (
    User, UserCreate, UserUpdate, LoginRequest, LoginResponse,
    RefreshRequest, RefreshResponse, PasswordChangeRequest, Token
)
from ...services.user_service import UserService
from ...utils.auth import (
    AuthService, get_current_user, get_current_active_user, get_admin_user,
    create_user_tokens, ACCESS_TOKEN_EXPIRE_MINUTES
)
from ...database.models.models import UserProfile

router = APIRouter()


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account

    Creates a new user account with the provided email and password.
    Returns access and refresh tokens for immediate login.
    """
    # Check if user already exists
    existing_user = UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Create new user
    new_user = UserService.create_user(db, user_data)

    # Generate tokens
    access_token, refresh_token = create_user_tokens(new_user)

    # Update last login
    UserService.update_last_login(db, new_user.id)

    # Convert to User schema
    user_response = User(
        id=new_user.id,
        email=new_user.email,
        display_name=new_user.display_name,
        organization=new_user.organization,
        role=new_user.role,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        last_login=new_user.last_login
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access tokens

    Validates user credentials and returns access and refresh tokens.

    SECURITY: Usa ORM en lugar de raw SQL para prevenir SQL injection
    """
    from datetime import datetime, timezone

    try:
        # SEGURIDAD: Usar ORM en lugar de raw SQL
        user = db.query(UserProfile).filter(
            UserProfile.email == login_data.email,
            UserProfile.is_active == True
        ).first()

        # Usar mensaje genérico para evitar user enumeration
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not AuthService.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create tokens
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "email": user.email, "role": user.role}
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": str(user.id)}
        )

        # Update last login usando ORM
        user.last_login = datetime.now(timezone.utc)
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

        # Create user response
        user_response = User(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            organization=user.organization,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Login error for {login_data.email}: {e}")
        # SEGURIDAD: No exponer detalles internos en producción
        import os
        if os.getenv("ENVIRONMENT") == "production":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error interno del servidor: {str(e)}"
            )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    Validates refresh token and returns a new access token and refresh token.
    """
    # Verify refresh token
    token_data = AuthService.verify_token(refresh_data.refresh_token, "refresh")
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    user = UserService.get_user_by_id(db, token_data.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new access token and refresh token
    access_token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }
    access_token = AuthService.create_access_token(access_token_data)
    new_refresh_token = AuthService.create_refresh_token({"sub": str(user.id)})

    return RefreshResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: UserProfile = Depends(get_current_active_user)
):
    """
    Get current user profile

    Returns the profile information of the currently authenticated user.
    """
    return User(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        organization=current_user.organization,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        last_login=current_user.last_login
    )


@router.put("/me", response_model=User)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile

    Updates the profile information of the currently authenticated user.
    """
    updated_user = UserService.update_user(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return User(
        id=updated_user.id,
        email=updated_user.email,
        display_name=updated_user.display_name,
        organization=updated_user.organization,
        role=updated_user.role,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at,
        last_login=updated_user.last_login
    )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChangeRequest,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password

    Changes the password for the currently authenticated user.
    """
    success = UserService.change_password(
        db,
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )

    return {"message": "Password changed successfully"}


@router.get("/users")
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserProfile = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get list of users (Admin only)

    Returns a paginated list of all users. Requires admin privileges.
    """
    users = UserService.get_users(db, skip=skip, limit=limit)
    user_list = [
        User(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            organization=user.organization,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        for user in users
    ]

    # Return in format expected by frontend
    return {
        "users": user_list,
        "total": len(user_list)
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: UserProfile = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user (Admin only)

    Deletes a user from the system. Requires admin privileges.
    Cannot delete yourself.
    """
    from uuid import UUID

    # Prevent self-deletion
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Get user to verify exists
    user = UserService.get_user_by_id(db, UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Delete user
    try:
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )


@router.post("/logout")
async def logout(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Logout user

    Invalidates the current session. In a real implementation,
    you might want to blacklist the token.
    """
    return {"message": "Successfully logged out"}


@router.get("/users/me/stats")
async def get_user_stats(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's statistics

    Returns statistics about the user's activity including
    total analyses, detections, validations, and reports.

    SECURITY: Usa ORM en lugar de raw SQL
    """
    from ...database.models.models import Analysis, Detection
    from sqlalchemy import func
    import os

    try:
        # SEGURIDAD: Usar ORM en lugar de raw SQL
        # Get user's analysis count
        analyses_count = db.query(func.count(Analysis.id)).filter(
            Analysis.user_id == current_user.id
        ).scalar() or 0

        # Get total detections from user's analyses
        detections_sum = db.query(func.coalesce(func.sum(Analysis.total_detections), 0)).filter(
            Analysis.user_id == current_user.id
        ).scalar() or 0

        # Get validated detections count (if user is expert/admin)
        validated_count = 0
        if current_user.role in ["admin", "expert"]:
            validated_count = db.query(func.count(Detection.id)).filter(
                Detection.validated_by == current_user.id
            ).scalar() or 0

        # For now, reports are not implemented, so return 0
        reports_count = 0

        return {
            "total_analyses": int(analyses_count),
            "total_detections": int(detections_sum),
            "validated_detections": int(validated_count),
            "created_reports": int(reports_count)
        }

    except Exception as e:
        logger.exception(f"Error retrieving stats for user {current_user.id}: {e}")
        # SEGURIDAD: No exponer detalles en producción
        if os.getenv("ENVIRONMENT") == "production":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user statistics"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving user statistics: {str(e)}"
            )


@router.get("/users/me/activities")
async def get_user_activities(
    limit: int = 10,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's recent activities

    Returns a list of recent activities including analyses created,
    detections validated, and other user actions.
    """
    from sqlalchemy import text
    from datetime import datetime, timedelta, timezone

    try:
        activities = []

        # Get recent analyses
        recent_analyses = db.execute(text("""
            SELECT id, image_filename, risk_level, total_detections, created_at
            FROM analyses
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
        """), {"user_id": current_user.id, "limit": limit}).fetchall()

        for analysis in recent_analyses:
            activities.append({
                "id": str(analysis[0]),
                "type": "analysis",
                "description": f"Análisis procesado: {analysis[1] or 'imagen'}",
                "risk": analysis[2] or "BAJO",
                "timestamp": analysis[4].isoformat() if analysis[4] else datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "detections_count": analysis[3] or 0
                }
            })

        # Get recent validations (if user is expert/admin)
        if current_user.role in ["admin", "expert"]:
            recent_validations = db.execute(text("""
                SELECT d.id, d.class_name, d.risk_level, d.validated_at
                FROM detections d
                WHERE d.validated_by = :user_id AND d.validated_at IS NOT NULL
                ORDER BY d.validated_at DESC
                LIMIT :limit
            """), {"user_id": current_user.id, "limit": limit // 2}).fetchall()

            for validation in recent_validations:
                activities.append({
                    "id": str(validation[0]),
                    "type": "validation",
                    "description": f"Detección validada: {validation[1] or 'desconocido'}",
                    "risk": validation[2] or "MEDIO",
                    "timestamp": validation[3].isoformat() if validation[3] else datetime.now(timezone.utc).isoformat(),
                })

        # Sort by timestamp and limit
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        activities = activities[:limit]

        return {
            "activities": activities,
            "total": len(activities)
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user activities: {str(e)}"
        )


@router.get("/users/me/settings")
async def get_user_settings(
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's settings

    Returns the user's application settings and preferences.
    """
    from ..database.models.models import UserSettings
    from ..schemas.settings import DEFAULT_USER_SETTINGS

    try:
        # Get or create user settings
        user_settings = db.query(UserSettings).filter(
            UserSettings.user_id == current_user.id
        ).first()

        if user_settings:
            # Merge with defaults to ensure all fields exist
            settings_data = {**DEFAULT_USER_SETTINGS, **user_settings.settings}
            return settings_data
        else:
            # Create default settings for new user
            new_settings = UserSettings(
                user_id=current_user.id,
                settings=DEFAULT_USER_SETTINGS
            )
            db.add(new_settings)
            db.commit()
            return DEFAULT_USER_SETTINGS

    except Exception as e:
        logger.error(f"Error retrieving user settings: {e}")
        # Fallback to defaults on error
        return DEFAULT_USER_SETTINGS


@router.put("/users/me/settings")
async def update_user_settings(
    settings_update: dict,
    current_user: UserProfile = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's settings

    Updates the user's application settings and preferences.
    """
    from ..database.models.models import UserSettings
    from ..schemas.settings import UserSettingsUpdate, DEFAULT_USER_SETTINGS

    try:
        # Validate settings update (optional fields)
        # Merge with existing settings
        user_settings = db.query(UserSettings).filter(
            UserSettings.user_id == current_user.id
        ).first()

        if user_settings:
            # Update existing settings (merge with current)
            current_settings = user_settings.settings or {}
            updated_settings = {**current_settings, **settings_update}
            user_settings.settings = updated_settings
        else:
            # Create new settings record
            updated_settings = {**DEFAULT_USER_SETTINGS, **settings_update}
            user_settings = UserSettings(
                user_id=current_user.id,
                settings=updated_settings
            )
            db.add(user_settings)

        db.commit()
        db.refresh(user_settings)

        return {
            "message": "Settings updated successfully",
            "settings": user_settings.settings
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating settings: {str(e)}"
        )