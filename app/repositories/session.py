"""Session repository."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Session, SessionStatusEnum
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository[Session]):
    """Repository for Session model."""

    def __init__(self, session: AsyncSession):
        """Initialize session repository."""
        super().__init__(session, Session)

    async def get_account_sessions(self, account_id: int) -> List[Session]:
        """Get all sessions for account."""
        return await self.get_multi(account_id=account_id)

    async def get_main_session(self, account_id: int) -> Optional[Session]:
        """Get main session for account."""
        return await self.get(account_id=account_id, is_main_session=True)

    async def get_active_sessions(self, account_id: int) -> List[Session]:
        """Get active sessions for account."""
        query = select(Session).where(
            Session.account_id == account_id,
            Session.status == SessionStatusEnum.ACTIVE,
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_unauthorized_sessions(self, account_id: int) -> List[Session]:
        """Get unauthorized sessions (all except main)."""
        query = select(Session).where(
            Session.account_id == account_id,
            Session.is_main_session == False,
            Session.status == SessionStatusEnum.ACTIVE,
        )
        result = await self.session.execute(query)
        return result.scalars().all()
