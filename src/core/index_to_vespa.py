#!/usr/bin/env python3
"""
Vespa indexing pipeline for Muvera
Indexes both single-vector and multi-vector documents
"""

import json
import numpy as np
import requests
import time
from pathlib import Path
from typing import Dict, List, Any
import argparse

class VespaIndexer:
    def __init__(self, vespa_url: str = "http://localhost:8080"):
        self.vespa_url = vespa_url
        self.document_api = f"{vespa_url}/document/v1"
        
    def create_single_vector_document(self, passage: Dict, embedding: np.ndarray) -> Dict:
        """Create a single vector document for Vespa"""
        doc = {
            "fields": {
                "id": passage['id'],
                "title": passage.get('title', ''),
                "content": passage['content'],
                "url": passage.get('url', ''),
                "embedding": {
                    "values": embedding.tolist()
                },
                "timestamp": int(time.time())
            }
        }
        return doc
    
    def create_multi_vector_document(self, passage: Dict, token_embeddings: np.ndarray) -> Dict:
        """Create a multi-vector document for Vespa"""
        # Convert token embeddings to Vespa tensor format
        if token_embeddings.ndim == 1:
            # Single token case
            token_embeddings = token_embeddings.reshape(1, -1)
        
        num_tokens, dim = token_embeddings.shape
        
        # Create tensor in Vespa format: tensor<float>(token{}, x[128])
        # Use the correct cells array format for sparse tensors
        tensor_cells = []
        for token_idx in range(num_tokens):
            for dim_idx in range(dim):
                tensor_cells.append({
                    "address": {"token": str(token_idx), "x": str(dim_idx)},
                    "value": float(token_embeddings[token_idx, dim_idx])
                })
        
        # For compressed embeddings, quantize to int8
        compressed_embeddings = np.clip(token_embeddings * 127, -127, 127).astype(np.int8)
        compressed_cells = []
        for token_idx in range(num_tokens):
            for dim_idx in range(dim):
                compressed_cells.append({
                    "address": {"token": str(token_idx), "x": str(dim_idx)},
                    "value": int(compressed_embeddings[token_idx, dim_idx])
                })
        
        doc = {
            "fields": {
                "id": passage['id'],
                "title": passage.get('title', ''),
                "content": passage['content'],
                "url": passage.get('url', ''),
                "token_embeddings": {
                    "cells": tensor_cells
                },
                "compressed_embeddings": {
                    "cells": compressed_cells
                },
                "timestamp": int(time.time())
            }
        }
        return doc
    
    def index_document(self, document: Dict, doc_id: str, schema: str) -> bool:
        """Index a single document to Vespa"""
        try:
            url = f"{self.document_api}/asmarc/{schema}/docid/{doc_id}"
            response = requests.post(
                url,
                json=document,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"❌ Failed to index document {doc_id}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error indexing document {doc_id}: {e}")
            return False
    
    def index_batch(self, documents: List[tuple], batch_size: int = 100) -> int:
        """Index a batch of documents"""
        successful = 0
        total = len(documents)
        
        for i in range(0, total, batch_size):
            batch = documents[i:i + batch_size]
            batch_successful = 0
            
            for doc, doc_id, schema in batch:
                if self.index_document(doc, doc_id, schema):
                    batch_successful += 1
                    successful += 1
            
            print(f"📊 Indexed batch {i//batch_size + 1}: {batch_successful}/{len(batch)} successful")
            
            # Small delay between batches
            time.sleep(0.1)
        
        return successful

def load_data():
    """Load processed data and embeddings"""
    print("📥 Loading data and embeddings...")
    
    # Load passages
    with open("data/processed/passages.jsonl", 'r') as f:
        passages = [json.loads(line) for line in f]
    
    # Load embeddings
    single_embeddings = np.load("data/embeddings/single_vector_passages.npy")
    multi_embeddings = np.load("data/embeddings/multi_vector_passages.npy", allow_pickle=True)
    
    print(f"✅ Loaded {len(passages)} passages")
    print(f"✅ Loaded single vector embeddings: {single_embeddings.shape}")
    print(f"✅ Loaded multi-vector embeddings: {len(multi_embeddings)} documents")
    
    return passages, single_embeddings, multi_embeddings

def main():
    parser = argparse.ArgumentParser(description="Index documents to Vespa")
    parser.add_argument("--type", choices=["single", "multi", "both"], default="both",
                       help="Type of documents to index")
    parser.add_argument("--batch-size", type=int, default=50,
                       help="Batch size for indexing")
    parser.add_argument("--max-docs", type=int, default=1000,
                       help="Maximum number of documents to index")
    
    args = parser.parse_args()
    
    # Initialize indexer
    indexer = VespaIndexer()
    
    # Load data
    passages, single_embeddings, multi_embeddings = load_data()
    
    # Limit number of documents
    max_docs = min(args.max_docs, len(passages))
    passages = passages[:max_docs]
    single_embeddings = single_embeddings[:max_docs]
    multi_embeddings = multi_embeddings[:max_docs]
    
    print(f"🎯 Indexing {max_docs} documents...")
    
    # Index single vector documents
    if args.type in ["single", "both"]:
        print("\n🔢 Indexing single vector documents...")
        single_docs = []
        
        for passage, embedding in zip(passages, single_embeddings):
            doc = indexer.create_single_vector_document(passage, embedding)
            single_docs.append((doc, passage['id'], 'single_vector_document'))
        
        successful = indexer.index_batch(single_docs, args.batch_size)
        print(f"✅ Successfully indexed {successful}/{len(single_docs)} single vector documents")
    
    # Index multi-vector documents
    if args.type in ["multi", "both"]:
        print("\n🔢 Indexing multi-vector documents...")
        multi_docs = []
        
        for passage, token_embeddings in zip(passages, multi_embeddings):
            doc = indexer.create_multi_vector_document(passage, token_embeddings)
            multi_docs.append((doc, passage['id'], 'multi_vector_document'))
        
        successful = indexer.index_batch(multi_docs, args.batch_size)
        print(f"✅ Successfully indexed {successful}/{len(multi_docs)} multi-vector documents")
    
    print("\n🎉 Indexing complete!")
    print("\n🔍 Test search endpoints:")
    print("   Single vector: http://localhost:8080/search/?yql=select%20*%20from%20single_vector_document")
    print("   Multi vector: http://localhost:8080/search/?yql=select%20*%20from%20multi_vector_document")

if __name__ == "__main__":
    main()