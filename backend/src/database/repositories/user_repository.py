"""
User Repository

Provides database operations for UserProfile model.
"""

from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .base import BaseRepository, NotFoundError
from ..models.models import UserProfile


class UserRepository(BaseRepository[UserProfile]):
    """Repository for UserProfile operations"""

    def __init__(self, db: Session):
        super().__init__(UserProfile, db)

    # ============================================
    # Custom Query Methods
    # ============================================

    def get_by_email(self, email: str) -> Optional[UserProfile]:
        """
        Get user by email address.

        Args:
            email: User's email address

        Returns:
            UserProfile instance or None if not found
        """
        return self.get_by_field("email", email)

    def get_by_email_or_404(self, email: str) -> UserProfile:
        """
        Get user by email or raise NotFoundError.

        Args:
            email: User's email address

        Returns:
            UserProfile instance

        Raises:
            NotFoundError: If user not found
        """
        user = self.get_by_email(email)
        if user is None:
            raise NotFoundError(f"User with email {email} not found")
        return user

    def get_active_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserProfile]:
        """
        Get all active users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active UserProfile instances
        """
        return self.filter_by(is_active=True)

    def get_verified_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserProfile]:
        """
        Get all verified users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of verified UserProfile instances
        """
        return self.filter_by(is_verified=True)

    def get_users_by_role(self, role: str) -> List[UserProfile]:
        """
        Get all users with a specific role.

        Args:
            role: User role (from UserRoleEnum)

        Returns:
            List of UserProfile instances with the specified role
        """
        return self.filter_by(role=role)

    def get_users_by_organization(
        self,
        organization: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserProfile]:
        """
        Get all users from an organization.

        Args:
            organization: Organization name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of UserProfile instances
        """
        return self.filter_by(organization=organization)

    # ============================================
    # User-Specific Operations
    # ============================================

    def create_user(
        self,
        email: str,
        hashed_password: str,
        display_name: Optional[str] = None,
        organization: Optional[str] = None,
        role: str = "user"
    ) -> UserProfile:
        """
        Create a new user.

        Args:
            email: User's email address
            hashed_password: Hashed password
            display_name: Optional display name
            organization: Optional organization
            role: User role (defaults to "user")

        Returns:
            Created UserProfile instance

        Raises:
            DuplicateError: If email already exists
        """
        return self.create(
            email=email,
            hashed_password=hashed_password,
            display_name=display_name,
            organization=organization,
            role=role
        )

    def update_last_login(self, user_id: UUID) -> UserProfile:
        """
        Update user's last login timestamp.

        Args:
            user_id: User's UUID

        Returns:
            Updated UserProfile instance

        Raises:
            NotFoundError: If user not found
        """
        return self.update_or_404(user_id, last_login=datetime.now(timezone.utc))

    def verify_user(self, user_id: UUID) -> UserProfile:
        """
        Mark user as verified.

        Args:
            user_id: User's UUID

        Returns:
            Updated UserProfile instance

        Raises:
            NotFoundError: If user not found
        """
        return self.update_or_404(user_id, is_verified=True)

    def deactivate_user(self, user_id: UUID) -> UserProfile:
        """
        Deactivate user account.

        Args:
            user_id: User's UUID

        Returns:
            Updated UserProfile instance

        Raises:
            NotFoundError: If user not found
        """
        return self.update_or_404(user_id, is_active=False)

    def activate_user(self, user_id: UUID) -> UserProfile:
        """
        Activate user account.

        Args:
            user_id: User's UUID

        Returns:
            Updated UserProfile instance

        Raises:
            NotFoundError: If user not found
        """
        return self.update_or_404(user_id, is_active=True)

    def update_profile(
        self,
        user_id: UUID,
        display_name: Optional[str] = None,
        organization: Optional[str] = None
    ) -> UserProfile:
        """
        Update user profile information.

        Args:
            user_id: User's UUID
            display_name: New display name
            organization: New organization

        Returns:
            Updated UserProfile instance

        Raises:
            NotFoundError: If user not found
        """
        updates = {}
        if display_name is not None:
            updates["display_name"] = display_name
        if organization is not None:
            updates["organization"] = organization

        return self.update_or_404(user_id, **updates)

    def change_password(self, user_id: UUID, new_hashed_password: str) -> UserProfile:
        """
        Change user's password.

        Args:
            user_id: User's UUID
            new_hashed_password: New hashed password

        Returns:
            Updated UserProfile instance

        Raises:
            NotFoundError: If user not found
        """
        return self.update_or_404(user_id, hashed_password=new_hashed_password)

    def change_role(self, user_id: UUID, new_role: str) -> UserProfile:
        """
        Change user's role.

        Args:
            user_id: User's UUID
            new_role: New role (from UserRoleEnum)

        Returns:
            Updated UserProfile instance

        Raises:
            NotFoundError: If user not found
        """
        return self.update_or_404(user_id, role=new_role)

    # ============================================
    # Statistics
    # ============================================

    def count_active_users(self) -> int:
        """
        Count active users.

        Returns:
            Number of active users
        """
        return self.count(is_active=True)

    def count_verified_users(self) -> int:
        """
        Count verified users.

        Returns:
            Number of verified users
        """
        return self.count(is_verified=True)

    def count_users_by_role(self, role: str) -> int:
        """
        Count users with a specific role.

        Args:
            role: User role

        Returns:
            Number of users with the role
        """
        return self.count(role=role)
