#!/usr/bin/env python3
"""
Verify tournament words are properly categorized and can be selected by week.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words, get_group_weeks, GROUP_CONFIG

print("=" * 80)
print("TOURNAMENT CATEGORIZATION VERIFICATION")
print("=" * 80)

for group in ["tournament", "grouptournament"]:
    print(f"\n[{group.upper()}]")
    
    total_words = 0
    for difficulty in ["easy", "medium", "hard"]:
        words = get_group_words(group, difficulty)
        weeks = get_group_weeks(group, difficulty)
        
        total_words += len(words)
        
        print(f"\n  {difficulty.upper()}:")
        print(f"    Total words: {len(words)}")
        print(f"    Weeks available: {len(weeks)}")
        
        for week_num, week_words in enumerate(weeks, 1):
            print(f"      Week {week_num}: {len(week_words)} words")
            if week_num == 1:
                print(f"        Sample: {', '.join(week_words[:5])}")

    print(f"\n  TOTAL: {total_words} words")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

# Verify all 194 words are present
all_words = set()
for group in ["tournament", "grouptournament"]:
    for difficulty in ["easy", "medium", "hard"]:
        words = get_group_words(group, difficulty)
        all_words.update(w.lower() for w in words)

print(f"Total unique words: {len(all_words)}")
print(f"Expected: 194")
print(f"Status: {'PASS' if len(all_words) == 194 else 'FAIL'}")

# Check for duplicates within categories
print("\nChecking for duplicates within each group...")
for group in ["tournament", "grouptournament"]:
    for difficulty in ["easy", "medium", "hard"]:
        words = get_group_words(group, difficulty)
        if len(words) != len(set(w.lower() for w in words)):
            print(f"  ERROR: {group} {difficulty} has duplicates!")
        else:
            print(f"  OK: {group} {difficulty} has no duplicates")

print("\nVerification complete!")
