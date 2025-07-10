#!/usr/bin/env python3
"""
ASMuvera Web UI
Interactive web interface for testing single vs multi-vector search
"""

from flask import Flask, render_template, request, jsonify
import json
import numpy as np
import time
from pathlib import Path
from search_evaluation import VespaSearchClient
import threading
import queue
import hashlib

app = Flask(__name__)

class SearchService:
    def __init__(self):
        self.client = VespaSearchClient()
        self.embedding_cache = {}
        self.load_sample_embeddings()
    
    def load_sample_embeddings(self):
        """Load sample embeddings for demo purposes"""
        try:
            # Load real embeddings if available
            single_emb_path = Path("data/embeddings/single_vector_queries.npy")
            multi_emb_path = Path("data/embeddings/multi_vector_queries.npy")
            
            if single_emb_path.exists():
                self.sample_single_embeddings = np.load(single_emb_path)
            else:
                self.sample_single_embeddings = np.random.rand(10, 384)
                
            if multi_emb_path.exists():
                self.sample_multi_embeddings = np.load(multi_emb_path, allow_pickle=True)
            else:
                self.sample_multi_embeddings = [np.random.rand(5, 128) for _ in range(10)]
            
            print("✅ Sample embeddings loaded")
        except Exception as e:
            print(f"⚠️  Using random embeddings: {e}")
            self.sample_single_embeddings = np.random.rand(10, 384)
            self.sample_multi_embeddings = [np.random.rand(5, 128) for _ in range(10)]
    
    def get_query_embeddings(self, query_text: str):
        """Get embeddings for a query (using simple hash-based approach)"""
        # Use hash to select consistent embeddings for same query
        query_hash = int(hashlib.md5(query_text.encode()).hexdigest(), 16) % len(self.sample_single_embeddings)
        
        single_emb = self.sample_single_embeddings[query_hash]
        multi_emb = self.sample_multi_embeddings[query_hash]
        
        return single_emb, multi_emb
    
    def search_all_approaches(self, query_text: str, max_results: int = 5):
        """Search using all approaches and return results"""
        
        single_emb, multi_emb = self.get_query_embeddings(query_text)
        
        results = {
            "query": query_text,
            "approaches": {}
        }
        
        # 1. Single Vector Search
        try:
            start_time = time.time()
            single_response = self.client.search_single_vector(single_emb, query_text, hits=max_results)
            single_time = (time.time() - start_time) * 1000
            
            results["approaches"]["single_vector"] = {
                "name": "Single Vector",
                "description": "Dense 384-dimensional vectors with cosine similarity",
                "time_ms": round(single_time, 1),
                "results": self._format_results(single_response),
                "color": "#4F46E5"
            }
        except Exception as e:
            results["approaches"]["single_vector"] = {
                "name": "Single Vector",
                "description": "Dense 384-dimensional vectors with cosine similarity",
                "time_ms": 0,
                "results": [],
                "error": str(e),
                "color": "#4F46E5"
            }
        
        # 2. Multi-Vector Search
        try:
            start_time = time.time()
            multi_response = self.client.search_multi_vector(multi_emb, query_text, hits=max_results)
            multi_time = (time.time() - start_time) * 1000
            
            results["approaches"]["multi_vector"] = {
                "name": "Multi-Vector (ColBERT-style)",
                "description": "Token-level vectors with MaxSim operations",
                "time_ms": round(multi_time, 1),
                "results": self._format_results(multi_response),
                "color": "#059669"
            }
        except Exception as e:
            results["approaches"]["multi_vector"] = {
                "name": "Multi-Vector (ColBERT-style)",
                "description": "Token-level vectors with MaxSim operations",
                "time_ms": 0,
                "results": [],
                "error": str(e),
                "color": "#059669"
            }
        
        # 3. Text-only Search (BM25)
        try:
            start_time = time.time()
            text_response = self.client.search_text_only(query_text, hits=max_results)
            text_time = (time.time() - start_time) * 1000
            
            results["approaches"]["text_only"] = {
                "name": "Text-only (BM25)",
                "description": "Traditional keyword-based search",
                "time_ms": round(text_time, 1),
                "results": self._format_results(text_response),
                "color": "#DC2626"
            }
        except Exception as e:
            results["approaches"]["text_only"] = {
                "name": "Text-only (BM25)",
                "description": "Traditional keyword-based search",
                "time_ms": 0,
                "results": [],
                "error": str(e),
                "color": "#DC2626"
            }
        
        # 4. Hybrid Search
        try:
            start_time = time.time()
            hybrid_response = self.client.search_single_vector(
                single_emb, query_text, rank_profile="hybrid", hits=max_results
            )
            hybrid_time = (time.time() - start_time) * 1000
            
            results["approaches"]["hybrid"] = {
                "name": "Hybrid (Text + Vector)",
                "description": "Combined text and semantic ranking",
                "time_ms": round(hybrid_time, 1),
                "results": self._format_results(hybrid_response),
                "color": "#7C2D12"
            }
        except Exception as e:
            results["approaches"]["hybrid"] = {
                "name": "Hybrid (Text + Vector)",
                "description": "Combined text and semantic ranking",
                "time_ms": 0,
                "results": [],
                "error": str(e),
                "color": "#7C2D12"
            }
        
        return results
    
    def _format_results(self, vespa_response):
        """Format Vespa response for UI"""
        formatted_results = []
        
        try:
            children = vespa_response.get("root", {}).get("children", [])
            
            for hit in children:
                fields = hit.get("fields", {})
                formatted_results.append({
                    "id": fields.get("id", "N/A"),
                    "title": fields.get("title", "No Title"),
                    "content": self._truncate_content(fields.get("content", "No content available")),
                    "url": fields.get("url", ""),
                    "relevance": round(hit.get("relevance", 0), 4),
                    "timestamp": fields.get("timestamp", 0)
                })
        except Exception as e:
            print(f"Error formatting results: {e}")
        
        return formatted_results
    
    def _truncate_content(self, content: str, max_length: int = 200) -> str:
        """Truncate content for display"""
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."
    
    def get_system_status(self):
        """Get system status information"""
        status = {
            "vespa_healthy": False,
            "document_counts": {
                "single_vector": 0,
                "multi_vector": 0
            },
            "embeddings_loaded": bool(hasattr(self, 'sample_single_embeddings'))
        }
        
        try:
            # Test Vespa connection
            import requests
            response = requests.get(f"{self.client.vespa_url}/state/v1/health", timeout=5)
            status["vespa_healthy"] = response.status_code == 200
        except:
            pass
        
        # Try to get document counts (simplified)
        try:
            single_response = self.client.search_single_vector(
                np.random.rand(384), hits=0
            )
            status["document_counts"]["single_vector"] = len(
                single_response.get("root", {}).get("children", [])
            )
        except:
            pass
        
        try:
            multi_response = self.client.search_multi_vector(
                np.random.rand(5, 128), hits=0
            )
            status["document_counts"]["multi_vector"] = len(
                multi_response.get("root", {}).get("children", [])
            )
        except:
            pass
        
        return status

# Initialize search service
search_service = SearchService()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """Search API endpoint"""
    data = request.json
    query = data.get('query', '').strip()
    max_results = min(data.get('max_results', 5), 20)  # Limit to 20 results max
    
    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        results = search_service.search_all_approaches(query, max_results)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status')
def api_status():
    """System status API endpoint"""
    try:
        status = search_service.get_system_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sample-queries')
def api_sample_queries():
    """Get sample queries for testing"""
    sample_queries = [
        "manhattan project atomic bomb",
        "nuclear physics research",
        "scientific development world war",
        "atomic energy applications",
        "historical documents archives",
        "research methodology science",
        "technology innovation history",
        "military applications nuclear",
        "government scientific projects",
        "wartime technological advances"
    ]
    return jsonify({"queries": sample_queries})

if __name__ == '__main__':
    print("🌐 Starting ASMuvera Web UI...")
    print("📍 Access the interface at: http://localhost:5000")
    print("🔍 Compare single vs multi-vector search approaches!")
    app.run(host='0.0.0.0', port=5000, debug=True)