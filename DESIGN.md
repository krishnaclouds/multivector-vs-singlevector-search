# ASMuvera: Multi-Vector Search Comparison Project

## Project Overview

ASMuvera (Advanced Semantic Multi-Vector Evaluation and Research Architecture) is a comprehensive research project designed to understand and compare the power of multi-vector representations versus single-vector representations in semantic search using Vespa.

## Objectives

1. **Compare Search Performance**: Evaluate the effectiveness of single-vector vs multi-vector representations
2. **Understand Trade-offs**: Analyze storage, memory, and query performance implications
3. **Benchmark Different Approaches**: Test various embedding models and indexing strategies
4. **Create Reproducible Framework**: Build a reusable evaluation pipeline for future research

## System Architecture

### Core Components

```
ASMuvera/
├── vespa/                    # Vespa application configuration
│   ├── schemas/             # Document schemas for single and multi-vector
│   ├── services.xml         # Vespa service configuration
│   └── hosts.xml           # Host configuration
├── data/                    # Dataset management
│   ├── raw/                # Original dataset files
│   ├── processed/          # Processed and indexed data
│   └── embeddings/         # Generated embeddings
├── indexing/               # Data indexing pipeline
│   ├── single_vector/      # Single vector indexing logic
│   ├── multi_vector/       # Multi-vector (ColBERT) indexing logic
│   └── embedders/          # Embedding model wrappers
├── queries/                # Query generation and management
│   ├── generators/         # Query set generators
│   ├── datasets/           # Query datasets
│   └── templates/          # Query templates
├── evaluation/             # Evaluation framework
│   ├── metrics/            # Performance metrics
│   ├── benchmarks/         # Benchmark runners
│   └── reports/            # Generated reports
├── scripts/                # Utility scripts
│   ├── setup/              # Environment setup
│   ├── data_prep/          # Data preprocessing
│   └── experiments/        # Experiment runners
└── config/                 # Configuration files
```

## Technical Stack

### Core Technologies
- **Vespa**: Search and ML platform for indexing and querying
- **Python**: Primary programming language for data processing and evaluation
- **Docker**: Containerization for Vespa deployment
- **Jupyter**: Interactive analysis and visualization

### Embedding Models
- **Single Vector**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **Multi Vector**: ColBERT model (128 dimensions per token)
- **Hybrid**: Combined approaches for comparison

## Dataset Selection

### Primary Dataset: MS MARCO Passages
- **Size**: 8.8M passages
- **Domain**: Web search passages
- **Queries**: 1M+ training queries, 6.8K dev queries
- **Relevance**: Human-annotated relevance judgments

### Secondary Dataset: Natural Questions
- **Size**: 307K training examples
- **Domain**: Question answering
- **Format**: Wikipedia passages with questions
- **Use Case**: Multi-hop reasoning evaluation

## Indexing Strategies

### Single Vector Approach
```yaml
Schema: single_vector_document
Fields:
  - id: string
  - title: string
  - content: string
  - embedding: tensor<float>(x[384])  # Single dense vector
  - timestamp: long

Indexing:
  - HNSW index on embedding field
  - Distance metric: angular (cosine similarity)
  - Max connections: 16
  - Ef construction: 200
```

### Multi Vector Approach (ColBERT)
```yaml
Schema: multi_vector_document
Fields:
  - id: string
  - title: string
  - content: string
  - token_embeddings: tensor<float>(token{}, x[128])  # Multi-vector representation
  - compressed_embeddings: tensor<int8>(token{}, x[128])  # Compressed version
  - timestamp: long

Indexing:
  - Multi-vector HNSW indexing
  - Token-level embeddings
  - Compression options: bfloat16, int8, binary
```

## Query Framework

### Query Types
1. **Factual Queries**: Direct information retrieval
2. **Semantic Queries**: Concept-based search
3. **Multi-hop Queries**: Reasoning across multiple documents
4. **Long-tail Queries**: Rare or specific information needs

### Query Generation Pipeline
```python
QueryGenerator:
  - Template-based generation
  - Paraphrase generation
  - Difficulty stratification
  - Domain-specific queries
```

## Evaluation Framework

### Performance Metrics
- **Relevance Metrics**: NDCG@10, MRR, MAP
- **Efficiency Metrics**: Query latency, memory usage, storage size
- **Recall Metrics**: Recall@100, Recall@1000

### Experimental Design
```python
Experiments:
  1. Baseline Comparison:
     - Single vector vs Multi vector
     - Different embedding models
     - Various compression techniques
  
  2. Scalability Testing:
     - Dataset size variations
     - Query load testing
     - Memory usage analysis
  
  3. Quality Analysis:
     - Relevance judgment comparison
     - Error analysis
     - Query type performance
```

### Evaluation Pipeline
```python
EvaluationPipeline:
  1. Index documents with both approaches
  2. Execute query sets
  3. Collect performance metrics
  4. Generate comparative reports
  5. Statistical significance testing
```

## Implementation Plan

### Phase 1: Environment Setup (Week 1)
- Set up Vespa locally using Docker
- Configure development environment
- Create basic project structure

### Phase 2: Data Preparation (Week 2)
- Download and preprocess MS MARCO dataset
- Generate embeddings for both approaches
- Create indexing pipelines

### Phase 3: Vespa Configuration (Week 3)
- Design and implement Vespa schemas
- Configure single vector indexing
- Implement multi-vector ColBERT indexing

### Phase 4: Query Framework (Week 4)
- Develop query generation pipeline
- Create diverse query sets
- Implement query execution framework

### Phase 5: Evaluation System (Week 5)
- Build evaluation metrics
- Create benchmark runners
- Develop reporting system

### Phase 6: Experiments & Analysis (Week 6)
- Run comprehensive experiments
- Analyze results
- Generate final reports

## Expected Outcomes

### Research Insights
1. **Performance Comparison**: Quantitative analysis of single vs multi-vector approaches
2. **Trade-off Analysis**: Storage, memory, and latency implications
3. **Use Case Recommendations**: When to use each approach
4. **Optimization Strategies**: Best practices for implementation

### Deliverables
1. **Comparative Analysis Report**: Detailed performance comparison
2. **Best Practices Guide**: Implementation recommendations
3. **Reusable Framework**: Extensible evaluation pipeline
4. **Open Source Contribution**: Shareable codebase and datasets

## Success Criteria

1. **Functional**: Successfully index and query both single and multi-vector approaches
2. **Comparative**: Generate meaningful performance comparisons
3. **Reproducible**: Create reusable evaluation framework
4. **Insightful**: Provide actionable insights for vector search implementation

## Risk Mitigation

### Technical Risks
- **Vespa Complexity**: Start with simple configurations, gradually add complexity
- **Data Size**: Begin with smaller datasets, scale up gradually
- **Performance Issues**: Monitor resource usage, optimize incrementally

### Resource Risks
- **Compute Requirements**: Use cloud resources if local resources insufficient
- **Storage Needs**: Implement data compression and cleanup strategies
- **Time Constraints**: Prioritize core functionality, defer advanced features

## Next Steps

1. Initialize project structure
2. Set up Vespa development environment
3. Begin data preparation pipeline
4. Implement basic indexing capabilities
5. Create initial query framework