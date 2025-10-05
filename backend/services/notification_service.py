"""
Notification Service - Business logic for notification operations.

Handles WhatsApp notifications for transactions and security alerts.
"""

import re
import logging
from typing import Dict, Any, Optional
from decimal import Decimal
import pywhatkit


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending WhatsApp notifications."""
    
    def __init__(self):
        """Initialize the Notification Service."""
        pass
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format.
        
        Expected format: +[country_code][number]
        Example: +1234567890, +919876543210
        
        Args:
            phone_number: Phone number string to validate
            
        Returns:
            bool: True if valid format, False otherwise
        """
        if not phone_number:
            return False
        
        # Pattern: + followed by country code (1-3 digits) and number (4-15 digits)
        pattern = r'^\+\d{1,3}\d{4,15}$'
        return bool(re.match(pattern, phone_number))
    
    def send_whatsapp(
        self,
        phone_number: str,
        message: str
    ) -> bool:
        """
        Send a WhatsApp message using pywhatkit.
        
        Args:
            phone_number: Recipient phone number in format +[country_code][number]
            message: Message text to send
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        try:
            # Validate phone number format
            if not self.validate_phone_number(phone_number):
                logger.error(f"Invalid phone number format: {phone_number}")
                return False
            
            # Send message instantly using pywhatkit
            pywhatkit.sendwhatmsg_instantly(
                phone_no=phone_number,
                message=message,
                wait_time=15,  # Wait 15 seconds for WhatsApp Web to load
                tab_close=True,  # Close tab after sending
                close_time=3  # Wait 3 seconds before closing
            )
            
            logger.info(f"WhatsApp message sent successfully to {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message to {phone_number}: {str(e)}")
            return False
    
    def send_transaction_notification(
        self,
        phone_number: str,
        transaction_type: str,
        amount: Decimal,
        from_address: str,
        to_address: str,
        transaction_id: str,
        memo: Optional[str] = None
    ) -> bool:
        """
        Send a transaction notification via WhatsApp.
        
        Args:
            phone_number: Recipient phone number
            transaction_type: Type of transaction ('send', 'receive', 'internal')
            amount: Transaction amount in ETH
            from_address: Sender address
            to_address: Recipient address
            transaction_id: Unique transaction ID
            memo: Optional transaction memo
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        try:
            # Format the message based on transaction type
            if transaction_type == 'send':
                message = (
                    f"🔴 *Transaction Sent*\n\n"
                    f"Amount: {amount} ETH\n"
                    f"To: {to_address[:10]}...{to_address[-8:]}\n"
                    f"From: {from_address[:10]}...{from_address[-8:]}\n"
                    f"TX ID: {transaction_id[:16]}...\n"
                )
            elif transaction_type == 'receive':
                message = (
                    f"🟢 *Transaction Received*\n\n"
                    f"Amount: {amount} ETH\n"
                    f"From: {from_address[:10]}...{from_address[-8:]}\n"
                    f"To: {to_address[:10]}...{to_address[-8:]}\n"
                    f"TX ID: {transaction_id[:16]}...\n"
                )
            elif transaction_type == 'internal':
                message = (
                    f"🔄 *Internal Transfer*\n\n"
                    f"Amount: {amount} ETH\n"
                    f"From: {from_address[:10]}...{from_address[-8:]}\n"
                    f"To: {to_address[:10]}...{to_address[-8:]}\n"
                    f"TX ID: {transaction_id[:16]}...\n"
                )
            else:
                message = (
                    f"💰 *Transaction*\n\n"
                    f"Amount: {amount} ETH\n"
                    f"From: {from_address[:10]}...{from_address[-8:]}\n"
                    f"To: {to_address[:10]}...{to_address[-8:]}\n"
                    f"TX ID: {transaction_id[:16]}...\n"
                )
            
            # Add memo if provided
            if memo:
                message += f"Memo: {memo}\n"
            
            message += "\n_Mock Web3 Wallet_"
            
            # Send the notification
            return self.send_whatsapp(phone_number, message)
            
        except Exception as e:
            logger.error(f"Failed to send transaction notification: {str(e)}")
            return False
    
    def send_security_alert(
        self,
        phone_number: str,
        alert_type: str,
        details: Optional[str] = None
    ) -> bool:
        """
        Send a security alert via WhatsApp.
        
        Args:
            phone_number: Recipient phone number
            alert_type: Type of security alert (e.g., 'password_change', 'wallet_unlock', 'failed_auth')
            details: Optional additional details about the alert
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        try:
            # Format the message based on alert type
            alert_messages = {
                'password_change': '🔐 *Security Alert*\n\nYour wallet password has been changed.',
                'wallet_unlock': '🔓 *Security Alert*\n\nYour wallet has been unlocked.',
                'wallet_lock': '🔒 *Security Alert*\n\nYour wallet has been locked.',
                'failed_auth': '⚠️ *Security Alert*\n\nFailed authentication attempt detected.',
                'account_created': '✅ *Security Alert*\n\nA new account has been created in your wallet.',
                'wallet_created': '🎉 *Security Alert*\n\nYour wallet has been successfully created.',
                'wallet_restored': '♻️ *Security Alert*\n\nYour wallet has been restored from mnemonic.'
            }
            
            message = alert_messages.get(
                alert_type,
                f"🔔 *Security Alert*\n\n{alert_type}"
            )
            
            # Add details if provided
            if details:
                message += f"\n\nDetails: {details}"
            
            message += "\n\n_Mock Web3 Wallet_"
            
            # Send the notification
            return self.send_whatsapp(phone_number, message)
            
        except Exception as e:
            logger.error(f"Failed to send security alert: {str(e)}")
            return False
    
    def send_test_notification(self, phone_number: str) -> bool:
        """
        Send a test notification to verify WhatsApp integration.
        
        Args:
            phone_number: Recipient phone number
            
        Returns:
            bool: True if notification sent successfully, False otherwise
        """
        try:
            message = (
                "✅ *Test Notification*\n\n"
                "Your WhatsApp notifications are configured correctly!\n\n"
                "_Mock Web3 Wallet_"
            )
            
            return self.send_whatsapp(phone_number, message)
            
        except Exception as e:
            logger.error(f"Failed to send test notification: {str(e)}")
            return False
