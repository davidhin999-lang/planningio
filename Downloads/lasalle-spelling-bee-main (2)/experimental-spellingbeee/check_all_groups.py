#!/usr/bin/env python3

"""Check status of all 4 groups"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from words import GROUP_CONFIG, get_group_words, get_words_for_week

def check_all_groups():
    print("=== STATUS OF ALL 4 GROUPS ===")
    print()
    
    for group_name, config in GROUP_CONFIG.items():
        print(f"=== {group_name.upper()} GROUP ===")
        print(f"Label: {config['label']}")
        print(f"Ranked Week: {config['ranked_week']}")
        
        # Check if group has custom words
        has_custom_words = "words" in config
        print(f"Custom Word Lists: {'Yes' if has_custom_words else 'No (uses global)'}")
        
        if has_custom_words:
            for difficulty in ["easy", "medium", "hard"]:
                words = get_group_words(group_name, difficulty)
                print(f"  {difficulty}: {len(words)} words")
                
                # Show week 1 words
                week1_words = get_words_for_week(difficulty, 1, group_name)
                print(f"    Week 1: {', '.join(week1_words[:6])}{'...' if len(week1_words) > 6 else ''}")
        else:
            print("  Uses global word lists")
            for difficulty in ["easy", "medium", "hard"]:
                words = get_group_words(group_name, difficulty)
                print(f"  {difficulty}: {len(words)} words")
        
        print()
    
    print("=== GROUP URLS ===")
    print("Default: https://lasalle-spelling-bee.vercel.app/")
    print("English6: https://lasalle-spelling-bee.vercel.app/?group=english6")
    print("Group3: https://lasalle-spelling-bee.vercel.app/?group=group3")
    print("Group4: https://lasalle-spelling-bee.vercel.app/?group=group4")

if __name__ == "__main__":
    check_all_groups()
