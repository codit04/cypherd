"""
Database initialization script.
Runs all SQL migration scripts in order to set up the database schema.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import database utility
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.database import DatabaseConnection, get_db_cursor


def run_migration(cursor, migration_file: Path) -> bool:
    """
    Run a single migration file.
    
    Args:
        cursor: Database cursor
        migration_file: Path to the SQL migration file
    
    Returns:
        bool: True if migration was successful, False otherwise
    """
    try:
        print(f"Running migration: {migration_file.name}")
        
        with open(migration_file, 'r') as f:
            sql = f.read()
        
        # Execute the SQL migration
        cursor.execute(sql)
        
        print(f"✓ Successfully ran migration: {migration_file.name}")
        return True
    
    except Exception as e:
        print(f"✗ Error running migration {migration_file.name}: {e}")
        return False


def init_database():
    """
    Initialize the database by running all migration scripts in order.
    """
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60)
    
    # Get the migrations directory
    migrations_dir = Path(__file__).parent
    
    # Get all SQL migration files in order
    migration_files = sorted(migrations_dir.glob("*.sql"))
    
    if not migration_files:
        print("No migration files found!")
        return False
    
    print(f"\nFound {len(migration_files)} migration(s) to run:\n")
    
    try:
        # Initialize the connection pool
        DatabaseConnection.initialize_pool()
        
        # Run all migrations in a single transaction
        with get_db_cursor() as cursor:
            for migration_file in migration_files:
                success = run_migration(cursor, migration_file)
                if not success:
                    print("\n✗ Migration failed! Rolling back all changes.")
                    return False
        
        print("\n" + "=" * 60)
        print("✓ All migrations completed successfully!")
        print("=" * 60)
        return True
    
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        return False
    
    finally:
        # Close the connection pool
        DatabaseConnection.close_pool()


def verify_schema():
    """
    Verify that all tables were created successfully.
    """
    print("\nVerifying database schema...")
    
    expected_tables = [
        'wallets',
        'accounts',
        'transactions',
        'notification_preferences'
    ]
    
    try:
        DatabaseConnection.initialize_pool()
        
        with get_db_cursor() as cursor:
            # Query for existing tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            existing_tables = [row['table_name'] for row in cursor.fetchall()]
            
            print(f"\nFound {len(existing_tables)} table(s):")
            for table in existing_tables:
                status = "✓" if table in expected_tables else "?"
                print(f"  {status} {table}")
            
            # Check if all expected tables exist
            missing_tables = set(expected_tables) - set(existing_tables)
            if missing_tables:
                print(f"\n✗ Missing tables: {', '.join(missing_tables)}")
                return False
            
            print("\n✓ All expected tables exist!")
            return True
    
    except Exception as e:
        print(f"\n✗ Schema verification failed: {e}")
        return False
    
    finally:
        DatabaseConnection.close_pool()


if __name__ == "__main__":
    print("\nStarting database initialization...\n")
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / '.env'
    if not env_file.exists():
        print("⚠ Warning: .env file not found!")
        print("Please create a .env file with your database credentials.")
        print("You can copy .env.example and fill in your values.\n")
        sys.exit(1)
    
    # Run migrations
    success = init_database()
    
    if success:
        # Verify the schema
        verify_schema()
        print("\n✓ Database is ready to use!\n")
        sys.exit(0)
    else:
        print("\n✗ Database initialization failed!\n")
        sys.exit(1)
