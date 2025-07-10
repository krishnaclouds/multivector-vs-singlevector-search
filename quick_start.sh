#!/bin/bash
# Muvera Quick Start Script
# One-command setup for the entire project

set -e

echo "🚀 Muvera Quick Start"
echo "===================="
echo

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Make setup script executable
chmod +x setup.py

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install basic dependencies first
echo "📦 Installing basic dependencies..."
pip install --upgrade pip
pip install pyyaml requests

# Run comprehensive setup
echo "🔧 Running comprehensive setup..."
python setup.py

# Make other scripts executable
chmod +x scripts/setup/*.sh
chmod +x scripts/data_prep/*.py
chmod +x scripts/experiments/*.py

echo
echo "✅ Quick start complete!"
echo
echo "🎯 To get started:"
echo "   source venv/bin/activate"
echo "   python scripts/data_prep/download_msmarco.py"
echo "   python scripts/data_prep/generate_embeddings.py"
echo "   python scripts/experiments/run_indexing.py"
echo
echo "🌐 To start the web UI:"
echo "   python src/ui/web_ui.py"
echo
echo "📊 To run evaluation:"
echo "   python scripts/experiments/run_evaluation.py"