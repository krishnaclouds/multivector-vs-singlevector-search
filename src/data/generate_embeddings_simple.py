#!/usr/bin/env python3
"""
Simple embedding generation for Muvera
Uses basic approaches that work without heavy ML dependencies
"""

import json
import numpy as np
import hashlib
from pathlib import Path
from typing import List, Dict
import re

def simple_tokenize(text: str) -> List[str]:
    """Simple tokenization"""
    # Lowercase and split on non-alphanumeric
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def create_vocabulary(passages: List[Dict], max_vocab: int = 10000) -> Dict[str, int]:
    """Create vocabulary from passages"""
    word_counts = {}
    
    for passage in passages:
        text = f"{passage['title']} {passage['content']}"
        tokens = simple_tokenize(text)
        
        for token in tokens:
            word_counts[token] = word_counts.get(token, 0) + 1
    
    # Sort by frequency and take top words
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    vocab = {word: idx for idx, (word, _) in enumerate(sorted_words[:max_vocab])}
    
    print(f"✅ Created vocabulary with {len(vocab)} words")
    return vocab

def text_to_vector(text: str, vocab: Dict[str, int], dim: int = 384) -> np.ndarray:
    """Convert text to simple vector representation"""
    tokens = simple_tokenize(text)
    
    # Create bag-of-words vector
    vector = np.zeros(dim)
    
    for token in tokens:
        if token in vocab:
            idx = vocab[token] % dim  # Map to vector dimension
            vector[idx] += 1.0
    
    # Normalize
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    
    return vector

def text_to_multi_vector(text: str, vocab: Dict[str, int], token_dim: int = 128, max_tokens: int = 32) -> List[np.ndarray]:
    """Convert text to multi-vector representation (simulate ColBERT)"""
    tokens = simple_tokenize(text)
    
    # Limit number of tokens
    tokens = tokens[:max_tokens]
    
    token_vectors = []
    for token in tokens:
        # Create a vector for each token
        vector = np.zeros(token_dim)
        
        if token in vocab:
            # Use hash-based approach for deterministic embeddings
            token_hash = int(hashlib.md5(token.encode()).hexdigest(), 16)
            
            # Fill vector with hash-based values
            for i in range(token_dim):
                vector[i] = ((token_hash + i) % 1000) / 1000.0 - 0.5
        
        # Normalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        token_vectors.append(vector)
    
    return token_vectors

def save_embeddings(embeddings: List, filename: str):
    """Save embeddings to numpy file"""
    embeddings_dir = Path("data/embeddings")
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = embeddings_dir / filename
    
    if filename.startswith("multi_vector"):
        # Save multi-vector embeddings as pickle-enabled numpy array
        np.save(filepath, np.array(embeddings, dtype=object), allow_pickle=True)
    else:
        # Save regular embeddings as standard array
        np.save(filepath, np.array(embeddings))
    
    print(f"💾 Saved embeddings to {filepath}")

def main():
    print("🔢 Generating embeddings for Muvera...")
    
    # Load processed data
    with open("data/processed/passages.jsonl", 'r') as f:
        passages = [json.loads(line) for line in f]
    
    with open("data/processed/queries.jsonl", 'r') as f:
        queries = [json.loads(line) for line in f]
    
    print(f"📊 Loaded {len(passages)} passages and {len(queries)} queries")
    
    # Create vocabulary from passages
    vocab = create_vocabulary(passages)
    
    # Generate single vector embeddings
    print("\n🔢 Generating single vector embeddings...")
    
    passage_embeddings = []
    for i, passage in enumerate(passages):
        if i % 1000 == 0:
            print(f"  Processing passage {i}/{len(passages)}")
        
        text = f"{passage['title']} {passage['content']}"
        embedding = text_to_vector(text, vocab, dim=384)
        passage_embeddings.append(embedding)
    
    query_embeddings = []
    for query in queries:
        embedding = text_to_vector(query['text'], vocab, dim=384)
        query_embeddings.append(embedding)
    
    # Save single vector embeddings
    save_embeddings(passage_embeddings, "single_vector_passages.npy")
    save_embeddings(query_embeddings, "single_vector_queries.npy")
    
    # Generate multi-vector embeddings
    print("\n🔢 Generating multi-vector embeddings...")
    
    passage_multi_embeddings = []
    for i, passage in enumerate(passages):
        if i % 1000 == 0:
            print(f"  Processing passage {i}/{len(passages)}")
        
        text = f"{passage['title']} {passage['content']}"
        token_embeddings = text_to_multi_vector(text, vocab, token_dim=128)
        
        # Convert to tensor format expected by Vespa
        if token_embeddings:
            # Stack token vectors into a matrix
            token_matrix = np.stack(token_embeddings)
        else:
            # Empty document - create single zero vector
            token_matrix = np.zeros((1, 128))
        
        passage_multi_embeddings.append(token_matrix)
    
    query_multi_embeddings = []
    for query in queries:
        token_embeddings = text_to_multi_vector(query['text'], vocab, token_dim=128)
        
        if token_embeddings:
            token_matrix = np.stack(token_embeddings)
        else:
            token_matrix = np.zeros((1, 128))
            
        query_multi_embeddings.append(token_matrix)
    
    # Save multi-vector embeddings
    save_embeddings(passage_multi_embeddings, "multi_vector_passages.npy")
    save_embeddings(query_multi_embeddings, "multi_vector_queries.npy")
    
    # Create metadata
    metadata = {
        'single_vector': {
            'model_name': 'simple_bow',
            'dimension': 384,
            'passages_count': len(passages),
            'queries_count': len(queries),
        },
        'multi_vector': {
            'model_name': 'simple_multi_token',
            'dimension': 128,
            'max_tokens': 32,
            'passages_count': len(passages),
            'queries_count': len(queries),
        },
        'vocabulary_size': len(vocab)
    }
    
    with open("data/embeddings/metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"📊 Embedding metadata saved")
    
    print("\n🎉 Embedding generation complete!")
    print(f"📁 Embeddings saved to: data/embeddings/")
    print("\n📊 Summary:")
    print(f"   Single vector passages: {len(passage_embeddings)} x 384")
    print(f"   Single vector queries: {len(query_embeddings)} x 384")
    print(f"   Multi-vector passages: {len(passage_multi_embeddings)} (variable tokens x 128)")
    print(f"   Multi-vector queries: {len(query_multi_embeddings)} (variable tokens x 128)")
    print(f"   Vocabulary size: {len(vocab)}")

if __name__ == "__main__":
    main()