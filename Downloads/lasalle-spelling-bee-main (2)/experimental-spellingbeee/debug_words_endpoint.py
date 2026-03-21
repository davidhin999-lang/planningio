#!/usr/bin/env python3
"""
Debug the tournament words endpoint issue
"""

import os
import sys
import requests
import json

def debug_tournament_words_endpoint():
    print("=" * 80)
    print("DEBUG TOURNAMENT WORDS ENDPOINT")
    print("=" * 80)
    
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    # Test different ways to call the words endpoint
    test_cases = [
        # Method 1: URL parameter
        f"{base_url}/words?group=tournament&difficulty=easy&week=0",
        # Method 2: URL parameter with encoded group
        f"{base_url}/words?group=tournament&difficulty=easy&week=1",
        # Method 3: Test without week parameter
        f"{base_url}/words?group=tournament&difficulty=easy",
        # Method 4: Test with different difficulty
        f"{base_url}/words?group=tournament&difficulty=medium&week=0",
    ]
    
    for i, url in enumerate(test_cases, 1):
        print(f"\nTest {i}: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"  Words returned: {len(data)}")
                        if data:
                            print(f"  First words: {', '.join(data[:3])}")
                        else:
                            print(f"  WARNING: Empty word list returned")
                    else:
                        print(f"  Response data: {data}")
                except json.JSONDecodeError:
                    print(f"  Response (not JSON): {response.text[:200]}")
            else:
                print(f"  Error response: {response.text[:200]}")
                
        except Exception as e:
            print(f"  Request failed: {e}")
    
    # Test the session/info endpoint to see what group is detected
    print(f"\nTesting session info...")
    
    try:
        info_url = f"{base_url}/session_info"
        response = requests.get(info_url, timeout=10)
        
        if response.status_code == 200:
            info_data = response.json()
            print(f"  Current group: {info_data.get('group', 'N/A')}")
            print(f"  Available groups: {list(info_data.get('groups', {}).keys())}")
        else:
            print(f"  Session info failed: {response.status_code}")
            
    except Exception as e:
        print(f"  Session info request failed: {e}")
    
    # Test with POST method to see if JSON body works
    print(f"\nTesting POST method with JSON body...")
    
    try:
        post_url = f"{base_url}/words"
        json_data = {
            "group": "tournament",
            "difficulty": "easy",
            "week": 0
        }
        
        response = requests.post(post_url, json=json_data, timeout=10)
        print(f"  POST Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"  POST Words returned: {len(data)}")
                if data:
                    print(f"  First words: {', '.join(data[:3])}")
            else:
                print(f"  POST Response: {data}")
        else:
            print(f"  POST Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"  POST request failed: {e}")
    
    print(f"\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    debug_tournament_words_endpoint()
