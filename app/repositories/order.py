"""Order repository."""

from typing import List, Optional
from datetime import datetime

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order, OrderStatusEnum
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Repository for Order model."""

    def __init__(self, session: AsyncSession):
        """Initialize order repository."""
        super().__init__(session, Order)

    async def get_user_orders(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders for user."""
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_account_id(self, account_id: int) -> Optional[Order]:
        """Get active order for account."""
        return await self.get(account_id=account_id, status=OrderStatusEnum.PAID)

    async def get_pending_payment_orders(self) -> List[Order]:
        """Get orders awaiting payment."""
        return await self.get_multi(status=OrderStatusEnum.PAYMENT_AWAITING)

    async def mark_paid(self, order_id: int) -> bool:
        """Mark order as paid."""
        stmt = (
            update(Order)
            .where(Order.id == order_id)
            .values(status=OrderStatusEnum.PAID, paid_at=datetime.utcnow())
            .returning(Order.id)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none() is not None

    async def mark_completed(self, order_id: int) -> bool:
        """Mark order as completed."""
        stmt = (
            update(Order)
            .where(Order.id == order_id)
            .values(status=OrderStatusEnum.COMPLETED, completed_at=datetime.utcnow())
            .returning(Order.id)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none() is not None

    async def cancel_order(self, order_id: int, reason: str) -> bool:
        """Cancel order."""
        stmt = (
            update(Order)
            .where(Order.id == order_id)
            .values(status=OrderStatusEnum.CANCELLED, cancel_reason=reason)
            .returning(Order.id)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none() is not None

    async def store_login_code(self, order_id: int, code: str, expires_at: datetime) -> bool:
        """Store login code for order."""
        from app.utils.encryption import encrypt_login_code

        encrypted_code = encrypt_login_code(code)
        stmt = (
            update(Order)
            .where(Order.id == order_id)
            .values(login_code=encrypted_code, login_code_expires_at=expires_at)
            .returning(Order.id)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none() is not None
