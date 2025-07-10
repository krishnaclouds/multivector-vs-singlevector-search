#!/usr/bin/env python3
"""
ASMuvera - MS MARCO Dataset Download and Preprocessing Script

This script downloads the MS MARCO passage ranking dataset and prepares it for indexing.
"""

import os
import sys
import gzip
import tarfile
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import yaml
import argparse
from typing import Dict, List, Optional


def load_config(config_path: str = "config/default.yaml") -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def download_file(url: str, filepath: Path, description: str = "") -> None:
    """Download a file with progress bar."""
    print(f"📥 Downloading {description or filepath.name}...")
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filepath, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=filepath.name) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))


def extract_gzip(filepath: Path) -> Path:
    """Extract gzipped file."""
    output_path = filepath.with_suffix('')
    
    if output_path.exists():
        print(f"✅ {output_path.name} already exists, skipping extraction")
        return output_path
    
    print(f"📦 Extracting {filepath.name}...")
    
    with gzip.open(filepath, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    return output_path


def extract_tar_gz(filepath: Path, extract_dir: Path) -> Path:
    """Extract tar.gz file."""
    print(f"📦 Extracting {filepath.name}...")
    
    with tarfile.open(filepath, 'r:gz') as tar:
        tar.extractall(path=extract_dir)
    
    # Find the collection.tsv file
    collection_file = extract_dir / "collection.tsv"
    if collection_file.exists():
        return collection_file
    
    # Search for collection.tsv in subdirectories
    for file in extract_dir.rglob("collection.tsv"):
        return file
    
    raise FileNotFoundError("collection.tsv not found in extracted files")


def process_passages(passages_file: Path, max_passages: int = -1) -> pd.DataFrame:
    """Process MS MARCO passages file."""
    print(f"📊 Processing passages from {passages_file.name}...")
    
    # Read TSV file
    passages = []
    with open(passages_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(tqdm(f, desc="Loading passages")):
            if max_passages > 0 and i >= max_passages:
                break
                
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                pid = parts[0]
                passage = parts[1]
                passages.append({
                    'id': pid,
                    'title': '',  # MS MARCO passages don't have titles
                    'content': passage,
                    'url': f'https://msmarco.blob.core.windows.net/passage/{pid}'
                })
    
    df = pd.DataFrame(passages)
    print(f"✅ Loaded {len(df)} passages")
    return df


def process_queries(queries_file: Path) -> pd.DataFrame:
    """Process MS MARCO queries file."""
    print(f"📊 Processing queries from {queries_file.name}...")
    
    queries = []
    with open(queries_file, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Loading queries"):
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                qid = parts[0]
                query = parts[1]
                queries.append({
                    'id': qid,
                    'text': query
                })
    
    df = pd.DataFrame(queries)
    print(f"✅ Loaded {len(df)} queries")
    return df


def process_qrels(qrels_file: Path) -> pd.DataFrame:
    """Process MS MARCO relevance judgments file."""
    print(f"📊 Processing relevance judgments from {qrels_file.name}...")
    
    qrels = []
    with open(qrels_file, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Loading qrels"):
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                qid = parts[0]
                pid = parts[2]
                rel = int(parts[3])
                qrels.append({
                    'query_id': qid,
                    'passage_id': pid,
                    'relevance': rel
                })
    
    df = pd.DataFrame(qrels)
    print(f"✅ Loaded {len(df)} relevance judgments")
    return df


def main():
    parser = argparse.ArgumentParser(description="Download and process MS MARCO dataset")
    parser.add_argument("--config", default="config/default.yaml", help="Configuration file path")
    parser.add_argument("--max-passages", type=int, default=-1, help="Maximum number of passages to process (-1 for all)")
    parser.add_argument("--skip-download", action="store_true", help="Skip download if files exist")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    dataset_config = config['datasets']['msmarco']
    
    # Create data directories
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Download files
    files_to_download = [
        ("passages", dataset_config['passages_url'], "collection.tsv"),
        ("queries", dataset_config['queries_url'], "queries.dev.small.tsv"),
        ("qrels", dataset_config['qrels_url'], "qrels.dev.small.tsv"),
    ]
    
    downloaded_files = {}
    
    for file_type, url, filename in files_to_download:
        filepath = raw_dir / filename
        
        if not args.skip_download or not filepath.exists():
            try:
                download_file(url, filepath, f"MS MARCO {file_type}")
                downloaded_files[file_type] = filepath
            except Exception as e:
                print(f"❌ Failed to download {file_type}: {e}")
                sys.exit(1)
        else:
            print(f"✅ {filename} already exists, skipping download")
            downloaded_files[file_type] = filepath
    
    # Extract compressed files if needed
    for file_type, filepath in downloaded_files.items():
        if filepath.suffix == '.gz':
            if filepath.name.endswith('.tar.gz'):
                # Handle tar.gz files
                downloaded_files[file_type] = extract_tar_gz(filepath, raw_dir)
            else:
                # Handle regular .gz files
                downloaded_files[file_type] = extract_gzip(filepath)
    
    # Process datasets
    max_passages = args.max_passages if args.max_passages > 0 else dataset_config.get('max_passages', -1)
    
    try:
        # Process passages
        passages_df = process_passages(downloaded_files['passages'], max_passages)
        passages_output = processed_dir / "passages.jsonl"
        passages_df.to_json(passages_output, orient='records', lines=True)
        print(f"💾 Saved passages to {passages_output}")
        
        # Process queries
        queries_df = process_queries(downloaded_files['queries'])
        queries_output = processed_dir / "queries.jsonl"
        queries_df.to_json(queries_output, orient='records', lines=True)
        print(f"💾 Saved queries to {queries_output}")
        
        # Process qrels
        qrels_df = process_qrels(downloaded_files['qrels'])
        qrels_output = processed_dir / "qrels.jsonl"
        qrels_df.to_json(qrels_output, orient='records', lines=True)
        print(f"💾 Saved qrels to {qrels_output}")
        
        # Create summary statistics
        stats = {
            'passages': len(passages_df),
            'queries': len(queries_df),
            'qrels': len(qrels_df),
            'unique_queries_with_rels': qrels_df['query_id'].nunique(),
            'unique_passages_with_rels': qrels_df['passage_id'].nunique(),
            'avg_passage_length': passages_df['content'].str.len().mean(),
            'avg_query_length': queries_df['text'].str.len().mean(),
        }
        
        stats_output = processed_dir / "dataset_stats.yaml"
        with open(stats_output, 'w') as f:
            yaml.dump(stats, f, default_flow_style=False)
        
        print(f"📊 Dataset statistics saved to {stats_output}")
        print("\n📈 Dataset Summary:")
        for key, value in stats.items():
            print(f"   {key}: {value:,.0f}" if isinstance(value, float) else f"   {key}: {value:,}")
        
    except Exception as e:
        print(f"❌ Error processing datasets: {e}")
        sys.exit(1)
    
    print("\n🎉 MS MARCO dataset download and processing complete!")
    print("\n🎯 Next steps:")
    print("   1. Generate embeddings: python scripts/data_prep/generate_embeddings.py")
    print("   2. Index documents: python scripts/experiments/run_indexing.py")


if __name__ == "__main__":
    main()