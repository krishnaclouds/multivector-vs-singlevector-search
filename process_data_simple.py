#!/usr/bin/env python3
"""
Simple data processing without dependencies
"""

import json
import os
from pathlib import Path

def process_collection(max_passages=10000):
    """Process collection.tsv file"""
    print(f"📊 Processing collection.tsv (max {max_passages} passages)...")
    
    collection_file = "data/raw/collection.tsv"
    passages = []
    
    with open(collection_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= max_passages:
                break
                
            # Skip tar header lines
            if line.startswith('collection.tsv') or len(line.strip().split('\t')) < 2:
                continue
                
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
    
    print(f"✅ Processed {len(passages)} passages")
    return passages

def save_jsonl(data, filename):
    """Save data as JSONL"""
    os.makedirs('data/processed', exist_ok=True)
    filepath = f'data/processed/{filename}'
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item) + '\n')
    
    print(f"💾 Saved {len(data)} items to {filepath}")

def create_sample_queries():
    """Create sample queries for testing"""
    queries = [
        {'id': '1', 'text': 'what is the manhattan project'},
        {'id': '2', 'text': 'atomic bomb world war ii'},
        {'id': '3', 'text': 'scientific research nuclear weapons'},
        {'id': '4', 'text': 'peaceful uses atomic energy'},
        {'id': '5', 'text': 'communication scientific minds'},
    ]
    
    # Create basic qrels (all queries relevant to first few passages)
    qrels = []
    for i, query in enumerate(queries):
        for pid in range(i*2, (i+1)*2):  # 2 relevant passages per query
            qrels.append({
                'query_id': query['id'],
                'passage_id': str(pid),
                'relevance': 1
            })
    
    return queries, qrels

def main():
    # Process passages
    passages = process_collection(10000)
    save_jsonl(passages, 'passages.jsonl')
    
    # Create sample queries and qrels
    queries, qrels = create_sample_queries()
    save_jsonl(queries, 'queries.jsonl')
    save_jsonl(qrels, 'qrels.jsonl')
    
    print("\n🎉 Data processing complete!")
    print(f"📊 Dataset summary:")
    print(f"   Passages: {len(passages):,}")
    print(f"   Queries: {len(queries):,}")
    print(f"   Qrels: {len(qrels):,}")

if __name__ == "__main__":
    main()