#!/usr/bin/env python3
"""
Test simple tensor format for Vespa
"""

import json
import requests

def test_simple_tensor():
    """Test a very simple tensor format"""
    
    vespa_url = "http://localhost:8080"
    doc_api = f"{vespa_url}/document/v1"
    
    # Simple test with minimal data
    # Create a sparse tensor with just a few cells
    doc = {
        "fields": {
            "id": "simple_test",
            "title": "Simple Test",
            "content": "Simple test document",
            "url": "",
            "token_embeddings": {
                "cells": [
                    {"address": {"token": "0", "x": "0"}, "value": 0.1},
                    {"address": {"token": "0", "x": "1"}, "value": 0.2},
                    {"address": {"token": "1", "x": "0"}, "value": 0.3},
                    {"address": {"token": "1", "x": "1"}, "value": 0.4}
                ]
            },
            "compressed_embeddings": {
                "cells": [
                    {"address": {"token": "0", "x": "0"}, "value": 12},
                    {"address": {"token": "0", "x": "1"}, "value": 25},
                    {"address": {"token": "1", "x": "0"}, "value": 38},
                    {"address": {"token": "1", "x": "1"}, "value": 51}
                ]
            },
            "timestamp": 1234567890
        }
    }
    
    try:
        url = f"{doc_api}/asmarc/multi_vector_document/docid/simple_test"
        response = requests.post(url, json=doc, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            print("✅ Simple tensor format SUCCESS")
            return True
        else:
            print(f"❌ Simple tensor format FAILED: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Simple tensor format ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing simple tensor format...")
    success = test_simple_tensor()
    
    if success:
        print("🎉 Simple tensor format worked!")
    else:
        print("😞 Simple tensor format failed.")