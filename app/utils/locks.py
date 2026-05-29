"""Distributed locks using Redis for race condition prevention."""

from typing import Optional

import aioredis
from aioredis import Redis

from app.core.config import get_settings
from app.core.exceptions import LockAcquisitionException

settings = get_settings()


class DistributedLock:
    """Distributed lock using Redis."""

    def __init__(self, redis: Redis, key: str, timeout: int = 30):
        """Initialize lock."""
        self.redis = redis
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.token: Optional[str] = None

    async def __aenter__(self) -> "DistributedLock":
        """Acquire lock."""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Release lock."""
        await self.release()

    async def acquire(self, retries: int = 3) -> bool:
        """Acquire lock with retries."""
        import uuid
        import asyncio

        self.token = str(uuid.uuid4())

        for attempt in range(retries):
            try:
                # Try to set lock with NX (only if not exists)
                result = await self.redis.set(
                    self.key,
                    self.token,
                    px=self.timeout * 1000,  # Convert to milliseconds
                    nx=True,  # Only set if not exists
                )

                if result:
                    return True

                # Wait before retry
                await asyncio.sleep(0.1 * (attempt + 1))

            except Exception as e:
                if attempt == retries - 1:
                    raise LockAcquisitionException(f"Failed to acquire lock: {str(e)}")

        raise LockAcquisitionException(f"Could not acquire lock after {retries} retries")

    async def release(self) -> bool:
        """Release lock using Lua script for atomic operation."""
        if not self.token:
            return False

        # Lua script to ensure we only delete if token matches
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """

        try:
            result = await self.redis.eval(lua_script, 1, self.key, self.token)
            return bool(result)
        except Exception:
            return False

    async def extend(self, additional_timeout: int) -> bool:
        """Extend lock timeout."""
        if not self.token:
            return False

        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("pexpire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """

        try:
            result = await self.redis.eval(
                lua_script,
                1,
                self.key,
                self.token,
                str((self.timeout + additional_timeout) * 1000),
            )
            return bool(result)
        except Exception:
            return False


class RedisLockManager:
    """Manager for Redis locks."""

    def __init__(self, redis_url: str):
        """Initialize lock manager."""
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        if self.redis is None:
            self.redis = await aioredis.from_url(self.redis_url)

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    async def acquire_lock(self, key: str, timeout: int = 30) -> DistributedLock:
        """Acquire a lock."""
        if self.redis is None:
            raise RuntimeError("Redis not connected. Call connect() first.")

        lock = DistributedLock(self.redis, key, timeout)
        await lock.acquire()
        return lock

    async def release_lock(self, lock: DistributedLock) -> bool:
        """Release a lock."""
        return await lock.release()

    async def get_lock(self, key: str, timeout: int = 30) -> DistributedLock:
        """Get lock context manager."""
        if self.redis is None:
            raise RuntimeError("Redis not connected. Call connect() first.")

        return DistributedLock(self.redis, key, timeout)


# Global lock manager instance
_lock_manager: Optional[RedisLockManager] = None


def get_lock_manager() -> RedisLockManager:
    """Get or create global lock manager."""
    global _lock_manager

    if _lock_manager is None:
        _lock_manager = RedisLockManager(settings.redis.url)

    return _lock_manager


async def get_distributed_lock(key: str, timeout: int = 30) -> DistributedLock:
    """Get distributed lock for dependency injection."""
    manager = get_lock_manager()
    if manager.redis is None:
        await manager.connect()

    return await manager.get_lock(key, timeout)
