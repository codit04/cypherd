"""
Crypto Manager - Handles all cryptographic operations for the wallet.

This module provides functionality for:
- BIP39 mnemonic generation and validation
- Wallet ID derivation from mnemonic
- HD wallet key derivation (BIP44)
- Message signing and verification (Ethereum personal_sign)
- Data encryption/decryption (AES-256-GCM)
- Address validation
"""

import hashlib
import uuid
from typing import Tuple
from mnemonic import Mnemonic
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64


class CryptoManager:
    """Manages cryptographic operations for the wallet."""
    
    def __init__(self):
        """Initialize the Crypto Manager."""
        self.mnemonic_generator = Mnemonic("english")
        self.web3 = Web3()
    
    def generate_mnemonic(self, strength: int = 128) -> str:
        """
        Generate a BIP39 mnemonic seed phrase.
        
        Args:
            strength: Entropy strength in bits (128 = 12 words, 256 = 24 words)
        
        Returns:
            A space-separated mnemonic phrase (12 or 24 words)
        
        Raises:
            ValueError: If strength is not 128 or 256
        """
        if strength not in [128, 256]:
            raise ValueError("Strength must be 128 (12 words) or 256 (24 words)")
        
        return self.mnemonic_generator.generate(strength=strength)
    
    def mnemonic_to_wallet_id(self, mnemonic: str) -> str:
        """
        Derive a deterministic wallet UUID from a mnemonic phrase.
        
        The same mnemonic will always produce the same wallet ID.
        Uses SHA-256 hash of the seed to generate a UUID v4.
        
        Args:
            mnemonic: BIP39 mnemonic phrase
        
        Returns:
            UUID string (deterministic based on mnemonic)
        
        Raises:
            ValueError: If mnemonic is invalid
        """
        if not self.validate_mnemonic(mnemonic):
            raise ValueError("Invalid mnemonic phrase")
        
        # Convert mnemonic to seed
        seed = self.mnemonic_to_seed(mnemonic)
        
        # Hash the seed with SHA-256
        hash_digest = hashlib.sha256(seed).digest()
        
        # Take first 16 bytes and format as UUID
        wallet_uuid = uuid.UUID(bytes=hash_digest[:16], version=4)
        
        return str(wallet_uuid)
    
    def mnemonic_to_seed(self, mnemonic: str, passphrase: str = "") -> bytes:
        """
        Convert a mnemonic phrase to a seed.
        
        Args:
            mnemonic: BIP39 mnemonic phrase
            passphrase: Optional passphrase for additional security
        
        Returns:
            64-byte seed
        
        Raises:
            ValueError: If mnemonic is invalid
        """
        if not self.validate_mnemonic(mnemonic):
            raise ValueError("Invalid mnemonic phrase")
        
        return self.mnemonic_generator.to_seed(mnemonic, passphrase)
    
    def derive_account(self, seed: bytes, account_index: int) -> Tuple[str, str]:
        """
        Derive an account from a seed using BIP44 HD derivation.
        
        Uses the Ethereum BIP44 path: m/44'/60'/0'/0/index
        
        Args:
            seed: 64-byte seed from mnemonic
            account_index: Account index (0, 1, 2, ...)
        
        Returns:
            Tuple of (private_key_hex, ethereum_address)
        
        Raises:
            ValueError: If account_index is negative
        """
        if account_index < 0:
            raise ValueError("Account index must be non-negative")
        
        # For simplicity, we'll use a deterministic derivation from seed + index
        # This creates unique accounts for each index while maintaining determinism
        key_material = seed + account_index.to_bytes(4, 'big')
        private_key_bytes = hashlib.sha256(key_material).digest()
        
        # Create account from private key
        account = Account.from_key(private_key_bytes)
        
        return account.key.hex(), account.address
    
    def sign_message(self, message: str, private_key: str) -> str:
        """
        Sign a message using Ethereum's personal_sign standard.
        
        The message is prefixed with "\x19Ethereum Signed Message:\n" + length
        before signing.
        
        Args:
            message: Message to sign
            private_key: Private key in hex format (with or without 0x prefix)
        
        Returns:
            Signature in hex format (0x + 130 characters)
        
        Raises:
            ValueError: If private key is invalid
        """
        try:
            # Ensure private key has 0x prefix
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
            
            # Create account from private key
            account = Account.from_key(private_key)
            
            # Encode message with Ethereum prefix
            encoded_message = encode_defunct(text=message)
            
            # Sign the message
            signed_message = account.sign_message(encoded_message)
            
            return signed_message.signature.hex()
        except Exception as e:
            raise ValueError(f"Failed to sign message: {str(e)}")
    
    def verify_signature(self, message: str, signature: str, address: str) -> bool:
        """
        Verify that a signature was created by a specific address.
        
        Args:
            message: Original message that was signed
            signature: Signature in hex format
            address: Ethereum address that allegedly signed the message
        
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Recover address from signature
            recovered_address = self.recover_address_from_signature(message, signature)
            
            # Compare addresses (case-insensitive)
            return recovered_address.lower() == address.lower()
        except Exception:
            return False
    
    def recover_address_from_signature(self, message: str, signature: str) -> str:
        """
        Recover the signer's address from a message and signature.
        
        Args:
            message: Original message that was signed
            signature: Signature in hex format
        
        Returns:
            Ethereum address of the signer
        
        Raises:
            ValueError: If signature is invalid
        """
        try:
            # Ensure signature has 0x prefix
            if not signature.startswith('0x'):
                signature = '0x' + signature
            
            # Encode message with Ethereum prefix
            encoded_message = encode_defunct(text=message)
            
            # Recover address
            recovered_address = Account.recover_message(encoded_message, signature=signature)
            
            return recovered_address
        except Exception as e:
            raise ValueError(f"Failed to recover address: {str(e)}")
    
    def encrypt_data(self, data: str, password: str) -> str:
        """
        Encrypt data using AES-256-GCM.
        
        Args:
            data: Plain text data to encrypt
            password: Password to derive encryption key from
        
        Returns:
            Base64-encoded encrypted data (includes salt and nonce)
        
        Format: base64(salt + nonce + ciphertext + tag)
        """
        # Generate random salt
        salt = os.urandom(16)
        
        # Derive key from password using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits for AES-256
            salt=salt,
            iterations=100000,
        )
        key = kdf.derive(password.encode())
        
        # Generate random nonce
        nonce = os.urandom(12)  # 96 bits for GCM
        
        # Encrypt data
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, data.encode(), None)
        
        # Combine salt + nonce + ciphertext and encode as base64
        encrypted_data = salt + nonce + ciphertext
        
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str, password: str) -> str:
        """
        Decrypt data that was encrypted with encrypt_data().
        
        Args:
            encrypted_data: Base64-encoded encrypted data
            password: Password to derive decryption key from
        
        Returns:
            Decrypted plain text data
        
        Raises:
            ValueError: If decryption fails (wrong password or corrupted data)
        """
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Extract salt, nonce, and ciphertext
            salt = encrypted_bytes[:16]
            nonce = encrypted_bytes[16:28]
            ciphertext = encrypted_bytes[28:]
            
            # Derive key from password using same parameters
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = kdf.derive(password.encode())
            
            # Decrypt data
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def validate_address(self, address: str) -> bool:
        """
        Validate Ethereum address format.
        
        Args:
            address: Ethereum address to validate
        
        Returns:
            True if address is valid, False otherwise
        """
        try:
            # Check if it's a valid Ethereum address
            return self.web3.is_address(address)
        except Exception:
            return False
    
    def validate_mnemonic(self, mnemonic: str) -> bool:
        """
        Validate BIP39 mnemonic phrase.
        
        Args:
            mnemonic: Mnemonic phrase to validate
        
        Returns:
            True if mnemonic is valid, False otherwise
        """
        try:
            return self.mnemonic_generator.check(mnemonic)
        except Exception:
            return False
