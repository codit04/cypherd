# Mock Web3 Wallet API Documentation

## Overview

This document provides comprehensive documentation for the Mock Web3 Wallet REST API built with FastAPI.

## Base URL

```
http://localhost:8000
```

## API Endpoints

### Health Check

#### GET /
Root endpoint for health check.

**Response:**
```json
{
  "status": "ok",
  "message": "Mock Web3 Wallet API is running",
  "version": "1.0.0"
}
```

#### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "mock-web3-wallet-api"
}
```

---

## Wallet Endpoints

### POST /api/wallet/create
Create a new wallet with a generated mnemonic.

**Request Body:**
```json
{
  "password": "string (min 8 characters)"
}
```

**Response (201 Created):**
```json
{
  "wallet_id": "uuid",
  "mnemonic": "12-word mnemonic phrase",
  "first_account": {
    "id": "uuid",
    "wallet_id": "uuid",
    "address": "0x...",
    "account_index": 0,
    "label": "Account 1",
    "balance": "5.12345678"
  }
}
```

### POST /api/wallet/restore
Restore a wallet from an existing mnemonic.

**Request Body:**
```json
{
  "mnemonic": "12-word mnemonic phrase",
  "password": "string (min 8 characters)"
}
```

**Response (200 OK):**
```json
{
  "wallet_id": "uuid",
  "exists": true,
  "accounts": [...]
}
```

### POST /api/wallet/authenticate
Authenticate with wallet password.

**Request Body:**
```json
{
  "wallet_id": "uuid",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Authentication successful"
}
```

### POST /api/wallet/lock
Lock a wallet.

**Request Body:**
```json
{
  "wallet_id": "uuid"
}
```

**Response (200 OK):**
```json
{
  "message": "Wallet locked successfully"
}
```

### POST /api/wallet/unlock
Unlock a wallet with password.

**Request Body:**
```json
{
  "wallet_id": "uuid",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Wallet unlocked successfully"
}
```

### GET /api/wallet/{wallet_id}
Get wallet information.

**Response (200 OK):**
```json
{
  "wallet_id": "uuid",
  "created_at": "2024-01-01T00:00:00",
  "last_accessed": "2024-01-01T00:00:00",
  "is_locked": false,
  "account_count": 3
}
```

### PUT /api/wallet/{wallet_id}/password
Change wallet password.

**Request Body:**
```json
{
  "wallet_id": "uuid",
  "old_password": "string",
  "new_password": "string (min 8 characters)"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

---

## Account Endpoints

### POST /api/accounts
Create a new account for a wallet.

**Request Body:**
```json
{
  "wallet_id": "uuid",
  "password": "string",
  "label": "string (optional)"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "wallet_id": "uuid",
  "address": "0x...",
  "account_index": 1,
  "label": "Account 2",
  "balance": "0.0",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### GET /api/accounts/{account_id}
Get account details by ID.

**Response (200 OK):**
```json
{
  "id": "uuid",
  "wallet_id": "uuid",
  "address": "0x...",
  "account_index": 0,
  "label": "Account 1",
  "balance": "5.12345678",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### GET /api/accounts/address/{address}
Get account details by Ethereum address.

**Response (200 OK):**
Same as GET /api/accounts/{account_id}

### GET /api/accounts/wallet/{wallet_id}
List all accounts for a wallet.

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "wallet_id": "uuid",
    "address": "0x...",
    "account_index": 0,
    "label": "Account 1",
    "balance": "5.12345678",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  ...
]
```

### PUT /api/accounts/{account_id}/label
Update account label.

**Request Body:**
```json
{
  "label": "string"
}
```

**Response (200 OK):**
```json
{
  "message": "Account label updated successfully"
}
```

### GET /api/accounts/{account_id}/balance
Get account balance.

**Response (200 OK):**
```json
{
  "account_id": "uuid",
  "balance": "5.12345678"
}
```

### GET /api/accounts/wallet/{wallet_id}/balance
Get total wallet balance across all accounts.

**Response (200 OK):**
```json
{
  "wallet_id": "uuid",
  "total_balance": "15.87654321",
  "account_count": 3
}
```

---

## Transaction Endpoints

### POST /api/transactions/create-approval
Create an approval message for a transaction.

**Request Body:**
```json
{
  "from_account_id": "uuid",
  "to_address": "0x...",
  "amount_eth": 1.5,  // Optional: specify ETH amount
  "amount_usd": 100.0,  // Optional: specify USD amount (will convert to ETH)
  "memo": "string (optional)"
}
```

**Note:** Specify either `amount_eth` OR `amount_usd`, not both.

**Response (201 Created):**
```json
{
  "message": "Transfer 1.5 ETH to 0x... from 0x...",
  "message_id": "uuid",
  "expires_at": "2024-01-01T00:00:30",
  "eth_amount": "1.5",
  "usd_amount": null
}
```

### POST /api/transactions/send
Execute a transaction with signature.

**Request Body:**
```json
{
  "message_id": "uuid",
  "signature": "0x... (hex signature)"
}
```

**Response (201 Created):**
```json
{
  "transaction_id": "uuid",
  "from_address": "0x...",
  "to_address": "0x...",
  "amount": "1.5",
  "memo": "Payment for services",
  "transaction_type": "send",
  "status": "completed",
  "created_at": "2024-01-01T00:00:00"
}
```

### GET /api/transactions/{transaction_id}
Get transaction details by ID.

**Response (200 OK):**
```json
{
  "transaction_id": "uuid",
  "from_address": "0x...",
  "to_address": "0x...",
  "amount": "1.5",
  "memo": "Payment for services",
  "transaction_type": "send",
  "status": "completed",
  "created_at": "2024-01-01T00:00:00"
}
```

### GET /api/transactions/account/{account_id}
Get transaction history for an account.

**Query Parameters:**
- `limit` (optional): Maximum number of transactions (default: 50, max: 100)

**Response (200 OK):**
```json
[
  {
    "transaction_id": "uuid",
    "from_address": "0x...",
    "to_address": "0x...",
    "amount": "1.5",
    "memo": "Payment for services",
    "transaction_type": "send",
    "status": "completed",
    "created_at": "2024-01-01T00:00:00"
  },
  ...
]
```

### DELETE /api/transactions/cleanup-expired
Clean up expired approval messages (maintenance endpoint).

**Response (200 OK):**
```json
{
  "message": "Cleaned up 5 expired approval messages",
  "count": 5
}
```

---

## Notification Endpoints

### POST /api/notifications/preferences
Set or update notification preferences.

**Request Body:**
```json
{
  "wallet_id": "uuid",
  "phone_number": "+1234567890",
  "enabled": true,
  "notify_incoming": true,
  "notify_outgoing": true,
  "notify_security": true
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "wallet_id": "uuid",
  "phone_number": "+1234567890",
  "enabled": true,
  "notify_incoming": true,
  "notify_outgoing": true,
  "notify_security": true,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### GET /api/notifications/preferences/{wallet_id}
Get notification preferences for a wallet.

**Response (200 OK):**
Same as POST response.

### POST /api/notifications/test
Send a test notification.

**Request Body:**
```json
{
  "phone_number": "+1234567890"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Test notification sent successfully"
}
```

### DELETE /api/notifications/preferences/{wallet_id}
Delete notification preferences.

**Response (200 OK):**
```json
{
  "message": "Notification preferences deleted successfully"
}
```

---

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "status_code": 400
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Validation error or invalid input
- `401 Unauthorized`: Authentication failed
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Running the API

### Development Mode

```bash
# From project root
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# From project root
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Interactive API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Authentication Flow

1. **Create Wallet**: POST /api/wallet/create
   - Save the mnemonic securely!
   - Returns wallet_id

2. **Authenticate**: POST /api/wallet/authenticate
   - Use wallet_id and password
   - Unlocks the wallet

3. **Use Wallet**: Access other endpoints with wallet_id

4. **Lock Wallet**: POST /api/wallet/lock
   - Requires re-authentication

---

## Transaction Flow

1. **Create Approval**: POST /api/transactions/create-approval
   - Specify amount in ETH or USD
   - Returns message to sign and message_id
   - Approval expires in 30 seconds

2. **Sign Message**: (Client-side)
   - Use eth-account to sign the approval message
   - Generate signature

3. **Send Transaction**: POST /api/transactions/send
   - Submit message_id and signature
   - Backend verifies signature
   - Executes transaction if valid

---

## Notes

- All ETH amounts use 8 decimal precision
- USD amounts are converted to ETH via Skip API
- Price tolerance for USD transfers: 1%
- Approval messages expire after 30 seconds
- Phone numbers must be in format: +[country_code][number]
