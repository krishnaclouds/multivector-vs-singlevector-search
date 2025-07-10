# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Muvera is a comprehensive research project designed to understand and compare the power of multi-vector representations versus single-vector representations in semantic search using Vespa.

## Quick Setup Commands

```bash
# 1. Install dependencies and set up environment
./scripts/setup/install_dependencies.sh

# 2. Activate virtual environment
source venv/bin/activate

# 3. Start Vespa locally
./scripts/setup/start_vespa.sh

# 4. Download and process MS MARCO dataset
python scripts/data_prep/download_msmarco.py

# 5. Generate embeddings
python scripts/data_prep/generate_embeddings.py

# 6. Run indexing experiments
python scripts/experiments/run_indexing.py

# 7. Run evaluation
python scripts/experiments/run_evaluation.py
```

## Project Architecture

### Core Components
- **vespa/**: Vespa application configuration with schemas for single and multi-vector documents
- **scripts/setup/**: Environment setup and Vespa deployment scripts
- **scripts/data_prep/**: Data download, processing, and embedding generation
- **scripts/experiments/**: Experiment runners and evaluation framework
- **indexing/**: Single and multi-vector indexing pipeline implementations
- **evaluation/**: Metrics calculation and benchmarking tools

### Key Technologies
- **Vespa**: Search platform for indexing and querying
- **Python**: Data processing and ML pipeline
- **sentence-transformers**: Single-vector embeddings
- **ColBERT**: Multi-vector token-level embeddings
- **MS MARCO**: Primary evaluation dataset

### Vespa Schema Design
- **single_vector_document**: Documents with single dense vector embeddings (384 dim)
- **multi_vector_document**: Documents with multi-vector ColBERT embeddings (128 dim per token)
- Multiple ranking profiles for different search strategies

## Development Workflow

1. **Data Pipeline**: Download → Process → Generate Embeddings → Index
2. **Experiments**: Single Vector vs Multi Vector comparison
3. **Evaluation**: NDCG@10, MAP, MRR, Recall metrics
4. **Analysis**: Performance, storage, and latency trade-offs

## Configuration

Main configuration in `config/default.yaml`:
- Vespa endpoints and settings
- Dataset URLs and processing parameters
- Embedding model configurations
- Evaluation metrics and parameters