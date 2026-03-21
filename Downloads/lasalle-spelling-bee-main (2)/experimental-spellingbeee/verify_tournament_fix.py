#!/usr/bin/env python3
"""
Verify that tournament/grouptournament groups only return their official words
and do NOT fall back to global word lists containing unwanted words.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words, GROUP_CONFIG

# Words that should NOT appear in tournament
FORBIDDEN_WORDS = {"alcoholism", "appreciate", "harmonious", "monitoring", "housewares", "mountainous"}

print("=" * 80)
print("TOURNAMENT GROUP WORD VERIFICATION")
print("=" * 80)

for group in ["tournament", "grouptournament"]:
    print(f"\n[{group.upper()}]")
    
    for difficulty in ["easy", "medium", "hard"]:
        words = get_group_words(group, difficulty)
        word_set = set(w.lower() for w in words)
        
        # Check for forbidden words
        forbidden_found = word_set & FORBIDDEN_WORDS
        
        print(f"\n  {difficulty.upper()}:")
        print(f"    Total words: {len(words)}")
        
        if forbidden_found:
            print(f"    ERROR: Found forbidden words: {sorted(forbidden_found)}")
        else:
            print(f"    OK: No forbidden words found")
        
        # Show first few words
        if words:
            print(f"    Sample: {', '.join(words[:5])}")
        else:
            print(f"    (empty list)")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

# Final verification
all_good = True
for group in ["tournament", "grouptournament"]:
    for difficulty in ["easy", "medium", "hard"]:
        words = get_group_words(group, difficulty)
        word_set = set(w.lower() for w in words)
        forbidden_found = word_set & FORBIDDEN_WORDS
        if forbidden_found:
            print(f"FAIL: {group} {difficulty} contains forbidden words: {forbidden_found}")
            all_good = False

if all_good:
    print("SUCCESS: Tournament groups are clean - no forbidden words found!")
else:
    print("FAILURE: Tournament groups still contain forbidden words")

sys.exit(0 if all_good else 1)
