"""SQLAlchemy database models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class AccountStatusEnum(str, Enum):
    """Account status enumeration."""

    PENDING_CLEANUP = "pending_cleanup"
    AVAILABLE = "available"
    RESERVED = "reserved"
    SOLD = "sold"
    BANNED = "banned"
    INVALID = "invalid"


class OrderStatusEnum(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    PAYMENT_AWAITING = "payment_awaiting"
    PAID = "paid"
    LOGIN_AWAITING = "login_awaiting"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatusEnum(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethodEnum(str, Enum):
    """Payment method enumeration."""

    CRYPTOBOT = "cryptobot"
    TON = "ton"
    TELEGRAM_STARS = "telegram_stars"


class SessionStatusEnum(str, Enum):
    """Session status enumeration."""

    ACTIVE = "active"
    CLEANED = "cleaned"
    FAILED = "failed"
    PENDING_CLEANUP = "pending_cleanup"


# ==================== User Models ====================


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    first_name: Mapped[Optional[str]] = mapped_column(String(255))
    last_name: Mapped[Optional[str]] = mapped_column(String(255))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    balance: Mapped[float] = mapped_column(Float, default=0.0)
    wallet_address: Mapped[Optional[str]] = mapped_column(String(255))
    preferred_payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    admin_logs: Mapped[list["AdminLog"]] = relationship("AdminLog", back_populates="admin", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_user_telegram_id", "telegram_id"),
        Index("idx_user_is_admin", "is_admin"),
        Index("idx_user_is_banned", "is_banned"),
    )


# ==================== Account Models ====================


class Region(Base):
    """Region/Country model."""

    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_code: Mapped[str] = mapped_column(String(5), unique=True, index=True)
    country_name: Mapped[str] = mapped_column(String(255), unique=True)
    phone_prefix: Mapped[str] = mapped_column(String(10))
    flag_emoji: Mapped[str] = mapped_column(String(10))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    accounts: Mapped[list["Account"]] = relationship("Account", back_populates="region", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_region_country_code", "country_code"),)


class Account(Base):
    """Telegram account model."""

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    region_id: Mapped[int] = mapped_column(Integer, ForeignKey("regions.id", ondelete="RESTRICT"))
    api_id: Mapped[int] = mapped_column(Integer)
    api_hash: Mapped[str] = mapped_column(String(255))
    session_string: Mapped[str] = mapped_column(Text)  # Encrypted
    session_password: Mapped[Optional[str]] = mapped_column(String(255))  # Encrypted if present
    price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(SQLEnum(AccountStatusEnum), default=AccountStatusEnum.PENDING_CLEANUP, index=True)
    follower_count: Mapped[Optional[int]] = mapped_column(Integer)
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    cleanup_retries: Mapped[int] = mapped_column(Integer, default=0)
    last_cleanup_attempt: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    region: Mapped["Region"] = relationship("Region", back_populates="accounts")
    sessions: Mapped[list["Session"]] = relationship("Session", back_populates="account", cascade="all, delete-orphan")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="account", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_account_phone_number", "phone_number"),
        Index("idx_account_status", "status"),
        Index("idx_account_region_id", "region_id"),
        UniqueConstraint("phone_number", name="uq_account_phone_number"),
    )


class Session(Base):
    """Telethon session model."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"))
    device_name: Mapped[Optional[str]] = mapped_column(String(255))
    app_name: Mapped[Optional[str]] = mapped_column(String(255))
    app_version: Mapped[Optional[str]] = mapped_column(String(50))
    system_version: Mapped[Optional[str]] = mapped_column(String(50))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    status: Mapped[str] = mapped_column(SQLEnum(SessionStatusEnum), default=SessionStatusEnum.ACTIVE)
    is_main_session: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="sessions")

    __table_args__ = (
        Index("idx_session_account_id", "account_id"),
        Index("idx_session_status", "status"),
    )


# ==================== Order Models ====================


class Order(Base):
    """Purchase order model."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(SQLEnum(OrderStatusEnum), default=OrderStatusEnum.PENDING, index=True)
    total_amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    payment_method: Mapped[str] = mapped_column(SQLEnum(PaymentMethodEnum))
    reserved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reservation_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    login_code: Mapped[Optional[str]] = mapped_column(String(255))  # Encrypted
    login_code_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    cancel_reason: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="orders")
    account: Mapped["Account"] = relationship("Account", back_populates="orders")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="order", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_order_user_id", "user_id"),
        Index("idx_order_account_id", "account_id"),
        Index("idx_order_status", "status"),
        Index("idx_order_created_at", "created_at"),
    )


# ==================== Payment Models ====================


class Payment(Base):
    """Payment transaction model."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    method: Mapped[str] = mapped_column(SQLEnum(PaymentMethodEnum))
    status: Mapped[str] = mapped_column(SQLEnum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING, index=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10))
    transaction_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True)
    transaction_hash: Mapped[Optional[str]] = mapped_column(String(255))
    external_payment_id: Mapped[Optional[str]] = mapped_column(String(255))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="payments")
    user: Mapped["User"] = relationship("User", back_populates="payments")

    __table_args__ = (
        Index("idx_payment_order_id", "order_id"),
        Index("idx_payment_user_id", "user_id"),
        Index("idx_payment_status", "status"),
        Index("idx_payment_method", "method"),
        Index("idx_payment_created_at", "created_at"),
    )


# ==================== Audit Models ====================


class AdminLog(Base):
    """Admin action log model."""

    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    admin_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(100), index=True)
    target_type: Mapped[Optional[str]] = mapped_column(String(50))
    target_id: Mapped[Optional[int]] = mapped_column(Integer)
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    admin: Mapped["User"] = relationship("User", back_populates="admin_logs")

    __table_args__ = (
        Index("idx_admin_log_admin_id", "admin_id"),
        Index("idx_admin_log_action", "action"),
        Index("idx_admin_log_created_at", "created_at"),
    )


class PaymentLog(Base):
    """Payment processing log model."""

    __tablename__ = "payment_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    payment_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("payments.id", ondelete="SET NULL"))
    method: Mapped[str] = mapped_column(String(50), index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50))
    amount: Mapped[Optional[float]] = mapped_column(Float)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_payment_log_method", "method"),
        Index("idx_payment_log_event_type", "event_type"),
        Index("idx_payment_log_created_at", "created_at"),
    )
