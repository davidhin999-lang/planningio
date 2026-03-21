#!/usr/bin/env python3
"""
Test the words_bombs endpoint locally
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words, get_bomb_words, GROUP_CONFIG

def test_local():
    print("Testing words_bombs logic locally...")
    
    # Simulate tournament group
    group = "tournament"
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\nTesting {difficulty}:")
        
        # Test the logic I implemented
        if group in ["tournament", "grouptournament"]:
            words = get_group_words(group, difficulty)
            bombs = words
        else:
            bombs = get_bomb_words(group)
        
        print(f"  Bomb words count: {len(bombs)}")
        print(f"  Sample: {bombs[:3]}")
        
        # Verify they're from the right difficulty
        expected_words = get_group_words(group, difficulty)
        from_correct_difficulty = [w for w in bombs if w in expected_words]
        
        print(f"  From correct difficulty: {len(from_correct_difficulty)}/{len(bombs)}")

if __name__ == "__main__":
    test_local()
