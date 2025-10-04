#!/bin/bash

# Install Playwright browsers for Railway
echo "Installing Playwright browsers..."
python -m playwright install firefox

# Set environment variables for Railway
export HEADLESS=true
export HOST=0.0.0.0
export PORT=${PORT:-8000}

# Start the server
echo "Starting server on $HOST:$PORT"
python start_server.py