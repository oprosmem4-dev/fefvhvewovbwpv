"""Encryption utilities for sensitive data."""

from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

from app.core.config import get_settings

settings = get_settings()


class EncryptionManager:
    """Manage encryption and decryption of sensitive data."""

    def __init__(self, encryption_key: str) -> None:
        """Initialize encryption manager with key."""
        # Convert string key to bytes and generate Fernet key
        if isinstance(encryption_key, str):
            key_bytes = encryption_key.encode()
        else:
            key_bytes = encryption_key

        # Ensure key is proper length for Fernet (32 bytes base64 encoded)
        if len(key_bytes) >= 32:
            # Use PBKDF2 to derive a proper Fernet key
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"telegram_marketplace_salt_v1",
                iterations=100000,
            )
            key = kdf.derive(key_bytes[:32])
            import base64

            self.cipher_suite = Fernet(base64.urlsafe_b64encode(key))
        else:
            raise ValueError("Encryption key must be at least 32 characters")

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext string."""
        if not plaintext:
            return ""

        encrypted = self.cipher_suite.encrypt(plaintext.encode())
        return encrypted.decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext string."""
        if not ciphertext:
            return ""

        try:
            decrypted = self.cipher_suite.decrypt(ciphertext.encode())
            return decrypted.decode()
        except Exception:
            # Return empty string if decryption fails
            return ""

    def encrypt_optional(self, value: Optional[str]) -> Optional[str]:
        """Encrypt optional value."""
        if value is None:
            return None
        return self.encrypt(value)

    def decrypt_optional(self, value: Optional[str]) -> Optional[str]:
        """Decrypt optional value."""
        if value is None:
            return None
        return self.decrypt(value)


# Global encryption manager instance
_encryption_manager: Optional[EncryptionManager] = None


def get_encryption_manager() -> EncryptionManager:
    """Get or create global encryption manager."""
    global _encryption_manager

    if _encryption_manager is None:
        _encryption_manager = EncryptionManager(settings.session.encryption_key)

    return _encryption_manager


def encrypt_session_string(session_string: str) -> str:
    """Encrypt Telethon session string."""
    manager = get_encryption_manager()
    return manager.encrypt(session_string)


def decrypt_session_string(encrypted_session: str) -> str:
    """Decrypt Telethon session string."""
    manager = get_encryption_manager()
    return manager.decrypt(encrypted_session)


def encrypt_login_code(code: str) -> str:
    """Encrypt login code."""
    manager = get_encryption_manager()
    return manager.encrypt(code)


def decrypt_login_code(encrypted_code: str) -> str:
    """Decrypt login code."""
    manager = get_encryption_manager()
    return manager.decrypt(encrypted_code)
