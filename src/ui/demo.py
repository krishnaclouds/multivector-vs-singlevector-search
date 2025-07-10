#!/usr/bin/env python3
"""
Muvera Demo Script
Interactive demonstration of single vs multi-vector search
"""

import json
import numpy as np
import requests
from search_evaluation import VespaSearchClient
import time

def demonstrate_search(client: VespaSearchClient):
    """Run an interactive demonstration"""
    
    print("🔍 Muvera: Multi-Vector Search Demonstration")
    print("=" * 60)
    print()
    
    # Load some sample embeddings for demonstration
    try:
        single_emb = np.load("data/embeddings/single_vector_queries.npy")[0]  # First query embedding
        multi_emb = np.load("data/embeddings/multi_vector_queries.npy", allow_pickle=True)[0]  # First query embedding
    except:
        print("⚠️  Using random embeddings for demo...")
        single_emb = np.random.rand(384)
        multi_emb = np.random.rand(5, 128)
    
    # Demo queries
    demo_queries = [
        "manhattan project atomic bomb",
        "nuclear physics research",
        "scientific development"
    ]
    
    for i, query in enumerate(demo_queries):
        print(f"📋 Demo Query {i+1}: '{query}'")
        print("-" * 40)
        
        # Single Vector Search
        print("🔢 Single Vector Approach:")
        start_time = time.time()
        single_results = client.search_single_vector(single_emb, query, hits=3)
        single_time = (time.time() - start_time) * 1000
        
        print(f"   ⏱️  Response time: {single_time:.1f}ms")
        single_hits = single_results.get("root", {}).get("children", [])
        print(f"   📄 Results found: {len(single_hits)}")
        
        for j, hit in enumerate(single_hits[:2]):  # Show top 2
            fields = hit.get("fields", {})
            relevance = hit.get("relevance", 0)
            title = fields.get("title", "No title")[:40]
            content = fields.get("content", "No content")[:80]
            print(f"     {j+1}. {title} (score: {relevance:.3f})")
            print(f"        {content}...")
        
        print()
        
        # Multi-Vector Search
        print("🧩 Multi-Vector Approach (ColBERT-style):")
        start_time = time.time()
        multi_results = client.search_multi_vector(multi_emb, query, hits=3)
        multi_time = (time.time() - start_time) * 1000
        
        print(f"   ⏱️  Response time: {multi_time:.1f}ms")
        multi_hits = multi_results.get("root", {}).get("children", [])
        print(f"   📄 Results found: {len(multi_hits)}")
        
        for j, hit in enumerate(multi_hits[:2]):  # Show top 2
            fields = hit.get("fields", {})
            relevance = hit.get("relevance", 0)
            title = fields.get("title", "No title")[:40]
            content = fields.get("content", "No content")[:80]
            print(f"     {j+1}. {title} (score: {relevance:.3f})")
            print(f"        {content}...")
        
        print()
        
        # Text-only Search for comparison
        print("📝 Text-only Search (BM25):")
        start_time = time.time()
        text_results = client.search_text_only(query, hits=3)
        text_time = (time.time() - start_time) * 1000
        
        print(f"   ⏱️  Response time: {text_time:.1f}ms")
        text_hits = text_results.get("root", {}).get("children", [])
        print(f"   📄 Results found: {len(text_hits)}")
        
        for j, hit in enumerate(text_hits[:2]):  # Show top 2
            fields = hit.get("fields", {})
            relevance = hit.get("relevance", 0)
            title = fields.get("title", "No title")[:40]
            content = fields.get("content", "No content")[:80]
            print(f"     {j+1}. {title} (score: {relevance:.3f})")
            print(f"        {content}...")
        
        print()
        
        # Performance comparison
        print("⚡ Performance Comparison:")
        fastest = min([("Single Vector", single_time), ("Multi-Vector", multi_time), ("Text-only", text_time)], key=lambda x: x[1])
        print(f"   🏆 Fastest: {fastest[0]} ({fastest[1]:.1f}ms)")
        
        if multi_time > single_time:
            print(f"   📊 Multi-vector is {multi_time - single_time:.1f}ms slower")
        else:
            print(f"   📊 Multi-vector is {single_time - multi_time:.1f}ms faster")
        
        print("\n" + "="*60 + "\n")

def show_system_status(client: VespaSearchClient):
    """Show the current system status"""
    print("💻 System Status Check")
    print("-" * 30)
    
    # Check if Vespa is responding
    try:
        response = requests.get(f"{client.vespa_url}/state/v1/health")
        if response.status_code == 200:
            print("✅ Vespa cluster: HEALTHY")
        else:
            print("❌ Vespa cluster: UNHEALTHY")
    except:
        print("❌ Vespa cluster: UNREACHABLE")
    
    # Check document counts
    try:
        # Single vector documents
        single_response = client.client.search_single_vector(np.random.rand(384), hits=0)
        single_count = single_response.get("root", {}).get("fields", {}).get("totalCount", 0)
        print(f"📄 Single vector documents: {single_count}")
        
        # Multi-vector documents  
        multi_response = client.search_multi_vector(np.random.rand(5, 128), hits=0)
        multi_count = multi_response.get("root", {}).get("fields", {}).get("totalCount", 0)
        print(f"🧩 Multi-vector documents: {multi_count}")
        
    except Exception as e:
        print(f"⚠️  Could not get document counts: {e}")
    
    print()

def main():
    print("🎯 Muvera: Advanced Semantic Multi-Vector Evaluation")
    print("Understanding the Power of Multi-Vector Search")
    print("=" * 70)
    print()
    
    # Initialize client
    client = VespaSearchClient()
    
    # Show system status
    show_system_status(client)
    
    # Run demonstration
    demonstrate_search(client)
    
    print("🎉 Demonstration Complete!")
    print()
    print("💡 Key Takeaways:")
    print("  • Multi-vector search enables ColBERT-style token interactions")
    print("  • Single vectors are faster but may miss fine-grained matches")  
    print("  • Multi-vectors capture more nuanced semantic relationships")
    print("  • Hybrid approaches can combine the best of both worlds")
    print()
    print("📖 Learn more about Muvera architecture in DESIGN.md")

if __name__ == "__main__":
    main()