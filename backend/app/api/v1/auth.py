"""
Authentication endpoints for Sentrix API
"""

from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    User, UserCreate, UserUpdate, LoginRequest, LoginResponse,
    RefreshRequest, RefreshResponse, PasswordChangeRequest, Token
)
from app.services.user_service import UserService
from app.utils.auth import (
    AuthService, get_current_user, get_current_active_user, get_admin_user,
    create_user_tokens, ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.database.models.models import UserProfile

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
    """
    from sqlalchemy import text
    from datetime import datetime

    try:
        # Query user directly with raw SQL to avoid enum issues
        result = db.execute(text("""
            SELECT id, email, hashed_password, display_name, organization, is_active, is_verified, role, created_at, updated_at, last_login
            FROM user_profiles
            WHERE email = :email AND is_active = true
        """), {"email": login_data.email})

        user_row = result.fetchone()

        if not user_row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id, email, hashed_password, display_name, organization, is_active, is_verified, role, created_at, updated_at, last_login = user_row

        # Verify password
        if not AuthService.verify_password(login_data.password, hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create tokens manually
        access_token = AuthService.create_access_token(
            data={"sub": str(user_id), "email": email, "role": role}
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": str(user_id)}
        )

        # Update last login
        now = datetime.utcnow()
        db.execute(text("""
            UPDATE user_profiles
            SET last_login = :now, updated_at = :now
            WHERE id = :user_id
        """), {"now": now, "user_id": user_id})
        db.commit()

        # Create user response
        user_response = User(
            id=user_id,
            email=email,
            display_name=display_name,
            organization=organization,
            role=role,
            is_active=is_active,
            is_verified=is_verified,
            created_at=created_at,
            updated_at=now,
            last_login=now
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

    Validates refresh token and returns a new access token.
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

    # Generate new access token
    access_token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    }
    access_token = AuthService.create_access_token(access_token_data)

    return RefreshResponse(
        access_token=access_token,
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


@router.get("/users", response_model=List[User])
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
    return [
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