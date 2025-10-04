#!/bin/bash
# Local development startup script for Schmick Membership Service

set -e

echo "🚀 Starting Schmick Membership Service..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your settings:"
    echo "   cp .env.example .env"
    echo "   # Then edit .env with your actual values"
    exit 1
fi

# Load environment variables
source .env

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python -m playwright install chromium

# Validate required environment variables
echo "🔍 Validating configuration..."
if [ -z "$PLAYWRIGHT_API_KEY" ] || [ -z "$SCHMICK_USER" ] || [ -z "$SCHMICK_PASS" ]; then
    echo "❌ Error: Missing required environment variables!"
    echo "📝 Please check your .env file and ensure these are set:"
    echo "   PLAYWRIGHT_API_KEY"
    echo "   SCHMICK_USER" 
    echo "   SCHMICK_PASS"
    exit 1
fi

# Set default port if not specified
PORT=${PORT:-8000}

echo "✅ Configuration validated successfully!"
echo "🎯 Starting server on port $PORT..."
echo "🔗 Health check: http://localhost:$PORT/health"
echo "📚 API docs: http://localhost:$PORT/docs"
echo ""
echo "💡 Tips:"
echo "   - Set HEADLESS=false in .env to see the browser in action"
echo "   - Check logs for detailed operation information"
echo "   - Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
uvicorn app:app --reload --host 0.0.0.0 --port "$PORT"