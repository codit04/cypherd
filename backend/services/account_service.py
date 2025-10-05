"""
Account Service - Business logic for account operations.

Handles account creation, retrieval, and balance operations.
"""

from typing import Dict, Any, List, Optional
from decimal import Decimal
from backend.utils.crypto_manager import CryptoManager
from backend.repositories.account_repository import AccountRepository
from backend.repositories.wallet_repository import WalletRepository


class AccountService:
    """Service for account management operations."""
    
    def __init__(self):
        """Initialize the Account Service with required dependencies."""
        self.crypto_manager = CryptoManager()
        self.account_repo = AccountRepository()
        self.wallet_repo = WalletRepository()
    
    def create_account(
        self,
        wallet_id: str,
        password: str,
        label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new account for a wallet using HD derivation.
        
        This method:
        1. Verifies the wallet exists
        2. Gets the next account index
        3. Decrypts the wallet seed
        4. Derives a new account from the seed
        5. Creates the account in the database
        
        Args:
            wallet_id: The wallet UUID
            password: Password to decrypt the wallet seed
            label: Optional label for the account
            
        Returns:
            Dict containing account information:
                - id: Account UUID
                - wallet_id: Wallet UUID
                - address: Ethereum address
                - account_index: HD derivation index
                - label: Account label
                - balance: Account balance (starts at 0.0)
                
        Raises:
            ValueError: If wallet not found or password incorrect
            Exception: If account creation fails
        """
        # Verify wallet exists
        wallet = self.wallet_repo.get_by_id(wallet_id)
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Get next account index
        next_index = self.account_repo.get_next_account_index(wallet_id)
        
        # Decrypt wallet seed
        try:
            mnemonic = self.crypto_manager.decrypt_data(
                wallet['encrypted_seed'],
                password
            )
        except Exception:
            raise ValueError("Failed to decrypt wallet seed - incorrect password")
        
        # Convert mnemonic to seed
        seed = self.crypto_manager.mnemonic_to_seed(mnemonic)
        
        # Derive new account
        private_key, address = self.crypto_manager.derive_account(seed, next_index)
        
        # Encrypt private key
        encrypted_private_key = self.crypto_manager.encrypt_data(private_key, password)
        
        # Set default label if not provided
        if not label:
            label = f"Account {next_index + 1}"
        
        # Create account in database
        account_data = {
            'wallet_id': wallet_id,
            'address': address,
            'encrypted_private_key': encrypted_private_key,
            'account_index': next_index,
            'label': label,
            'balance': Decimal('0.0')
        }
        
        account_id = self.account_repo.create(account_data)
        
        # Fetch the created account to get timestamps
        created_account = self.account_repo.get_by_id(account_id)
        
        # Return account info (include private key for testing/development)
        return {
            'id': account_id,
            'wallet_id': wallet_id,
            'address': address,
            'account_index': next_index,
            'label': label,
            'balance': Decimal('0.0'),
            'created_at': created_account['created_at'],
            'updated_at': created_account['updated_at'],
            'private_key': private_key  # Include for testing purposes
        }
    
    def get_account(self, account_id: str) -> Dict[str, Any]:
        """
        Retrieve an account by its ID.
        
        Args:
            account_id: The account UUID
            
        Returns:
            Dict containing account information (without private key)
            
        Raises:
            ValueError: If account not found
        """
        account = self.account_repo.get_by_id(account_id)
        
        if not account:
            raise ValueError("Account not found")
        
        # Return account info without encrypted private key
        return {
            'id': account['id'],
            'wallet_id': account['wallet_id'],
            'address': account['address'],
            'account_index': account['account_index'],
            'label': account['label'],
            'balance': account['balance'],
            'created_at': account['created_at'],
            'updated_at': account['updated_at']
        }
    
    def get_account_by_address(self, address: str) -> Dict[str, Any]:
        """
        Retrieve an account by its Ethereum address.
        
        Args:
            address: The Ethereum address
            
        Returns:
            Dict containing account information (without private key)
            
        Raises:
            ValueError: If account not found or address invalid
        """
        # Validate address format
        if not self.crypto_manager.validate_address(address):
            raise ValueError("Invalid Ethereum address format")
        
        account = self.account_repo.get_by_address(address)
        
        if not account:
            raise ValueError("Account not found")
        
        # Return account info without encrypted private key
        return {
            'id': account['id'],
            'wallet_id': account['wallet_id'],
            'address': account['address'],
            'account_index': account['account_index'],
            'label': account['label'],
            'balance': account['balance'],
            'created_at': account['created_at'],
            'updated_at': account['updated_at']
        }
    
    def list_accounts(self, wallet_id: str) -> List[Dict[str, Any]]:
        """
        Get all accounts for a specific wallet.
        
        Args:
            wallet_id: The wallet UUID
            
        Returns:
            List of account dictionaries (without private keys), ordered by account_index
            
        Raises:
            ValueError: If wallet not found
        """
        # Verify wallet exists
        wallet = self.wallet_repo.get_by_id(wallet_id)
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Get all accounts for wallet
        accounts = self.account_repo.get_by_wallet_id(wallet_id)
        
        # Return accounts without encrypted private keys
        return [
            {
                'id': account['id'],
                'wallet_id': account['wallet_id'],
                'address': account['address'],
                'account_index': account['account_index'],
                'label': account['label'],
                'balance': account['balance'],
                'created_at': account['created_at'],
                'updated_at': account['updated_at']
            }
            for account in accounts
        ]
    
    def update_account_label(self, account_id: str, label: str) -> bool:
        """
        Update the label of an account.
        
        Args:
            account_id: The account UUID
            label: New label for the account
            
        Returns:
            bool: True if update successful
            
        Raises:
            ValueError: If account not found or label invalid
        """
        # Validate label
        if not label or not label.strip():
            raise ValueError("Label cannot be empty")
        
        # Verify account exists
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        
        # Update label
        success = self.account_repo.update(account_id, {'label': label.strip()})
        
        if not success:
            raise Exception("Failed to update account label")
        
        return True
    
    def get_account_balance(self, account_id: str) -> Decimal:
        """
        Get the balance of a specific account.
        
        Args:
            account_id: The account UUID
            
        Returns:
            Decimal: The account balance
            
        Raises:
            ValueError: If account not found
        """
        account = self.account_repo.get_by_id(account_id)
        
        if not account:
            raise ValueError("Account not found")
        
        return account['balance']
    
    def get_total_balance(self, wallet_id: str) -> Decimal:
        """
        Calculate the total balance across all accounts in a wallet.
        
        Args:
            wallet_id: The wallet UUID
            
        Returns:
            Decimal: The total balance across all accounts
            
        Raises:
            ValueError: If wallet not found
        """
        # Verify wallet exists
        wallet = self.wallet_repo.get_by_id(wallet_id)
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Get all accounts for wallet
        accounts = self.account_repo.get_by_wallet_id(wallet_id)
        
        # Sum all balances
        total_balance = sum(
            (account['balance'] for account in accounts),
            Decimal('0.0')
        )
        
        return total_balance
