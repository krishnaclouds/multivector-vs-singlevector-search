"""
Search Service Implementation
Handles all search operations using Qdrant vector database
"""

import json
import time
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.http.exceptions import UnexpectedResponse

from app.core.config import Config

logger = logging.getLogger(__name__)

class SearchService:
    """Main search service class"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.client = None
        self.model = None
        self.embedding_cache = {}
        self.sample_data = []
        
        # Initialize components
        self._initialize_client()
        self._initialize_model()
        self._load_sample_data()
    
    def _initialize_client(self):
        """Initialize Qdrant client"""
        try:
            self.client = QdrantClient(
                host=self.config.QDRANT_HOST,
                port=self.config.QDRANT_PORT,
                api_key=self.config.QDRANT_API_KEY,
                timeout=self.config.SEARCH_TIMEOUT
            )
            
            # Test connection
            collections = self.client.get_collections()
            logger.info(f"✅ Connected to Qdrant at {self.config.QDRANT_URL}")
            
            # Create collection if it doesn't exist
            self._ensure_collection_exists()
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Qdrant: {e}")
            # For development, use in-memory search
            self.client = None
    
    def _initialize_model(self):
        """Initialize embedding model"""
        try:
            self.model = SentenceTransformer(
                self.config.EMBEDDING_MODEL,
                cache_folder=self.config.MODEL_CACHE_DIR
            )
            logger.info(f"✅ Loaded embedding model: {self.config.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            self.model = None
    
    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.config.COLLECTION_NAME not in collection_names:
                self.client.create_collection(
                    collection_name=self.config.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.config.VECTOR_SIZE,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ Created collection: {self.config.COLLECTION_NAME}")
            else:
                logger.info(f"✅ Collection exists: {self.config.COLLECTION_NAME}")
        except Exception as e:
            logger.error(f"❌ Failed to ensure collection exists: {e}")
    
    def _load_sample_data(self):
        """Load sample data for demonstration"""
        try:
            # Load from processed data if available
            processed_file = self.config.PROCESSED_DIR / 'passages.jsonl'
            if processed_file.exists():
                with open(processed_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            self.sample_data.append(json.loads(line))
                logger.info(f"✅ Loaded {len(self.sample_data)} documents from processed data")
            else:
                # Create sample data
                self.sample_data = self._create_sample_data()
                logger.info(f"✅ Created {len(self.sample_data)} sample documents")
        except Exception as e:
            logger.error(f"❌ Failed to load sample data: {e}")
            self.sample_data = self._create_sample_data()
    
    def _create_sample_data(self) -> List[Dict]:
        """Create sample documents for demonstration"""
        topics = [
            "Artificial Intelligence and Machine Learning",
            "Climate Change and Environmental Science",
            "Space Exploration and Astronomy",
            "Quantum Computing and Physics",
            "Biotechnology and Genetics",
            "Renewable Energy Technologies",
            "Cybersecurity and Privacy",
            "Blockchain and Cryptocurrency",
            "Medical Research and Healthcare",
            "Robotics and Automation"
        ]
        
        sample_docs = []
        for i, topic in enumerate(topics):
            for j in range(50):  # 50 docs per topic
                doc_id = f"doc_{i}_{j}"
                title = f"{topic} Research Paper {j+1}"
                content = f"This is a comprehensive research document about {topic.lower()}. " \
                         f"It covers the latest developments, methodologies, and future directions " \
                         f"in the field. The paper discusses various aspects including theoretical " \
                         f"foundations, practical applications, and emerging trends. Document {j+1} " \
                         f"of the {topic} collection provides detailed insights and analysis."
                
                sample_docs.append({
                    'id': doc_id,
                    'title': title,
                    'content': content,
                    'topic': topic,
                    'timestamp': int(time.time()),
                    'url': f"https://example.com/research/{doc_id}"
                })
        
        return sample_docs
    
    def get_query_embeddings(self, query_text: str) -> np.ndarray:
        """Get embeddings for a query"""
        if not self.model:
            # Fallback to hash-based approach
            return self._get_hash_embedding(query_text)
        
        try:
            # Check cache first
            cache_key = hashlib.md5(query_text.encode()).hexdigest()
            if cache_key in self.embedding_cache:
                return self.embedding_cache[cache_key]
            
            # Generate embedding
            embedding = self.model.encode(query_text)
            
            # Cache the result
            self.embedding_cache[cache_key] = embedding
            
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return self._get_hash_embedding(query_text)
    
    def _get_hash_embedding(self, text: str) -> np.ndarray:
        """Generate hash-based embedding as fallback"""
        # Simple hash-based embedding for demonstration
        hash_val = hashlib.md5(text.encode()).hexdigest()
        np.random.seed(int(hash_val[:8], 16))
        return np.random.rand(self.config.VECTOR_SIZE)
    
    def search_semantic(self, query_text: str, max_results: int = 10) -> Dict[str, Any]:
        """Perform semantic search"""
        start_time = time.time()
        
        try:
            # Get query embedding
            query_embedding = self.get_query_embeddings(query_text)
            
            if self.client:
                # Search using Qdrant
                results = self.client.search(
                    collection_name=self.config.COLLECTION_NAME,
                    query_vector=query_embedding.tolist(),
                    limit=max_results
                )
                
                # Format results
                formatted_results = []
                for result in results:
                    formatted_results.append({
                        'id': result.id,
                        'title': result.payload.get('title', 'Untitled'),
                        'content': self._truncate_content(result.payload.get('content', '')),
                        'url': result.payload.get('url', ''),
                        'relevance': round(result.score, 4),
                        'timestamp': result.payload.get('timestamp', 0)
                    })
            else:
                # Fallback to in-memory search
                formatted_results = self._search_in_memory(query_text, query_embedding, max_results)
            
            search_time = (time.time() - start_time) * 1000
            
            return {
                'name': 'Semantic Search',
                'description': 'Dense vector similarity search',
                'time_ms': round(search_time, 1),
                'results': formatted_results,
                'color': '#4F46E5'
            }
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return {
                'name': 'Semantic Search',
                'description': 'Dense vector similarity search',
                'time_ms': 0,
                'results': [],
                'error': str(e),
                'color': '#4F46E5'
            }
    
    def search_keyword(self, query_text: str, max_results: int = 10) -> Dict[str, Any]:
        """Perform keyword-based search"""
        start_time = time.time()
        
        try:
            # Simple keyword matching on sample data
            query_words = set(query_text.lower().split())
            results = []
            
            for doc in self.sample_data:
                # Calculate keyword overlap score
                doc_words = set((doc['title'] + ' ' + doc['content']).lower().split())
                overlap = len(query_words.intersection(doc_words))
                
                if overlap > 0:
                    # Simple TF-IDF like scoring
                    score = overlap / len(query_words)
                    results.append({
                        'doc': doc,
                        'score': score
                    })
            
            # Sort by score and limit results
            results.sort(key=lambda x: x['score'], reverse=True)
            results = results[:max_results]
            
            # Format results
            formatted_results = []
            for result in results:
                doc = result['doc']
                formatted_results.append({
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': self._truncate_content(doc['content']),
                    'url': doc['url'],
                    'relevance': round(result['score'], 4),
                    'timestamp': doc['timestamp']
                })
            
            search_time = (time.time() - start_time) * 1000
            
            return {
                'name': 'Keyword Search',
                'description': 'Traditional keyword-based search',
                'time_ms': round(search_time, 1),
                'results': formatted_results,
                'color': '#DC2626'
            }
            
        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return {
                'name': 'Keyword Search',
                'description': 'Traditional keyword-based search',
                'time_ms': 0,
                'results': [],
                'error': str(e),
                'color': '#DC2626'
            }
    
    def search_hybrid(self, query_text: str, max_results: int = 10) -> Dict[str, Any]:
        """Perform hybrid search (semantic + keyword)"""
        start_time = time.time()
        
        try:
            # Get results from both approaches
            semantic_results = self.search_semantic(query_text, max_results * 2)
            keyword_results = self.search_keyword(query_text, max_results * 2)
            
            # Combine and re-rank results
            combined_results = {}
            
            # Add semantic results with weight
            for result in semantic_results['results']:
                doc_id = result['id']
                if doc_id not in combined_results:
                    combined_results[doc_id] = result.copy()
                    combined_results[doc_id]['semantic_score'] = result['relevance']
                    combined_results[doc_id]['keyword_score'] = 0
                    combined_results[doc_id]['hybrid_score'] = result['relevance'] * 0.7
            
            # Add keyword results with weight
            for result in keyword_results['results']:
                doc_id = result['id']
                if doc_id in combined_results:
                    combined_results[doc_id]['keyword_score'] = result['relevance']
                    combined_results[doc_id]['hybrid_score'] += result['relevance'] * 0.3
                else:
                    combined_results[doc_id] = result.copy()
                    combined_results[doc_id]['semantic_score'] = 0
                    combined_results[doc_id]['keyword_score'] = result['relevance']
                    combined_results[doc_id]['hybrid_score'] = result['relevance'] * 0.3
            
            # Sort by hybrid score and format
            sorted_results = sorted(
                combined_results.values(),
                key=lambda x: x['hybrid_score'],
                reverse=True
            )[:max_results]
            
            # Clean up results
            for result in sorted_results:
                result['relevance'] = round(result['hybrid_score'], 4)
                # Remove intermediate scores
                result.pop('semantic_score', None)
                result.pop('keyword_score', None)
                result.pop('hybrid_score', None)
            
            search_time = (time.time() - start_time) * 1000
            
            return {
                'name': 'Hybrid Search',
                'description': 'Combined semantic and keyword search',
                'time_ms': round(search_time, 1),
                'results': sorted_results,
                'color': '#7C2D12'
            }
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return {
                'name': 'Hybrid Search',
                'description': 'Combined semantic and keyword search',
                'time_ms': 0,
                'results': [],
                'error': str(e),
                'color': '#7C2D12'
            }
    
    def _search_in_memory(self, query_text: str, query_embedding: np.ndarray, max_results: int) -> List[Dict]:
        """Fallback in-memory search"""
        results = []
        
        for doc in self.sample_data:
            # Generate document embedding
            doc_embedding = self._get_hash_embedding(doc['title'] + ' ' + doc['content'])
            
            # Calculate cosine similarity
            similarity = np.dot(query_embedding, doc_embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
            )
            
            results.append({
                'doc': doc,
                'score': similarity
            })
        
        # Sort by similarity and limit results
        results.sort(key=lambda x: x['score'], reverse=True)
        results = results[:max_results]
        
        # Format results
        formatted_results = []
        for result in results:
            doc = result['doc']
            formatted_results.append({
                'id': doc['id'],
                'title': doc['title'],
                'content': self._truncate_content(doc['content']),
                'url': doc['url'],
                'relevance': round(result['score'], 4),
                'timestamp': doc['timestamp']
            })
        
        return formatted_results
    
    def search_all_approaches(self, query_text: str, max_results: int = 10) -> Dict[str, Any]:
        """Search using all available approaches"""
        return {
            'query': query_text,
            'approaches': {
                'semantic': self.search_semantic(query_text, max_results),
                'keyword': self.search_keyword(query_text, max_results),
                'hybrid': self.search_hybrid(query_text, max_results)
            }
        }
    
    def _truncate_content(self, content: str, max_length: int = 200) -> str:
        """Truncate content for display"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information"""
        status = {
            'qdrant_healthy': False,
            'model_loaded': bool(self.model),
            'embeddings_loaded': bool(self.embedding_cache),
            'document_count': len(self.sample_data),
            'collection_info': {}
        }
        
        # Check Qdrant health
        try:
            if self.client:
                collections = self.client.get_collections()
                status['qdrant_healthy'] = True
                
                # Get collection info
                try:
                    collection_info = self.client.get_collection(self.config.COLLECTION_NAME)
                    status['collection_info'] = {
                        'name': collection_info.name,
                        'status': collection_info.status,
                        'vectors_count': collection_info.vectors_count,
                        'indexed_vectors_count': collection_info.indexed_vectors_count
                    }
                except:
                    status['collection_info'] = {'name': self.config.COLLECTION_NAME, 'status': 'not_found'}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            status['qdrant_healthy'] = False
        
        return status
    
    def index_documents(self, documents: List[Dict]) -> bool:
        """Index documents to Qdrant"""
        if not self.client:
            logger.error("Qdrant client not available")
            return False
        
        try:
            points = []
            for doc in documents:
                # Generate embedding for document
                doc_text = f"{doc['title']} {doc['content']}"
                embedding = self.get_query_embeddings(doc_text)
                
                point = PointStruct(
                    id=doc['id'],
                    vector=embedding.tolist(),
                    payload=doc
                )
                points.append(point)
            
            # Index to Qdrant
            self.client.upsert(
                collection_name=self.config.COLLECTION_NAME,
                points=points
            )
            
            logger.info(f"✅ Indexed {len(points)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to index documents: {e}")
            return False