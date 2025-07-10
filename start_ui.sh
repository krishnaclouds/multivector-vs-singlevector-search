#!/bin/bash

echo "🌐 Starting Muvera Web UI..."
echo "================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check if Vespa is running
if ! docker ps | grep -q vespa; then
    echo "⚠️  Vespa container not running. Starting Vespa..."
    ./setup_vespa.sh
    echo "⏳ Waiting for Vespa to start..."
    sleep 10
fi

# Activate virtual environment and start web UI
source venv/bin/activate

echo "🚀 Starting web interface..."
echo "📍 Access at: http://localhost:5000"
echo ""
echo "💡 Features:"
echo "  • Compare single vs multi-vector search"
echo "  • Real-time performance metrics"
echo "  • Interactive result comparison"
echo "  • System status monitoring"
echo ""
echo "🔍 Try sample queries or enter your own!"
echo "================================"
echo ""

python web_ui.py