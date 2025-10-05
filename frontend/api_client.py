"""
API Client for Mock Web3 Wallet Backend

Handles all HTTP communication with the FastAPI backend.
"""

import requests
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class WalletAPIClient:
    """Client for interacting with the Mock Web3 Wallet API."""
    
    def __init__(self, base_url: str):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API (e.g., http://localhost:8000)
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise exceptions for errors.
        
        Args:
            response: Response object from requests
            
        Returns:
            Parsed JSON response
            
        Raises:
            Exception: If the API returns an error
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Try to extract error message from response
            try:
                error_data = response.json()
                error_message = error_data.get("detail", str(e))
                error_code = error_data.get("error_code", "UNKNOWN_ERROR")
                raise Exception(f"{error_message} (Code: {error_code})")
            except ValueError:
                # Response is not JSON
                raise Exception(f"API Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    # ========================================================================
    # Wallet Endpoints
    # ========================================================================
    
    def create_wallet(self, password: str) -> Dict[str, Any]:
        """
        Create a new wallet.
        
        Args:
            password: Wallet password (min 8 characters)
            
        Returns:
            Dict containing wallet_id, mnemonic, and first_account
        """
        url = f"{self.base_url}/api/wallet/create"
        payload = {"password": password}
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to create wallet: {str(e)}")
            raise
    
    def restore_wallet(self, mnemonic: str, password: str) -> Dict[str, Any]:
        """
        Restore a wallet from mnemonic.
        
        Args:
            mnemonic: 12-word BIP39 mnemonic phrase
            password: Wallet password (min 8 characters)
            
        Returns:
            Dict containing wallet_id, exists flag, and accounts list
        """
        url = f"{self.base_url}/api/wallet/restore"
        payload = {
            "mnemonic": mnemonic,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to restore wallet: {str(e)}")
            raise
    
    def authenticate(self, wallet_id: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with wallet password.
        
        Args:
            wallet_id: Wallet UUID
            password: Wallet password
            
        Returns:
            Dict containing success flag and message
        """
        url = f"{self.base_url}/api/wallet/authenticate"
        payload = {
            "wallet_id": wallet_id,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to authenticate: {str(e)}")
            raise
    
    def lock_wallet(self, wallet_id: str) -> Dict[str, Any]:
        """
        Lock a wallet.
        
        Args:
            wallet_id: Wallet UUID
            
        Returns:
            Dict containing success message
        """
        url = f"{self.base_url}/api/wallet/lock"
        payload = {"wallet_id": wallet_id}
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to lock wallet: {str(e)}")
            raise
    
    def unlock_wallet(self, wallet_id: str, password: str) -> Dict[str, Any]:
        """
        Unlock a wallet.
        
        Args:
            wallet_id: Wallet UUID
            password: Wallet password
            
        Returns:
            Dict containing success flag and message
        """
        url = f"{self.base_url}/api/wallet/unlock"
        payload = {
            "wallet_id": wallet_id,
            "password": password
        }
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to unlock wallet: {str(e)}")
            raise
    
    def get_wallet_info(self, wallet_id: str) -> Dict[str, Any]:
        """
        Get wallet information.
        
        Args:
            wallet_id: Wallet UUID
            
        Returns:
            Dict containing wallet information
        """
        url = f"{self.base_url}/api/wallet/{wallet_id}"
        
        try:
            response = self.session.get(url)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to get wallet info: {str(e)}")
            raise
    
    def change_password(self, wallet_id: str, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        Change wallet password.
        
        Args:
            wallet_id: Wallet UUID
            old_password: Current password
            new_password: New password (min 8 characters)
            
        Returns:
            Dict containing success message
        """
        url = f"{self.base_url}/api/wallet/{wallet_id}/password"
        payload = {
            "wallet_id": wallet_id,
            "old_password": old_password,
            "new_password": new_password
        }
        
        try:
            response = self.session.put(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to change password: {str(e)}")
            raise
    
    # ========================================================================
    # Account Endpoints
    # ========================================================================
    
    def create_account(self, wallet_id: str, password: str, label: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new account.
        
        Args:
            wallet_id: Wallet UUID
            password: Wallet password for authentication
            label: Optional account label
            
        Returns:
            Dict containing account information
        """
        url = f"{self.base_url}/api/accounts"
        payload = {
            "wallet_id": wallet_id,
            "password": password,
            "label": label
        }
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to create account: {str(e)}")
            raise
    
    def get_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get account details.
        
        Args:
            account_id: Account UUID
            
        Returns:
            Dict containing account information
        """
        url = f"{self.base_url}/api/accounts/{account_id}"
        
        try:
            response = self.session.get(url)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to get account: {str(e)}")
            raise
    
    def get_account_by_address(self, address: str) -> Dict[str, Any]:
        """
        Get account by address.
        
        Args:
            address: Ethereum address
            
        Returns:
            Dict containing account information
        """
        url = f"{self.base_url}/api/accounts/address/{address}"
        
        try:
            response = self.session.get(url)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to get account by address: {str(e)}")
            raise
    
    def get_accounts(self, wallet_id: str) -> List[Dict[str, Any]]:
        """
        Get all accounts for a wallet.
        
        Args:
            wallet_id: Wallet UUID
            
        Returns:
            List of account dictionaries
        """
        url = f"{self.base_url}/api/accounts/wallet/{wallet_id}"
        
        try:
            response = self.session.get(url)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to get accounts: {str(e)}")
            raise
    
    def update_account_label(self, account_id: str, label: str) -> Dict[str, Any]:
        """
        Update account label.
        
        Args:
            account_id: Account UUID
            label: New label
            
        Returns:
            Dict containing success message
        """
        url = f"{self.base_url}/api/accounts/{account_id}/label"
        payload = {"label": label}
        
        try:
            response = self.session.put(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to update account label: {str(e)}")
            raise
    
    def get_account_balance(self, account_id: str) -> Dict[str, Any]:
        """
        Get account balance.
        
        Args:
            account_id: Account UUID
            
        Returns:
            Dict containing account_id and balance
        """
        url = f"{self.base_url}/api/accounts/{account_id}/balance"
        
        try:
            response = self.session.get(url)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to get account balance: {str(e)}")
            raise
    
    def get_total_balance(self, wallet_id: str) -> Dict[str, Any]:
        """
        Get total wallet balance.
        
        Args:
            wallet_id: Wallet UUID
            
        Returns:
            Dict containing wallet_id, total_balance, and account_count
        """
        url = f"{self.base_url}/api/accounts/wallet/{wallet_id}/balance"
        
        try:
            response = self.session.get(url)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to get total balance: {str(e)}")
            raise
    
    # ========================================================================
    # Transaction Endpoints
    # ========================================================================
    
    def create_approval(
        self,
        from_account_id: str,
        to_address: str,
        amount_eth: Optional[float] = None,
        amount_usd: Optional[float] = None,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create transaction approval message.
        
        Args:
            from_account_id: Sender account UUID
            to_address: Recipient address
            amount_eth: Amount in ETH (optional if amount_usd provided)
            amount_usd: Amount in USD (optional if amount_eth provided)
            memo: Optional transaction memo
            
        Returns:
            Dict containing approval message, message_id, expires_at, eth_amount, usd_amount
        """
        url = f"{self.base_url}/api/transactions/create-approval"
        payload = {
            "from_account_id": from_account_id,
            "to_address": to_address,
            "amount_eth": amount_eth,
            "amount_usd": amount_usd,
            "memo": memo
        }
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to create approval: {str(e)}")
            raise
    
    def send_transaction(self, message_id: str, signature: str) -> Dict[str, Any]:
        """
        Send transaction with signed approval.
        
        Args:
            message_id: Approval message ID
            signature: Signed approval message in hex format
            
        Returns:
            Dict containing transaction details
        """
        url = f"{self.base_url}/api/transactions/send"
        payload = {
            "message_id": message_id,
            "signature": signature
        }
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to send transaction: {str(e)}")
            raise
    
    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get transaction details.
        
        Args:
            transaction_id: Transaction UUID
            
        Returns:
            Dict containing transaction information
        """
        url = f"{self.base_url}/api/transactions/{transaction_id}"
        
        try:
            response = self.session.get(url)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to get transaction: {str(e)}")
            raise
    
    def get_account_transactions(self, account_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get account transaction history.
        
        Args:
            account_id: Account UUID
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction dictionaries
        """
        url = f"{self.base_url}/api/transactions/account/{account_id}"
        params = {"limit": limit}
        
        try:
            response = self.session.get(url, params=params)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to get account transactions: {str(e)}")
            raise
    
    # ========================================================================
    # Notification Endpoints
    # ========================================================================
    
    def set_notification_preferences(
        self,
        wallet_id: str,
        phone_number: Optional[str] = None,
        enabled: bool = False,
        notify_incoming: bool = True,
        notify_outgoing: bool = True,
        notify_security: bool = True
    ) -> Dict[str, Any]:
        """
        Set notification preferences.
        
        Args:
            wallet_id: Wallet UUID
            phone_number: Phone number in format +[country_code][number]
            enabled: Enable/disable notifications
            notify_incoming: Notify on incoming transactions
            notify_outgoing: Notify on outgoing transactions
            notify_security: Notify on security events
            
        Returns:
            Dict containing notification preferences
        """
        url = f"{self.base_url}/api/notifications/preferences"
        payload = {
            "wallet_id": wallet_id,
            "phone_number": phone_number,
            "enabled": enabled,
            "notify_incoming": notify_incoming,
            "notify_outgoing": notify_outgoing,
            "notify_security": notify_security
        }
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to set notification preferences: {str(e)}")
            raise
    
    def get_notification_preferences(self, wallet_id: str) -> Dict[str, Any]:
        """
        Get notification preferences.
        
        Args:
            wallet_id: Wallet UUID
            
        Returns:
            Dict containing notification preferences
        """
        url = f"{self.base_url}/api/notifications/preferences/{wallet_id}"
        
        try:
            response = self.session.get(url)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to get notification preferences: {str(e)}")
            raise
    
    def test_notification(self, phone_number: str) -> Dict[str, Any]:
        """
        Send test notification.
        
        Args:
            phone_number: Phone number in format +[country_code][number]
            
        Returns:
            Dict containing success flag and message
        """
        url = f"{self.base_url}/api/notifications/test"
        payload = {"phone_number": phone_number}
        
        try:
            response = self.session.post(url, json=payload)
            return self._handle_response(response)
        except Exception as e:
            logger.error(f"Failed to send test notification: {str(e)}")
            raise
