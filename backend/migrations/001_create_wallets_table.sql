-- Migration: Create wallets table
-- Description: Stores wallet information including encrypted seed and authentication data

CREATE TABLE IF NOT EXISTS wallets (
    id UUID PRIMARY KEY,
    encrypted_seed TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP,
    is_locked BOOLEAN DEFAULT TRUE
);
