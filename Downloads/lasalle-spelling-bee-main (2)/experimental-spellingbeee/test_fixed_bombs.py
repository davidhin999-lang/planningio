#!/usr/bin/env python3
"""
Test the fixed bomb words endpoint
"""

import requests
import json

def test_fixed_bombs():
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    print("Testing FIXED bomb words endpoint...")
    
    # Test different difficulties
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\nTesting {difficulty} bomb words:")
        
        try:
            response = requests.get(f"{base_url}/words_bombs?group=tournament&difficulty={difficulty}", timeout=10)
            
            if response.status_code == 200:
                bomb_words = response.json()
                print(f"  Status: {response.status_code}")
                print(f"  Bomb words count: {len(bomb_words)}")
                
                if bomb_words:
                    print(f"  Sample: {bomb_words[:3]}")
                    
                    # Check if bomb words are from correct difficulty
                    import sys
                    import os
                    sys.path.insert(0, os.path.dirname(__file__))
                    
                    from words import get_group_words
                    
                    expected_words = get_group_words("tournament", difficulty)
                    from_correct_difficulty = [w for w in bomb_words if w in expected_words]
                    
                    print(f"  From correct difficulty: {len(from_correct_difficulty)}/{len(bomb_words)}")
                    
                    if len(from_correct_difficulty) == len(bomb_words):
                        print(f"  ✓ FIXED: All bomb words are from {difficulty} difficulty!")
                    else:
                        print(f"  ✗ Still has words from wrong difficulty")
                else:
                    print(f"  No bomb words returned")
            else:
                print(f"  Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  Request failed: {e}")

if __name__ == "__main__":
    test_fixed_bombs()
