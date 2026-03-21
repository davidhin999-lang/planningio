#!/usr/bin/env python3
"""
Debug the get_group_words function for tournament
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words

def debug_get_group_words():
    print("Debugging get_group_words for tournament...")
    
    for difficulty in ["easy", "medium", "hard"]:
        words = get_group_words("tournament", difficulty)
        print(f"\n{difficulty}:")
        print(f"  Count: {len(words)}")
        print(f"  Sample: {words[:3]}")
        
        # Check if these are the right words
        if difficulty == "easy":
            expected_first = ["address", "balloon", "bathroom"]
        elif difficulty == "medium":
            expected_first = ["afternoon", "airplane", "amazing"]
        else:  # hard
            expected_first = ["american", "apostrophe", "businessman"]
        
        if words[:3] == expected_first:
            print(f"  OK: Correct words for {difficulty}")
        else:
            print(f"  ERROR: Wrong words for {difficulty}")
            print(f"  Expected: {expected_first}")
            print(f"  Got: {words[:3]}")

if __name__ == "__main__":
    debug_get_group_words()
