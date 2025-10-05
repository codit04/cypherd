"""
Wallet Service - Business logic for wallet operations.

Handles wallet lifecycle including creation, authentication, and recovery.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import random
import bcrypt
from backend.utils.crypto_manager import CryptoManager
from backend.repositories.wallet_repository import WalletRepository
from backend.repositories.account_repository import AccountRepository


class WalletService:
    """Service for wallet management operations."""
    
    def __init__(self):
        """Initialize the Wallet Service with required dependencies."""
        self.crypto_manager = CryptoManager()
        self.wallet_repo = WalletRepository()
        self.account_repo = AccountRepository()
    
    def create_wallet(self, password: str) -> Dict[str, Any]:
        """
        Create a new wallet with a generated mnemonic.
        
        This method:
        1. Generates a 12-word BIP39 mnemonic
        2. Derives a deterministic wallet ID from the mnemonic
        3. Checks if wallet already exists
        4. Creates the wallet in the database
        5. Creates the first account with a random balance (1.0-10.0 ETH)
        
        Args:
            password: Password to encrypt the wallet seed
            
        Returns:
            Dict containing:
                - wallet_id: The wallet UUID (derived from mnemonic)
                - mnemonic: The 12-word mnemonic phrase (user must save this!)
                - first_account: Dictionary with first account details
                
        Raises:
            ValueError: If password is invalid or wallet already exists
            Exception: If wallet creation fails
        """
        # Validate password
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Generate 12-word mnemonic
        mnemonic = self.crypto_manager.generate_mnemonic(strength=128)
        
        # Derive wallet ID from mnemonic (deterministic)
        wallet_id = self.crypto_manager.mnemonic_to_wallet_id(mnemonic)
        
        # Check if wallet already exists
        if self.wallet_repo.exists(wallet_id):
            raise ValueError("Wallet already exists with this mnemonic")
        
        # Hash password with bcrypt
        password_hash, salt = self._hash_password(password)
        
        # Encrypt the mnemonic seed phrase
        encrypted_seed = self.crypto_manager.encrypt_data(mnemonic, password)
        
        # Create wallet in database
        wallet_data = {
            'id': wallet_id,
            'encrypted_seed': encrypted_seed,
            'password_hash': password_hash,
            'salt': salt,
            'is_locked': False  # Unlocked after creation
        }
        
        created_wallet_id = self.wallet_repo.create(wallet_data)
        
        # Create first account with random balance (1.0-10.0 ETH)
        first_account = self._create_first_account(wallet_id, mnemonic, password)
        
        return {
            'wallet_id': created_wallet_id,
            'mnemonic': mnemonic,
            'first_account': first_account
        }
    
    def restore_wallet(self, mnemonic: str, password: str) -> Dict[str, Any]:
        """
        Restore a wallet from an existing mnemonic.
        
        This method:
        1. Validates the mnemonic phrase
        2. Derives the wallet ID from the mnemonic
        3. Checks if wallet exists in database
        4. If exists, verifies it's the same wallet
        5. If not exists, creates a new wallet entry
        
        Args:
            mnemonic: The 12-word BIP39 mnemonic phrase
            password: Password to encrypt the wallet seed
            
        Returns:
            Dict containing:
                - wallet_id: The wallet UUID
                - exists: Boolean indicating if wallet was already in database
                - accounts: List of existing accounts (if wallet existed)
                
        Raises:
            ValueError: If mnemonic is invalid or password is invalid
            Exception: If restoration fails
        """
        # Validate mnemonic
        if not self.crypto_manager.validate_mnemonic(mnemonic):
            raise ValueError("Invalid mnemonic phrase")
        
        # Validate password
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Derive wallet ID from mnemonic
        wallet_id = self.crypto_manager.mnemonic_to_wallet_id(mnemonic)
        
        # Check if wallet exists
        existing_wallet = self.wallet_repo.get_by_id(wallet_id)
        
        if existing_wallet:
            # Wallet exists - verify password can decrypt the seed
            try:
                stored_seed = self.crypto_manager.decrypt_data(
                    existing_wallet['encrypted_seed'],
                    password
                )
                
                # Verify the decrypted seed matches the provided mnemonic
                if stored_seed != mnemonic:
                    raise ValueError("Password is incorrect")
                
            except Exception:
                raise ValueError("Password is incorrect")
            
            # Get existing accounts
            accounts = self.account_repo.get_by_wallet_id(wallet_id)
            
            # Update wallet to unlocked state
            self.wallet_repo.update(wallet_id, {
                'is_locked': False,
                'last_accessed': datetime.now()
            })
            
            return {
                'wallet_id': wallet_id,
                'exists': True,
                'accounts': accounts
            }
        else:
            # Wallet doesn't exist - create new entry
            password_hash, salt = self._hash_password(password)
            encrypted_seed = self.crypto_manager.encrypt_data(mnemonic, password)
            
            wallet_data = {
                'id': wallet_id,
                'encrypted_seed': encrypted_seed,
                'password_hash': password_hash,
                'salt': salt,
                'is_locked': False
            }
            
            created_wallet_id = self.wallet_repo.create(wallet_data)
            
            # Create first account with random balance
            first_account = self._create_first_account(wallet_id, mnemonic, password)
            
            return {
                'wallet_id': created_wallet_id,
                'exists': False,
                'accounts': [first_account]
            }
    
    def authenticate(self, wallet_id: str, password: str) -> bool:
        """
        Authenticate a user with their wallet password.
        
        Args:
            wallet_id: The wallet UUID
            password: The password to verify
            
        Returns:
            bool: True if authentication successful, False otherwise
            
        Raises:
            ValueError: If wallet not found
            Exception: If authentication check fails
        """
        # Get wallet from database
        wallet = self.wallet_repo.get_by_id(wallet_id)
        
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Verify password
        is_valid = self._verify_password(password, wallet['password_hash'])
        
        if is_valid:
            # Update last accessed time and unlock wallet
            self.wallet_repo.update(wallet_id, {
                'is_locked': False,
                'last_accessed': datetime.now()
            })
        
        return is_valid
    
    def lock_wallet(self, wallet_id: str) -> None:
        """
        Lock a wallet to require authentication for future access.
        
        Args:
            wallet_id: The wallet UUID
            
        Raises:
            ValueError: If wallet not found
            Exception: If lock operation fails
        """
        # Verify wallet exists
        wallet = self.wallet_repo.get_by_id(wallet_id)
        
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Update wallet to locked state
        self.wallet_repo.update(wallet_id, {'is_locked': True})
    
    def unlock_wallet(self, wallet_id: str, password: str) -> bool:
        """
        Unlock a wallet with password verification.
        
        Args:
            wallet_id: The wallet UUID
            password: The password to verify
            
        Returns:
            bool: True if unlock successful, False if password incorrect
            
        Raises:
            ValueError: If wallet not found
            Exception: If unlock operation fails
        """
        # Authenticate and unlock in one operation
        return self.authenticate(wallet_id, password)
    
    def change_password(self, wallet_id: str, old_password: str, new_password: str) -> bool:
        """
        Change the wallet password.
        
        This method:
        1. Verifies the old password
        2. Decrypts the seed with old password
        3. Re-encrypts the seed with new password
        4. Updates the password hash
        
        Args:
            wallet_id: The wallet UUID
            old_password: Current password
            new_password: New password to set
            
        Returns:
            bool: True if password change successful
            
        Raises:
            ValueError: If wallet not found, old password incorrect, or new password invalid
            Exception: If password change fails
        """
        # Validate new password
        if not new_password or len(new_password) < 8:
            raise ValueError("New password must be at least 8 characters long")
        
        # Get wallet from database
        wallet = self.wallet_repo.get_by_id(wallet_id)
        
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Verify old password
        if not self._verify_password(old_password, wallet['password_hash']):
            raise ValueError("Current password is incorrect")
        
        # Decrypt seed with old password
        try:
            mnemonic = self.crypto_manager.decrypt_data(
                wallet['encrypted_seed'],
                old_password
            )
        except Exception:
            raise ValueError("Failed to decrypt wallet seed")
        
        # Re-encrypt seed with new password
        new_encrypted_seed = self.crypto_manager.encrypt_data(mnemonic, new_password)
        
        # Hash new password
        new_password_hash, new_salt = self._hash_password(new_password)
        
        # Update wallet in database
        update_data = {
            'encrypted_seed': new_encrypted_seed,
            'password_hash': new_password_hash,
            'salt': new_salt
        }
        
        success = self.wallet_repo.update(wallet_id, update_data)
        
        if not success:
            raise Exception("Failed to update wallet password")
        
        return True
    
    def get_wallet_info(self, wallet_id: str) -> Dict[str, Any]:
        """
        Get wallet information (without sensitive data).
        
        Args:
            wallet_id: The wallet UUID
            
        Returns:
            Dict containing wallet information:
                - wallet_id: The wallet UUID
                - created_at: Wallet creation timestamp
                - last_accessed: Last access timestamp
                - is_locked: Lock status
                - account_count: Number of accounts
                
        Raises:
            ValueError: If wallet not found
        """
        wallet = self.wallet_repo.get_by_id(wallet_id)
        
        if not wallet:
            raise ValueError("Wallet not found")
        
        # Get account count
        accounts = self.account_repo.get_by_wallet_id(wallet_id)
        
        return {
            'wallet_id': wallet['id'],
            'created_at': wallet['created_at'],
            'last_accessed': wallet.get('last_accessed'),
            'is_locked': wallet['is_locked'],
            'account_count': len(accounts)
        }
    
    def _hash_password(self, password: str) -> tuple[str, str]:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Tuple of (password_hash, salt) as strings
        """
        # Generate salt
        salt = bcrypt.gensalt()
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        # Return as strings
        return password_hash.decode('utf-8'), salt.decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against a hash.
        
        Args:
            password: Plain text password to verify
            password_hash: Stored password hash
            
        Returns:
            bool: True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    def _create_first_account(
        self,
        wallet_id: str,
        mnemonic: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Create the first account for a new wallet with random balance.
        
        Args:
            wallet_id: The wallet UUID
            mnemonic: The wallet mnemonic
            password: Password to encrypt the private key
            
        Returns:
            Dict containing account information
        """
        # Convert mnemonic to seed
        seed = self.crypto_manager.mnemonic_to_seed(mnemonic)
        
        # Derive first account (index 0)
        private_key, address = self.crypto_manager.derive_account(seed, 0)
        
        # Encrypt private key
        encrypted_private_key = self.crypto_manager.encrypt_data(private_key, password)
        
        # Generate random balance between 1.0 and 10.0 ETH
        random_balance = Decimal(str(round(random.uniform(1.0, 10.0), 8)))
        
        # Create account in database
        account_data = {
            'wallet_id': wallet_id,
            'address': address,
            'encrypted_private_key': encrypted_private_key,
            'account_index': 0,
            'label': 'Account 1',
            'balance': random_balance
        }
        
        account_id = self.account_repo.create(account_data)
        
        # Return account info
        return {
            'id': account_id,
            'wallet_id': wallet_id,
            'address': address,
            'account_index': 0,
            'label': 'Account 1',
            'balance': random_balance
        }
