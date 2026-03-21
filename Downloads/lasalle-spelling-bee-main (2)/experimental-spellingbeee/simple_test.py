#!/usr/bin/env python3
"""
Simple test of deployed endpoint
"""

import requests
import json

def simple_test():
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    print("Testing basic words_bombs endpoint...")
    
    try:
        # Test without difficulty first
        response = requests.get(f"{base_url}/words_bombs?group=tournament", timeout=10)
        print(f"Without difficulty - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Count: {len(data)}")
            print(f"Sample: {data[:3]}")
        else:
            print(f"Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simple_test()
