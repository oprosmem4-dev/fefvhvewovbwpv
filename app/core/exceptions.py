"""Custom exceptions for the application."""


class BaseAppException(Exception):
    """Base application exception."""

    pass


class AccountNotFoundException(BaseAppException):
    """Account not found."""

    pass


class AccountUnavailableException(BaseAppException):
    """Account is not available for purchase."""

    pass


class InvalidAccountStatusException(BaseAppException):
    """Invalid account status."""

    pass


class RaceConditionException(BaseAppException):
    """Race condition detected - account already reserved or sold."""

    pass


class OrderNotFoundException(BaseAppException):
    """Order not found."""

    pass


class InvalidOrderStatusException(BaseAppException):
    """Invalid order status."""

    pass


class PaymentFailedException(BaseAppException):
    """Payment processing failed."""

    pass


class PaymentNotConfirmedException(BaseAppException):
    """Payment not confirmed yet."""

    pass


class TelethonSessionException(BaseAppException):
    """Telethon session error."""

    pass


class SessionCleanupException(BaseAppException):
    """Session cleanup failed."""

    pass


class LoginCodeNotReceivedException(BaseAppException):
    """Login code was not received."""

    pass


class InvalidSessionStringException(BaseAppException):
    """Invalid session string."""

    pass


class UserNotFoundException(BaseAppException):
    """User not found."""

    pass


class UnauthorizedException(BaseAppException):
    """User is not authorized."""

    pass


class PermissionDeniedException(BaseAppException):
    """User does not have permission."""

    pass


class RedisException(BaseAppException):
    """Redis operation failed."""

    pass


class LockAcquisitionException(BaseAppException):
    """Could not acquire distributed lock."""

    pass


class CryptoBotAPIException(BaseAppException):
    """CryptoBot API error."""

    pass


class TONWatcherException(BaseAppException):
    """TON watcher error."""

    pass


class ValidationException(BaseAppException):
    """Validation error."""

    pass


class RateLimitException(BaseAppException):
    """Rate limit exceeded."""

    pass


class FloodDetectedException(BaseAppException):
    """Flood detected."""

    pass
