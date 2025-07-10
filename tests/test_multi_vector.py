#!/usr/bin/env python3
"""
Test script to understand the correct tensor format for multi-vector documents
"""

import json
import numpy as np
import requests

def test_tensor_formats():
    """Test different tensor formats to find what works"""
    
    vespa_url = "http://localhost:8080"
    doc_api = f"{vespa_url}/document/v1"
    
    # Simple test with 2 tokens, 4 dimensions each
    token_embeddings = np.array([
        [0.1, 0.2, 0.3, 0.4],  # token 0
        [0.5, 0.6, 0.7, 0.8]   # token 1
    ])
    
    # Format 1: String keys
    format1 = {
        "fields": {
            "id": "test1",
            "title": "Test Document",
            "content": "This is a test document",
            "url": "",
            "token_embeddings": {
                "cells": {
                    "token:0,x:0": 0.1, "token:0,x:1": 0.2, "token:0,x:2": 0.3, "token:0,x:3": 0.4,
                    "token:1,x:0": 0.5, "token:1,x:1": 0.6, "token:1,x:2": 0.7, "token:1,x:3": 0.8
                }
            },
            "compressed_embeddings": {
                "cells": {
                    "token:0,x:0": 12, "token:0,x:1": 25, "token:0,x:2": 38, "token:0,x:3": 51,
                    "token:1,x:0": 64, "token:1,x:1": 76, "token:1,x:2": 89, "token:1,x:3": 102
                }
            },
            "timestamp": 1234567890
        }
    }
    
    # Format 2: Object keys
    format2 = {
        "fields": {
            "id": "test2",
            "title": "Test Document 2",
            "content": "This is another test document",
            "url": "",
            "token_embeddings": {
                "cells": {
                    ("token", "0", "x", "0"): 0.1, ("token", "0", "x", "1"): 0.2,
                    ("token", "0", "x", "2"): 0.3, ("token", "0", "x", "3"): 0.4,
                    ("token", "1", "x", "0"): 0.5, ("token", "1", "x", "1"): 0.6,
                    ("token", "1", "x", "2"): 0.7, ("token", "1", "x", "3"): 0.8
                }
            },
            "compressed_embeddings": {
                "cells": {
                    ("token", "0", "x", "0"): 12, ("token", "0", "x", "1"): 25,
                    ("token", "0", "x", "2"): 38, ("token", "0", "x", "3"): 51,
                    ("token", "1", "x", "0"): 64, ("token", "1", "x", "1"): 76,
                    ("token", "1", "x", "2"): 89, ("token", "1", "x", "3"): 102
                }
            },
            "timestamp": 1234567890
        }
    }
    
    # Format 3: List format
    format3 = {
        "fields": {
            "id": "test3",
            "title": "Test Document 3",
            "content": "This is yet another test document",
            "url": "",
            "token_embeddings": {
                "values": token_embeddings.flatten().tolist()
            },
            "compressed_embeddings": {
                "values": np.clip(token_embeddings * 127, -127, 127).astype(np.int8).flatten().tolist()
            },
            "timestamp": 1234567890
        }
    }
    
    # Try each format
    formats = [("Format 1 (string keys)", format1), ("Format 2 (object keys)", format2), ("Format 3 (values)", format3)]
    
    for name, doc in formats:
        try:
            url = f"{doc_api}/asmarc/multi_vector_document/docid/{doc['fields']['id']}"
            response = requests.post(url, json=doc, headers={'Content-Type': 'application/json'})
            
            if response.status_code == 200:
                print(f"✅ {name} - SUCCESS")
                return name, doc
            else:
                print(f"❌ {name} - FAILED: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ {name} - ERROR: {e}")
    
    return None, None

if __name__ == "__main__":
    print("🧪 Testing multi-vector tensor formats...")
    success_format, success_doc = test_tensor_formats()
    
    if success_format:
        print(f"\n🎉 {success_format} worked!")
        print("Successful document format:")
        print(json.dumps(success_doc, indent=2))
    else:
        print("\n😞 No format worked. Need to check schema definition.")