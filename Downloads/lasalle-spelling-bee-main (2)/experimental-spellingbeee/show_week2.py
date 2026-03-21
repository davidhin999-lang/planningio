#!/usr/bin/env python3

"""Show words for week 2 in Group 3"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from words import get_words_for_week

def show_week2_words():
    print("=== GROUP 3 - WEEK 2 WORDS ===")
    print()
    
    difficulties = ["easy", "medium", "hard"]
    
    for difficulty in difficulties:
        words = get_words_for_week(difficulty, 2, "group3")
        print(f"{difficulty.upper()} - Week 2:")
        print(f"  Total words: {len(words)}")
        print(f"  Words: {', '.join(words)}")
        print()
    
    print("=== SUMMARY ===")
    print("Week 2 contains the next 18 words for each difficulty level")
    print("Each game uses 6 words per round × 3 rounds = 18 words total")

if __name__ == "__main__":
    import os
    show_week2_words()
