# Mock Web3 Wallet

A simplified cryptocurrency wallet application that simulates Web3 wallet functionality.

- Secure wallet creation with BIP39 mnemonic seed phrases
- Multiple account management with HD derivation
- Send and receive mock cryptocurrency transactions
- Transaction history tracking
- Password-protected wallet with auto-lock
- WhatsApp notifications for transactions
- ETH/USD conversion using Skip API
- Transaction signature approval system

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** (Supabase) - Database
- **psycopg2** - PostgreSQL adapter
- **eth-account** - Ethereum signing and verification
- **mnemonic** - BIP39 mnemonic generation
- **bcrypt** - Password hashing
- **httpx** - Async HTTP client

### Frontend
- **Streamlit** - Web interface
- **requests** - HTTP client for API calls

## Project Structure

```
mock-web3-wallet/
├── backend/
│   ├── migrations/       # Database schema migrations
│   ├── models/           # Pydantic models and schemas
│   ├── repositories/     # Data access layer
│   ├── routers/          # FastAPI route handlers
│   ├── services/         # Business logic layer
│   ├── utils/            # Utility functions (database, crypto)
│   ├── main.py           # FastAPI application entry point
│   └── .env.example      # Environment variables template
├── frontend/
│   ├── app.py            # Streamlit application
│   └── .env.example      # Frontend environment variables
├── requirements.txt      # Python dependencies
└── README.md
```

## Setup

### Prerequisites

- Python 3.9 or higher
- PostgreSQL database (Supabase recommended)

### Installation

1. Clone the repository and navigate to the project directory

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example.frontend frontend/.env
   ```
   Edit `backend/.env` with your Supabase credentials:
   ```
   host=your-supabase-host.pooler.supabase.com
   port=6543
   dbname=postgres
   user=postgres.your-project-id
   password=your-password
   ```

5. Initialize database:
   ```bash
   python3 backend/migrations/init_db.py
   ```

### Running

Start the backend:
```bash
cd backend
uvicorn main:app --reload
```

Start the frontend (in a new terminal):
```bash
cd frontend
streamlit run app.py
```

Access the application at http://localhost:8501
