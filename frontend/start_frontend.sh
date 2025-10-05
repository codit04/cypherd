#!/bin/bash

# Start the Streamlit frontend for Mock Web3 Wallet

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Starting Mock Web3 Wallet Frontend..."
echo "Make sure the backend is running at the configured API_BASE_URL"
echo ""

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
    elif [ -f .env.example.frontend ]; then
        echo "Creating .env from .env.example.frontend..."
        cp .env.example.frontend .env
    else
        echo "Warning: No .env.example file found. Creating default .env..."
        echo "API_BASE_URL=http://localhost:8000" > .env
    fi
fi

echo "Starting Streamlit application..."
echo ""

# Run Streamlit using python -m to ensure it uses the correct environment
python3 -m streamlit run app.py
