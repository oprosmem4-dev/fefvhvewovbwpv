"""User repository."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository."""
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        return await self.get(telegram_id=telegram_id)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return await self.get(username=username)

    async def get_admins(self) -> List[User]:
        """Get all admin users."""
        return await self.get_multi(is_admin=True)

    async def get_banned(self) -> List[User]:
        """Get all banned users."""
        return await self.get_multi(is_banned=True)

    async def is_admin(self, telegram_id: int) -> bool:
        """Check if user is admin."""
        user = await self.get_by_telegram_id(telegram_id)
        return user.is_admin if user else False

    async def is_banned(self, telegram_id: int) -> bool:
        """Check if user is banned."""
        user = await self.get_by_telegram_id(telegram_id)
        return user.is_banned if user else False

    async def count_users(self) -> int:
        """Count total users."""
        return await self.count()
