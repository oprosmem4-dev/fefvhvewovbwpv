"""Base repository class."""

from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

T = TypeVar("T", bound=DeclarativeBase)


class BaseRepository(Generic[T]):
    """Base repository class with common CRUD operations."""

    def __init__(self, session: AsyncSession, model: Type[T]):
        """Initialize repository."""
        self.session = session
        self.model = model

    async def create(self, **kwargs: Any) -> T:
        """Create and return new object."""
        db_obj = self.model(**kwargs)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def get_by_id(self, obj_id: Any) -> Optional[T]:
        """Get object by ID."""
        return await self.session.get(self.model, obj_id)

    async def get(self, **kwargs: Any) -> Optional[T]:
        """Get single object by filter."""
        query = select(self.model)
        for key, value in kwargs.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all objects with pagination."""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_multi(self, **filters: Any) -> List[T]:
        """Get multiple objects by filters."""
        query = select(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, obj: T, **kwargs: Any) -> T:
        """Update object."""
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: T) -> None:
        """Delete object."""
        await self.session.delete(obj)
        await self.session.flush()

    async def delete_by_id(self, obj_id: Any) -> bool:
        """Delete object by ID."""
        obj = await self.get_by_id(obj_id)
        if obj:
            await self.delete(obj)
            return True
        return False

    async def exists(self, **kwargs: Any) -> bool:
        """Check if object exists."""
        query = select(self.model)
        for key, value in kwargs.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalars().first() is not None

    async def count(self, **filters: Any) -> int:
        """Count objects."""
        from sqlalchemy import func

        query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar() or 0
