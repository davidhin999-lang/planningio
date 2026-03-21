#!/usr/bin/env python3
"""
Test deployed fix after waiting
"""

import requests
import time
import sys
import os

def wait_and_test():
    print("Waiting 30 seconds for deployment...")
    time.sleep(30)
    
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    print("Testing deployed fix...")
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\nTesting {difficulty} bomb words:")
        
        try:
            response = requests.get(f"{base_url}/words_bombs?group=tournament&difficulty={difficulty}", timeout=10)
            
            if response.status_code == 200:
                bomb_words = response.json()
                print(f"  Status: {response.status_code}")
                print(f"  Count: {len(bomb_words)}")
                
                if bomb_words:
                    print(f"  Sample: {bomb_words[:3]}")
                    
                    # Check difficulty
                    sys.path.insert(0, os.path.dirname(__file__))
                    from words import get_group_words
                    
                    expected_words = get_group_words("tournament", difficulty)
                    from_correct_difficulty = [w for w in bomb_words if w in expected_words]
                    
                    if len(from_correct_difficulty) == len(bomb_words):
                        print(f"  SUCCESS: All bomb words from {difficulty}!")
                    else:
                        print(f"  ISSUE: {len(from_correct_difficulty)}/{len(bomb_words)} from {difficulty}")
                        
                        # Show what we got vs expected
                        if difficulty == "easy":
                            expected_sample = ["address", "balloon", "bathroom"]
                        elif difficulty == "medium":
                            expected_sample = ["afternoon", "airplane", "amazing"]
                        else:
                            expected_sample = ["american", "apostrophe", "businessman"]
                        
                        print(f"  Expected sample: {expected_sample}")
                        print(f"  Got sample: {bomb_words[:3]}")
                else:
                    print(f"  No bomb words")
            else:
                print(f"  HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    wait_and_test()
