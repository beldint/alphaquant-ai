"""
Project: AlphaQuant AI
File: backend/repository/base.py
Description: Generic async SQLAlchemy repository implementation.
Python Version: 3.11.9
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from loguru import logger
from sqlalchemy import Select, delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import DatabaseException, NotFoundException
from backend.database.base import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic repository for CRUD operations on a SQLAlchemy model."""

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        """
        Initialize repository with an async database session.

        Args:
            session: SQLAlchemy async session.
            model: ORM model class managed by this repository.
        """
        self.session = session
        self.model = model

    async def get_by_id(self, entity_id: str) -> ModelT | None:
        """
        Fetch a model instance by primary key.

        Args:
            entity_id: Primary key value.

        Returns:
            Matching model instance or None.
        """
        try:
            return await self.session.get(self.model, entity_id)
        except SQLAlchemyError as exc:
            logger.exception("Failed to get {model} by id", model=self.model.__name__)
            raise DatabaseException(cause=exc) from exc

    async def get_required_by_id(self, entity_id: str) -> ModelT:
        """
        Fetch a model instance by primary key or raise NotFoundException.

        Args:
            entity_id: Primary key value.

        Returns:
            Matching model instance.

        Raises:
            NotFoundException: If the entity does not exist.
        """
        entity = await self.get_by_id(entity_id)
        if entity is None:
            raise NotFoundException(
                f"{self.model.__name__} not found",
                resource=self.model.__name__,
                identifier=entity_id,
            )
        return entity

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        statement: Select[tuple[ModelT]] | None = None,
    ) -> list[ModelT]:
        """
        List model instances with pagination.

        Args:
            offset: Number of records to skip.
            limit: Maximum number of records to return.
            statement: Optional custom select statement.

        Returns:
            List of model instances.
        """
        if offset < 0:
            raise ValueError("offset must be greater than or equal to 0")
        if limit < 1:
            raise ValueError("limit must be greater than or equal to 1")
        query = statement if statement is not None else select(self.model)
        query = query.offset(offset).limit(limit)
        try:
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as exc:
            logger.exception("Failed to list {model}", model=self.model.__name__)
            raise DatabaseException(cause=exc) from exc

    async def count(self, statement: Select[tuple[Any]] | None = None) -> int:
        """
        Count model instances.

        Args:
            statement: Optional custom count select statement.

        Returns:
            Number of matched records.
        """
        query = statement if statement is not None else select(func.count()).select_from(self.model)
        try:
            result = await self.session.execute(query)
            return int(result.scalar_one())
        except SQLAlchemyError as exc:
            logger.exception("Failed to count {model}", model=self.model.__name__)
            raise DatabaseException(cause=exc) from exc

    async def create(self, attributes: dict[str, Any]) -> ModelT:
        """
        Create a model instance without committing the transaction.

        Args:
            attributes: Model attributes.

        Returns:
            Created model instance.
        """
        entity = self.model(**attributes)
        try:
            self.session.add(entity)
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except SQLAlchemyError as exc:
            logger.exception("Failed to create {model}", model=self.model.__name__)
            raise DatabaseException(cause=exc) from exc

    async def update(self, entity: ModelT, attributes: dict[str, Any]) -> ModelT:
        """
        Update a model instance without committing the transaction.

        Args:
            entity: Existing model instance.
            attributes: Attributes to update.

        Returns:
            Updated model instance.
        """
        for key, value in attributes.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        try:
            await self.session.flush()
            await self.session.refresh(entity)
            return entity
        except SQLAlchemyError as exc:
            logger.exception("Failed to update {model}", model=self.model.__name__)
            raise DatabaseException(cause=exc) from exc

    async def delete_by_id(self, entity_id: str) -> bool:
        """
        Delete a model instance by primary key without committing the transaction.

        Args:
            entity_id: Primary key value.

        Returns:
            True if a row was deleted.
        """
        try:
            result = await self.session.execute(
                delete(self.model).where(self.model.id == entity_id),
            )
            return bool(result.rowcount)
        except SQLAlchemyError as exc:
            logger.exception("Failed to delete {model}", model=self.model.__name__)
            raise DatabaseException(cause=exc) from exc

    async def exists(self, entity_id: str) -> bool:
        """
        Check whether a model instance exists by primary key.

        Args:
            entity_id: Primary key value.

        Returns:
            True when the entity exists.
        """
        entity = await self.get_by_id(entity_id)
        return entity is not None

    @staticmethod
    def normalize_sequence(items: Sequence[ModelT]) -> list[ModelT]:
        """
        Normalize SQLAlchemy sequences into plain lists.

        Args:
            items: Sequence of model instances.

        Returns:
            Plain list of model instances.
        """
        return list(items)

