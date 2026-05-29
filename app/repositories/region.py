"""Region repository."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Region
from app.repositories.base import BaseRepository


class RegionRepository(BaseRepository[Region]):
    """Repository for Region model."""

    def __init__(self, session: AsyncSession):
        """Initialize region repository."""
        super().__init__(session, Region)

    async def get_by_country_code(self, country_code: str) -> Optional[Region]:
        """Get region by country code."""
        return await self.get(country_code=country_code)

    async def get_by_country_name(self, country_name: str) -> Optional[Region]:
        """Get region by country name."""
        return await self.get(country_name=country_name)

    async def get_enabled(self) -> List[Region]:
        """Get all enabled regions."""
        return await self.get_multi(enabled=True)

    async def get_with_accounts(self) -> List[Region]:
        """Get regions with active accounts."""
        query = select(Region).where(Region.enabled == True)
        result = await self.session.execute(query)
        return result.scalars().all()
