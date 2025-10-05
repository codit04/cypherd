"""
FastAPI Backend Application for Mock Web3 Wallet.

This module initializes the FastAPI application, configures CORS middleware,
registers routers, and sets up exception handlers.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Import routers
from backend.routers import wallet, accounts, transactions, notifications

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Mock Web3 Wallet API",
    description="REST API for Mock Web3 Wallet application",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import custom exceptions
from backend.utils.exceptions import (
    WalletException,
    AuthenticationError,
    InvalidPasswordError,
    WalletLockedError,
    SessionExpiredError,
    UnauthorizedError,
    ValidationError,
    InvalidAddressError,
    InvalidAmountError,
    InvalidMnemonicError,
    InsufficientBalanceError,
    InvalidPhoneNumberError,
    TransactionError,
    ApprovalExpiredError,
    InvalidSignatureError,
    PriceToleranceExceededError,
    ApprovalNotFoundError,
    TransactionFailedError,
    ResourceNotFoundError,
    WalletNotFoundError,
    AccountNotFoundError,
    TransactionNotFoundError,
    DatabaseError,
    DatabaseConnectionError,
    DatabaseConstraintError,
    DuplicateResourceError,
    CryptoError,
    DecryptionError,
    EncryptionError,
    KeyDerivationError,
    ExternalServiceError,
    SkipAPIError,
    NotificationError
)


# ============================================================================
# Exception Handlers
# ============================================================================

@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors with 401 Unauthorized."""
    logger.warning(f"Authentication error: {exc.message} (Code: {exc.error_code})")
    return JSONResponse(
        status_code=401,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "status_code": 401
        }
    )


@app.exception_handler(UnauthorizedError)
async def unauthorized_error_handler(request: Request, exc: UnauthorizedError):
    """Handle unauthorized access with 403 Forbidden."""
    logger.warning(f"Unauthorized access: {exc.message} (Code: {exc.error_code})")
    return JSONResponse(
        status_code=403,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "status_code": 403
        }
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle validation errors with 400 Bad Request."""
    logger.warning(f"Validation error: {exc.message} (Code: {exc.error_code})")
    
    # Build response content
    content = {
        "detail": exc.message,
        "error_code": exc.error_code,
        "status_code": 400
    }
    
    # Add additional context for InsufficientBalanceError
    if isinstance(exc, InsufficientBalanceError):
        if exc.available is not None:
            content["available_balance"] = exc.available
        if exc.required is not None:
            content["required_amount"] = exc.required
    
    return JSONResponse(status_code=400, content=content)


@app.exception_handler(InsufficientBalanceError)
async def insufficient_balance_error_handler(request: Request, exc: InsufficientBalanceError):
    """Handle insufficient balance errors with 400 Bad Request."""
    logger.warning(f"Insufficient balance: {exc.message} (Code: {exc.error_code})")
    
    content = {
        "detail": exc.message,
        "error_code": exc.error_code,
        "status_code": 400
    }
    
    if exc.available is not None:
        content["available_balance"] = exc.available
    if exc.required is not None:
        content["required_amount"] = exc.required
    
    return JSONResponse(status_code=400, content=content)


@app.exception_handler(TransactionError)
async def transaction_error_handler(request: Request, exc: TransactionError):
    """Handle transaction errors with 400 Bad Request."""
    logger.warning(f"Transaction error: {exc.message} (Code: {exc.error_code})")
    
    content = {
        "detail": exc.message,
        "error_code": exc.error_code,
        "status_code": 400
    }
    
    # Add additional context for PriceToleranceExceededError
    if isinstance(exc, PriceToleranceExceededError):
        if exc.original_price is not None:
            content["original_price"] = exc.original_price
        if exc.new_price is not None:
            content["new_price"] = exc.new_price
        if exc.tolerance is not None:
            content["tolerance_percent"] = exc.tolerance
    
    return JSONResponse(status_code=400, content=content)


@app.exception_handler(ResourceNotFoundError)
async def resource_not_found_handler(request: Request, exc: ResourceNotFoundError):
    """Handle resource not found errors with 404 Not Found."""
    logger.info(f"Resource not found: {exc.message} (Code: {exc.error_code})")
    
    content = {
        "detail": exc.message,
        "error_code": exc.error_code,
        "status_code": 404
    }
    
    if exc.resource_type:
        content["resource_type"] = exc.resource_type
    if exc.resource_id:
        content["resource_id"] = exc.resource_id
    
    return JSONResponse(status_code=404, content=content)


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    """Handle database errors with 500 Internal Server Error."""
    logger.error(f"Database error: {exc.message} (Code: {exc.error_code})", exc_info=True)
    
    # For duplicate resource errors, return 409 Conflict
    if isinstance(exc, DuplicateResourceError):
        return JSONResponse(
            status_code=409,
            content={
                "detail": exc.message,
                "error_code": exc.error_code,
                "status_code": 409,
                "resource_type": exc.resource_type
            }
        )
    
    # For other database errors, return 500
    return JSONResponse(
        status_code=500,
        content={
            "detail": "A database error occurred",
            "error_code": exc.error_code,
            "status_code": 500
        }
    )


@app.exception_handler(CryptoError)
async def crypto_error_handler(request: Request, exc: CryptoError):
    """Handle cryptographic errors with 500 Internal Server Error."""
    logger.error(f"Cryptographic error: {exc.message} (Code: {exc.error_code})", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "A cryptographic operation failed",
            "error_code": exc.error_code,
            "status_code": 500
        }
    )


@app.exception_handler(ExternalServiceError)
async def external_service_error_handler(request: Request, exc: ExternalServiceError):
    """Handle external service errors with 503 Service Unavailable."""
    logger.error(f"External service error: {exc.message} (Code: {exc.error_code})")
    
    # For notification errors, return 500 (non-critical)
    if isinstance(exc, NotificationError):
        return JSONResponse(
            status_code=500,
            content={
                "detail": exc.message,
                "error_code": exc.error_code,
                "status_code": 500,
                "service": exc.service_name
            }
        )
    
    # For other external services (like Skip API), return 503
    return JSONResponse(
        status_code=503,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "status_code": 503,
            "service": exc.service_name
        }
    )


@app.exception_handler(WalletException)
async def wallet_exception_handler(request: Request, exc: WalletException):
    """Handle generic wallet exceptions with 400 Bad Request."""
    logger.warning(f"Wallet exception: {exc.message} (Code: {exc.error_code})")
    return JSONResponse(
        status_code=400,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "status_code": 400
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions with 400 Bad Request."""
    logger.warning(f"ValueError: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
            "error_code": "VALIDATION_ERROR",
            "status_code": 400
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with 500 Internal Server Error."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "error_code": "INTERNAL_ERROR",
            "status_code": 500
        }
    )


# ============================================================================
# Register Routers
# ============================================================================

app.include_router(
    wallet.router,
    prefix="/api/wallet",
    tags=["Wallet"]
)

app.include_router(
    accounts.router,
    prefix="/api/accounts",
    tags=["Accounts"]
)

app.include_router(
    transactions.router,
    prefix="/api/transactions",
    tags=["Transactions"]
)

app.include_router(
    notifications.router,
    prefix="/api/notifications",
    tags=["Notifications"]
)


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint for health check."""
    return {
        "status": "ok",
        "message": "Mock Web3 Wallet API is running",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "mock-web3-wallet-api"
    }


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Execute on application startup."""
    logger.info("Mock Web3 Wallet API starting up...")
    logger.info("API documentation available at /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Execute on application shutdown."""
    logger.info("Mock Web3 Wallet API shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
