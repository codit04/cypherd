-- Migration: Create accounts table
-- Description: Stores account information with HD derivation and balances

CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    address TEXT UNIQUE NOT NULL,
    encrypted_private_key TEXT NOT NULL,
    account_index INTEGER NOT NULL,
    label TEXT,
    balance NUMERIC(20, 8) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_wallet_account_index UNIQUE(wallet_id, account_index),
    CONSTRAINT check_balance_non_negative CHECK (balance >= 0),
    CONSTRAINT check_account_index_non_negative CHECK (account_index >= 0)
);

-- Index for looking up accounts by wallet (most common query)
CREATE INDEX IF NOT EXISTS idx_accounts_wallet_id ON accounts(wallet_id);
