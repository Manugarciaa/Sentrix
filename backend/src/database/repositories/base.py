"""
Base Repository Pattern

Provides generic CRUD operations for database models with type safety.
All specific repositories should inherit from BaseRepository.
"""

from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update, delete, func

from ..models.base import Base


# Type variable for SQLAlchemy models
ModelType = TypeVar("ModelType", bound=Base)


class RepositoryError(Exception):
    """Base exception for repository errors"""
    pass


class NotFoundError(RepositoryError):
    """Raised when a record is not found"""
    pass


class DuplicateError(RepositoryError):
    """Raised when trying to create a duplicate record"""
    pass


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing generic CRUD operations.

    Usage:
        class UserRepository(BaseRepository[UserProfile]):
            def __init__(self, db: Session):
                super().__init__(UserProfile, db)
    """

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    # ============================================
    # Create Operations
    # ============================================

    def create(self, **kwargs) -> ModelType:
        """
        Create a new record.

        Args:
            **kwargs: Field values for the new record

        Returns:
            Created model instance

        Raises:
            DuplicateError: If unique constraint is violated
            RepositoryError: If creation fails
        """
        try:
            instance = self.model(**kwargs)
            self.db.add(instance)
            self.db.flush()  # Get ID without committing
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            if "unique" in str(e).lower() or "duplicate" in str(e).lower():
                raise DuplicateError(f"Record with these values already exists: {e}")
            raise RepositoryError(f"Failed to create record: {e}")

    def bulk_create(self, records: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Create multiple records in bulk.

        Args:
            records: List of dictionaries with field values

        Returns:
            List of created model instances

        Raises:
            RepositoryError: If bulk creation fails
        """
        try:
            instances = [self.model(**record) for record in records]
            self.db.add_all(instances)
            self.db.flush()
            for instance in instances:
                self.db.refresh(instance)
            return instances
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to bulk create records: {e}")

    # ============================================
    # Read Operations
    # ============================================

    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """
        Get a record by its ID.

        Args:
            id: UUID of the record

        Returns:
            Model instance or None if not found
        """
        try:
            stmt = select(self.model).where(self.model.id == id)
            result = self.db.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get record by id: {e}")

    def get_by_id_or_404(self, id: UUID) -> ModelType:
        """
        Get a record by ID or raise NotFoundError.

        Args:
            id: UUID of the record

        Returns:
            Model instance

        Raises:
            NotFoundError: If record not found
        """
        instance = self.get_by_id(id)
        if instance is None:
            raise NotFoundError(f"{self.model.__name__} with id {id} not found")
        return instance

    def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """
        Get a single record by any field.

        Args:
            field_name: Name of the field to filter by
            value: Value to match

        Returns:
            Model instance or None if not found
        """
        try:
            field = getattr(self.model, field_name)
            stmt = select(self.model).where(field == value)
            result = self.db.execute(stmt)
            return result.scalar_one_or_none()
        except AttributeError:
            raise RepositoryError(f"Field {field_name} does not exist on {self.model.__name__}")
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get record by {field_name}: {e}")

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = False
    ) -> List[ModelType]:
        """
        Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            order_by: Field name to order by (defaults to 'created_at')
            descending: If True, order in descending order

        Returns:
            List of model instances
        """
        try:
            stmt = select(self.model)

            # Apply ordering
            if order_by:
                order_field = getattr(self.model, order_by)
            else:
                # Default to created_at if it exists, otherwise id
                order_field = getattr(self.model, "created_at", self.model.id)

            if descending:
                stmt = stmt.order_by(order_field.desc())
            else:
                stmt = stmt.order_by(order_field)

            # Apply pagination
            stmt = stmt.offset(skip).limit(limit)

            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to get all records: {e}")

    def filter_by(self, **filters) -> List[ModelType]:
        """
        Filter records by multiple fields.

        Args:
            **filters: Field-value pairs to filter by

        Returns:
            List of matching model instances
        """
        try:
            stmt = select(self.model)
            for field_name, value in filters.items():
                field = getattr(self.model, field_name)
                stmt = stmt.where(field == value)

            result = self.db.execute(stmt)
            return list(result.scalars().all())
        except AttributeError as e:
            raise RepositoryError(f"Invalid filter field: {e}")
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to filter records: {e}")

    def count(self, **filters) -> int:
        """
        Count records matching filters.

        Args:
            **filters: Field-value pairs to filter by

        Returns:
            Number of matching records
        """
        try:
            stmt = select(func.count()).select_from(self.model)
            for field_name, value in filters.items():
                field = getattr(self.model, field_name)
                stmt = stmt.where(field == value)

            result = self.db.execute(stmt)
            return result.scalar_one()
        except SQLAlchemyError as e:
            raise RepositoryError(f"Failed to count records: {e}")

    def exists(self, **filters) -> bool:
        """
        Check if any record exists matching filters.

        Args:
            **filters: Field-value pairs to filter by

        Returns:
            True if at least one record exists, False otherwise
        """
        return self.count(**filters) > 0

    # ============================================
    # Update Operations
    # ============================================

    def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        """
        Update a record by ID.

        Args:
            id: UUID of the record to update
            **kwargs: Fields to update

        Returns:
            Updated model instance or None if not found

        Raises:
            RepositoryError: If update fails
        """
        try:
            instance = self.get_by_id(id)
            if instance is None:
                return None

            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            self.db.flush()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to update record: {e}")

    def update_or_404(self, id: UUID, **kwargs) -> ModelType:
        """
        Update a record by ID or raise NotFoundError.

        Args:
            id: UUID of the record to update
            **kwargs: Fields to update

        Returns:
            Updated model instance

        Raises:
            NotFoundError: If record not found
            RepositoryError: If update fails
        """
        instance = self.update(id, **kwargs)
        if instance is None:
            raise NotFoundError(f"{self.model.__name__} with id {id} not found")
        return instance

    def bulk_update(self, filters: Dict[str, Any], values: Dict[str, Any]) -> int:
        """
        Update multiple records matching filters.

        Args:
            filters: Field-value pairs to filter records
            values: Field-value pairs to update

        Returns:
            Number of records updated

        Raises:
            RepositoryError: If bulk update fails
        """
        try:
            stmt = update(self.model).values(**values)
            for field_name, value in filters.items():
                field = getattr(self.model, field_name)
                stmt = stmt.where(field == value)

            result = self.db.execute(stmt)
            self.db.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to bulk update records: {e}")

    # ============================================
    # Delete Operations
    # ============================================

    def delete(self, id: UUID) -> bool:
        """
        Delete a record by ID.

        Args:
            id: UUID of the record to delete

        Returns:
            True if deleted, False if not found

        Raises:
            RepositoryError: If deletion fails
        """
        try:
            instance = self.get_by_id(id)
            if instance is None:
                return False

            self.db.delete(instance)
            self.db.flush()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to delete record: {e}")

    def delete_or_404(self, id: UUID) -> None:
        """
        Delete a record by ID or raise NotFoundError.

        Args:
            id: UUID of the record to delete

        Raises:
            NotFoundError: If record not found
            RepositoryError: If deletion fails
        """
        if not self.delete(id):
            raise NotFoundError(f"{self.model.__name__} with id {id} not found")

    def bulk_delete(self, **filters) -> int:
        """
        Delete multiple records matching filters.

        Args:
            **filters: Field-value pairs to filter records

        Returns:
            Number of records deleted

        Raises:
            RepositoryError: If bulk deletion fails
        """
        try:
            stmt = delete(self.model)
            for field_name, value in filters.items():
                field = getattr(self.model, field_name)
                stmt = stmt.where(field == value)

            result = self.db.execute(stmt)
            self.db.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to bulk delete records: {e}")

    # ============================================
    # Transaction Management
    # ============================================

    def commit(self) -> None:
        """Commit the current transaction."""
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryError(f"Failed to commit transaction: {e}")

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.db.rollback()

    def refresh(self, instance: ModelType) -> ModelType:
        """
        Refresh an instance from the database.

        Args:
            instance: Model instance to refresh

        Returns:
            Refreshed model instance
        """
        self.db.refresh(instance)
        return instance
