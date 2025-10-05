-- Migration: Create transactions table
-- Description: Stores transaction history with sender/recipient information

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
    to_account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
    from_address TEXT NOT NULL,
    to_address TEXT NOT NULL,
    amount NUMERIC(20, 8) NOT NULL,
    memo TEXT,
    transaction_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT check_amount_positive CHECK (amount > 0),
    CONSTRAINT check_transaction_type CHECK (transaction_type IN ('send', 'receive', 'internal')),
    CONSTRAINT check_status CHECK (status IN ('completed', 'pending', 'failed'))
);

-- Index for looking up transactions by account (most common query)
CREATE INDEX IF NOT EXISTS idx_transactions_from_account_id ON transactions(from_account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_to_account_id ON transactions(to_account_id);
