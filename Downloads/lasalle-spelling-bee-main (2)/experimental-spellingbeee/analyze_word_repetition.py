#!/usr/bin/env python3
"""
Analyze word repetition across difficulties in tournament/grouptournament groups.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words, GROUP_CONFIG

print("=" * 80)
print("WORD REPETITION ANALYSIS")
print("=" * 80)

for group in ["tournament", "grouptournament"]:
    print(f"\n[{group.upper()}]")
    
    easy_words = set(w.lower() for w in get_group_words(group, "easy"))
    medium_words = set(w.lower() for w in get_group_words(group, "medium"))
    hard_words = set(w.lower() for w in get_group_words(group, "hard"))
    
    print(f"\nWord counts:")
    print(f"  Easy: {len(easy_words)}")
    print(f"  Medium: {len(medium_words)}")
    print(f"  Hard: {len(hard_words)}")
    
    # Check for overlaps
    easy_medium_overlap = easy_words & medium_words
    easy_hard_overlap = easy_words & hard_words
    medium_hard_overlap = medium_words & hard_words
    all_three_overlap = easy_words & medium_words & hard_words
    
    print(f"\nOverlaps:")
    print(f"  Easy & Medium: {len(easy_medium_overlap)}")
    if easy_medium_overlap:
        print(f"    Words: {sorted(easy_medium_overlap)}")
    
    print(f"  Easy & Hard: {len(easy_hard_overlap)}")
    if easy_hard_overlap:
        print(f"    Words: {sorted(easy_hard_overlap)}")
    
    print(f"  Medium & Hard: {len(medium_hard_overlap)}")
    if medium_hard_overlap:
        print(f"    Words: {sorted(medium_hard_overlap)}")
    
    print(f"  All three: {len(all_three_overlap)}")
    if all_three_overlap:
        print(f"    Words: {sorted(all_three_overlap)}")
    
    # Total unique words
    all_words = easy_words | medium_words | hard_words
    print(f"\nTotal unique words: {len(all_words)}")
    print(f"Expected: 194")
    
    # Check for duplicates within each difficulty
    easy_list = get_group_words(group, "easy")
    medium_list = get_group_words(group, "medium")
    hard_list = get_group_words(group, "hard")
    
    print(f"\nDuplicates within difficulties:")
    easy_dups = [w for w in easy_list if easy_list.count(w) > 1]
    medium_dups = [w for w in medium_list if medium_list.count(w) > 1]
    hard_dups = [w for w in hard_list if hard_list.count(w) > 1]
    
    print(f"  Easy duplicates: {len(set(easy_dups))}")
    if easy_dups:
        print(f"    {set(easy_dups)}")
    
    print(f"  Medium duplicates: {len(set(medium_dups))}")
    if medium_dups:
        print(f"    {set(medium_dups)}")
    
    print(f"  Hard duplicates: {len(set(hard_dups))}")
    if hard_dups:
        print(f"    {set(hard_dups)}")

print("\n" + "=" * 80)
print("CHECKING GROUP CONFIG")
print("=" * 80)

for group in ["tournament", "grouptournament"]:
    cfg = GROUP_CONFIG.get(group, {})
    words_cfg = cfg.get("words", {})
    
    print(f"\n[{group.upper()}] Config:")
    for difficulty in ["easy", "medium", "hard"]:
        word_list = words_cfg.get(difficulty, [])
        print(f"  {difficulty}: {len(word_list)} words")
        if word_list:
            print(f"    First 5: {word_list[:5]}")
            print(f"    Last 5: {word_list[-5:]}")
