"""Payment repository."""

from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Payment, PaymentMethodEnum, PaymentStatusEnum
from app.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    """Repository for Payment model."""

    def __init__(self, session: AsyncSession):
        """Initialize payment repository."""
        super().__init__(session, Payment)

    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """Get payment by transaction ID."""
        return await self.get(transaction_id=transaction_id)

    async def get_order_payments(self, order_id: int) -> List[Payment]:
        """Get all payments for order."""
        return await self.get_multi(order_id=order_id)

    async def get_user_payments(self, user_id: int) -> List[Payment]:
        """Get all payments for user."""
        return await self.get_multi(user_id=user_id)

    async def get_pending_payments(self) -> List[Payment]:
        """Get pending payments."""
        return await self.get_multi(status=PaymentStatusEnum.PENDING)

    async def get_by_method(self, method: PaymentMethodEnum) -> List[Payment]:
        """Get payments by method."""
        return await self.get_multi(method=method)

    async def get_by_external_id(self, external_id: str) -> Optional[Payment]:
        """Get payment by external payment ID."""
        return await self.get(external_payment_id=external_id)
