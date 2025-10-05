"""
Simple test script to verify database connection.
Run this after setting up your .env file to ensure database connectivity.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import test_connection, DatabaseConnection


def main():
    print("=" * 60)
    print("Database Connection Test")
    print("=" * 60)
    
    print("\nTesting database connection...")
    
    try:
        # Initialize connection pool
        DatabaseConnection.initialize_pool()
        
        # Test connection
        if test_connection():
            print("✓ Database connection successful!")
            print("\nYou can now run the migration script:")
            print("  python backend/migrations/init_db.py")
            return True
        else:
            print("✗ Database connection failed!")
            print("\nPlease check your .env file and ensure:")
            print("  1. Database credentials are correct")
            print("  2. Database server is accessible")
            print("  3. Database exists")
            return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nPlease check your .env file configuration.")
        return False
    
    finally:
        # Close connection pool
        DatabaseConnection.close_pool()


if __name__ == "__main__":
    success = main()
    print()
    sys.exit(0 if success else 1)
