"""
Account Repository - Data access layer for account operations.
Handles CRUD operations for the accounts table.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
import uuid
from backend.utils.database import get_db_cursor


class AccountRepository:
    """Repository for account data access operations."""
    
    def create(self, account_data: Dict[str, Any]) -> str:
        """
        Create a new account in the database.
        
        Args:
            account_data: Dictionary containing account information:
                - wallet_id: UUID of the parent wallet
                - address: Ethereum address
                - encrypted_private_key: Encrypted private key
                - account_index: HD derivation index
                - label: Optional account label
                - balance: Initial balance (default: 0.0)
                
        Returns:
            str: The account ID (UUID)
            
        Raises:
            Exception: If account creation fails
        """
        query = """
            INSERT INTO accounts (id, wallet_id, address, encrypted_private_key, 
                                 account_index, label, balance, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        try:
            with get_db_cursor() as cursor:
                account_id = str(uuid.uuid4())
                now = datetime.now()
                
                cursor.execute(query, (
                    account_id,
                    account_data['wallet_id'],
                    account_data['address'],
                    account_data['encrypted_private_key'],
                    account_data['account_index'],
                    account_data.get('label'),
                    account_data.get('balance', Decimal('0.0')),
                    now,
                    now
                ))
                
                result = cursor.fetchone()
                return result['id']
                
        except Exception as e:
            raise Exception(f"Failed to create account: {str(e)}")
    
    def get_by_id(self, account_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an account by its ID.
        
        Args:
            account_id: The account UUID
            
        Returns:
            Optional[Dict[str, Any]]: Account data as dictionary, or None if not found
        """
        query = """
            SELECT id, wallet_id, address, encrypted_private_key, account_index,
                   label, balance, created_at, updated_at
            FROM accounts
            WHERE id = %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (account_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            raise Exception(f"Failed to retrieve account: {str(e)}")
    
    def get_by_address(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an account by its Ethereum address.
        
        Args:
            address: The Ethereum address
            
        Returns:
            Optional[Dict[str, Any]]: Account data as dictionary, or None if not found
        """
        query = """
            SELECT id, wallet_id, address, encrypted_private_key, account_index,
                   label, balance, created_at, updated_at
            FROM accounts
            WHERE address = %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (address,))
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            raise Exception(f"Failed to retrieve account by address: {str(e)}")
    
    def get_by_wallet_id(self, wallet_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all accounts for a specific wallet.
        
        Args:
            wallet_id: The wallet UUID
            
        Returns:
            List[Dict[str, Any]]: List of account dictionaries
        """
        query = """
            SELECT id, wallet_id, address, encrypted_private_key, account_index,
                   label, balance, created_at, updated_at
            FROM accounts
            WHERE wallet_id = %s
            ORDER BY account_index ASC
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (wallet_id,))
                results = cursor.fetchall()
                return [dict(row) for row in results] if results else []
                
        except Exception as e:
            raise Exception(f"Failed to retrieve accounts for wallet: {str(e)}")
    
    def update_balance(self, account_id: str, new_balance: Decimal) -> bool:
        """
        Update the balance of an account.
        
        Args:
            account_id: The account UUID
            new_balance: The new balance value
            
        Returns:
            bool: True if update was successful, False if account not found
            
        Raises:
            Exception: If update operation fails
        """
        query = """
            UPDATE accounts
            SET balance = %s, updated_at = %s
            WHERE id = %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (new_balance, datetime.now(), account_id))
                return cursor.rowcount > 0
                
        except Exception as e:
            raise Exception(f"Failed to update account balance: {str(e)}")
    
    def update(self, account_id: str, account_data: Dict[str, Any]) -> bool:
        """
        Update account information.
        
        Args:
            account_id: The account UUID
            account_data: Dictionary containing fields to update
            
        Returns:
            bool: True if update was successful, False if account not found
            
        Raises:
            Exception: If update operation fails
        """
        # Build dynamic update query based on provided fields
        allowed_fields = ['label', 'balance', 'encrypted_private_key']
        update_fields = []
        values = []
        
        for field in allowed_fields:
            if field in account_data:
                update_fields.append(f"{field} = %s")
                values.append(account_data[field])
        
        if not update_fields:
            return False
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = %s")
        values.append(datetime.now())
        
        # Add account_id for WHERE clause
        values.append(account_id)
        
        query = f"""
            UPDATE accounts
            SET {', '.join(update_fields)}
            WHERE id = %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, values)
                return cursor.rowcount > 0
                
        except Exception as e:
            raise Exception(f"Failed to update account: {str(e)}")
    
    def delete(self, account_id: str) -> bool:
        """
        Delete an account from the database.
        
        Args:
            account_id: The account UUID
            
        Returns:
            bool: True if deletion was successful, False if account not found
            
        Raises:
            Exception: If delete operation fails
        """
        query = "DELETE FROM accounts WHERE id = %s"
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (account_id,))
                return cursor.rowcount > 0
                
        except Exception as e:
            raise Exception(f"Failed to delete account: {str(e)}")
    
    def get_next_account_index(self, wallet_id: str) -> int:
        """
        Get the next available account index for a wallet.
        
        Args:
            wallet_id: The wallet UUID
            
        Returns:
            int: The next account index (0 if no accounts exist)
        """
        query = """
            SELECT COALESCE(MAX(account_index), -1) + 1 as next_index
            FROM accounts
            WHERE wallet_id = %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (wallet_id,))
                result = cursor.fetchone()
                return result['next_index'] if result else 0
                
        except Exception as e:
            raise Exception(f"Failed to get next account index: {str(e)}")
