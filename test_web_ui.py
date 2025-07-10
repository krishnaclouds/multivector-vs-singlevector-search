#!/usr/bin/env python3
"""
Test script for ASMuvera Web UI
Demonstrates the web interface functionality
"""

import requests
import json
import time

def test_web_ui():
    """Test the web UI API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing ASMuvera Web UI")
    print("=" * 40)
    
    # Test 1: System Status
    print("\n1. Testing system status endpoint...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ System status retrieved:")
            print(f"   Vespa Health: {'✅' if status.get('vespa_healthy') else '❌'}")
            print(f"   Single Vector Docs: {status.get('document_counts', {}).get('single_vector', 0)}")
            print(f"   Multi-Vector Docs: {status.get('document_counts', {}).get('multi_vector', 0)}")
            print(f"   Embeddings Loaded: {'✅' if status.get('embeddings_loaded') else '❌'}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status test failed: {e}")
    
    # Test 2: Sample Queries
    print("\n2. Testing sample queries endpoint...")
    try:
        response = requests.get(f"{base_url}/api/sample-queries")
        if response.status_code == 200:
            data = response.json()
            queries = data.get('queries', [])
            print(f"✅ Retrieved {len(queries)} sample queries:")
            for i, query in enumerate(queries[:3], 1):
                print(f"   {i}. {query}")
            if len(queries) > 3:
                print(f"   ... and {len(queries) - 3} more")
        else:
            print(f"❌ Sample queries endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Sample queries test failed: {e}")
    
    # Test 3: Search API
    print("\n3. Testing search endpoint...")
    test_query = "manhattan project atomic bomb"
    
    try:
        search_data = {
            "query": test_query,
            "max_results": 3
        }
        
        print(f"   Query: '{test_query}'")
        
        start_time = time.time()
        response = requests.post(
            f"{base_url}/api/search",
            json=search_data,
            headers={'Content-Type': 'application/json'}
        )
        total_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search completed in {total_time:.1f}ms total")
            print(f"   Query processed: '{results.get('query', 'N/A')}'")
            
            approaches = results.get('approaches', {})
            print(f"   Approaches tested: {len(approaches)}")
            
            for approach_name, approach_data in approaches.items():
                name = approach_data.get('name', approach_name)
                time_ms = approach_data.get('time_ms', 0)
                result_count = len(approach_data.get('results', []))
                error = approach_data.get('error')
                
                if error:
                    print(f"   ❌ {name}: ERROR - {error}")
                else:
                    print(f"   ✅ {name}: {time_ms}ms, {result_count} results")
                    
                    # Show top result if available
                    results_list = approach_data.get('results', [])
                    if results_list:
                        top_result = results_list[0]
                        title = top_result.get('title', 'No title')[:40]
                        score = top_result.get('relevance', 0)
                        print(f"      Top: {title} (score: {score})")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Search test failed: {e}")
    
    # Test 4: Web Interface Access
    print("\n4. Testing web interface access...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("✅ Web interface accessible")
            print(f"   Content length: {len(response.text)} characters")
            if "ASMuvera" in response.text:
                print("   ✅ ASMuvera branding detected")
            if "Multi-Vector" in response.text:
                print("   ✅ Multi-Vector content detected")
        else:
            print(f"❌ Web interface failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Web UI testing complete!")
    print()
    print("💡 Next steps:")
    print("   1. Open http://localhost:5000 in your browser")
    print("   2. Try the sample queries or enter your own")
    print("   3. Compare the different search approaches")
    print("   4. Monitor performance metrics in real-time")
    print()
    print("🔍 Features to explore:")
    print("   • Real-time search comparison")
    print("   • Performance metrics dashboard")
    print("   • System status monitoring")
    print("   • Mobile-responsive interface")

if __name__ == "__main__":
    test_web_ui()