"""
Wallet Router - API endpoints for wallet operations.

Handles wallet creation, restoration, authentication, locking, and password management.
"""

from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import (
    WalletCreateRequest,
    WalletCreateResponse,
    WalletRestoreRequest,
    WalletRestoreResponse,
    WalletAuthRequest,
    WalletAuthResponse,
    WalletLockRequest,
    WalletUnlockRequest,
    WalletChangePasswordRequest,
    WalletInfoResponse
)
from backend.services.wallet_service import WalletService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
wallet_service = WalletService()


@router.post("/create", response_model=WalletCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(request: WalletCreateRequest):
    """
    Create a new wallet with a generated mnemonic.
    
    This endpoint:
    - Generates a 12-word BIP39 mnemonic
    - Creates a wallet with deterministic UUID
    - Creates the first account with random balance (1.0-10.0 ETH)
    - Returns wallet ID and mnemonic (user must save the mnemonic!)
    """
    try:
        result = wallet_service.create_wallet(request.password)
        logger.info(f"Wallet created successfully: {result['wallet_id']}")
        return WalletCreateResponse(**result)
    except ValueError as e:
        logger.warning(f"Wallet creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Wallet creation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create wallet"
        )


@router.post("/restore", response_model=WalletRestoreResponse, status_code=status.HTTP_200_OK)
async def restore_wallet(request: WalletRestoreRequest):
    """
    Restore a wallet from an existing mnemonic.
    
    This endpoint:
    - Validates the mnemonic phrase
    - Derives wallet UUID from mnemonic
    - If wallet exists, verifies password and returns existing accounts
    - If wallet doesn't exist, creates new wallet entry
    """
    try:
        result = wallet_service.restore_wallet(request.mnemonic, request.password)
        logger.info(f"Wallet restored: {result['wallet_id']}, exists: {result['exists']}")
        return WalletRestoreResponse(**result)
    except ValueError as e:
        logger.warning(f"Wallet restoration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Wallet restoration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restore wallet"
        )


@router.post("/authenticate", response_model=WalletAuthResponse, status_code=status.HTTP_200_OK)
async def authenticate_wallet(request: WalletAuthRequest):
    """
    Authenticate a user with their wallet password.
    
    This endpoint:
    - Verifies the password against stored hash
    - Unlocks the wallet if authentication successful
    - Updates last accessed timestamp
    """
    try:
        success = wallet_service.authenticate(request.wallet_id, request.password)
        
        if success:
            logger.info(f"Wallet authenticated successfully: {request.wallet_id}")
            return WalletAuthResponse(
                success=True,
                message="Authentication successful"
            )
        else:
            logger.warning(f"Authentication failed for wallet: {request.wallet_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
    except ValueError as e:
        logger.warning(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/lock", status_code=status.HTTP_200_OK)
async def lock_wallet(request: WalletLockRequest):
    """
    Lock a wallet to require authentication for future access.
    
    This endpoint:
    - Sets wallet to locked state
    - Requires authentication to unlock
    """
    try:
        wallet_service.lock_wallet(request.wallet_id)
        logger.info(f"Wallet locked: {request.wallet_id}")
        return {"message": "Wallet locked successfully"}
    except ValueError as e:
        logger.warning(f"Lock wallet failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Lock wallet error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to lock wallet"
        )


@router.post("/unlock", response_model=WalletAuthResponse, status_code=status.HTTP_200_OK)
async def unlock_wallet(request: WalletUnlockRequest):
    """
    Unlock a wallet with password verification.
    
    This endpoint:
    - Verifies the password
    - Unlocks the wallet if password correct
    """
    try:
        success = wallet_service.unlock_wallet(request.wallet_id, request.password)
        
        if success:
            logger.info(f"Wallet unlocked successfully: {request.wallet_id}")
            return WalletAuthResponse(
                success=True,
                message="Wallet unlocked successfully"
            )
        else:
            logger.warning(f"Unlock failed for wallet: {request.wallet_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
    except ValueError as e:
        logger.warning(f"Unlock wallet error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unlock wallet error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlock wallet"
        )


@router.get("/{wallet_id}", response_model=WalletInfoResponse, status_code=status.HTTP_200_OK)
async def get_wallet_info(wallet_id: str):
    """
    Get wallet information (without sensitive data).
    
    Returns:
    - Wallet ID
    - Creation timestamp
    - Last accessed timestamp
    - Lock status
    - Number of accounts
    """
    try:
        info = wallet_service.get_wallet_info(wallet_id)
        return WalletInfoResponse(**info)
    except ValueError as e:
        logger.warning(f"Get wallet info failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get wallet info error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve wallet information"
        )


@router.put("/{wallet_id}/password", status_code=status.HTTP_200_OK)
async def change_password(wallet_id: str, request: WalletChangePasswordRequest):
    """
    Change the wallet password.
    
    This endpoint:
    - Verifies the old password
    - Decrypts and re-encrypts the seed with new password
    - Updates the password hash
    """
    # Ensure wallet_id in path matches request body
    if wallet_id != request.wallet_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wallet ID mismatch"
        )
    
    try:
        success = wallet_service.change_password(
            request.wallet_id,
            request.old_password,
            request.new_password
        )
        
        if success:
            logger.info(f"Password changed successfully for wallet: {wallet_id}")
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to change password"
            )
    except ValueError as e:
        logger.warning(f"Change password failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Change password error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )
