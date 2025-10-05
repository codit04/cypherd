"""
Database connection utility for PostgreSQL/Supabase.
Provides connection pooling and helper functions for database operations.
"""

import os
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class DatabaseConnection:
    """Manages PostgreSQL database connections using connection pooling."""
    
    _connection_pool: Optional[pool.SimpleConnectionPool] = None
    
    @classmethod
    def initialize_pool(cls, minconn: int = 1, maxconn: int = 10):
        """
        Initialize the connection pool.
        
        Args:
            minconn: Minimum number of connections in the pool
            maxconn: Maximum number of connections in the pool
        """
        if cls._connection_pool is not None:
            return
        
        # Get database configuration from environment
        # Priority: individual params (lowercase/uppercase) > DATABASE_URL
        # This ensures compatibility with existing .env configurations
        host = os.getenv('host') or os.getenv('DB_HOST')
        port = os.getenv('port') or os.getenv('DB_PORT')
        dbname = os.getenv('dbname') or os.getenv('DB_NAME')
        user = os.getenv('user') or os.getenv('DB_USER')
        password = os.getenv('password') or os.getenv('DB_PASSWORD')
        database_url = os.getenv('DATABASE_URL')
        
        # Use individual parameters if any are provided, otherwise fall back to DATABASE_URL
        if host or user or password:
            # Use individual connection parameters
            cls._connection_pool = pool.SimpleConnectionPool(
                minconn,
                maxconn,
                host=host,
                port=port or 5432,
                database=dbname or 'postgres',
                user=user,
                password=password
            )
        elif database_url:
            # Fall back to DATABASE_URL if no individual params provided
            cls._connection_pool = pool.SimpleConnectionPool(
                minconn,
                maxconn,
                database_url
            )
        else:
            raise ValueError(
                "No database configuration found. Please set either:\n"
                "  - Individual parameters (host, port, dbname, user, password)\n"
                "  - Or DATABASE_URL in your .env file"
            )
    
    @classmethod
    def close_pool(cls):
        """Close all connections in the pool."""
        if cls._connection_pool is not None:
            cls._connection_pool.closeall()
            cls._connection_pool = None
    
    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Context manager for getting a database connection from the pool.
        
        Yields:
            psycopg2.connection: Database connection
        """
        if cls._connection_pool is None:
            cls.initialize_pool()
        
        conn = cls._connection_pool.getconn()
        try:
            yield conn
        finally:
            cls._connection_pool.putconn(conn)
    
    @classmethod
    @contextmanager
    def get_cursor(cls, cursor_factory=RealDictCursor):
        """
        Context manager for getting a database cursor.
        
        Args:
            cursor_factory: Cursor factory class (default: RealDictCursor for dict results)
        
        Yields:
            psycopg2.cursor: Database cursor
        """
        with cls.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                cursor.close()


def get_db_connection():
    """
    Get a database connection from the pool.
    This is a convenience function for use in repositories.
    
    Returns:
        Context manager for database connection
    """
    return DatabaseConnection.get_connection()


def get_db_cursor(cursor_factory=RealDictCursor):
    """
    Get a database cursor with automatic commit/rollback.
    This is a convenience function for use in repositories.
    
    Args:
        cursor_factory: Cursor factory class (default: RealDictCursor)
    
    Returns:
        Context manager for database cursor
    """
    return DatabaseConnection.get_cursor(cursor_factory)


def test_connection() -> bool:
    """
    Test the database connection.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False
