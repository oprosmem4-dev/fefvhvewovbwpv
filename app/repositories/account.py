"""Account repository."""

from typing import Any, List, Optional

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Account, AccountStatusEnum
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    """Repository for Account model."""

    def __init__(self, session: AsyncSession):
        """Initialize account repository."""
        super().__init__(session, Account)

    async def get_by_phone(self, phone_number: str) -> Optional[Account]:
        """Get account by phone number."""
        return await self.get(phone_number=phone_number)

    async def get_available_by_region(
        self, region_id: int, skip: int = 0, limit: int = 100
    ) -> List[Account]:
        """Get available accounts by region."""
        query = (
            select(Account)
            .where(
                and_(
                    Account.region_id == region_id,
                    Account.status == AccountStatusEnum.AVAILABLE,
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_available_by_region_sorted(
        self,
        region_id: int,
        sort_by: str = "price",
        sort_order: str = "asc",
        skip: int = 0,
        limit: int = 100,
    ) -> List[Account]:
        """Get available accounts by region with sorting."""
        from sqlalchemy import asc, desc

        sort_column = getattr(Account, sort_by, Account.price)
        sort_func = asc if sort_order == "asc" else desc

        query = (
            select(Account)
            .where(
                and_(
                    Account.region_id == region_id,
                    Account.status == AccountStatusEnum.AVAILABLE,
                )
            )
            .order_by(sort_func(sort_column))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_all_available(
        self, skip: int = 0, limit: int = 100
    ) -> List[Account]:
        """Get all available accounts."""
        query = (
            select(Account)
            .where(Account.status == AccountStatusEnum.AVAILABLE)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_status(
        self, status: AccountStatusEnum, skip: int = 0, limit: int = 100
    ) -> List[Account]:
        """Get accounts by status."""
        query = (
            select(Account)
            .where(Account.status == status)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def reserve_account(self, account_id: int) -> bool:
        """
        Reserve account (atomically change status from AVAILABLE to RESERVED).
        Returns True if successful, False if account was not available.
        """
        # Use row-level locking to prevent race conditions
        stmt = (
            update(Account)
            .where(
                and_(
                    Account.id == account_id,
                    Account.status == AccountStatusEnum.AVAILABLE,
                )
            )
            .values(status=AccountStatusEnum.RESERVED)
            .returning(Account.id)
        )

        result = await self.session.execute(stmt)
        await self.session.flush()

        # Check if update was successful
        return result.scalar_one_or_none() is not None

    async def mark_sold(self, account_id: int) -> bool:
        """Mark account as sold."""
        stmt = (
            update(Account)
            .where(Account.id == account_id)
            .values(status=AccountStatusEnum.SOLD)
            .returning(Account.id)
        )

        result = await self.session.execute(stmt)
        await self.session.flush()

        return result.scalar_one_or_none() is not None

    async def mark_available(self, account_id: int) -> bool:
        """Mark account as available."""
        stmt = (
            update(Account)
            .where(Account.id == account_id)
            .values(status=AccountStatusEnum.AVAILABLE)
            .returning(Account.id)
        )

        result = await self.session.execute(stmt)
        await self.session.flush()

        return result.scalar_one_or_none() is not None

    async def update_cleanup_status(
        self, account_id: int, retries: int, last_attempt_time: Any
    ) -> Optional[Account]:
        """Update cleanup retry information."""
        from datetime import datetime

        account = await self.get_by_id(account_id)
        if account:
            account.cleanup_retries = retries
            account.last_cleanup_attempt = last_attempt_time or datetime.utcnow()
            await self.session.flush()
            await self.session.refresh(account)

        return account

    async def get_pending_cleanup_accounts(self) -> List[Account]:
        """Get accounts pending session cleanup."""
        query = select(Account).where(
            Account.status == AccountStatusEnum.PENDING_CLEANUP
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count_available_by_region(self, region_id: int) -> int:
        """Count available accounts in region."""
        return await self.count(
            region_id=region_id, status=AccountStatusEnum.AVAILABLE
        )

    async def search_accounts(
        self,
        status: Optional[AccountStatusEnum] = None,
        region_id: Optional[int] = None,
        is_premium: Optional[bool] = None,
        price_min: Optional[float] = None,
        price_max: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Account]:
        """Search accounts with multiple filters."""
        query = select(Account)

        if status:
            query = query.where(Account.status == status)
        if region_id:
            query = query.where(Account.region_id == region_id)
        if is_premium is not None:
            query = query.where(Account.is_premium == is_premium)
        if price_min is not None:
            query = query.where(Account.price >= price_min)
        if price_max is not None:
            query = query.where(Account.price <= price_max)

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
