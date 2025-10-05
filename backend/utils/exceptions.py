"""
Custom exception classes for Mock Web3 Wallet application.

This module defines domain-specific exceptions that provide clear error
messages and error codes for consistent error handling across the application.
"""


class WalletException(Exception):
    """Base exception for all wallet-related errors."""
    
    def __init__(self, message: str, error_code: str = "WALLET_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


# ============================================================================
# Authentication Exceptions
# ============================================================================

class AuthenticationError(WalletException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class InvalidPasswordError(AuthenticationError):
    """Raised when password is incorrect."""
    
    def __init__(self, message: str = "Invalid password"):
        super().__init__(message)
        self.error_code = "INVALID_PASSWORD"


class WalletLockedError(AuthenticationError):
    """Raised when attempting to access a locked wallet."""
    
    def __init__(self, message: str = "Wallet is locked"):
        super().__init__(message)
        self.error_code = "WALLET_LOCKED"


class SessionExpiredError(AuthenticationError):
    """Raised when user session has expired."""
    
    def __init__(self, message: str = "Session has expired"):
        super().__init__(message)
        self.error_code = "SESSION_EXPIRED"


class UnauthorizedError(AuthenticationError):
    """Raised when user is not authorized to perform an action."""
    
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message)
        self.error_code = "UNAUTHORIZED"


# ============================================================================
# Validation Exceptions
# ============================================================================

class ValidationError(WalletException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, "VALIDATION_ERROR")


class InvalidAddressError(ValidationError):
    """Raised when an Ethereum address is invalid."""
    
    def __init__(self, message: str = "Invalid Ethereum address format"):
        super().__init__(message)
        self.error_code = "INVALID_ADDRESS"


class InvalidAmountError(ValidationError):
    """Raised when transaction amount is invalid."""
    
    def __init__(self, message: str = "Invalid transaction amount"):
        super().__init__(message)
        self.error_code = "INVALID_AMOUNT"


class InvalidMnemonicError(ValidationError):
    """Raised when mnemonic phrase is invalid."""
    
    def __init__(self, message: str = "Invalid mnemonic phrase"):
        super().__init__(message)
        self.error_code = "INVALID_MNEMONIC"


class InsufficientBalanceError(ValidationError):
    """Raised when account has insufficient balance for transaction."""
    
    def __init__(self, message: str = "Insufficient balance", available: float = None, required: float = None):
        if available is not None and required is not None:
            message = f"Insufficient balance. Available: {available} ETH, Required: {required} ETH"
        super().__init__(message)
        self.error_code = "INSUFFICIENT_BALANCE"
        self.available = available
        self.required = required


class InvalidPhoneNumberError(ValidationError):
    """Raised when phone number format is invalid."""
    
    def __init__(self, message: str = "Invalid phone number format. Expected: +[country_code][number]"):
        super().__init__(message)
        self.error_code = "INVALID_PHONE_NUMBER"


# ============================================================================
# Transaction Exceptions
# ============================================================================

class TransactionError(WalletException):
    """Base exception for transaction-related errors."""
    
    def __init__(self, message: str = "Transaction failed"):
        super().__init__(message, "TRANSACTION_ERROR")


class ApprovalExpiredError(TransactionError):
    """Raised when transaction approval message has expired."""
    
    def __init__(self, message: str = "Transaction approval has expired"):
        super().__init__(message)
        self.error_code = "APPROVAL_EXPIRED"


class InvalidSignatureError(TransactionError):
    """Raised when transaction signature is invalid."""
    
    def __init__(self, message: str = "Invalid transaction signature"):
        super().__init__(message)
        self.error_code = "INVALID_SIGNATURE"


class PriceToleranceExceededError(TransactionError):
    """Raised when price change exceeds tolerance threshold."""
    
    def __init__(self, message: str = "Price change exceeds tolerance threshold", 
                 original_price: float = None, new_price: float = None, tolerance: float = 1.0):
        if original_price is not None and new_price is not None:
            change_percent = abs((new_price - original_price) / original_price * 100)
            message = f"Price changed by {change_percent:.2f}% (tolerance: {tolerance}%). Original: {original_price} ETH, New: {new_price} ETH"
        super().__init__(message)
        self.error_code = "PRICE_TOLERANCE_EXCEEDED"
        self.original_price = original_price
        self.new_price = new_price
        self.tolerance = tolerance


class ApprovalNotFoundError(TransactionError):
    """Raised when approval message is not found."""
    
    def __init__(self, message: str = "Transaction approval not found or already used"):
        super().__init__(message)
        self.error_code = "APPROVAL_NOT_FOUND"


class TransactionFailedError(TransactionError):
    """Raised when transaction execution fails."""
    
    def __init__(self, message: str = "Transaction execution failed"):
        super().__init__(message)
        self.error_code = "TRANSACTION_FAILED"


# ============================================================================
# Resource Exceptions
# ============================================================================

class ResourceNotFoundError(WalletException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str = None):
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} with ID '{resource_id}' not found"
        super().__init__(message, "RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


class WalletNotFoundError(ResourceNotFoundError):
    """Raised when wallet is not found."""
    
    def __init__(self, wallet_id: str = None):
        super().__init__("Wallet", wallet_id)
        self.error_code = "WALLET_NOT_FOUND"


class AccountNotFoundError(ResourceNotFoundError):
    """Raised when account is not found."""
    
    def __init__(self, account_id: str = None):
        super().__init__("Account", account_id)
        self.error_code = "ACCOUNT_NOT_FOUND"


class TransactionNotFoundError(ResourceNotFoundError):
    """Raised when transaction is not found."""
    
    def __init__(self, transaction_id: str = None):
        super().__init__("Transaction", transaction_id)
        self.error_code = "TRANSACTION_NOT_FOUND"


# ============================================================================
# Database Exceptions
# ============================================================================

class DatabaseError(WalletException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, "DATABASE_ERROR")


class DatabaseConnectionError(DatabaseError):
    """Raised when database connection fails."""
    
    def __init__(self, message: str = "Failed to connect to database"):
        super().__init__(message)
        self.error_code = "DATABASE_CONNECTION_ERROR"


class DatabaseConstraintError(DatabaseError):
    """Raised when database constraint is violated."""
    
    def __init__(self, message: str = "Database constraint violation"):
        super().__init__(message)
        self.error_code = "DATABASE_CONSTRAINT_ERROR"


class DuplicateResourceError(DatabaseError):
    """Raised when attempting to create a duplicate resource."""
    
    def __init__(self, resource_type: str, message: str = None):
        if not message:
            message = f"{resource_type} already exists"
        super().__init__(message)
        self.error_code = "DUPLICATE_RESOURCE"
        self.resource_type = resource_type


# ============================================================================
# Cryptographic Exceptions
# ============================================================================

class CryptoError(WalletException):
    """Raised when cryptographic operations fail."""
    
    def __init__(self, message: str = "Cryptographic operation failed"):
        super().__init__(message, "CRYPTO_ERROR")


class DecryptionError(CryptoError):
    """Raised when decryption fails."""
    
    def __init__(self, message: str = "Failed to decrypt data"):
        super().__init__(message)
        self.error_code = "DECRYPTION_ERROR"


class EncryptionError(CryptoError):
    """Raised when encryption fails."""
    
    def __init__(self, message: str = "Failed to encrypt data"):
        super().__init__(message)
        self.error_code = "ENCRYPTION_ERROR"


class KeyDerivationError(CryptoError):
    """Raised when key derivation fails."""
    
    def __init__(self, message: str = "Failed to derive key"):
        super().__init__(message)
        self.error_code = "KEY_DERIVATION_ERROR"


# ============================================================================
# External Service Exceptions
# ============================================================================

class ExternalServiceError(WalletException):
    """Raised when external service calls fail."""
    
    def __init__(self, service_name: str, message: str = None):
        if not message:
            message = f"{service_name} service error"
        super().__init__(message, "EXTERNAL_SERVICE_ERROR")
        self.service_name = service_name


class SkipAPIError(ExternalServiceError):
    """Raised when Skip API calls fail."""
    
    def __init__(self, message: str = "Skip API request failed"):
        super().__init__("Skip API", message)
        self.error_code = "SKIP_API_ERROR"


class NotificationError(ExternalServiceError):
    """Raised when notification delivery fails."""
    
    def __init__(self, message: str = "Failed to send notification"):
        super().__init__("Notification Service", message)
        self.error_code = "NOTIFICATION_ERROR"
