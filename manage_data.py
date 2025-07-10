#!/usr/bin/env python3
"""
Data Management Script for ASMuvera
Helps manage large data files that shouldn't be committed to git
"""

import os
import json
import hashlib
from pathlib import Path
import argparse

def get_file_hash(filepath):
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except FileNotFoundError:
        return None

def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except FileNotFoundError:
        return 0

def format_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def create_data_manifest():
    """Create a manifest of all data files with metadata"""
    
    data_files = {
        "raw_data": [
            "data/raw/collection.tsv",
            "data/raw/queries.train.tsv",
            "data/raw/qrels.train.tsv"
        ],
        "processed_data": [
            "data/processed/passages.jsonl",
            "data/processed/queries.jsonl", 
            "data/processed/qrels.jsonl"
        ],
        "embeddings": [
            "data/embeddings/single_vector_passages.npy",
            "data/embeddings/single_vector_queries.npy",
            "data/embeddings/multi_vector_passages.npy",
            "data/embeddings/multi_vector_queries.npy"
        ]
    }
    
    manifest = {
        "project": "ASMuvera",
        "description": "Data manifest for Advanced Semantic Multi-Vector Evaluation",
        "generated": "2025-07-10",
        "files": {}
    }
    
    print("📊 Creating data manifest...")
    
    for category, files in data_files.items():
        manifest["files"][category] = {}
        
        for filepath in files:
            if os.path.exists(filepath):
                size = get_file_size(filepath)
                file_hash = get_file_hash(filepath)
                
                manifest["files"][category][filepath] = {
                    "size_bytes": size,
                    "size_human": format_size(size),
                    "md5_hash": file_hash,
                    "exists": True
                }
                
                print(f"  ✅ {filepath}: {format_size(size)}")
            else:
                manifest["files"][category][filepath] = {
                    "size_bytes": 0,
                    "size_human": "0B",
                    "md5_hash": None,
                    "exists": False
                }
                
                print(f"  ❌ {filepath}: Missing")
    
    # Save manifest
    manifest_path = "data/DATA_MANIFEST.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n💾 Manifest saved to {manifest_path}")
    return manifest

def check_git_status():
    """Check if large files are accidentally staged for commit"""
    import subprocess
    
    print("🔍 Checking git status for large files...")
    
    try:
        # Get staged files
        result = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True)
        staged_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        
        large_staged_files = []
        for filepath in staged_files:
            if os.path.exists(filepath):
                size = get_file_size(filepath)
                if size > 10 * 1024 * 1024:  # 10MB threshold
                    large_staged_files.append((filepath, size))
        
        if large_staged_files:
            print("⚠️  WARNING: Large files staged for commit:")
            for filepath, size in large_staged_files:
                print(f"    {filepath}: {format_size(size)}")
            print("\n💡 Consider unstaging with: git reset HEAD <file>")
        else:
            print("✅ No large files staged for commit")
            
    except subprocess.CalledProcessError:
        print("⚠️  Not in a git repository or git not available")

def create_download_instructions():
    """Create instructions for downloading/generating data"""
    
    instructions = """# ASMuvera Data Setup Instructions

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
"""
    
    with open("DATA_SETUP.md", 'w') as f:
        f.write(instructions)
    
    print("📝 Created DATA_SETUP.md with download instructions")

def clean_large_files():
    """Remove large data files (with confirmation)"""
    
    large_files = [
        "data/raw/collection.tsv",
        "data/embeddings/single_vector_passages.npy",
        "data/embeddings/multi_vector_passages.npy"
    ]
    
    total_size = sum(get_file_size(f) for f in large_files if os.path.exists(f))
    
    if total_size == 0:
        print("✅ No large files to clean")
        return
    
    print(f"🗑️  Found {format_size(total_size)} of large files:")
    for filepath in large_files:
        if os.path.exists(filepath):
            size = get_file_size(filepath)
            print(f"    {filepath}: {format_size(size)}")
    
    response = input("\n⚠️  Delete these files? (y/N): ")
    if response.lower() in ['y', 'yes']:
        for filepath in large_files:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"  🗑️  Deleted {filepath}")
        print(f"✅ Cleaned {format_size(total_size)}")
    else:
        print("❌ Cancelled")

def main():
    parser = argparse.ArgumentParser(description="Manage ASMuvera data files")
    parser.add_argument("--check", action="store_true", help="Check data file status")
    parser.add_argument("--manifest", action="store_true", help="Create data manifest")
    parser.add_argument("--git-check", action="store_true", help="Check git status for large files")
    parser.add_argument("--setup-docs", action="store_true", help="Create setup documentation")
    parser.add_argument("--clean", action="store_true", help="Clean large data files")
    parser.add_argument("--all", action="store_true", help="Run all checks and create docs")
    
    args = parser.parse_args()
    
    if args.all or not any(vars(args).values()):
        # Default action: run all checks
        print("🔧 ASMuvera Data Management")
        print("=" * 40)
        
        manifest = create_data_manifest()
        print()
        check_git_status()
        print()
        create_download_instructions()
        
        # Summary
        total_size = 0
        for category in manifest["files"].values():
            for file_info in category.values():
                if file_info["exists"]:
                    total_size += file_info["size_bytes"]
        
        print(f"\n📊 Summary:")
        print(f"  Total data size: {format_size(total_size)}")
        print(f"  Files tracked: {sum(len(cat) for cat in manifest['files'].values())}")
        
    else:
        if args.check or args.manifest:
            create_data_manifest()
        
        if args.git_check:
            check_git_status()
        
        if args.setup_docs:
            create_download_instructions()
        
        if args.clean:
            clean_large_files()

if __name__ == "__main__":
    main()