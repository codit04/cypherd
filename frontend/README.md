# Mock Web3 Wallet - Frontend

Streamlit-based web interface for the Mock Web3 Wallet application.

## Setup

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Configure Environment**

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set the backend API URL (default: `http://localhost:8000`).

3. **Start the Backend**

Make sure the FastAPI backend is running before starting the frontend:

```bash
cd ../backend
python main.py
# Or use uvicorn directly:
# uvicorn backend.main:app --reload
```

4. **Run the Frontend**

From the workspace root:
```bash
./frontend/start_frontend.sh
```

Or from within the frontend directory:
```bash
cd frontend
python -m streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`.

## Features

### Welcome/Authentication Page

- **Create New Wallet**: Generate a new wallet with a 12-word mnemonic phrase
- **Import Wallet**: Restore an existing wallet using your mnemonic phrase
- **Unlock Wallet**: Access an existing wallet with your wallet ID and password

### Wallet Creation Flow

1. Enter a secure password (minimum 8 characters)
2. Receive a 12-word mnemonic phrase
3. **Important**: Save the mnemonic phrase securely - it's the only way to recover your wallet
4. Confirm you've saved the mnemonic
5. Access your wallet dashboard

### Wallet Import Flow

1. Enter your 12-word mnemonic phrase
2. Set a password to protect the wallet
3. Access your wallet with all existing accounts restored

### Wallet Unlock Flow

1. Enter your wallet ID
2. Enter your password
3. Access your wallet dashboard

## Project Structure

```
frontend/
├── app.py              # Main Streamlit application
├── api_client.py       # API client for backend communication
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment configuration
└── README.md          # This file
```

## Environment Variables

- `API_BASE_URL`: Backend API URL (default: `http://localhost:8000`)

## Security Notes

- Never share your mnemonic phrase with anyone
- Use a strong password (minimum 8 characters)
- The mnemonic phrase is displayed only once during wallet creation
- Store your mnemonic phrase in a secure location (not on your computer)

## Troubleshooting

### Cannot connect to backend

- Ensure the backend is running on the configured URL
- Check that the `API_BASE_URL` in `.env` matches your backend URL
- Verify there are no firewall issues blocking the connection

### Wallet creation fails

- Ensure your password is at least 8 characters long
- Check the backend logs for detailed error messages
- Verify the database is properly configured and accessible

### Import wallet fails

- Verify your mnemonic phrase is exactly 12 words
- Ensure there are no extra spaces or special characters
- Check that the mnemonic is valid (BIP39 standard)
