"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============================================================================
# Wallet Models
# ============================================================================

class WalletCreateRequest(BaseModel):
    """Request model for creating a new wallet."""
    password: str = Field(..., min_length=8, description="Wallet password (min 8 characters)")


class WalletCreateResponse(BaseModel):
    """Response model for wallet creation."""
    wallet_id: str
    mnemonic: str
    first_account: dict


class WalletRestoreRequest(BaseModel):
    """Request model for restoring a wallet from mnemonic."""
    mnemonic: str = Field(..., description="12-word BIP39 mnemonic phrase")
    password: str = Field(..., min_length=8, description="Wallet password (min 8 characters)")


class WalletRestoreResponse(BaseModel):
    """Response model for wallet restoration."""
    wallet_id: str
    exists: bool
    accounts: List[dict]


class WalletAuthRequest(BaseModel):
    """Request model for wallet authentication."""
    wallet_id: str
    password: str


class WalletAuthResponse(BaseModel):
    """Response model for wallet authentication."""
    success: bool
    message: str


class WalletLockRequest(BaseModel):
    """Request model for locking a wallet."""
    wallet_id: str


class WalletUnlockRequest(BaseModel):
    """Request model for unlocking a wallet."""
    wallet_id: str
    password: str


class WalletChangePasswordRequest(BaseModel):
    """Request model for changing wallet password."""
    wallet_id: str
    old_password: str
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class WalletInfoResponse(BaseModel):
    """Response model for wallet information."""
    wallet_id: str
    created_at: datetime
    last_accessed: Optional[datetime]
    is_locked: bool
    account_count: int


# ============================================================================
# Account Models
# ============================================================================

class AccountCreateRequest(BaseModel):
    """Request model for creating a new account."""
    wallet_id: str
    password: str
    label: Optional[str] = None


class AccountResponse(BaseModel):
    """Response model for account information."""
    id: str
    wallet_id: str
    address: str
    account_index: int
    label: Optional[str]
    balance: str  # String representation of Decimal
    created_at: datetime
    updated_at: datetime
    private_key: Optional[str] = None  # Only included on account creation for testing


class AccountUpdateLabelRequest(BaseModel):
    """Request model for updating account label."""
    label: str = Field(..., min_length=1, description="New account label")


class AccountBalanceResponse(BaseModel):
    """Response model for account balance."""
    account_id: str
    balance: str  # String representation of Decimal


class WalletBalanceResponse(BaseModel):
    """Response model for total wallet balance."""
    wallet_id: str
    total_balance: str  # String representation of Decimal
    account_count: int


# ============================================================================
# Transaction Models
# ============================================================================

class TransactionApprovalRequest(BaseModel):
    """Request model for creating transaction approval."""
    from_account_id: str
    to_address: str
    amount_eth: Optional[Decimal] = None
    amount_usd: Optional[Decimal] = None
    memo: Optional[str] = None
    
    @validator('amount_eth', 'amount_usd')
    def validate_positive(cls, v):
        """Validate that amounts are positive if provided."""
        if v is not None and v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v


class TransactionApprovalResponse(BaseModel):
    """Response model for transaction approval."""
    message: str
    message_id: str
    expires_at: str  # ISO format datetime string
    eth_amount: str
    usd_amount: Optional[str]


class TransactionSendRequest(BaseModel):
    """Request model for sending a transaction with signature."""
    message_id: str
    signature: str = Field(..., description="Signed approval message in hex format")


class TransactionResponse(BaseModel):
    """Response model for transaction details."""
    transaction_id: str
    from_address: str
    to_address: str
    amount: str  # String representation of Decimal
    memo: Optional[str]
    transaction_type: str
    status: str
    created_at: str  # ISO format datetime string


# ============================================================================
# Notification Models
# ============================================================================

class NotificationPreferencesRequest(BaseModel):
    """Request model for setting notification preferences."""
    wallet_id: str
    phone_number: Optional[str] = None
    enabled: bool = False
    notify_incoming: bool = True
    notify_outgoing: bool = True
    notify_security: bool = True


class NotificationPreferencesResponse(BaseModel):
    """Response model for notification preferences."""
    id: str
    wallet_id: str
    phone_number: Optional[str]
    enabled: bool
    notify_incoming: bool
    notify_outgoing: bool
    notify_security: bool
    created_at: datetime
    updated_at: datetime


class NotificationTestRequest(BaseModel):
    """Request model for testing notifications."""
    phone_number: str = Field(..., description="Phone number in format +[country_code][number]")


class NotificationTestResponse(BaseModel):
    """Response model for notification test."""
    success: bool
    message: str


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str
    error_code: Optional[str] = None
    status_code: int
