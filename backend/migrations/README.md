# Database Migrations

This directory contains SQL migration scripts for setting up the Mock Web3 Wallet database schema.

## Migration Files

The migrations are numbered and run in order:

1. **001_create_wallets_table.sql** - Creates the wallets table for storing wallet information
2. **002_create_accounts_table.sql** - Creates the accounts table with foreign key to wallets
3. **003_create_transactions_table.sql** - Creates the transactions table with foreign keys to accounts
4. **004_create_notification_preferences_table.sql** - Creates the notification preferences table

## Running Migrations

### Prerequisites

1. Ensure you have a `.env` file in the `backend/` directory with your database credentials:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Edit the `.env` file and add your Supabase PostgreSQL credentials:
   ```
   # Option 1: Use DATABASE_URL (recommended)
   DATABASE_URL=postgresql://user:password@host:port/database
   
   # Option 2: Use individual parameters (uppercase)
   DB_HOST=your-supabase-host.supabase.co
   DB_PORT=5432
   DB_NAME=postgres
   DB_USER=postgres
   DB_PASSWORD=your-database-password
   
   # Option 3: Use individual parameters (lowercase - also supported)
   host=your-supabase-host.supabase.co
   port=5432
   dbname=postgres
   user=postgres
   password=your-database-password
   ```

### Initialize Database

Run the initialization script from the project root:

```bash
python backend/migrations/init_db.py
```

This will:
- Run all migration scripts in order
- Create all tables with proper constraints and indexes
- Verify that all tables were created successfully
- Roll back all changes if any migration fails

### Manual Migration

If you prefer to run migrations manually, you can execute each SQL file directly:

```bash
psql $DATABASE_URL -f backend/migrations/001_create_wallets_table.sql
psql $DATABASE_URL -f backend/migrations/002_create_accounts_table.sql
psql $DATABASE_URL -f backend/migrations/003_create_transactions_table.sql
psql $DATABASE_URL -f backend/migrations/004_create_notification_preferences_table.sql
```

## Database Schema

### Tables

#### wallets
- Stores wallet information including encrypted seed phrase and authentication data
- Primary key: `id` (UUID, derived from mnemonic)
- Contains: encrypted_seed, password_hash, salt, timestamps, lock status

#### accounts
- Stores HD-derived accounts for each wallet
- Primary key: `id` (UUID)
- Foreign key: `wallet_id` references wallets(id)
- Contains: address, encrypted_private_key, account_index, label, balance

#### transactions
- Stores transaction history
- Primary key: `id` (UUID)
- Foreign keys: `from_account_id`, `to_account_id` reference accounts(id)
- Contains: addresses, amount, memo, type, status, timestamp

#### notification_preferences
- Stores WhatsApp notification preferences per wallet
- Primary key: `id` (UUID)
- Foreign key: `wallet_id` references wallets(id)
- Contains: phone_number, enabled flags for different notification types

## Indexes

All tables have appropriate indexes for:
- Foreign key relationships
- Frequently queried columns (addresses, timestamps)
- Sorting operations (created_at DESC)

## Constraints

- Foreign key constraints with CASCADE/SET NULL on delete
- Unique constraints on addresses and wallet-account combinations
- Check constraints for valid values (balance >= 0, valid transaction types, etc.)
