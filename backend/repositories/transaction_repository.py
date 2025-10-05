"""
Transaction Repository - Data access layer for transaction operations.
Handles CRUD operations for the transactions table.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal
import uuid
from backend.utils.database import get_db_cursor


class TransactionRepository:
    """Repository for transaction data access operations."""
    
    def create(self, transaction_data: Dict[str, Any]) -> str:
        """
        Create a new transaction in the database.
        
        Args:
            transaction_data: Dictionary containing transaction information:
                - from_account_id: UUID of sender account (optional)
                - to_account_id: UUID of recipient account (optional)
                - from_address: Sender Ethereum address
                - to_address: Recipient Ethereum address
                - amount: Transaction amount
                - memo: Optional transaction memo
                - transaction_type: Type ('send', 'receive', 'internal')
                - status: Transaction status (default: 'completed')
                
        Returns:
            str: The transaction ID (UUID)
            
        Raises:
            Exception: If transaction creation fails
        """
        query = """
            INSERT INTO transactions (id, from_account_id, to_account_id, from_address,
                                     to_address, amount, memo, transaction_type, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        try:
            with get_db_cursor() as cursor:
                transaction_id = str(uuid.uuid4())
                now = datetime.now()
                
                cursor.execute(query, (
                    transaction_id,
                    transaction_data.get('from_account_id'),
                    transaction_data.get('to_account_id'),
                    transaction_data['from_address'],
                    transaction_data['to_address'],
                    transaction_data['amount'],
                    transaction_data.get('memo'),
                    transaction_data['transaction_type'],
                    transaction_data.get('status', 'completed'),
                    now
                ))
                
                result = cursor.fetchone()
                return result['id']
                
        except Exception as e:
            raise Exception(f"Failed to create transaction: {str(e)}")
    
    def get_by_id(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a transaction by its ID.
        
        Args:
            transaction_id: The transaction UUID
            
        Returns:
            Optional[Dict[str, Any]]: Transaction data as dictionary, or None if not found
        """
        query = """
            SELECT id, from_account_id, to_account_id, from_address, to_address,
                   amount, memo, transaction_type, status, created_at
            FROM transactions
            WHERE id = %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (transaction_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
                
        except Exception as e:
            raise Exception(f"Failed to retrieve transaction: {str(e)}")
    
    def get_by_account_id(self, account_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve all transactions for a specific account.
        
        Args:
            account_id: The account UUID
            limit: Maximum number of transactions to return (default: 50)
            
        Returns:
            List[Dict[str, Any]]: List of transaction dictionaries, ordered by created_at DESC
        """
        query = """
            SELECT id, from_account_id, to_account_id, from_address, to_address,
                   amount, memo, transaction_type, status, created_at
            FROM transactions
            WHERE from_account_id = %s OR to_account_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (account_id, account_id, limit))
                results = cursor.fetchall()
                return [dict(row) for row in results] if results else []
                
        except Exception as e:
            raise Exception(f"Failed to retrieve transactions for account: {str(e)}")
    
    def get_by_address(self, address: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve all transactions for a specific address.
        
        Args:
            address: The Ethereum address
            limit: Maximum number of transactions to return (default: 50)
            
        Returns:
            List[Dict[str, Any]]: List of transaction dictionaries, ordered by created_at DESC
        """
        query = """
            SELECT id, from_account_id, to_account_id, from_address, to_address,
                   amount, memo, transaction_type, status, created_at
            FROM transactions
            WHERE from_address = %s OR to_address = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (address, address, limit))
                results = cursor.fetchall()
                return [dict(row) for row in results] if results else []
                
        except Exception as e:
            raise Exception(f"Failed to retrieve transactions for address: {str(e)}")
    
    def get_by_wallet_id(self, wallet_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve all transactions for accounts belonging to a specific wallet.
        
        Args:
            wallet_id: The wallet UUID
            limit: Maximum number of transactions to return (default: 50)
            
        Returns:
            List[Dict[str, Any]]: List of transaction dictionaries, ordered by created_at DESC
        """
        query = """
            SELECT DISTINCT t.id, t.from_account_id, t.to_account_id, t.from_address, 
                   t.to_address, t.amount, t.memo, t.transaction_type, t.status, t.created_at
            FROM transactions t
            LEFT JOIN accounts a1 ON t.from_account_id = a1.id
            LEFT JOIN accounts a2 ON t.to_account_id = a2.id
            WHERE a1.wallet_id = %s OR a2.wallet_id = %s
            ORDER BY t.created_at DESC
            LIMIT %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (wallet_id, wallet_id, limit))
                results = cursor.fetchall()
                return [dict(row) for row in results] if results else []
                
        except Exception as e:
            raise Exception(f"Failed to retrieve transactions for wallet: {str(e)}")
    
    def update_status(self, transaction_id: str, status: str) -> bool:
        """
        Update the status of a transaction.
        
        Args:
            transaction_id: The transaction UUID
            status: The new status ('completed', 'pending', 'failed')
            
        Returns:
            bool: True if update was successful, False if transaction not found
            
        Raises:
            Exception: If update operation fails
        """
        query = """
            UPDATE transactions
            SET status = %s
            WHERE id = %s
        """
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (status, transaction_id))
                return cursor.rowcount > 0
                
        except Exception as e:
            raise Exception(f"Failed to update transaction status: {str(e)}")
    
    def delete(self, transaction_id: str) -> bool:
        """
        Delete a transaction from the database.
        
        Args:
            transaction_id: The transaction UUID
            
        Returns:
            bool: True if deletion was successful, False if transaction not found
            
        Raises:
            Exception: If delete operation fails
        """
        query = "DELETE FROM transactions WHERE id = %s"
        
        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (transaction_id,))
                return cursor.rowcount > 0
                
        except Exception as e:
            raise Exception(f"Failed to delete transaction: {str(e)}")
