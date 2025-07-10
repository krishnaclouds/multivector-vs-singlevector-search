# Muvera

Muvera is a comprehensive framework for understanding and evaluating the power of multi-vector search using Vespa. It demonstrates the differences between single dense vectors and multi-vector (ColBERT-style) approaches for semantic search.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Python 3.8+
- 8GB+ RAM recommended

### One-Command Setup
```bash
# Complete setup in one command
./quick_start.sh
```

### Manual Setup

1. **Run comprehensive setup:**
```bash
python setup.py
```

2. **OR use the CLI interface:**
```bash
# Setup project
python muvera.py setup

# Download data
python muvera.py download

# Generate embeddings
python muvera.py embeddings

# Run indexing
python muvera.py index

# Start evaluation
python muvera.py evaluate

# Launch web UI
python muvera.py ui

# Run complete pipeline
python muvera.py pipeline
```

3. **Check project status:**
```bash
python muvera.py status
```

## 🏗️ Production-Ready Architecture

### Project Structure

```
ASMuvera/
├── src/                      # Source code
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration management
│   │   └── index_to_vespa.py # Vespa indexing
│   ├── data/                 # Data processing
│   │   ├── process_data_simple.py
│   │   └── generate_embeddings_simple.py
│   ├── evaluation/           # Evaluation and metrics
│   │   └── search_evaluation.py
│   ├── ui/                   # User interfaces
│   │   ├── web_ui.py         # Web interface
│   │   ├── demo.py           # Interactive demo
│   │   ├── templates/        # HTML templates
│   │   └── static/           # Static assets
│   └── utils/                # Utility functions
│       └── manage_data.py    # Data management
├── tests/                    # Test suite
├── data/                     # Data storage
│   ├── raw/                  # Raw downloaded data
│   ├── processed/            # Processed data in JSONL format
│   └── embeddings/           # Generated embeddings
├── vespa/                    # Vespa configuration
│   ├── schemas/              # Vespa schema definitions
│   ├── services.xml          # Vespa services configuration
│   └── hosts.xml             # Vespa hosts configuration
├── scripts/                  # Utility scripts
│   ├── setup/                # Environment setup scripts
│   ├── data_prep/            # Data download and processing
│   └── experiments/          # Experiment runners
├── config/                   # Configuration files
│   └── default.yaml          # Default configuration
├── logs/                     # Log files
├── muvera.py                 # Main CLI entry point
├── setup.py                  # Comprehensive setup script
├── quick_start.sh            # One-command setup
└── pyproject.toml            # Package configuration
```

### Configuration Management

The project uses a centralized configuration system with environment variable support:

```bash
# Environment variables (optional)
export VESPA_ENDPOINT=http://localhost:8080
export MAX_PASSAGES=100000
export SINGLE_VECTOR_MODEL=sentence-transformers/all-MiniLM-L6-v2
export LOG_LEVEL=INFO

# Or use configuration files
# config/default.yaml
# .env file
```

## 🔬 Architecture Overview

Muvera implements two distinct semantic search approaches:

### Single Vector Approach
- **Embedding**: One 384-dimensional dense vector per document
- **Storage**: `tensor<float>(x[384])` in Vespa
- **Search**: Cosine similarity between query and document vectors
- **Pros**: Fast, simple, memory efficient
- **Cons**: Limited granular matching, information bottleneck

### Multi-Vector Approach (ColBERT-style)
- **Embedding**: Multiple token-level vectors (128-dimensional each)
- **Storage**: `tensor<float>(token{}, x[128])` in Vespa  
- **Search**: MaxSim operations between query and document token vectors
- **Pros**: Fine-grained matching, captures token interactions
- **Cons**: Higher latency, more storage requirements

## 📊 Evaluation Framework

Run comprehensive evaluations:

```bash
# Using CLI
python muvera.py evaluate

# Direct evaluation
python src/evaluation/search_evaluation.py --max-queries 5

# Results saved to evaluation_results.json
```

The evaluation compares:
- **Single Vector**: Dense semantic search
- **Multi-Vector**: ColBERT-style token matching
- **Text-only**: BM25 keyword search
- **Hybrid**: Combined text + semantic ranking

## 🛠️ Key Components

### Data Pipeline
- `src/data/process_data_simple.py` - Downloads and processes MS MARCO data
- `src/data/generate_embeddings_simple.py` - Creates both single and multi-vector embeddings

### Indexing
- `src/core/index_to_vespa.py` - Indexes documents into Vespa with proper tensor formatting
- Support for both single and multi-vector document schemas

### Search & Evaluation
- `src/evaluation/search_evaluation.py` - Comprehensive evaluation framework
- `src/ui/demo.py` - Interactive demonstration
- `src/ui/web_ui.py` - Web-based interactive interface
- Multiple ranking profiles (semantic, text, hybrid)

### Vespa Configuration
- `vespa/schemas/single_vector_document.sd` - Single vector schema
- `vespa/schemas/multi_vector_document.sd` - Multi-vector schema  
- `vespa/services.xml` - Vespa service configuration

## 📈 Performance Insights

Based on evaluation results:

- **Speed**: Text-only (BM25) > Single Vector > Multi-Vector
- **Relevance**: Context-dependent, multi-vector shows promise for complex queries
- **Storage**: Multi-vector requires ~10x more storage than single vector
- **Scalability**: Single vector scales better to large document collections

## 🎯 Use Cases

**Single Vector is ideal for:**
- High-throughput applications
- Large document collections
- Simple semantic similarity tasks
- Resource-constrained environments

**Multi-Vector excels at:**
- Complex information needs
- Fine-grained semantic matching
- Research and analysis tasks
- When accuracy matters more than speed

## 🌐 Web Interface Features

The interactive web UI (`http://localhost:5000`) provides:

- **Real-time Search Comparison**: Test all approaches simultaneously
- **Performance Metrics**: Live timing and relevance scoring
- **System Status**: Monitor Vespa health and document counts
- **Sample Queries**: Pre-built queries for quick testing
- **Mobile Responsive**: Works on desktop, tablet, and mobile
- **Visual Comparison**: Side-by-side result comparison

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build and run with Docker
docker build -t muvera .
docker run -p 5000:5000 -p 8080:8080 muvera

# Or use Docker Compose
docker-compose up -d
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f k8s/
```

### Environment Variables
```bash
# Production configuration
VESPA_ENDPOINT=https://your-vespa-cluster.com
MAX_PASSAGES=1000000
LOG_LEVEL=WARNING
FLASK_ENV=production
```

## 🔧 Development

### Installation for Development
```bash
# Install in development mode
pip install -e .[dev]

# Run tests
python -m pytest tests/

# Code formatting
black src/ tests/

# Type checking
mypy src/
```

### Testing
```bash
# Run all tests
python -m pytest

# Run specific test
python -m pytest tests/test_multi_vector.py

# Run with coverage
python -m pytest --cov=src
```

## 📚 Learning Resources

- **DESIGN.md** - Detailed architectural documentation
- **GIT_GUIDELINES.md** - Git workflow and file management
- **DATA_SETUP.md** - Instructions for setting up data files
- **Vespa Documentation** - https://docs.vespa.ai/
- **ColBERT Paper** - https://arxiv.org/abs/2004.12832
- **MS MARCO Dataset** - https://microsoft.github.io/msmarco/

## 🗂️ Data Management

Large data files (embeddings, datasets) are excluded from git. Use the data management script:

```bash
# Check data file status
python src/utils/manage_data.py --check

# Clean large files before committing
python src/utils/manage_data.py --clean

# Create data manifest
python src/utils/manage_data.py --manifest
```

## 🔍 Troubleshooting

### Common Issues

1. **Vespa not starting**: Check Docker is running and port 8080 is available
2. **Out of memory**: Reduce MAX_PASSAGES or increase Docker memory limit
3. **Slow indexing**: Reduce batch size or document count
4. **Connection refused**: Ensure Vespa is fully started (wait 30s after container start)

### Logs
```bash
# View logs
tail -f logs/muvera.log

# Check Vespa logs
docker logs vespa
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Muvera** - Advancing our understanding of multi-vector search architectures 🔍✨