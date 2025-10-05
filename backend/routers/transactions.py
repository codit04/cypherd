"""
Transactions Router - API endpoints for transaction operations.

Handles transaction approval creation, signature verification, execution, and history retrieval.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.models.schemas import (
    TransactionApprovalRequest,
    TransactionApprovalResponse,
    TransactionSendRequest,
    TransactionResponse
)
from backend.services.transaction_service import TransactionService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
transaction_service = TransactionService()


@router.post("/create-approval", response_model=TransactionApprovalResponse, status_code=status.HTTP_201_CREATED)
async def create_approval(request: TransactionApprovalRequest):
    """
    Create an approval message for a transaction with 30-second expiration.
    
    This endpoint:
    - Validates sender account and recipient address
    - Handles ETH or USD amount (converts USD to ETH via Skip API)
    - Generates approval message for user to sign
    - Returns message details with expiration timestamp
    
    The user must sign this message and submit it via the /send endpoint.
    """
    try:
        result = transaction_service.create_approval_message(
            from_account_id=request.from_account_id,
            to_address=request.to_address,
            amount_eth=request.amount_eth,
            amount_usd=request.amount_usd,
            memo=request.memo
        )
        
        logger.info(
            f"Approval created: {result['message_id']} for "
            f"{result['eth_amount']} ETH transfer"
        )
        
        return TransactionApprovalResponse(**result)
    except ValueError as e:
        logger.warning(f"Create approval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Create approval error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transaction approval"
        )


@router.post("/send", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def send_transaction(request: TransactionSendRequest):
    """
    Execute a transaction with signature verification.
    
    This endpoint:
    - Retrieves pending approval from cache
    - Verifies signature matches sender address
    - Checks if approval has expired
    - For USD transfers, verifies price tolerance (1%)
    - Validates sender has sufficient balance
    - Executes atomic balance updates
    - Records transaction in database
    - Returns transaction details
    
    Raises:
    - 400: Invalid signature, expired approval, insufficient balance, price tolerance exceeded
    - 404: Approval not found
    - 500: Transaction execution failed
    """
    try:
        result = transaction_service.send_transaction(
            message_id=request.message_id,
            signature=request.signature
        )
        
        logger.info(
            f"Transaction completed: {result['transaction_id']} - "
            f"{result['amount']} ETH from {result['from_address']} to {result['to_address']}"
        )
        
        return TransactionResponse(**result)
    except ValueError as e:
        logger.warning(f"Send transaction failed: {str(e)}")
        
        # Determine appropriate status code based on error message
        if "not found" in str(e).lower():
            status_code = status.HTTP_404_NOT_FOUND
        else:
            status_code = status.HTTP_400_BAD_REQUEST
        
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Send transaction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute transaction"
        )


@router.get("/{transaction_id}", response_model=TransactionResponse, status_code=status.HTTP_200_OK)
async def get_transaction(transaction_id: str):
    """
    Retrieve a transaction by its ID.
    
    Returns complete transaction details including:
    - Transaction ID
    - From/to addresses
    - Amount
    - Memo
    - Transaction type (send/receive/internal)
    - Status
    - Timestamp
    """
    try:
        result = transaction_service.get_transaction(transaction_id)
        
        return TransactionResponse(**result)
    except ValueError as e:
        logger.warning(f"Get transaction failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get transaction error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transaction"
        )


@router.get("/account/{account_id}", response_model=List[TransactionResponse], status_code=status.HTTP_200_OK)
async def get_account_transactions(account_id: str, limit: int = 50):
    """
    Retrieve all transactions for a specific account.
    
    Returns a list of transactions ordered by timestamp (most recent first).
    
    Query Parameters:
    - limit: Maximum number of transactions to return (default: 50, max: 100)
    """
    # Validate limit
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 100"
        )
    
    try:
        results = transaction_service.get_account_transactions(account_id, limit)
        
        return [TransactionResponse(**result) for result in results]
    except ValueError as e:
        logger.warning(f"Get account transactions failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get account transactions error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve transactions"
        )


@router.delete("/cleanup-expired", status_code=status.HTTP_200_OK)
async def cleanup_expired_approvals():
    """
    Clean up expired approval messages from cache.
    
    This is a maintenance endpoint that can be called periodically
    to prevent memory leaks from expired approvals.
    
    Returns the number of expired approvals removed.
    """
    try:
        count = transaction_service.cleanup_expired_approvals()
        
        logger.info(f"Cleaned up {count} expired approval messages")
        
        return {
            "message": f"Cleaned up {count} expired approval messages",
            "count": count
        }
    except Exception as e:
        logger.error(f"Cleanup expired approvals error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup expired approvals"
        )
