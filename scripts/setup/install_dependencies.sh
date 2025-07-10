#!/bin/bash

# Muvera - Dependencies Installation Script
# This script sets up the Python environment and installs all required dependencies

set -e

echo "📦 Installing Muvera dependencies..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing Python packages..."
pip install -r requirements.txt

# Install PyTorch with appropriate backend
echo "🔥 Installing PyTorch..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if [[ $(uname -m) == "arm64" ]]; then
        # Apple Silicon
        pip install torch torchvision torchaudio
    else
        # Intel Mac
        pip install torch torchvision torchaudio
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux - install CUDA version if available
    if command -v nvidia-smi &> /dev/null; then
        echo "🚀 CUDA detected, installing PyTorch with CUDA support..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    else
        echo "💻 Installing CPU-only PyTorch..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    fi
fi

# Create config directory and default config
echo "⚙️ Creating configuration files..."
mkdir -p config

cat > config/default.yaml << 'EOF'
# Muvera Configuration

# Vespa settings
vespa:
  endpoint: "http://localhost:8080"
  document_api: "http://localhost:8080/document/v1"
  search_api: "http://localhost:8080/search/"

# Dataset settings
datasets:
  msmarco:
    passages_url: "https://msmarco.blob.core.windows.net/msmarcoranking/collection.tsv"
    queries_url: "https://msmarco.blob.core.windows.net/msmarcoranking/queries.dev.small.tsv"
    qrels_url: "https://msmarco.blob.core.windows.net/msmarcoranking/qrels.dev.small.tsv"
    max_passages: 100000  # Set to -1 for full dataset
    
# Embedding models
models:
  single_vector:
    model_name: "sentence-transformers/all-MiniLM-L6-v2"
    dimension: 384
    
  multi_vector:
    model_name: "colbert-ir/colbertv2.0"
    dimension: 128
    max_tokens: 512

# Evaluation settings
evaluation:
  metrics: ["ndcg_cut_10", "map", "recip_rank", "recall_100", "recall_1000"]
  query_batch_size: 32
  top_k: 1000
EOF

echo "✅ Dependencies installation complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Activate virtual environment: source venv/bin/activate"
echo "   2. Start Vespa: ./scripts/setup/start_vespa.sh"
echo "   3. Download data: python scripts/data_prep/download_msmarco.py"
echo ""
echo "💡 Configuration file created at: config/default.yaml"