"""
Complete setup verification script.
Verifies database connection, schema, and basic operations.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database import DatabaseConnection, get_db_cursor


def verify_connection():
    """Verify database connection."""
    print("1. Testing database connection...")
    try:
        DatabaseConnection.initialize_pool()
        with get_db_cursor() as cursor:
            cursor.execute("SELECT NOW()")
            result = cursor.fetchone()
            print(f"   ✓ Connection successful! Server time: {result['now']}")
        return True
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return False


def verify_tables():
    """Verify all required tables exist."""
    print("\n2. Verifying database schema...")
    
    expected_tables = ['wallets', 'accounts', 'transactions', 'notification_preferences']
    
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """)
            
            existing_tables = [row['table_name'] for row in cursor.fetchall()]
            
            all_exist = True
            for table in expected_tables:
                if table in existing_tables:
                    print(f"   ✓ Table '{table}' exists")
                else:
                    print(f"   ✗ Table '{table}' missing")
                    all_exist = False
            
            return all_exist
    
    except Exception as e:
        print(f"   ✗ Schema verification failed: {e}")
        return False


def verify_constraints():
    """Verify key constraints and indexes."""
    print("\n3. Verifying constraints and indexes...")
    
    try:
        with get_db_cursor() as cursor:
            # Check foreign keys
            cursor.execute("""
                SELECT COUNT(*) as fk_count
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                AND table_schema = 'public'
            """)
            fk_count = cursor.fetchone()['fk_count']
            print(f"   ✓ Found {fk_count} foreign key constraints")
            
            # Check indexes
            cursor.execute("""
                SELECT COUNT(*) as idx_count
                FROM pg_indexes
                WHERE schemaname = 'public'
            """)
            idx_count = cursor.fetchone()['idx_count']
            print(f"   ✓ Found {idx_count} indexes")
            
            return True
    
    except Exception as e:
        print(f"   ✗ Constraint verification failed: {e}")
        return False


def test_basic_operations():
    """Test basic CRUD operations."""
    print("\n4. Testing basic database operations...")
    
    try:
        with get_db_cursor() as cursor:
            # Test INSERT
            cursor.execute("""
                INSERT INTO wallets (id, encrypted_seed, password_hash, salt)
                VALUES (gen_random_uuid(), 'test_seed', 'test_hash', 'test_salt')
                RETURNING id
            """)
            wallet_id = cursor.fetchone()['id']
            print(f"   ✓ INSERT successful (wallet_id: {wallet_id})")
            
            # Test SELECT
            cursor.execute("SELECT COUNT(*) as count FROM wallets WHERE id = %s", (wallet_id,))
            count = cursor.fetchone()['count']
            print(f"   ✓ SELECT successful (found {count} record)")
            
            # Test UPDATE
            cursor.execute("""
                UPDATE wallets 
                SET is_locked = false 
                WHERE id = %s
                RETURNING is_locked
            """, (wallet_id,))
            is_locked = cursor.fetchone()['is_locked']
            print(f"   ✓ UPDATE successful (is_locked: {is_locked})")
            
            # Test DELETE
            cursor.execute("DELETE FROM wallets WHERE id = %s", (wallet_id,))
            print(f"   ✓ DELETE successful")
            
            return True
    
    except Exception as e:
        print(f"   ✗ Basic operations test failed: {e}")
        return False


def main():
    print("=" * 60)
    print("Database Setup Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Run all verification steps
    results.append(("Connection", verify_connection()))
    results.append(("Schema", verify_tables()))
    results.append(("Constraints", verify_constraints()))
    results.append(("Operations", test_basic_operations()))
    
    # Close connection pool
    DatabaseConnection.close_pool()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All verifications passed!")
        print("Your database is ready for development.")
        print("\nNext steps:")
        print("  - Implement Task 3: Crypto Manager utility")
        print("  - Implement Task 4: Repository layer")
        print("  - Implement Task 5: Wallet Service")
    else:
        print("\n⚠️  Some verifications failed.")
        print("Please review the errors above and fix any issues.")
    
    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
