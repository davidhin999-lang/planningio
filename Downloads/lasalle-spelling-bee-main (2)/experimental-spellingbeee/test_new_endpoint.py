#!/usr/bin/env python3
"""
Test the new tournament-specific bomb words endpoint
"""

import requests
import json
import time
import sys
import os

def test_new_endpoint():
    print("Testing new tournament-specific bomb words endpoint...")
    print("Waiting 30 seconds for deployment...")
    time.sleep(30)
    
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\nTesting {difficulty} bomb words:")
        
        try:
            response = requests.get(f"{base_url}/words_bombs_tournament?group=tournament&difficulty={difficulty}", timeout=10)
            
            if response.status_code == 200:
                bomb_words = response.json()
                print(f"  Status: {response.status_code}")
                print(f"  Count: {len(bomb_words)}")
                print(f"  Sample: {bomb_words[:3]}")
                
                # Verify they're from the right difficulty
                sys.path.insert(0, os.path.dirname(__file__))
                from words import get_group_words
                
                expected_words = get_group_words("tournament", difficulty)
                from_correct_difficulty = [w for w in bomb_words if w in expected_words]
                
                if len(from_correct_difficulty) == len(bomb_words):
                    print(f"  SUCCESS: All bomb words from {difficulty}!")
                else:
                    print(f"  ISSUE: {len(from_correct_difficulty)}/{len(bomb_words)} from {difficulty}")
            else:
                print(f"  HTTP {response.status_code}")
                if response.status_code != 200:
                    print(f"  Error: {response.text[:200]}")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_new_endpoint()
