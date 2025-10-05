-- Migration: Create notification_preferences table
-- Description: Stores user notification preferences for WhatsApp notifications

CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    wallet_id UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    phone_number TEXT,
    enabled BOOLEAN DEFAULT FALSE,
    notify_incoming BOOLEAN DEFAULT TRUE,
    notify_outgoing BOOLEAN DEFAULT TRUE,
    notify_security BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT unique_wallet_notification_prefs UNIQUE(wallet_id)
);
