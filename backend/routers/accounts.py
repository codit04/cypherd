"""
Accounts Router - API endpoints for account operations.

Handles account creation, retrieval, label updates, and balance queries.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from backend.models.schemas import (
    AccountCreateRequest,
    AccountResponse,
    AccountUpdateLabelRequest,
    AccountBalanceResponse,
    WalletBalanceResponse
)
from backend.services.account_service import AccountService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
account_service = AccountService()


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(request: AccountCreateRequest):
    """
    Create a new account for a wallet using HD derivation.
    
    This endpoint:
    - Derives a new account from the wallet's seed
    - Uses the next available account index
    - Creates the account with zero initial balance
    - Returns account details including address
    """
    try:
        result = account_service.create_account(
            request.wallet_id,
            request.password,
            request.label
        )
        logger.info(f"Account created: {result['id']} for wallet {request.wallet_id}")
        
        # Convert balance to string for response
        result['balance'] = str(result['balance'])
        
        return AccountResponse(**result)
    except ValueError as e:
        logger.warning(f"Account creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Account creation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account"
        )


@router.get("/{account_id}", response_model=AccountResponse, status_code=status.HTTP_200_OK)
async def get_account(account_id: str):
    """
    Retrieve an account by its ID.
    
    Returns account details including:
    - Account ID
    - Wallet ID
    - Ethereum address
    - Account index
    - Label
    - Balance
    - Timestamps
    """
    try:
        result = account_service.get_account(account_id)
        
        # Convert balance to string for response
        result['balance'] = str(result['balance'])
        
        return AccountResponse(**result)
    except ValueError as e:
        logger.warning(f"Get account failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get account error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account"
        )


@router.get("/address/{address}", response_model=AccountResponse, status_code=status.HTTP_200_OK)
async def get_account_by_address(address: str):
    """
    Retrieve an account by its Ethereum address.
    
    Returns account details for the specified address.
    """
    try:
        result = account_service.get_account_by_address(address)
        
        # Convert balance to string for response
        result['balance'] = str(result['balance'])
        
        return AccountResponse(**result)
    except ValueError as e:
        logger.warning(f"Get account by address failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get account by address error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account"
        )


@router.get("/wallet/{wallet_id}", response_model=List[AccountResponse], status_code=status.HTTP_200_OK)
async def list_accounts(wallet_id: str):
    """
    Get all accounts for a specific wallet.
    
    Returns a list of all accounts ordered by account index.
    """
    try:
        results = account_service.list_accounts(wallet_id)
        
        # Convert balances to strings for response
        for result in results:
            result['balance'] = str(result['balance'])
        
        return [AccountResponse(**result) for result in results]
    except ValueError as e:
        logger.warning(f"List accounts failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"List accounts error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve accounts"
        )


@router.put("/{account_id}/label", status_code=status.HTTP_200_OK)
async def update_account_label(account_id: str, request: AccountUpdateLabelRequest):
    """
    Update the label of an account.
    
    Allows users to set custom labels for their accounts.
    """
    try:
        success = account_service.update_account_label(account_id, request.label)
        
        if success:
            logger.info(f"Account label updated: {account_id}")
            return {"message": "Account label updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update account label"
            )
    except ValueError as e:
        logger.warning(f"Update account label failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Update account label error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update account label"
        )


@router.get("/{account_id}/balance", response_model=AccountBalanceResponse, status_code=status.HTTP_200_OK)
async def get_account_balance(account_id: str):
    """
    Get the balance of a specific account.
    
    Returns the current balance in ETH.
    """
    try:
        balance = account_service.get_account_balance(account_id)
        
        return AccountBalanceResponse(
            account_id=account_id,
            balance=str(balance)
        )
    except ValueError as e:
        logger.warning(f"Get account balance failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get account balance error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account balance"
        )


@router.get("/wallet/{wallet_id}/balance", response_model=WalletBalanceResponse, status_code=status.HTTP_200_OK)
async def get_total_balance(wallet_id: str):
    """
    Calculate the total balance across all accounts in a wallet.
    
    Returns the sum of all account balances.
    """
    try:
        total_balance = account_service.get_total_balance(wallet_id)
        accounts = account_service.list_accounts(wallet_id)
        
        return WalletBalanceResponse(
            wallet_id=wallet_id,
            total_balance=str(total_balance),
            account_count=len(accounts)
        )
    except ValueError as e:
        logger.warning(f"Get total balance failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Get total balance error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve total balance"
        )
