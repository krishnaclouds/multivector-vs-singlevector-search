# ASMuvera Data Setup Instructions

This file contains instructions for setting up the data files needed for ASMuvera.

## Required Data Files

### 1. Raw Data (2.9GB total)
The MS MARCO passage collection:
```bash
# Download and process data
python process_data_simple.py
```

### 2. Embeddings (337MB total)
Pre-computed vector embeddings:
```bash
# Generate embeddings (takes ~10-15 minutes)
python generate_embeddings_simple.py
```

### 3. Alternative: Download Pre-computed Data
If available, you can download pre-computed embeddings from:
- [Add your cloud storage link here]
- [Add alternative download location]

## File Sizes Reference
- `data/raw/collection.tsv`: ~2.9GB
- `data/embeddings/single_vector_passages.npy`: ~29MB
- `data/embeddings/multi_vector_passages.npy`: ~308MB
- `data/embeddings/*_queries.npy`: ~36KB total

## Setup Checklist
- [ ] Run `python process_data_simple.py`
- [ ] Run `python generate_embeddings_simple.py`
- [ ] Verify files with `python manage_data.py --check`
- [ ] Start Vespa with `./setup_vespa.sh`
- [ ] Index documents with `python index_to_vespa.py`

## Troubleshooting
- If downloads fail, check internet connection
- If generation is slow, consider reducing dataset size
- For storage issues, ensure 4GB+ free space
