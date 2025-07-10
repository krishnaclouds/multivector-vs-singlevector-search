# Git Guidelines for Muvera

This document explains the git workflow and file management strategy for the Muvera project.

## 📁 What TO Commit

### ✅ Essential Code & Configuration
- **Source code**: All `.py` files
- **Configuration**: `vespa/services.xml`, `vespa/schemas/*.sd`, `config/*.yaml`
- **Documentation**: `README.md`, `DESIGN.md`, `*.md` files
- **Dependencies**: `requirements.txt`, `setup.py`, `pyproject.toml`
- **Scripts**: Shell scripts like `setup_vespa.sh`, `start_ui.sh`
- **Templates**: HTML templates, CSS files
- **Tests**: Test files and small test datasets

### ✅ Small Reference Files
- **Sample data**: Small example files in `data/samples/`
- **Metadata**: `data/embeddings/metadata.json` (without the actual embeddings)
- **Sample results**: Example evaluation outputs for documentation
- **Configuration examples**: Template configuration files

## 🚫 What NOT to Commit

### ❌ Large Data Files
- **Raw datasets**: MS MARCO collections (multi-GB files)
- **Embeddings**: `.npy`, `.pkl` files with vector data
- **Model files**: Pre-trained models, `.bin`, `.safetensors` files
- **Generated data**: Large processed datasets

### ❌ Environment & Runtime Files
- **Virtual environments**: `venv/`, `env/`, etc.
- **Cache files**: `__pycache__/`, `.cache/`, transformers cache
- **Logs**: Application logs, Vespa logs
- **Temporary files**: `.tmp`, `.temp`, backup files

### ❌ Personal & System Files
- **IDE configurations**: `.vscode/`, `.idea/` (unless shared team settings)
- **OS files**: `.DS_Store`, `Thumbs.db`, etc.
- **Personal configs**: Local environment variables, credentials

### ❌ Generated/Build Artifacts
- **Docker volumes**: Vespa runtime data
- **Build outputs**: Distribution packages, compiled files
- **Evaluation results**: Large result files (keep samples only)

## 🔧 Git Workflow Recommendations

### Initial Setup
```bash
# Clone the repository
git clone <repository-url>
cd folder

# Set up local environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Download/generate data (not committed)
python process_data_simple.py
python generate_embeddings_simple.py
```

### Working with Data
```bash
# Data files are in .gitignore, so they won't be committed automatically
# If you need to share small sample data:
git add data/samples/small_example.json  # Force add if needed
git add data/embeddings/metadata.json   # Metadata is allowed

# Large files should be shared via external means:
# - Cloud storage (Google Drive, Dropbox)
# - Data versioning tools (DVC, Git LFS)
# - Shared network drives
```

### Branch Strategy
```bash
# Feature development
git checkout -b feature/new-embedding-model
# Make changes
git add .
git commit -m "Add support for new embedding model"
git push origin feature/new-embedding-model

# Bug fixes
git checkout -b fix/vespa-indexing-error
# Make changes
git add .
git commit -m "Fix tensor format error in multi-vector indexing"
git push origin fix/vespa-indexing-error
```

### Commit Message Convention
```bash
# Good commit messages:
git commit -m "Add ColBERT multi-vector search implementation"
git commit -m "Fix tensor formatting in Vespa indexing pipeline"
git commit -m "Update web UI with real-time performance metrics"
git commit -m "Add comprehensive evaluation framework"

# Bad commit messages:
git commit -m "fix bug"
git commit -m "update stuff"
git commit -m "wip"
```

## 📦 Handling Large Files

### Option 1: External Storage
```bash
# Store large files externally and document how to get them
echo "Download embeddings from: https://drive.google.com/..." > data/embeddings/DOWNLOAD.md
```

### Option 2: Git LFS (if repository supports it)
```bash
# Track large files with Git LFS
git lfs track "data/embeddings/*.npy"
git lfs track "data/raw/*.tsv"
git add .gitattributes
git commit -m "Add Git LFS tracking for large data files"
```

### Option 3: Data Version Control (DVC)
```bash
# Use DVC for data versioning
dvc add data/embeddings/
dvc add data/raw/
git add data/embeddings/.gitignore data/embeddings/single_vector_passages.npy.dvc
git commit -m "Add data versioning with DVC"
```

## 🔍 Checking What Will Be Committed

```bash
# See what files are staged
git status

# See what changes will be committed
git diff --cached

# Check if large files are accidentally staged
git ls-files --stage | awk '$4 > 1048576 {print $4, $NF}' | sort -nr

# Check repository size
git count-objects -vH
```

## 🧹 Cleaning Up

### Remove accidentally committed large files
```bash
# Remove from git history (CAREFUL - rewrites history)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch data/embeddings/large_file.npy' \
  --prune-empty --tag-name-filter cat -- --all

# Cleanup
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Clean local repository
```bash
# Remove untracked files (be careful!)
git clean -fd

# Remove ignored files
git clean -fdX
```

## 📋 Pre-commit Checklist

Before committing, ensure:

- [ ] No large data files (>10MB) are staged
- [ ] No personal credentials or API keys
- [ ] Code follows project style guidelines
- [ ] Tests pass (if applicable)
- [ ] Documentation is updated
- [ ] Commit message is descriptive

## 🤝 Collaboration Guidelines

### Sharing Data
- **Small samples**: Commit to `data/samples/`
- **Large datasets**: Share download instructions
- **Embeddings**: Share generation scripts, not the files
- **Models**: Share model configs and training scripts

### Code Reviews
- Focus on code quality and architecture
- Ensure no sensitive data is committed
- Check that large files aren't included
- Verify documentation is updated

### Release Process
```bash
# Tag releases
git tag -a v1.0.0 -m "Muvera v1.0.0: Initial release with multi-vector search"
git push origin v1.0.0

# Create release notes
# Document what data/models are needed
# Provide setup instructions
```

This approach ensures the repository stays clean, fast, and focused on the code while providing clear guidance for handling the data components of the Muvera project.