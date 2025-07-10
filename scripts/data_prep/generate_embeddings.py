#!/usr/bin/env python3
"""
ASMuvera - Embedding Generation Script

This script generates both single-vector and multi-vector embeddings for the MS MARCO dataset.
"""

import os
import sys
import json
import yaml
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from typing import Dict, List, Optional, Tuple
import torch
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SingleVectorEmbedder:
    """Generate single-vector embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str, device: str = "auto"):
        """Initialize single vector embedder."""
        self.model_name = model_name
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        
        logger.info(f"Loading single-vector model: {model_name} on {self.device}")
        self.model = SentenceTransformer(model_name, device=self.device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        logger.info(f"Model loaded. Embedding dimension: {self.dimension}")
    
    def encode_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode a batch of texts to embeddings."""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        return embeddings
    
    def encode_queries(self, queries: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode queries with potential query prefix."""
        # Add query prefix if model supports it
        if hasattr(self.model, 'encode') and 'query:' in str(self.model):
            queries = [f"query: {q}" for q in queries]
        
        return self.encode_batch(queries, batch_size)
    
    def encode_passages(self, passages: List[str], batch_size: int = 32) -> np.ndarray:
        """Encode passages with potential passage prefix."""
        # Add passage prefix if model supports it
        if hasattr(self.model, 'encode') and 'passage:' in str(self.model):
            passages = [f"passage: {p}" for p in passages]
        
        return self.encode_batch(passages, batch_size)


class MultiVectorEmbedder:
    """Generate multi-vector embeddings using ColBERT-style approach."""
    
    def __init__(self, model_name: str, max_tokens: int = 512, device: str = "auto"):
        """Initialize multi-vector embedder."""
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.device = device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
        
        logger.info(f"Loading multi-vector model: {model_name} on {self.device}")
        
        # Use a BERT-based model for ColBERT-style embeddings
        if "colbert" in model_name.lower():
            try:
                from transformers import AutoTokenizer, AutoModel
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModel.from_pretrained(model_name).to(self.device)
            except:
                # Fallback to sentence-transformers
                logger.warning(f"ColBERT model not found, using sentence-transformers")
                self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', device=self.device)
                self.tokenizer = self.model.tokenizer
        else:
            # Use sentence-transformers as base
            self.model = SentenceTransformer(model_name, device=self.device)
            self.tokenizer = self.model.tokenizer
        
        self.dimension = 128  # ColBERT dimension
        logger.info(f"Multi-vector model loaded. Token embedding dimension: {self.dimension}")
    
    def encode_batch(self, texts: List[str], batch_size: int = 16) -> List[np.ndarray]:
        """Encode texts to multi-vector embeddings."""
        embeddings = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="Encoding multi-vector"):
            batch_texts = texts[i:i + batch_size]
            batch_embeddings = self._encode_batch_internal(batch_texts)
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def _encode_batch_internal(self, texts: List[str]) -> List[np.ndarray]:
        """Internal method to encode a batch."""
        # Tokenize
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_tokens,
            return_tensors="pt"
        ).to(self.device)
        
        # Get embeddings
        with torch.no_grad():
            if hasattr(self.model, 'encode'):
                # sentence-transformers model
                embeddings = []
                for text in texts:
                    # Get token-level embeddings
                    tokens = self.tokenizer(
                        text,
                        padding=True,
                        truncation=True,
                        max_length=self.max_tokens,
                        return_tensors="pt"
                    ).to(self.device)
                    
                    # Simple approach: use the model's hidden states
                    outputs = self.model[0].auto_model(**tokens)
                    token_embeddings = outputs.last_hidden_state[0]  # [seq_len, hidden_dim]
                    
                    # Project to target dimension if needed
                    if token_embeddings.shape[-1] != self.dimension:
                        # Simple linear projection
                        token_embeddings = token_embeddings[:, :self.dimension]
                    
                    # Remove padding tokens
                    attention_mask = tokens['attention_mask'][0]
                    token_embeddings = token_embeddings[attention_mask.bool()]
                    
                    embeddings.append(token_embeddings.cpu().numpy())
            else:
                # Transformer model
                outputs = self.model(**inputs)
                hidden_states = outputs.last_hidden_state  # [batch_size, seq_len, hidden_dim]
                
                embeddings = []
                for i, text in enumerate(texts):
                    # Get attention mask for this sequence
                    attention_mask = inputs['attention_mask'][i]
                    seq_len = attention_mask.sum().item()
                    
                    # Get token embeddings for non-padding tokens
                    token_embeddings = hidden_states[i, :seq_len, :]  # [actual_seq_len, hidden_dim]
                    
                    # Project to target dimension if needed
                    if token_embeddings.shape[-1] != self.dimension:
                        token_embeddings = token_embeddings[:, :self.dimension]
                    
                    embeddings.append(token_embeddings.cpu().numpy())
        
        return embeddings


def load_config(config_path: str) -> Dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_embeddings(embeddings: List, output_path: Path, embedding_type: str = "single"):
    """Save embeddings to file."""
    logger.info(f"Saving {embedding_type} embeddings to {output_path}")
    
    if embedding_type == "single":
        # Single vector embeddings: save as numpy array
        np.save(output_path, np.array(embeddings))
    else:
        # Multi-vector embeddings: save as list of arrays
        with open(output_path, 'wb') as f:
            np.save(f, embeddings, allow_pickle=True)


def main():
    parser = argparse.ArgumentParser(description="Generate embeddings for MS MARCO dataset")
    parser.add_argument("--config", default="config/default.yaml", help="Configuration file path")
    parser.add_argument("--type", choices=["single", "multi", "both"], default="both", 
                       help="Type of embeddings to generate")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for encoding")
    parser.add_argument("--max-samples", type=int, default=-1, help="Maximum number of samples to process")
    parser.add_argument("--device", default="auto", help="Device to use (auto, cpu, cuda)")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Create embeddings directory
    embeddings_dir = Path("data/embeddings")
    embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    # Load processed data
    processed_dir = Path("data/processed")
    
    logger.info("Loading processed data...")
    passages_df = pd.read_json(processed_dir / "passages.jsonl", lines=True)
    queries_df = pd.read_json(processed_dir / "queries.jsonl", lines=True)
    
    if args.max_samples > 0:
        passages_df = passages_df.head(args.max_samples)
        queries_df = queries_df.head(min(args.max_samples, len(queries_df)))
    
    logger.info(f"Loaded {len(passages_df)} passages and {len(queries_df)} queries")
    
    # Generate single-vector embeddings
    if args.type in ["single", "both"]:
        logger.info("🔢 Generating single-vector embeddings...")
        
        single_config = config['models']['single_vector']
        embedder = SingleVectorEmbedder(
            model_name=single_config['model_name'],
            device=args.device
        )
        
        # Encode passages
        logger.info("Encoding passages...")
        passage_texts = [f"{row['title']} {row['content']}".strip() for _, row in passages_df.iterrows()]
        passage_embeddings = embedder.encode_passages(passage_texts, batch_size=args.batch_size)
        
        # Save passage embeddings
        save_embeddings(
            passage_embeddings,
            embeddings_dir / "single_vector_passages.npy",
            "single"
        )
        
        # Encode queries
        logger.info("Encoding queries...")
        query_texts = queries_df['text'].tolist()
        query_embeddings = embedder.encode_queries(query_texts, batch_size=args.batch_size)
        
        # Save query embeddings
        save_embeddings(
            query_embeddings,
            embeddings_dir / "single_vector_queries.npy",
            "single"
        )
        
        logger.info("✅ Single-vector embeddings generated successfully")
    
    # Generate multi-vector embeddings
    if args.type in ["multi", "both"]:
        logger.info("🔢 Generating multi-vector embeddings...")
        
        multi_config = config['models']['multi_vector']
        embedder = MultiVectorEmbedder(
            model_name=multi_config['model_name'],
            max_tokens=multi_config['max_tokens'],
            device=args.device
        )
        
        # Encode passages
        logger.info("Encoding passages with multi-vector...")
        passage_texts = [f"{row['title']} {row['content']}".strip() for _, row in passages_df.iterrows()]
        passage_embeddings = embedder.encode_batch(passage_texts, batch_size=args.batch_size)
        
        # Save passage embeddings
        save_embeddings(
            passage_embeddings,
            embeddings_dir / "multi_vector_passages.npy",
            "multi"
        )
        
        # Encode queries
        logger.info("Encoding queries with multi-vector...")
        query_texts = queries_df['text'].tolist()
        query_embeddings = embedder.encode_batch(query_texts, batch_size=args.batch_size)
        
        # Save query embeddings
        save_embeddings(
            query_embeddings,
            embeddings_dir / "multi_vector_queries.npy",
            "multi"
        )
        
        logger.info("✅ Multi-vector embeddings generated successfully")
    
    # Create embedding metadata
    metadata = {
        'single_vector': {
            'model_name': config['models']['single_vector']['model_name'],
            'dimension': config['models']['single_vector']['dimension'],
            'passages_count': len(passages_df),
            'queries_count': len(queries_df),
        },
        'multi_vector': {
            'model_name': config['models']['multi_vector']['model_name'],
            'dimension': config['models']['multi_vector']['dimension'],
            'max_tokens': config['models']['multi_vector']['max_tokens'],
            'passages_count': len(passages_df),
            'queries_count': len(queries_df),
        }
    }
    
    with open(embeddings_dir / "metadata.yaml", 'w') as f:
        yaml.dump(metadata, f, default_flow_style=False)
    
    logger.info(f"📊 Embedding metadata saved to {embeddings_dir / 'metadata.yaml'}")
    
    print("\n🎉 Embedding generation complete!")
    print(f"📁 Embeddings saved to: {embeddings_dir}")
    print("\n🎯 Next steps:")
    print("   1. Index documents: python scripts/experiments/run_indexing.py")
    print("   2. Run evaluation: python scripts/experiments/run_evaluation.py")


if __name__ == "__main__":
    main()