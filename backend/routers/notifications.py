"""
Notifications Router - API endpoints for notification operations.

Handles notification preferences management and test notifications.
"""

from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import (
    NotificationPreferencesRequest,
    NotificationPreferencesResponse,
    NotificationTestRequest,
    NotificationTestResponse
)
from backend.services.notification_service import NotificationService
from backend.repositories.notification_preferences_repository import NotificationPreferencesRepository
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
notification_service = NotificationService()
preferences_repo = NotificationPreferencesRepository()


@router.post("/preferences", response_model=NotificationPreferencesResponse, status_code=status.HTTP_201_CREATED)
async def set_notification_preferences(request: NotificationPreferencesRequest):
    """
    Set or update notification preferences for a wallet.
    
    This endpoint:
    - Validates phone number format if provided
    - Creates or updates notification preferences
    - Returns the updated preferences
    
    Phone number format: +[country_code][number]
    Example: +1234567890, +919876543210
    """
    try:
        # Validate phone number if provided and enabled
        if request.enabled and request.phone_number:
            if not notification_service.validate_phone_number(request.phone_number):
                raise ValueError(
                    "Invalid phone number format. "
                    "Expected format: +[country_code][number] (e.g., +1234567890)"
                )
        
        # Check if preferences already exist
        existing_prefs = preferences_repo.get_by_wallet_id(request.wallet_id)
        
        preferences_data = {
            'wallet_id': request.wallet_id,
            'phone_number': request.phone_number,
            'enabled': request.enabled,
            'notify_incoming': request.notify_incoming,
            'notify_outgoing': request.notify_outgoing,
            'notify_security': request.notify_security
        }
        
        if existing_prefs:
            # Update existing preferences
            success = preferences_repo.update(request.wallet_id, preferences_data)
            
            if not success:
                raise Exception("Failed to update notification preferences")
            
            # Get updated preferences
            updated_prefs = preferences_repo.get_by_wallet_id(request.wallet_id)
            
            logger.info(f"Notification preferences updated for wallet: {request.wallet_id}")
            
            return NotificationPreferencesResponse(**updated_prefs)
        else:
            # Create new preferences
            prefs_id = preferences_repo.create(preferences_data)
            
            # Get created preferences
            created_prefs = preferences_repo.get_by_wallet_id(request.wallet_id)
            
            logger.info(f"Notification preferences created for wallet: {request.wallet_id}")
            
            return NotificationPreferencesResponse(**created_prefs)
            
    except ValueError as e:
        logger.warning(f"Set notification preferences failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Set notification preferences error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set notification preferences"
        )


@router.get("/preferences/{wallet_id}", response_model=NotificationPreferencesResponse, status_code=status.HTTP_200_OK)
async def get_notification_preferences(wallet_id: str):
    """
    Get notification preferences for a wallet.
    
    Returns the current notification preferences or default values if not set.
    """
    try:
        preferences = preferences_repo.get_by_wallet_id(wallet_id)
        
        if not preferences:
            # Return default preferences if not set
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification preferences not found for this wallet"
            )
        
        return NotificationPreferencesResponse(**preferences)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get notification preferences error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve notification preferences"
        )


@router.post("/test", response_model=NotificationTestResponse, status_code=status.HTTP_200_OK)
async def test_notification(request: NotificationTestRequest):
    """
    Send a test notification to verify WhatsApp integration.
    
    This endpoint:
    - Validates phone number format
    - Sends a test WhatsApp message
    - Returns success/failure status
    
    Note: This requires WhatsApp Web to be accessible and may open a browser tab.
    """
    try:
        # Validate phone number
        if not notification_service.validate_phone_number(request.phone_number):
            raise ValueError(
                "Invalid phone number format. "
                "Expected format: +[country_code][number] (e.g., +1234567890)"
            )
        
        # Send test notification
        success = notification_service.send_test_notification(request.phone_number)
        
        if success:
            logger.info(f"Test notification sent successfully to {request.phone_number}")
            return NotificationTestResponse(
                success=True,
                message="Test notification sent successfully"
            )
        else:
            logger.warning(f"Test notification failed for {request.phone_number}")
            return NotificationTestResponse(
                success=False,
                message="Failed to send test notification. Please check your phone number and try again."
            )
            
    except ValueError as e:
        logger.warning(f"Test notification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Test notification error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test notification"
        )


@router.delete("/preferences/{wallet_id}", status_code=status.HTTP_200_OK)
async def delete_notification_preferences(wallet_id: str):
    """
    Delete notification preferences for a wallet.
    
    This will disable all notifications for the wallet.
    """
    try:
        success = preferences_repo.delete(wallet_id)
        
        if success:
            logger.info(f"Notification preferences deleted for wallet: {wallet_id}")
            return {"message": "Notification preferences deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification preferences not found for this wallet"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete notification preferences error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification preferences"
        )
