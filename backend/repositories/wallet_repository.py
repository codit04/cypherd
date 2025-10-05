"""
Wallet Repository - Data access layer for wallet operations.
Handles CRUD operations for the wallets table.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from backend.utils.database import get_db_cursor


class WalletRepository:
    """Repository for wallet data access operations."""
    
    def create(self, wallet_data: Dict[str, Any]) -> str:
        """
        Create a new wallet in the database.
        
        Args:
            wallet_data: Dictionary containing wallet information:
                - id: Wallet UUID (derived from mnemonic)
                - encrypted_seed: Encrypted mnemonic seed phrase
                - password_hash: Hashed password
                - salt: Salt used for password hashing
                
        Returns:
            str: The wallet ID (UUID)
            
        Raises:
            Exception: If wallet creation fails or wallet already exists
        """
        query = """
            INSERT INTO wallets (id, encrypted_seed, password_hash, salt, created_at, updated_at, is_locked)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        try:
            with get_db_cursor() as cursor:
                wallet_id = wallet_data.get('id') or str(uuid.uuid4())
                now = datetime.now()
                
                cursor.execute(query, (
                    wallet_id,
                    wallet_data['encrypted_seed'],
                    wallet_data['password_hash'],
                    wallet_data['salt'],
                    now,
                    now,
                    wallet_data.get('is_locked', True)
                ))
                
                result = cursor.fetchone()
                return result['id']
                
        except Exception as e:
            raise Exception(f"Failed to create wallet: {str(e)}")
    
    def get_by_id(self, wallet_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a wallet by its ID.
        
        Args:
            wallet_id: The wallet UUID
            
        Returns:
            Optional[Dict[str, Any]]: Wallet data as dictionary, or None if not found
        """
        query = """
            SELECT id, encrypted_seed, password_hash, salt, created_at, 
                   updated_at, last_accessed, is_locked
            FROM wallets
            WHERE id = %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (wallet_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            raise Exception(f"Failed to retrieve wallet: {str(e)}")
    
    def exists(self, wallet_id: str) -> bool:
        """
        Check if a wallet exists in the database.
        
        Args:
            wallet_id: The wallet UUID
            
        Returns:
            bool: True if wallet exists, False otherwise
        """
        query = "SELECT EXISTS(SELECT 1 FROM wallets WHERE id = %s)"
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (wallet_id,))
                result = cursor.fetchone()
                return result['exists'] if result else False
                
        except Exception as e:
            raise Exception(f"Failed to check wallet existence: {str(e)}")
    
    def update(self, wallet_id: str, wallet_data: Dict[str, Any]) -> bool:
        """
        Update wallet information.
        
        Args:
            wallet_id: The wallet UUID
            wallet_data: Dictionary containing fields to update
            
        Returns:
            bool: True if update was successful, False if wallet not found
            
        Raises:
            Exception: If update operation fails
        """
        # Build dynamic update query based on provided fields
        allowed_fields = ['encrypted_seed', 'password_hash', 'salt', 'last_accessed', 'is_locked']
        update_fields = []
        values = []
        
        for field in allowed_fields:
            if field in wallet_data:
                update_fields.append(f"{field} = %s")
                values.append(wallet_data[field])
        
        if not update_fields:
            return False
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = %s")
        values.append(datetime.now())
        
        # Add wallet_id for WHERE clause
        values.append(wallet_id)
        
        query = f"""
            UPDATE wallets
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, values)
                return cursor.rowcount > 0
                
        except Exception as e:
            raise Exception(f"Failed to update wallet: {str(e)}")
    
    def delete(self, wallet_id: str) -> bool:
        """
        Delete a wallet from the database.
        
        Args:
            wallet_id: The wallet UUID
            
        Returns:
            bool: True if deletion was successful, False if wallet not found
            
        Raises:
            Exception: If delete operation fails
        """
        query = "DELETE FROM wallets WHERE id = %s"
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (wallet_id,))
                return cursor.rowcount > 0
                
        except Exception as e:
            raise Exception(f"Failed to delete wallet: {str(e)}")
