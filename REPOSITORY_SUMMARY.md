# ASMuvera Repository Summary

## 📋 Git Repository Status

This document provides an overview of the ASMuvera repository structure and git management approach.

## ✅ Files Ready for Git

### Core Application Code (Safe to commit)
```
├── .gitignore                           # Comprehensive gitignore rules
├── README.md                           # Main documentation
├── DESIGN.md                           # Architectural documentation  
├── GIT_GUIDELINES.md                   # Git workflow guidelines
├── DATA_SETUP.md                       # Data setup instructions
├── requirements.txt                    # Python dependencies
├── manage_data.py                      # Data management utility
├── demo.py                            # CLI demonstration
├── search_evaluation.py               # Evaluation framework
├── web_ui.py                          # Web interface
├── index_to_vespa.py                  # Document indexing
├── generate_embeddings_simple.py      # Embedding generation
├── process_data_simple.py             # Data processing
├── start_ui.sh                        # Web UI startup script
├── templates/                         # Web UI templates
│   └── index.html
├── static/                            # Web UI assets
│   └── style.css
├── vespa/                             # Vespa configuration
│   ├── services.xml
│   ├── hosts.xml
│   └── schemas/
│       ├── single_vector_document.sd
│       └── multi_vector_document.sd
└── config/
    └── default.yaml
```

### Small Data Files (Safe to commit)
```
├── data/
│   ├── DATA_MANIFEST.json             # Data file metadata
│   ├── processed/
│   │   ├── queries.jsonl              # Small query file (265B)
│   │   └── qrels.jsonl                # Small relevance file (530B)
│   └── embeddings/
│       ├── metadata.json              # Embedding metadata
│       ├── single_vector_queries.npy  # Small query embeddings (15KB)
│       └── multi_vector_queries.npy   # Small query embeddings (21KB)
```

## 🚫 Files Excluded from Git

### Large Data Files (3.24GB total)
```
data/
├── raw/
│   └── collection.tsv                  # 2.9GB - MS MARCO passages
├── processed/
│   └── passages.jsonl                 # 4MB - Processed passages  
└── embeddings/
    ├── single_vector_passages.npy     # 29MB - Single vector embeddings
    └── multi_vector_passages.npy      # 308MB - Multi-vector embeddings
```

### Environment & Runtime Files
```
venv/                                   # Python virtual environment
__pycache__/                           # Python bytecode cache
*.log                                   # Application logs
.DS_Store                              # macOS system files
```

### Generated Files
```
evaluation_results.json                # Evaluation outputs
vespa-app*.zip                         # Vespa deployment packages
```

## 🔧 Repository Management Commands

### Before First Commit
```bash
# Check what will be committed
git status

# Check for large files
python manage_data.py --git-check

# Create data manifest
python manage_data.py --manifest
```

### Regular Development Workflow
```bash
# Stage source code files
git add *.py *.md *.sh templates/ static/ vespa/ config/

# Check staged files
git status --cached

# Commit with descriptive message
git commit -m "Add comprehensive multi-vector search evaluation framework"

# Push to remote
git push origin main
```

### Data Management
```bash
# Clean large files before committing
python manage_data.py --clean

# Regenerate data files after cloning
python process_data_simple.py
python generate_embeddings_simple.py
```

## 📊 Repository Statistics

- **Total project size**: ~3.24GB (mostly data)
- **Code size**: ~500KB (Python, configs, docs)
- **Committed size**: ~500KB (excludes large data files)
- **Number of Python files**: 8
- **Number of config files**: 4
- **Documentation files**: 5

## 🎯 Git Strategy Benefits

1. **Fast cloning**: Repository stays small (~500KB vs 3.24GB)
2. **Clean history**: No accidentally committed large files
3. **Flexible data**: Users can generate or download data separately
4. **Collaboration friendly**: Easy to share code without data overhead
5. **CI/CD ready**: Fast builds and deployments

## 🔄 Recommended Workflow for New Contributors

1. **Clone repository**: `git clone <repo-url>`
2. **Set up environment**: `python3 -m venv venv && source venv/bin/activate`
3. **Install dependencies**: `pip install -r requirements.txt`
4. **Generate data**: `python process_data_simple.py`
5. **Create embeddings**: `python generate_embeddings_simple.py`
6. **Start Vespa**: `./setup_vespa.sh`
7. **Index documents**: `python index_to_vespa.py --type both`
8. **Test system**: `python demo.py` or start web UI

## 📝 Best Practices

### ✅ DO
- Commit all source code and configuration files
- Include comprehensive documentation
- Add small sample/test data files
- Use descriptive commit messages
- Check for large files before committing

### ❌ DON'T
- Commit large data files (>10MB)
- Include virtual environments or cache directories
- Add personal configuration files
- Commit generated/temporary files
- Use vague commit messages

## 🆘 Emergency Recovery

If large files were accidentally committed:

```bash
# Remove from staging
git reset HEAD large_file.npy

# Remove from git history (CAREFUL!)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch large_file.npy' \
  --prune-empty --tag-name-filter cat -- --all

# Clean up
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

This approach ensures the ASMuvera repository remains clean, fast, and focused on the code while providing clear guidance for data management.