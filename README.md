# Mock Web3 Wallet

A simplified cryptocurrency wallet application that simulates Web3 wallet functionality without requiring actual blockchain integration.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)

## Features

### Core Wallet Features
- **Secure Wallet Creation**: Generate wallets with BIP39 12-word mnemonic seed phrases
- **Wallet Recovery**: Restore wallets from existing mnemonic phrases
- **HD Wallet Derivation**: Create multiple accounts using BIP44 hierarchical deterministic derivation (m/44'/60'/0'/0/index)
- **Password Protection**: Secure wallet access with bcrypt password hashing
- **Auto-Lock**: Automatic wallet locking after idle period for enhanced security

### Account Management
- **Multiple Accounts**: Create and manage multiple accounts within a single wallet
- **Custom Labels**: Assign custom labels to accounts for easy identification
- **Balance Tracking**: View individual account balances and total wallet balance
- **Address Management**: Copy-to-clipboard functionality for easy address sharing

### Transaction Features
- **Signature Approval System**: Secure transaction approval with Ethereum-style message signing
- **ETH/USD Conversion**: Real-time price conversion using Skip API
- **Price Tolerance Protection**: 1% price tolerance check for USD transfers
- **Transaction History**: Complete transaction history with filtering by account
- **Internal Transfers**: Seamless transfers between accounts within the same wallet
- **Transaction Memos**: Add optional notes to transactions

### Notifications
- **WhatsApp Integration**: Real-time WhatsApp notifications for transactions
- **Configurable Alerts**: Enable/disable notifications for incoming, outgoing, and security events
- **Test Notifications**: Verify notification setup with test messages

### Security Features
- **AES-256-GCM Encryption**: All private keys and seed phrases encrypted at rest
- **Message Signing**: Ethereum personal_sign standard for transaction approval
- **Signature Verification**: Backend verification of transaction signatures
- **Approval Expiration**: 30-second expiration window for transaction approvals
- **Input Validation**: Comprehensive validation of addresses, amounts, and user inputs

## Tech Stack

### Backend
- **FastAPI** - Modern, high-performance Python web framework
- **PostgreSQL** (Supabase) - Reliable relational database
- **psycopg2** - PostgreSQL database adapter
- **eth-account** - Ethereum signing and verification
- **mnemonic** - BIP39 mnemonic generation
- **bcrypt** - Secure password hashing
- **httpx** - Async HTTP client for Skip API integration
- **pywhatkit** - WhatsApp notification delivery
- **cryptography** - AES encryption for sensitive data
- **pydantic** - Data validation and settings management

### Frontend
- **Streamlit** - Interactive web interface
- **requests** - HTTP client for backend API communication
- **eth-account** - Client-side message signing

### External Services
- **Skip API** - Real-time ETH/USD price conversion
- **WhatsApp** - Transaction notifications via pywhatkit

## Architecture

The application follows a layered architecture pattern:

```
┌─────────────────────────────────────────┐
│         Streamlit Frontend              │
│  (User Interface & Client-side Signing) │
└──────────────┬──────────────────────────┘
               │ HTTP/REST
┌──────────────▼──────────────────────────┐
│          FastAPI Backend                │
│         (API Layer)                     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Service Layer                    │
│  (Business Logic & Orchestration)       │
│  - WalletService                        │
│  - AccountService                       │
│  - TransactionService                   │
│  - NotificationService                  │
│  - SkipAPIService                       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Repository Layer                   │
│     (Data Access)                       │
│  - WalletRepository                     │
│  - AccountRepository                    │
│  - TransactionRepository                │
│  - NotificationPreferencesRepository    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      PostgreSQL Database                │
│         (Supabase)                      │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│        Utility Layer                    │
│  - CryptoManager (Key derivation,       │
│    encryption, signing)                 │
│  - Database connection pooling          │
│  - Exception handling                   │
└─────────────────────────────────────────┘
```

### Key Design Patterns
- **Repository Pattern**: Abstracts data access logic
- **Service Layer Pattern**: Encapsulates business logic
- **Dependency Injection**: Services receive dependencies via constructors
- **RESTful API**: Standard HTTP methods and status codes

## Project Structure

```
mock-web3-wallet/
├── backend/
│   ├── config/
│   │   └── skip_api_config.json      # Skip API configuration
│   ├── migrations/
│   │   ├── 001_create_wallets_table.sql
│   │   ├── 002_create_accounts_table.sql
│   │   ├── 003_create_transactions_table.sql
│   │   ├── 004_create_notification_preferences_table.sql
│   │   ├── init_db.py                # Database initialization script
│   │   └── README.md
│   ├── models/
│   │   └── schemas.py                # Pydantic request/response models
│   ├── repositories/
│   │   ├── wallet_repository.py
│   │   ├── account_repository.py
│   │   ├── transaction_repository.py
│   │   └── notification_preferences_repository.py
│   ├── routers/
│   │   ├── wallets.py                # Wallet API endpoints
│   │   ├── accounts.py               # Account API endpoints
│   │   ├── transactions.py           # Transaction API endpoints
│   │   └── notifications.py          # Notification API endpoints
│   ├── services/
│   │   ├── wallet_service.py
│   │   ├── account_service.py
│   │   ├── transaction_service.py
│   │   ├── notification_service.py
│   │   └── skip_api_service.py
│   ├── utils/
│   │   ├── crypto_manager.py         # Cryptographic operations
│   │   ├── database.py               # Database connection
│   │   └── exceptions.py             # Custom exceptions
│   ├── main.py                       # FastAPI application entry point
│   ├── .env.example                  # Environment variables template
│   ├── start_api.sh                  # Backend startup script
│   └── API_DOCUMENTATION.md          # Detailed API documentation
├── frontend/
│   ├── app.py                        # Streamlit application
│   ├── api_client.py                 # Backend API client
│   ├── .env.example.frontend         # Frontend environment variables
│   └── start_frontend.sh             # Frontend startup script
├── .kiro/
│   ├── specs/mock-web3-wallet/       # Feature specification documents
│   ├── docs/                         # Additional documentation
│   └── tests/                        # Integration tests
├── requirements.txt                  # Python dependencies
├── TEST_ACCOUNTS.md                  # Test account information
└── README.md                         # This file
```

## Setup Instructions

### Prerequisites

- **Python 3.9 or higher**
- **PostgreSQL database** (Supabase recommended for easy setup)
- **Git** (for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd mock-web3-wallet
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes all necessary packages:
- FastAPI and Uvicorn (backend server)
- Streamlit (frontend)
- PostgreSQL adapter (psycopg2)
- Cryptography libraries (eth-account, mnemonic, cryptography, bcrypt)
- HTTP clients (httpx, requests)
- WhatsApp integration (pywhatkit)

### Step 4: Configure Environment Variables

#### Backend Configuration

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your Supabase credentials:

```env
# Supabase PostgreSQL Connection
host=your-project.pooler.supabase.com
port=6543
dbname=postgres
user=postgres.your-project-id
password=your-secure-password

# Optional: Skip API Configuration (uses defaults if not set)
# SKIP_API_URL=https://api.skip.build/v2/fungible/msgs_direct
```

**Getting Supabase Credentials:**
1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Project Settings > Database
4. Use the "Connection Pooling" credentials (port 6543)

#### Frontend Configuration

```bash
cp frontend/.env.example.frontend frontend/.env
```

Edit `frontend/.env`:

```env
# Backend API URL
BACKEND_URL=http://localhost:8000
```

### Step 5: Initialize Database

Run the database initialization script to create all required tables:

```bash
python3 backend/migrations/init_db.py
```

This will create:
- `wallets` table - Stores encrypted wallet data
- `accounts` table - Stores account information and balances
- `transactions` table - Stores transaction history
- `notification_preferences` table - Stores WhatsApp notification settings

### Step 6: Verify Setup

Test the database connection:

```bash
python3 backend/test_db_connection.py
```

You should see: "Database connection successful!"

## Running the Application

### Option 1: Using Startup Scripts (Recommended)

#### Start Backend
```bash
cd backend
./start_api.sh
```

#### Start Frontend (in a new terminal)
```bash
cd frontend
./start_frontend.sh
```

### Option 2: Manual Start

#### Start Backend
```bash
# From project root
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

#### Start Frontend
```bash
# From project root (in a new terminal)
cd frontend
streamlit run app.py
```

The frontend will be available at: http://localhost:8501


## Usage Guide

### 1. Creating a New Wallet

1. Open the application at http://localhost:8501
2. Click **"Create New Wallet"**
3. Enter a secure password (minimum 8 characters)
4. **IMPORTANT**: Save the 12-word mnemonic phrase securely
   - This is the ONLY way to recover your wallet
   - Write it down on paper and store it safely
   - Never share it with anyone
5. Confirm you've saved the mnemonic
6. Your wallet is created with a default account and random initial balance (1-10 ETH)

### 2. Restoring an Existing Wallet

1. Click **"Import Existing Wallet"**
2. Enter your 12-word mnemonic phrase
3. Enter your password
4. Click **"Restore Wallet"**
5. Your wallet and all accounts will be restored

### 3. Managing Accounts

#### Creating Additional Accounts
1. Navigate to **"Accounts"** page
2. Click **"Create New Account"**
3. Optionally provide a custom label
4. New account is created with 0 balance

#### Editing Account Labels
1. Go to **"Accounts"** page
2. Click the edit icon next to an account
3. Enter new label and save

#### Viewing Account Details
- Each account displays:
  - Ethereum address (with copy button)
  - Current balance
  - Custom label
  - Account index

### 4. Sending Transactions

#### ETH Transfer
1. Navigate to **"Send Transaction"** page
2. Select **From Account** (dropdown)
3. Enter **Recipient Address** (0x...)
4. Select **"ETH"** as currency
5. Enter **Amount** in ETH
6. Optionally add a **Memo**
7. Click **"Create Approval"**
8. Review the approval message
9. Click **"Confirm & Sign"** within 30 seconds
10. Transaction is executed and confirmed

#### USD Transfer (with Skip API conversion)
1. Follow steps 1-3 above
2. Select **"USD"** as currency
3. Enter **Amount** in USD
4. The system fetches current ETH price from Skip API
5. Review the ETH equivalent amount
6. Click **"Create Approval"**
7. Review and confirm within 30 seconds
8. System re-checks price (must be within 1% tolerance)
9. Transaction is executed if price is stable

#### Transaction Approval Flow
```
User initiates → Backend creates approval message (30s expiry)
                ↓
User reviews → Frontend signs message with private key
                ↓
User confirms → Backend verifies signature
                ↓
Signature valid → Backend executes transaction
                ↓
Balances updated → Transaction recorded in history
                ↓
Notification sent → WhatsApp alert (if enabled)
```

### 5. Viewing Transaction History

1. Navigate to **"Transaction History"** page
2. Filter by:
   - All accounts
   - Specific account
3. View transaction details:
   - Transaction ID
   - Timestamp
   - Type (Send/Receive/Internal)
   - Amount
   - From/To addresses
   - Memo
   - Status

### 6. Configuring Notifications

1. Navigate to **"Settings"** page
2. Scroll to **"Notification Preferences"**
3. Enter phone number in international format: `+1234567890`
4. Toggle **"Enable Notifications"**
5. Select notification types:
   - Incoming transactions
   - Outgoing transactions
   - Security alerts
6. Click **"Save Preferences"**
7. Click **"Send Test Notification"** to verify setup

**Note**: WhatsApp notifications require WhatsApp Web to be active on the server.

### 7. Security Features

#### Changing Password
1. Go to **"Settings"** page
2. Enter **Old Password**
3. Enter **New Password** (min 8 characters)
4. Click **"Change Password"**

#### Locking Wallet
1. Click **"Lock Wallet"** in Settings or sidebar
2. Wallet is locked immediately
3. Re-authentication required to access

## API Documentation

### Quick Reference

#### Wallet Endpoints
- `POST /api/wallet/create` - Create new wallet
- `POST /api/wallet/restore` - Restore from mnemonic
- `POST /api/wallet/authenticate` - Authenticate with password
- `POST /api/wallet/lock` - Lock wallet
- `GET /api/wallet/{wallet_id}` - Get wallet info
- `PUT /api/wallet/{wallet_id}/password` - Change password

#### Account Endpoints
- `POST /api/accounts` - Create new account
- `GET /api/accounts/{account_id}` - Get account details
- `GET /api/accounts/wallet/{wallet_id}` - List all accounts
- `PUT /api/accounts/{account_id}/label` - Update label
- `GET /api/accounts/{account_id}/balance` - Get balance
- `GET /api/accounts/wallet/{wallet_id}/balance` - Get total balance

#### Transaction Endpoints
- `POST /api/transactions/create-approval` - Create approval message
- `POST /api/transactions/send` - Execute transaction with signature
- `GET /api/transactions/{transaction_id}` - Get transaction details
- `GET /api/transactions/account/{account_id}` - Get transaction history

#### Notification Endpoints
- `POST /api/notifications/preferences` - Set preferences
- `GET /api/notifications/preferences/{wallet_id}` - Get preferences
- `POST /api/notifications/test` - Send test notification

### Interactive API Documentation

Once the backend is running, access interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

For detailed API documentation, see [backend/API_DOCUMENTATION.md](backend/API_DOCUMENTATION.md)

Demo Video : https://drive.google.com/file/d/1fxeSj9Jw_LPDSHjWL_VU952cGnwaYKvv/view?usp=sharing
Schema Diagram : https://drive.google.com/file/d/1Wr7GMK3b2bS1-Yeea6-J7mQJ1sQmS-fc/view?usp=sharing

