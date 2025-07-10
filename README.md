# ASMuvera: Advanced Semantic Multi-Vector Evaluation and Research Architecture

ASMuvera is a comprehensive framework for understanding and evaluating the power of multi-vector search using Vespa. It demonstrates the differences between single dense vectors and multi-vector (ColBERT-style) approaches for semantic search.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop
- Python 3.8+
- 8GB+ RAM recommended

### Setup

1. **Set up Python environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Start Vespa:**
```bash
./setup_vespa.sh
```

3. **Download and process data:**
```bash
python process_data_simple.py
```

4. **Generate embeddings:**
```bash
python generate_embeddings_simple.py
```

5. **Index documents:**
```bash
# Index single vector documents
python index_to_vespa.py --type single --max-docs 10

# Index multi-vector documents  
python index_to_vespa.py --type multi --max-docs 5
```

6. **Run the demonstration:**
```bash
python demo.py
```

7. **Start the Web UI (Interactive):**
```bash
./start_ui.sh
# Or manually:
# source venv/bin/activate && python web_ui.py
# Then open http://localhost:5000
```

## 🔬 Architecture Overview

ASMuvera implements two distinct semantic search approaches:

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
# Evaluate with 5 queries
python search_evaluation.py --max-queries 5

# Results saved to evaluation_results.json
```

The evaluation compares:
- **Single Vector**: Dense semantic search
- **Multi-Vector**: ColBERT-style token matching
- **Text-only**: BM25 keyword search
- **Hybrid**: Combined text + semantic ranking

## 🛠️ Key Components

### Data Pipeline
- `process_data_simple.py` - Downloads and processes MS MARCO data
- `generate_embeddings_simple.py` - Creates both single and multi-vector embeddings

### Indexing
- `index_to_vespa.py` - Indexes documents into Vespa with proper tensor formatting
- Support for both single and multi-vector document schemas

### Search & Evaluation
- `search_evaluation.py` - Comprehensive evaluation framework
- `demo.py` - Interactive demonstration
- `web_ui.py` - Web-based interactive interface
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

### Web UI Components

- **Search Interface**: Enter queries and select result count
- **Performance Dashboard**: Compare speed and relevance
- **Result Panels**: Detailed results for each approach
- **System Monitor**: Real-time system health status

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
python manage_data.py --check

# Clean large files before committing
python manage_data.py --clean

# Create data manifest
python manage_data.py --manifest
```

See **GIT_GUIDELINES.md** for detailed information about what should and shouldn't be committed.

---

**ASMuvera** - Advancing our understanding of multi-vector search architectures 🔍✨