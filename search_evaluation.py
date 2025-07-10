#!/usr/bin/env python3
"""
ASMuvera Search and Evaluation Framework
Compares single-vector vs multi-vector search performance
"""

import json
import numpy as np
import requests
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any
import argparse

class VespaSearchClient:
    def __init__(self, vespa_url: str = "http://localhost:8080"):
        self.vespa_url = vespa_url
        self.search_api = f"{vespa_url}/search/"
        
    def search_single_vector(self, query_embedding: np.ndarray, query_text: str = "", 
                           rank_profile: str = "default", hits: int = 10) -> Dict:
        """Search using single vector approach"""
        
        # Build YQL query
        yql = f"select * from single_vector_document where true"
        
        params = {
            "yql": yql,
            "hits": hits,
            "ranking": rank_profile,
            "input.query(q_embedding)": self._format_dense_vector(query_embedding)
        }
        
        if query_text:
            params["query"] = query_text
            
        try:
            response = requests.get(self.search_api, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Single vector search failed: {response.status_code} - {response.text}")
                return {"root": {"children": []}}
        except Exception as e:
            print(f"❌ Single vector search error: {e}")
            return {"root": {"children": []}}
    
    def search_multi_vector(self, query_embeddings: np.ndarray, query_text: str = "",
                          rank_profile: str = "default", hits: int = 10) -> Dict:
        """Search using multi-vector approach"""
        
        # Build YQL query  
        yql = f"select * from multi_vector_document where true"
        
        params = {
            "yql": yql,
            "hits": hits,
            "ranking": rank_profile,
            "input.query(q_token_embeddings)": self._format_sparse_tensor(query_embeddings)
        }
        
        if query_text:
            params["query"] = query_text
            
        try:
            response = requests.get(self.search_api, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Multi-vector search failed: {response.status_code} - {response.text}")
                return {"root": {"children": []}}
        except Exception as e:
            print(f"❌ Multi-vector search error: {e}")
            return {"root": {"children": []}}
    
    def search_text_only(self, query_text: str, schema: str = "single_vector_document", hits: int = 10) -> Dict:
        """Search using text matching only"""
        
        yql = f"select * from {schema} where userQuery()"
        
        params = {
            "yql": yql,
            "query": query_text,
            "hits": hits,
            "ranking": "bm25"
        }
        
        try:
            response = requests.get(self.search_api, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Text search failed: {response.status_code} - {response.text}")
                return {"root": {"children": []}}
        except Exception as e:
            print(f"❌ Text search error: {e}")
            return {"root": {"children": []}}
    
    def _format_dense_vector(self, vector: np.ndarray) -> str:
        """Format dense vector for Vespa"""
        values = ",".join([str(float(x)) for x in vector.flatten()])
        return f"[{values}]"
    
    def _format_sparse_tensor(self, embeddings: np.ndarray) -> str:
        """Format sparse tensor for Vespa"""
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        
        num_tokens, dim = embeddings.shape
        cells = []
        
        for token_idx in range(num_tokens):
            for dim_idx in range(dim):
                value = float(embeddings[token_idx, dim_idx])
                if abs(value) > 1e-6:  # Only include non-zero values for sparsity
                    cells.append(f"{{token:{token_idx},x:{dim_idx}}}:{value}")
        
        return "{" + ",".join(cells) + "}"

class SearchEvaluator:
    def __init__(self, client: VespaSearchClient):
        self.client = client
        self.results = []
        
    def load_queries_and_embeddings(self):
        """Load test queries and their embeddings"""
        print("📥 Loading queries and embeddings...")
        
        # Load queries
        queries_path = Path("data/processed/queries.jsonl")
        if queries_path.exists():
            with open(queries_path, 'r') as f:
                self.queries = [json.loads(line) for line in f]
        else:
            # Create some sample queries if no queries file exists
            self.queries = [
                {"id": "q1", "text": "manhattan project atomic bomb"},
                {"id": "q2", "text": "world war 2 events"},
                {"id": "q3", "text": "nuclear energy physics"},
                {"id": "q4", "text": "historical documents archives"},
                {"id": "q5", "text": "scientific research development"}
            ]
        
        # Load query embeddings
        single_emb_path = Path("data/embeddings/single_vector_queries.npy")
        multi_emb_path = Path("data/embeddings/multi_vector_queries.npy")
        
        if single_emb_path.exists():
            self.single_query_embeddings = np.load(single_emb_path)
        else:
            print("⚠️  No single vector query embeddings found, generating dummy ones...")
            self.single_query_embeddings = np.random.rand(len(self.queries), 384)
            
        if multi_emb_path.exists():
            self.multi_query_embeddings = np.load(multi_emb_path, allow_pickle=True)
        else:
            print("⚠️  No multi-vector query embeddings found, generating dummy ones...")
            self.multi_query_embeddings = [np.random.rand(5, 128) for _ in self.queries]
        
        print(f"✅ Loaded {len(self.queries)} queries")
        print(f"✅ Single vector embeddings: {self.single_query_embeddings.shape}")
        print(f"✅ Multi-vector embeddings: {len(self.multi_query_embeddings)} documents")
    
    def run_evaluation(self, max_queries: int = 5):
        """Run comprehensive evaluation"""
        print(f"\n🧪 Running evaluation with {min(max_queries, len(self.queries))} queries...")
        
        self.results = []
        
        for i in range(min(max_queries, len(self.queries))):
            query = self.queries[i]
            single_emb = self.single_query_embeddings[i]
            multi_emb = self.multi_query_embeddings[i]
            
            print(f"\n📋 Query {i+1}: '{query['text']}'")
            
            # Measure search times and get results
            result = {
                "query_id": query["id"],
                "query_text": query["text"],
                "approaches": {}
            }
            
            # 1. Single Vector Semantic Search
            start_time = time.time()
            single_results = self.client.search_single_vector(single_emb, hits=5)
            single_time = time.time() - start_time
            
            result["approaches"]["single_vector"] = {
                "time_ms": single_time * 1000,
                "num_results": len(single_results.get("root", {}).get("children", [])),
                "results": self._extract_results(single_results)
            }
            
            # 2. Multi-Vector Semantic Search  
            start_time = time.time()
            multi_results = self.client.search_multi_vector(multi_emb, hits=5)
            multi_time = time.time() - start_time
            
            result["approaches"]["multi_vector"] = {
                "time_ms": multi_time * 1000,
                "num_results": len(multi_results.get("root", {}).get("children", [])),
                "results": self._extract_results(multi_results)
            }
            
            # 3. Text-only Search (BM25)
            start_time = time.time()
            text_results = self.client.search_text_only(query["text"], hits=5)
            text_time = time.time() - start_time
            
            result["approaches"]["text_only"] = {
                "time_ms": text_time * 1000,
                "num_results": len(text_results.get("root", {}).get("children", [])),
                "results": self._extract_results(text_results)
            }
            
            # 4. Hybrid Search (if available)
            start_time = time.time()
            hybrid_results = self.client.search_single_vector(
                single_emb, query["text"], rank_profile="hybrid", hits=5
            )
            hybrid_time = time.time() - start_time
            
            result["approaches"]["hybrid"] = {
                "time_ms": hybrid_time * 1000, 
                "num_results": len(hybrid_results.get("root", {}).get("children", [])),
                "results": self._extract_results(hybrid_results)
            }
            
            self.results.append(result)
            
            # Print summary for this query
            self._print_query_summary(result)
        
        # Save results
        self._save_results()
        
        # Print overall summary
        self._print_overall_summary()
    
    def _extract_results(self, search_response: Dict) -> List[Dict]:
        """Extract clean results from Vespa response"""
        results = []
        children = search_response.get("root", {}).get("children", [])
        
        for hit in children:
            fields = hit.get("fields", {})
            results.append({
                "id": fields.get("id", ""),
                "title": fields.get("title", ""),
                "content": fields.get("content", "")[:200] + "..." if len(fields.get("content", "")) > 200 else fields.get("content", ""),
                "relevance": hit.get("relevance", 0.0)
            })
        
        return results
    
    def _print_query_summary(self, result: Dict):
        """Print summary for a single query"""
        query_text = result["query_text"]
        approaches = result["approaches"]
        
        print(f"  📊 Results for '{query_text}':")
        for approach, data in approaches.items():
            time_ms = data["time_ms"]
            num_results = data["num_results"]
            avg_relevance = np.mean([r["relevance"] for r in data["results"]]) if data["results"] else 0
            
            print(f"    {approach:12} | {time_ms:6.1f}ms | {num_results} results | avg relevance: {avg_relevance:.3f}")
        
        # Show top result for each approach
        print("  🏆 Top results:")
        for approach, data in approaches.items():
            if data["results"]:
                top_result = data["results"][0]
                print(f"    {approach:12} | {top_result['title'][:50]}")
    
    def _print_overall_summary(self):
        """Print overall evaluation summary"""
        print(f"\n📊 OVERALL EVALUATION SUMMARY")
        print("=" * 80)
        
        # Calculate averages
        approach_stats = {}
        for result in self.results:
            for approach, data in result["approaches"].items():
                if approach not in approach_stats:
                    approach_stats[approach] = {"times": [], "num_results": [], "relevances": []}
                
                approach_stats[approach]["times"].append(data["time_ms"])
                approach_stats[approach]["num_results"].append(data["num_results"])
                
                if data["results"]:
                    avg_rel = np.mean([r["relevance"] for r in data["results"]])
                    approach_stats[approach]["relevances"].append(avg_rel)
        
        # Print comparison table
        print(f"{'Approach':<15} | {'Avg Time':<10} | {'Avg Results':<12} | {'Avg Relevance':<15}")
        print("-" * 80)
        
        for approach, stats in approach_stats.items():
            avg_time = np.mean(stats["times"])
            avg_results = np.mean(stats["num_results"])
            avg_relevance = np.mean(stats["relevances"]) if stats["relevances"] else 0
            
            print(f"{approach:<15} | {avg_time:8.1f}ms | {avg_results:10.1f} | {avg_relevance:13.3f}")
        
        print("\n💡 Key Insights:")
        
        # Find fastest approach
        fastest = min(approach_stats.keys(), key=lambda k: np.mean(approach_stats[k]["times"]))
        print(f"  • Fastest approach: {fastest}")
        
        # Find most relevant approach
        most_relevant = max(approach_stats.keys(), 
                          key=lambda k: np.mean(approach_stats[k]["relevances"]) if approach_stats[k]["relevances"] else 0)
        print(f"  • Most relevant results: {most_relevant}")
        
        # Compare single vs multi-vector
        if "single_vector" in approach_stats and "multi_vector" in approach_stats:
            single_time = np.mean(approach_stats["single_vector"]["times"])
            multi_time = np.mean(approach_stats["multi_vector"]["times"])
            single_rel = np.mean(approach_stats["single_vector"]["relevances"]) if approach_stats["single_vector"]["relevances"] else 0
            multi_rel = np.mean(approach_stats["multi_vector"]["relevances"]) if approach_stats["multi_vector"]["relevances"] else 0
            
            print(f"  • Multi-vector vs Single-vector:")
            print(f"    - Speed: {'Multi-vector faster' if multi_time < single_time else 'Single-vector faster'} ({abs(multi_time - single_time):.1f}ms difference)")
            print(f"    - Relevance: {'Multi-vector better' if multi_rel > single_rel else 'Single-vector better'} ({abs(multi_rel - single_rel):.3f} difference)")
    
    def _save_results(self):
        """Save evaluation results to file"""
        results_path = Path("evaluation_results.json")
        with open(results_path, 'w') as f:
            json.dump({
                "timestamp": time.time(),
                "queries_evaluated": len(self.results),
                "results": self.results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to {results_path}")

def main():
    parser = argparse.ArgumentParser(description="ASMuvera Search Evaluation")
    parser.add_argument("--max-queries", type=int, default=5, help="Maximum number of queries to evaluate")
    parser.add_argument("--vespa-url", default="http://localhost:8080", help="Vespa URL")
    
    args = parser.parse_args()
    
    print("🔍 ASMuvera Search Evaluation Framework")
    print("=" * 50)
    
    # Initialize components
    client = VespaSearchClient(args.vespa_url)
    evaluator = SearchEvaluator(client)
    
    # Load data
    evaluator.load_queries_and_embeddings()
    
    # Run evaluation
    evaluator.run_evaluation(max_queries=args.max_queries)
    
    print("\n✅ Evaluation complete!")

if __name__ == "__main__":
    main()