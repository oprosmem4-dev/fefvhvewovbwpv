"""Application constants."""

from enum import Enum

# Telegram
TELEGRAM_CODE_WAIT_TIMEOUT = 120  # seconds to wait for login code
TELEGRAM_CODE_VALIDITY = 300  # login code validity period (5 minutes)

# Order
ORDER_RESERVATION_DEFAULT_TTL = 3600  # 1 hour
ORDER_PAYMENT_TIMEOUT = 1800  # 30 minutes

# Cleanup
CLEANUP_RETRY_INTERVAL = 1800  # 30 minutes
CLEANUP_MAX_RETRIES = 10

# Rate Limiting
RATE_LIMIT_DEFAULT_REQUESTS = 10
RATE_LIMIT_DEFAULT_PERIOD = 60

# Anti-spam
FLOOD_THRESHOLD = 5  # messages
FLOOD_BLOCK_DURATION = 600  # 10 minutes

# Cache TTL
CACHE_TTL_SHORT = 300  # 5 minutes
CACHE_TTL_MEDIUM = 3600  # 1 hour
CACHE_TTL_LONG = 86400  # 1 day

# Telethon
TELETHON_SESSION_TIMEOUT = 30  # seconds
TELETHON_CONNECTION_RETRIES = 3

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Error messages
ACCOUNT_NOT_FOUND = "Account not found"
ACCOUNT_UNAVAILABLE = "Account is not available for purchase"
ORDER_NOT_FOUND = "Order not found"
PAYMENT_FAILED = "Payment processing failed"
UNAUTHORIZED = "Unauthorized access"

class CurrencyEnum(str, Enum):
    """Supported currencies."""

    USD = "USD"
    TON = "TON"
    USDT = "USDT"
    BTC = "BTC"
    ETH = "ETH"
