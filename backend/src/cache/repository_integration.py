"""
Repository Integration Examples

Shows how to integrate caching with repository pattern.
"""

from typing import Optional, List
from uuid import UUID

from ..database.repositories import UserRepository, AnalysisRepository
from .decorators import cached, cache_invalidate
from .utils import CacheKeyBuilder, get_or_set


class CachedUserRepository(UserRepository):
    """
    User repository with caching layer.

    Example of extending repositories with caching.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_builder = CacheKeyBuilder("user")

    @cached(ttl=600, serializer="pickle")  # Cache for 10 minutes
    def get_by_id(self, id: UUID):
        """Get user by ID with caching."""
        return super().get_by_id(id)

    @cached(ttl=300, serializer="pickle")
    def get_by_email(self, email: str):
        """Get user by email with caching."""
        return super().get_by_email(email)

    @cache_invalidate(pattern="user:*")
    def create_user(self, *args, **kwargs):
        """Create user and invalidate cache."""
        return super().create_user(*args, **kwargs)

    @cache_invalidate(keys=lambda self, user_id, **kwargs: [f"user:*:{user_id}:*"])
    def update(self, user_id: UUID, **kwargs):
        """Update user and invalidate cache."""
        result = super().update(user_id, **kwargs)

        # Invalidate specific user caches
        from .cache_service import get_cache
        cache = get_cache()
        cache.delete_pattern(f"*:user_id={user_id}:*")

        return result


class CachedAnalysisRepository(AnalysisRepository):
    """
    Analysis repository with caching layer.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_builder = CacheKeyBuilder("analysis")

    @cached(ttl=300, serializer="pickle")
    def get_by_id(self, id: UUID):
        """Get analysis by ID with caching."""
        return super().get_by_id(id)

    def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100):
        """Get user's analyses with caching."""
        cache_key = self.key_builder.build(
            method="get_by_user",
            user_id=str(user_id),
            skip=skip,
            limit=limit
        )

        return get_or_set(
            key=cache_key,
            default_factory=lambda: super().get_by_user(user_id, skip, limit),
            ttl=300
        )

    @cached(ttl=600, serializer="pickle")
    def get_statistics(self, user_id: Optional[UUID] = None):
        """Get analysis statistics with caching."""
        return super().get_statistics(user_id)

    @cache_invalidate(pattern="analysis:*")
    def create_analysis(self, *args, **kwargs):
        """Create analysis and invalidate cache."""
        return super().create_analysis(*args, **kwargs)


# ============================================
# Service Layer with Caching
# ============================================

class CachedAnalysisService:
    """
    Example service layer with integrated caching.
    """

    def __init__(self, analysis_repo: AnalysisRepository):
        self.analysis_repo = analysis_repo
        self.key_builder = CacheKeyBuilder("service:analysis")

    @cached(ttl=600)
    def get_user_dashboard_data(self, user_id: UUID) -> dict:
        """
        Get comprehensive dashboard data for a user.

        This aggregates multiple queries and caches the result.
        """
        # Get analyses
        recent_analyses = self.analysis_repo.get_recent_analyses(user_id, limit=10)

        # Get statistics
        stats = self.analysis_repo.get_statistics(user_id)

        # Get high-risk analyses
        high_risk = self.analysis_repo.get_high_risk_analyses(user_id, limit=5)

        return {
            "recent_analyses": recent_analyses,
            "statistics": stats,
            "high_risk_analyses": high_risk,
            "user_id": str(user_id)
        }

    def invalidate_user_dashboard(self, user_id: UUID) -> None:
        """Invalidate dashboard cache after updates."""
        from .cache_service import get_cache
        cache = get_cache()

        # Clear all dashboard-related caches
        patterns = [
            f"*:get_user_dashboard_data:*{user_id}*",
            f"analysis:*:user_id={user_id}:*",
            f"service:analysis:user_id={user_id}:*"
        ]

        for pattern in patterns:
            cache.delete_pattern(pattern)


# ============================================
# FastAPI Integration Example
# ============================================

def create_cached_repositories(db_session):
    """
    Factory function to create cached repository instances.

    Usage in FastAPI:
        @app.get("/users/{user_id}")
        async def get_user(
            user_id: UUID,
            db: Session = Depends(get_db)
        ):
            repos = create_cached_repositories(db)
            user = repos["user"].get_by_id(user_id)
            return user
    """
    return {
        "user": CachedUserRepository(db_session),
        "analysis": CachedAnalysisRepository(db_session)
    }
