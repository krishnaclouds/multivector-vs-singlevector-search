#!/usr/bin/env python3
"""
Simple MS MARCO data loader using datasets library for queries and qrels
"""

import pandas as pd
from pathlib import Path
import tarfile
from datasets import load_dataset
import argparse


def extract_collection():
    """Extract collection.tsv from the downloaded tar.gz"""
    raw_dir = Path("data/raw")
    collection_file = raw_dir / "collection.tsv"
    
    if collection_file.exists():
        print(f"✅ Collection already extracted: {collection_file}")
        return collection_file
    
    # Find the tar.gz file
    tar_files = list(raw_dir.glob("*.tar.gz"))
    if not tar_files:
        print("❌ No tar.gz files found. Please download the collection first.")
        return None
    
    tar_file = tar_files[0]
    print(f"📦 Extracting {tar_file.name}...")
    
    with tarfile.open(tar_file, 'r:gz') as tar:
        tar.extractall(path=raw_dir)
    
    # Find collection.tsv
    if collection_file.exists():
        return collection_file
    
    # Search in subdirectories
    for file in raw_dir.rglob("collection.tsv"):
        return file
    
    print("❌ collection.tsv not found in extracted files")
    return None


def load_queries_and_qrels():
    """Load queries and qrels using datasets library"""
    print("📥 Loading MS MARCO dev queries and qrels...")
    
    try:
        # Load the dev set
        dataset = load_dataset("microsoft/ms_marco", "v1.1", split="validation")
        
        # Extract queries
        queries = []
        for item in dataset:
            queries.append({
                'id': item['query_id'],
                'text': item['query']
            })
        
        queries_df = pd.DataFrame(queries)
        print(f"✅ Loaded {len(queries_df)} queries")
        
        # Create qrels from the dataset
        qrels = []
        for item in dataset:
            if 'passages' in item and item['passages']:
                for passage in item['passages']:
                    if passage['is_selected']:
                        qrels.append({
                            'query_id': item['query_id'],
                            'passage_id': passage['passage_id'],
                            'relevance': 1
                        })
        
        qrels_df = pd.DataFrame(qrels)
        print(f"✅ Loaded {len(qrels_df)} relevance judgments")
        
        return queries_df, qrels_df
        
    except Exception as e:
        print(f"❌ Failed to load from datasets library: {e}")
        return None, None


def process_collection(collection_file, max_passages=-1):
    """Process the collection.tsv file"""
    print(f"📊 Processing collection from {collection_file.name}...")
    
    passages = []
    with open(collection_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if max_passages > 0 and i >= max_passages:
                break
                
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                pid = parts[0]
                passage = parts[1]
                passages.append({
                    'id': pid,
                    'title': '',
                    'content': passage,
                    'url': f'https://msmarco.blob.core.windows.net/passage/{pid}'
                })
    
    df = pd.DataFrame(passages)
    print(f"✅ Processed {len(df)} passages")
    return df


def main():
    parser = argparse.ArgumentParser(description="Simple MS MARCO data preparation")
    parser.add_argument("--max-passages", type=int, default=10000, help="Maximum passages to process")
    args = parser.parse_args()
    
    # Create directories
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract collection
    collection_file = extract_collection()
    if not collection_file:
        return
    
    # Process collection
    passages_df = process_collection(collection_file, args.max_passages)
    passages_output = processed_dir / "passages.jsonl"
    passages_df.to_json(passages_output, orient='records', lines=True)
    print(f"💾 Saved passages to {passages_output}")
    
    # Load queries and qrels
    queries_df, qrels_df = load_queries_and_qrels()
    
    if queries_df is not None:
        queries_output = processed_dir / "queries.jsonl"
        queries_df.to_json(queries_output, orient='records', lines=True)
        print(f"💾 Saved queries to {queries_output}")
    
    if qrels_df is not None:
        qrels_output = processed_dir / "qrels.jsonl"
        qrels_df.to_json(qrels_output, orient='records', lines=True)
        print(f"💾 Saved qrels to {qrels_output}")
    
    print("\n🎉 Data preparation complete!")
    print(f"📊 Dataset summary:")
    print(f"   Passages: {len(passages_df):,}")
    if queries_df is not None:
        print(f"   Queries: {len(queries_df):,}")
    if qrels_df is not None:
        print(f"   Qrels: {len(qrels_df):,}")


if __name__ == "__main__":
    main()