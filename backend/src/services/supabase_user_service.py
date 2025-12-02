"""
Supabase User Service - Auth and user management using Supabase
Servicio de usuarios con Supabase - Autenticación y gestión con Supabase
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status

from ..schemas.auth import UserCreate, UserUpdate
from ..utils.supabase_client import get_supabase_client
from ..database.models.models import UserProfile
from ..logging_config import get_logger

logger = get_logger(__name__)


class SupabaseUserService:
    """Service for managing users with Supabase Auth + Database"""

    def __init__(self):
        self.supabase = get_supabase_client()

    def create_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Create a new user using Supabase Auth and create profile in user_profiles table

        Returns:
            Dict with user data and tokens
        """
        try:
            # 1. Create user in Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "display_name": user_data.display_name,
                        "organization": user_data.organization
                    }
                }
            })

            if not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user in Supabase Auth"
                )

            user_id = auth_response.user.id
            logger.info("user_created_in_auth", user_id=user_id, email=user_data.email)

            # 2. Create user profile in user_profiles table
            profile_data = {
                "id": str(user_id),
                "email": user_data.email,
                "display_name": user_data.display_name,
                "organization": user_data.organization,
                "role": "user",
                "is_active": True,
                "is_verified": False
            }

            profile_result = self.supabase.table('user_profiles').insert(profile_data).execute()

            if not profile_result.data:
                logger.error("failed_to_create_profile", user_id=user_id)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user profile"
                )

            logger.info("user_profile_created", user_id=user_id)

            return {
                "user": auth_response.user,
                "session": auth_response.session,
                "profile": profile_result.data[0]
            }

        except Exception as e:
            logger.error("user_creation_failed", error=str(e), email=user_data.email)
            if "already registered" in str(e).lower() or "already exists" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )

    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with Supabase Auth

        Returns:
            Dict with user data and tokens
        """
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not auth_response.user or not auth_response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password"
                )

            # Get user profile from database
            profile_result = self.supabase.table('user_profiles').select('*').eq('id', str(auth_response.user.id)).execute()

            if not profile_result.data:
                logger.error("profile_not_found", user_id=str(auth_response.user.id))
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )

            profile = profile_result.data[0]

            # Check if user is active
            if not profile.get('is_active', True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is deactivated"
                )

            # Update last login
            self.supabase.table('user_profiles').update({
                "last_login": datetime.now(timezone.utc).isoformat()
            }).eq('id', str(auth_response.user.id)).execute()

            logger.info("user_authenticated", user_id=str(auth_response.user.id), email=email)

            return {
                "user": auth_response.user,
                "session": auth_response.session,
                "profile": profile,
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("authentication_failed", error=str(e), email=email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

    def get_user_from_token(self, access_token: str) -> Dict[str, Any]:
        """
        Get user from access token

        Args:
            access_token: Supabase access token

        Returns:
            Dict with user data
        """
        try:
            # Verify token with Supabase
            user_response = self.supabase.auth.get_user(access_token)

            if not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token"
                )

            # Get user profile
            profile_result = self.supabase.table('user_profiles').select('*').eq('id', str(user_response.user.id)).execute()

            if not profile_result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )

            profile = profile_result.data[0]

            # Check if user is active
            if not profile.get('is_active', True):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is deactivated"
                )

            return {
                "user": user_response.user,
                "profile": profile
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("token_verification_failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh user session

        Args:
            refresh_token: Supabase refresh token

        Returns:
            Dict with new tokens
        """
        try:
            session_response = self.supabase.auth.refresh_session(refresh_token)

            if not session_response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token"
                )

            return {
                "session": session_response.session,
                "access_token": session_response.session.access_token,
                "refresh_token": session_response.session.refresh_token
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("token_refresh_failed", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

    def update_user_profile(self, user_id: str, user_data: UserUpdate) -> Dict[str, Any]:
        """Update user profile information"""
        try:
            update_data = user_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

            result = self.supabase.table('user_profiles').update(update_data).eq('id', user_id).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            return result.data[0]

        except HTTPException:
            raise
        except Exception as e:
            logger.error("profile_update_failed", error=str(e), user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update profile: {str(e)}"
            )

    def change_password(self, user_id: str, new_password: str) -> bool:
        """Change user password"""
        try:
            # Update password in Supabase Auth
            self.supabase.auth.admin.update_user_by_id(
                user_id,
                {"password": new_password}
            )

            # Update timestamp in profile
            self.supabase.table('user_profiles').update({
                "updated_at": datetime.now(timezone.utc).isoformat()
            }).eq('id', user_id).execute()

            logger.info("password_changed", user_id=user_id)
            return True

        except Exception as e:
            logger.error("password_change_failed", error=str(e), user_id=user_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to change password: {str(e)}"
            )


# Global instance
supabase_user_service = SupabaseUserService()
