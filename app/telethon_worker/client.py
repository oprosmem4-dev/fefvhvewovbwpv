"""Telethon client manager."""

import os
from typing import Optional
from telethon import TelegramClient
from telethon.sessions import StringSession
import logging

from app.core.config import get_settings
from app.core.exceptions import TelethonSessionException

logger = logging.getLogger(__name__)
settings = get_settings()


class TelethonClientManager:
    """Manage Telethon client instances."""

    def __init__(self):
        """Initialize client manager."""
        self.api_id = settings.telethon.api_id
        self.api_hash = settings.telethon.api_hash
        self.clients: dict[str, TelegramClient] = {}

    async def get_client(self, session_string: str) -> TelegramClient:
        """
        Get or create Telethon client from session string.
        Uses StringSession for serverless operation.
        """
        # Use session string hash as key
        session_key = hash(session_string) % ((2**31) - 1)
        session_key_str = str(session_key)

        if session_key_str in self.clients:
            client = self.clients[session_key_str]
            if client.is_connected():
                return client

        try:
            # Create client from session string (no need to login again)
            client = TelegramClient(
                StringSession(session_string),
                self.api_id,
                self.api_hash,
                system_version="4.16.30",
                app_version="10.1 x64",
            )

            await client.connect()

            # Check if session is valid
            if not await client.is_user_authorized():
                raise TelethonSessionException("Session is not authorized")

            self.clients[session_key_str] = client
            logger.info(f"Created new Telethon client from session string")

            return client

        except Exception as e:
            logger.error(f"Failed to create Telethon client: {str(e)}")
            raise TelethonSessionException(f"Failed to create client: {str(e)}")

    async def disconnect_client(self, session_string: str) -> None:
        """Disconnect and remove client."""
        session_key = hash(session_string) % ((2**31) - 1)
        session_key_str = str(session_key)

        if session_key_str in self.clients:
            client = self.clients[session_key_str]
            try:
                await client.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting client: {str(e)}")
            finally:
                del self.clients[session_key_str]

    async def close_all(self) -> None:
        """Close all active clients."""
        for session_key, client in self.clients.items():
            try:
                await client.disconnect()
            except Exception as e:
                logger.error(f"Error closing client {session_key}: {str(e)}")

        self.clients.clear()


# Global instance
_telethon_manager: Optional[TelethonClientManager] = None


def get_telethon_manager() -> TelethonClientManager:
    """Get or create global Telethon manager."""
    global _telethon_manager
    if _telethon_manager is None:
        _telethon_manager = TelethonClientManager()
    return _telethon_manager
