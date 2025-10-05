"""
Transaction Service - Business logic for transaction operations with signature approval.

Handles transaction creation, validation, signature verification, and execution.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import logging
from backend.utils.crypto_manager import CryptoManager
from backend.repositories.transaction_repository import TransactionRepository
from backend.repositories.account_repository import AccountRepository
from backend.repositories.wallet_repository import WalletRepository
from backend.repositories.notification_preferences_repository import NotificationPreferencesRepository
from backend.services.skip_api_service import SkipAPIService
from backend.services.notification_service import NotificationService

# Configure logging
logger = logging.getLogger(__name__)


class PendingApproval:
    """Data class for pending transaction approvals."""
    
    def __init__(
        self,
        message_id: str,
        message: str,
        from_account_id: str,
        to_address: str,
        amount_eth: Decimal,
        amount_usd: Optional[Decimal] = None,
        original_eth_quote: Optional[Decimal] = None,
        expires_at: datetime = None,
        memo: Optional[str] = None
    ):
        self.message_id = message_id
        self.message = message
        self.from_account_id = from_account_id
        self.to_address = to_address
        self.amount_eth = amount_eth
        self.amount_usd = amount_usd
        self.original_eth_quote = original_eth_quote
        self.expires_at = expires_at or datetime.now() + timedelta(seconds=30)
        self.created_at = datetime.now()
        self.memo = memo


class TransactionService:
    """Service for transaction management operations."""
    
    # In-memory cache for pending approvals (message_id -> PendingApproval)
    _pending_approvals: Dict[str, PendingApproval] = {}
    
    def __init__(self):
        """Initialize the Transaction Service with required dependencies."""
        self.crypto_manager = CryptoManager()
        self.transaction_repo = TransactionRepository()
        self.account_repo = AccountRepository()
        self.wallet_repo = WalletRepository()
        self.notification_prefs_repo = NotificationPreferencesRepository()
        self.skip_api_service = SkipAPIService()
        self.notification_service = NotificationService()
    
    def create_approval_message(
        self,
        from_account_id: str,
        to_address: str,
        amount_eth: Optional[Decimal] = None,
        amount_usd: Optional[Decimal] = None,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an approval message for a transaction with 30-second expiration.
        
        This method:
        1. Validates the from account exists
        2. Validates the to address format
        3. Handles ETH or USD amount (converts USD to ETH via Skip API)
        4. Generates approval message
        5. Stores pending approval in memory cache
        6. Returns message details with expiration
        
        Args:
            from_account_id: UUID of sender account
            to_address: Recipient Ethereum address
            amount_eth: Amount in ETH (if specified)
            amount_usd: Amount in USD (if specified, will convert to ETH)
            memo: Optional transaction memo
            
        Returns:
            Dict containing:
                - message: Approval message to sign
                - message_id: Unique message identifier
                - expires_at: Expiration timestamp
                - eth_amount: ETH amount for transaction
                - usd_amount: USD amount (if USD transfer)
                
        Raises:
            ValueError: If validation fails or both/neither amount specified
            Exception: If approval creation fails
        """
        # Validate from account exists
        from_account = self.account_repo.get_by_id(from_account_id)
        if not from_account:
            raise ValueError("Sender account not found")
        
        # Validate to address format
        if not self.crypto_manager.validate_address(to_address):
            raise ValueError("Invalid recipient address format")
        
        # Validate exactly one amount is specified
        if (amount_eth is None and amount_usd is None) or \
           (amount_eth is not None and amount_usd is not None):
            raise ValueError("Must specify either amount_eth or amount_usd, not both")
        
        # Handle USD to ETH conversion if needed
        original_eth_quote = None
        if amount_usd is not None:
            # Query Skip API for ETH quote
            try:
                quote = self.skip_api_service.get_eth_quote_for_usd(amount_usd)
                amount_eth = quote['eth_amount']
                original_eth_quote = amount_eth
                logger.info(f"USD to ETH conversion: ${amount_usd} = {amount_eth} ETH")
            except Exception as e:
                logger.error(f"Failed to get ETH quote for USD: {e}")
                raise Exception(f"Failed to convert USD to ETH: {str(e)}")
        else:
            # Validate ETH amount
            if amount_eth <= 0:
                raise ValueError("Amount must be greater than 0")
        
        # Generate unique message ID
        message_id = str(uuid.uuid4())
        
        # Create approval message
        if amount_usd is not None:
            message = f"Transfer {amount_eth} ETH (${amount_usd} USD) to {to_address} from {from_account['address']}"
        else:
            message = f"Transfer {amount_eth} ETH to {to_address} from {from_account['address']}"
        
        # Set expiration to 30 seconds from now
        expires_at = datetime.now() + timedelta(seconds=30)
        
        # Create pending approval object
        pending_approval = PendingApproval(
            message_id=message_id,
            message=message,
            from_account_id=from_account_id,
            to_address=to_address,
            amount_eth=amount_eth,
            amount_usd=amount_usd,
            original_eth_quote=original_eth_quote,
            expires_at=expires_at,
            memo=memo
        )
        
        # Store in memory cache
        self._pending_approvals[message_id] = pending_approval
        
        logger.info(f"Created approval message {message_id} for {amount_eth} ETH transfer")
        
        return {
            'message': message,
            'message_id': message_id,
            'expires_at': expires_at.isoformat(),
            'eth_amount': str(amount_eth),
            'usd_amount': str(amount_usd) if amount_usd else None
        }

    
    def verify_signature(self, message: str, signature: str, address: str) -> bool:
        """
        Verify that a signature was created by a specific address.
        
        Uses CryptoManager to verify Ethereum personal_sign signature.
        
        Args:
            message: Original message that was signed
            signature: Signature in hex format
            address: Ethereum address that allegedly signed the message
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            return self.crypto_manager.verify_signature(message, signature, address)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def send_transaction(
        self,
        message_id: str,
        signature: str
    ) -> Dict[str, Any]:
        """
        Execute a transaction with signature verification and validation.
        
        This method:
        1. Retrieves pending approval from cache
        2. Checks if approval has expired
        3. Verifies signature matches sender address
        4. For USD transfers, fetches new quote and checks price tolerance
        5. Validates sender has sufficient balance
        6. Executes atomic balance updates (deduct from sender, add to recipient)
        7. Creates recipient account if address doesn't exist in wallet
        8. Records transaction in database
        9. Cleans up pending approval from cache
        
        Args:
            message_id: Unique message identifier from create_approval_message
            signature: Signed message from user's private key
            
        Returns:
            Dict containing:
                - transaction_id: Unique transaction ID
                - from_address: Sender address
                - to_address: Recipient address
                - amount: Transaction amount in ETH
                - memo: Transaction memo (if any)
                - status: Transaction status
                - created_at: Transaction timestamp
                
        Raises:
            ValueError: If validation fails (expired, invalid signature, insufficient balance, etc.)
            Exception: If transaction execution fails
        """
        # Retrieve pending approval
        pending_approval = self._pending_approvals.get(message_id)
        if not pending_approval:
            raise ValueError("Approval message not found or already used")
        
        # Check if approval has expired
        if datetime.now() > pending_approval.expires_at:
            # Clean up expired approval
            del self._pending_approvals[message_id]
            raise ValueError("Approval message has expired")
        
        # Get sender account
        from_account = self.account_repo.get_by_id(pending_approval.from_account_id)
        if not from_account:
            raise ValueError("Sender account not found")
        
        # Verify signature
        is_valid = self.verify_signature(
            pending_approval.message,
            signature,
            from_account['address']
        )
        
        if not is_valid:
            raise ValueError("Invalid signature - signature does not match sender address")
        
        # For USD transfers, check price tolerance
        final_eth_amount = pending_approval.amount_eth
        if pending_approval.amount_usd is not None:
            try:
                # Fetch new quote
                new_quote = self.skip_api_service.get_eth_quote_for_usd(pending_approval.amount_usd)
                new_eth_amount = new_quote['eth_amount']
                
                # Check if price is within tolerance (1%)
                within_tolerance = self.skip_api_service.check_price_tolerance(
                    pending_approval.original_eth_quote,
                    new_eth_amount
                )
                
                if not within_tolerance:
                    # Clean up approval
                    del self._pending_approvals[message_id]
                    raise ValueError(
                        f"Price has moved beyond tolerance. "
                        f"Original: {pending_approval.original_eth_quote} ETH, "
                        f"Current: {new_eth_amount} ETH. "
                        f"Please create a new transaction."
                    )
                
                # Use new quote for transaction
                final_eth_amount = new_eth_amount
                logger.info(f"Price tolerance check passed: {pending_approval.original_eth_quote} -> {new_eth_amount}")
                
            except ValueError:
                # Re-raise validation errors
                raise
            except Exception as e:
                logger.error(f"Failed to check price tolerance: {e}")
                raise Exception(f"Failed to verify current price: {str(e)}")
        
        # Validate sender has sufficient balance
        if from_account['balance'] < final_eth_amount:
            raise ValueError(
                f"Insufficient balance. "
                f"Available: {from_account['balance']} ETH, "
                f"Required: {final_eth_amount} ETH"
            )
        
        # Check if recipient account exists in the same wallet
        to_account = self.account_repo.get_by_address(pending_approval.to_address)
        
        # Determine transaction type
        if to_account and to_account['wallet_id'] == from_account['wallet_id']:
            transaction_type = 'internal'
        else:
            transaction_type = 'send'
        
        try:
            # Execute atomic balance updates
            # Deduct from sender
            new_sender_balance = from_account['balance'] - final_eth_amount
            success = self.account_repo.update_balance(
                pending_approval.from_account_id,
                new_sender_balance
            )
            
            if not success:
                raise Exception("Failed to update sender balance")
            
            # Add to recipient (if account exists in wallet)
            to_account_id = None
            if to_account:
                new_recipient_balance = to_account['balance'] + final_eth_amount
                success = self.account_repo.update_balance(
                    to_account['id'],
                    new_recipient_balance
                )
                
                if not success:
                    # Rollback sender balance
                    self.account_repo.update_balance(
                        pending_approval.from_account_id,
                        from_account['balance']
                    )
                    raise Exception("Failed to update recipient balance")
                
                to_account_id = to_account['id']
            
            # Generate unique transaction ID
            transaction_id = str(uuid.uuid4())
            
            # Record transaction in database
            transaction_data = {
                'from_account_id': pending_approval.from_account_id,
                'to_account_id': to_account_id,
                'from_address': from_account['address'],
                'to_address': pending_approval.to_address,
                'amount': final_eth_amount,
                'memo': pending_approval.memo,
                'transaction_type': transaction_type,
                'status': 'completed'
            }
            
            created_tx_id = self.transaction_repo.create(transaction_data)
            
            # Clean up pending approval from cache
            del self._pending_approvals[message_id]
            
            logger.info(
                f"Transaction {created_tx_id} completed: "
                f"{final_eth_amount} ETH from {from_account['address']} to {pending_approval.to_address}"
            )
            
            # Send notifications after successful transaction
            self._send_transaction_notifications(
                from_account=from_account,
                to_account=to_account,
                to_address=pending_approval.to_address,
                transaction_id=created_tx_id,
                amount=final_eth_amount,
                transaction_type=transaction_type,
                memo=pending_approval.memo
            )
            
            # Return transaction details
            return {
                'transaction_id': created_tx_id,
                'from_address': from_account['address'],
                'to_address': pending_approval.to_address,
                'amount': str(final_eth_amount),
                'memo': pending_approval.memo,
                'transaction_type': transaction_type,
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            }
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Transaction execution failed: {e}")
            raise Exception(f"Failed to execute transaction: {str(e)}")
    
    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Retrieve a transaction by its ID.
        
        Args:
            transaction_id: The transaction UUID
            
        Returns:
            Dict containing transaction details
            
        Raises:
            ValueError: If transaction not found
            Exception: If retrieval fails
        """
        transaction = self.transaction_repo.get_by_id(transaction_id)
        
        if not transaction:
            raise ValueError("Transaction not found")
        
        return {
            'transaction_id': transaction['id'],
            'from_account_id': transaction['from_account_id'],
            'to_account_id': transaction['to_account_id'],
            'from_address': transaction['from_address'],
            'to_address': transaction['to_address'],
            'amount': str(transaction['amount']),
            'memo': transaction['memo'],
            'transaction_type': transaction['transaction_type'],
            'status': transaction['status'],
            'created_at': transaction['created_at'].isoformat()
        }
    
    def get_account_transactions(
        self,
        account_id: str,
        limit: int = 50
    ) -> list[Dict[str, Any]]:
        """
        Retrieve all transactions for a specific account.
        
        Args:
            account_id: The account UUID
            limit: Maximum number of transactions to return (default: 50)
            
        Returns:
            List of transaction dictionaries, ordered by created_at DESC
            
        Raises:
            ValueError: If account not found
            Exception: If retrieval fails
        """
        # Verify account exists
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        
        # Get transactions
        transactions = self.transaction_repo.get_by_account_id(account_id, limit)
        
        # Format transactions
        return [
            {
                'transaction_id': tx['id'],
                'from_account_id': tx['from_account_id'],
                'to_account_id': tx['to_account_id'],
                'from_address': tx['from_address'],
                'to_address': tx['to_address'],
                'amount': str(tx['amount']),
                'memo': tx['memo'],
                'transaction_type': tx['transaction_type'],
                'status': tx['status'],
                'created_at': tx['created_at'].isoformat()
            }
            for tx in transactions
        ]
    
    def validate_transaction(
        self,
        from_account_id: str,
        amount: Decimal
    ) -> tuple[bool, str]:
        """
        Validate a transaction before creating approval.
        
        Args:
            from_account_id: UUID of sender account
            amount: Transaction amount
            
        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is empty string
        """
        # Check if account exists
        account = self.account_repo.get_by_id(from_account_id)
        if not account:
            return False, "Sender account not found"
        
        # Check if amount is positive
        if amount <= 0:
            return False, "Amount must be greater than 0"
        
        # Check if account has sufficient balance
        if account['balance'] < amount:
            return False, f"Insufficient balance. Available: {account['balance']} ETH"
        
        return True, ""
    
    def cleanup_expired_approvals(self) -> int:
        """
        Clean up expired approval messages from cache.
        
        This method should be called periodically to prevent memory leaks.
        
        Returns:
            int: Number of expired approvals removed
        """
        now = datetime.now()
        expired_ids = [
            message_id
            for message_id, approval in self._pending_approvals.items()
            if now > approval.expires_at
        ]
        
        for message_id in expired_ids:
            del self._pending_approvals[message_id]
        
        if expired_ids:
            logger.info(f"Cleaned up {len(expired_ids)} expired approval messages")
        
        return len(expired_ids)
    
    def _send_transaction_notifications(
        self,
        from_account: Dict[str, Any],
        to_account: Optional[Dict[str, Any]],
        to_address: str,
        transaction_id: str,
        amount: Decimal,
        transaction_type: str,
        memo: Optional[str] = None
    ) -> None:
        """
        Send notifications for a completed transaction.
        
        This method:
        1. Retrieves notification preferences for sender's wallet
        2. Sends notification to sender if enabled and outgoing notifications are on
        3. If recipient is in the same wallet, sends notification if incoming notifications are on
        4. Handles notification failures gracefully without blocking transaction
        5. Logs all notification attempts and results
        
        Args:
            from_account: Sender account dictionary
            to_account: Recipient account dictionary (None if external address)
            to_address: Recipient Ethereum address
            transaction_id: Unique transaction ID
            amount: Transaction amount in ETH
            transaction_type: Type of transaction ('send', 'receive', 'internal')
            memo: Optional transaction memo
        """
        try:
            # Get sender's wallet notification preferences
            sender_prefs = self.notification_prefs_repo.get_by_wallet_id(from_account['wallet_id'])
            
            if sender_prefs and sender_prefs['enabled'] and sender_prefs['phone_number']:
                # Send notification to sender if outgoing notifications are enabled
                if sender_prefs['notify_outgoing']:
                    logger.info(f"Sending outgoing transaction notification to sender for TX {transaction_id}")
                    
                    success = self.notification_service.send_transaction_notification(
                        phone_number=sender_prefs['phone_number'],
                        transaction_type='send',
                        amount=amount,
                        from_address=from_account['address'],
                        to_address=to_address,
                        transaction_id=transaction_id,
                        memo=memo
                    )
                    
                    if success:
                        logger.info(f"Successfully sent outgoing notification for TX {transaction_id}")
                    else:
                        logger.warning(f"Failed to send outgoing notification for TX {transaction_id}")
                else:
                    logger.info(f"Outgoing notifications disabled for wallet {from_account['wallet_id']}")
            else:
                logger.info(f"Notifications not enabled for sender wallet {from_account['wallet_id']}")
            
            # If recipient is also in a wallet (internal or to another wallet account), send notification
            if to_account:
                recipient_prefs = self.notification_prefs_repo.get_by_wallet_id(to_account['wallet_id'])
                
                if recipient_prefs and recipient_prefs['enabled'] and recipient_prefs['phone_number']:
                    # Send notification to recipient if incoming notifications are enabled
                    if recipient_prefs['notify_incoming']:
                        logger.info(f"Sending incoming transaction notification to recipient for TX {transaction_id}")
                        
                        success = self.notification_service.send_transaction_notification(
                            phone_number=recipient_prefs['phone_number'],
                            transaction_type='receive' if transaction_type != 'internal' else 'internal',
                            amount=amount,
                            from_address=from_account['address'],
                            to_address=to_address,
                            transaction_id=transaction_id,
                            memo=memo
                        )
                        
                        if success:
                            logger.info(f"Successfully sent incoming notification for TX {transaction_id}")
                        else:
                            logger.warning(f"Failed to send incoming notification for TX {transaction_id}")
                    else:
                        logger.info(f"Incoming notifications disabled for wallet {to_account['wallet_id']}")
                else:
                    logger.info(f"Notifications not enabled for recipient wallet {to_account['wallet_id']}")
            
        except Exception as e:
            # Log error but don't raise - notifications should not block transactions
            logger.error(f"Error sending transaction notifications for TX {transaction_id}: {str(e)}")
            logger.info("Transaction completed successfully despite notification failure")
