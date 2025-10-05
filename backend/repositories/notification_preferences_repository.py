"""
Notification Preferences Repository - Data access layer for notification preferences.

Handles database operations for notification preferences.
"""

from typing import Dict, Any, Optional
import uuid
from datetime import datetime
from backend.utils.database import get_db_connection
import logging

logger = logging.getLogger(__name__)


class NotificationPreferencesRepository:
    """Repository for notification preferences data access."""
    
    def create(self, preferences_data: Dict[str, Any]) -> str:
        """
        Create new notification preferences.
        
        Args:
            preferences_data: Dictionary containing preferences data
            
        Returns:
            str: The created preferences ID
            
        Raises:
            Exception: If creation fails
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            preferences_id = preferences_data.get('id', str(uuid.uuid4()))
            
            cursor.execute("""
                INSERT INTO notification_preferences (
                    id, wallet_id, phone_number, enabled,
                    notify_incoming, notify_outgoing, notify_security
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                preferences_id,
                preferences_data['wallet_id'],
                preferences_data.get('phone_number'),
                preferences_data.get('enabled', False),
                preferences_data.get('notify_incoming', True),
                preferences_data.get('notify_outgoing', True),
                preferences_data.get('notify_security', True)
            ))
            
            result = cursor.fetchone()
            conn.commit()
            
            logger.info(f"Notification preferences created: {result[0]}")
            return result[0]
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create notification preferences: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_by_wallet_id(self, wallet_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve notification preferences by wallet ID.
        
        Args:
            wallet_id: The wallet UUID
            
        Returns:
            Dict containing preferences data or None if not found
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, wallet_id, phone_number, enabled,
                       notify_incoming, notify_outgoing, notify_security,
                       created_at, updated_at
                FROM notification_preferences
                WHERE wallet_id = %s
            """, (wallet_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'wallet_id': row[1],
                    'phone_number': row[2],
                    'enabled': row[3],
                    'notify_incoming': row[4],
                    'notify_outgoing': row[5],
                    'notify_security': row[6],
                    'created_at': row[7],
                    'updated_at': row[8]
                }
            
            return None
            
        finally:
            cursor.close()
            conn.close()
    
    def update(self, wallet_id: str, preferences_data: Dict[str, Any]) -> bool:
        """
        Update notification preferences.
        
        Args:
            wallet_id: The wallet UUID
            preferences_data: Dictionary containing updated preferences data
            
        Returns:
            bool: True if update successful, False otherwise
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Build dynamic update query
            update_fields = []
            values = []
            
            if 'phone_number' in preferences_data:
                update_fields.append("phone_number = %s")
                values.append(preferences_data['phone_number'])
            
            if 'enabled' in preferences_data:
                update_fields.append("enabled = %s")
                values.append(preferences_data['enabled'])
            
            if 'notify_incoming' in preferences_data:
                update_fields.append("notify_incoming = %s")
                values.append(preferences_data['notify_incoming'])
            
            if 'notify_outgoing' in preferences_data:
                update_fields.append("notify_outgoing = %s")
                values.append(preferences_data['notify_outgoing'])
            
            if 'notify_security' in preferences_data:
                update_fields.append("notify_security = %s")
                values.append(preferences_data['notify_security'])
            
            if not update_fields:
                return True  # Nothing to update
            
            # Add updated_at timestamp
            update_fields.append("updated_at = %s")
            values.append(datetime.now())
            
            # Add wallet_id for WHERE clause
            values.append(wallet_id)
            
            query = f"""
                UPDATE notification_preferences
                SET {', '.join(update_fields)}
                WHERE wallet_id = %s
            """
            
            cursor.execute(query, values)
            conn.commit()
            
            success = cursor.rowcount > 0
            
            if success:
                logger.info(f"Notification preferences updated for wallet: {wallet_id}")
            
            return success
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update notification preferences: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def delete(self, wallet_id: str) -> bool:
        """
        Delete notification preferences.
        
        Args:
            wallet_id: The wallet UUID
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                DELETE FROM notification_preferences
                WHERE wallet_id = %s
            """, (wallet_id,))
            
            conn.commit()
            
            success = cursor.rowcount > 0
            
            if success:
                logger.info(f"Notification preferences deleted for wallet: {wallet_id}")
            
            return success
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to delete notification preferences: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
