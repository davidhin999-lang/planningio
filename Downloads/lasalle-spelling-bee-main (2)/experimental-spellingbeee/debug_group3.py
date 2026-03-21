#!/usr/bin/env python3

"""Check what words Group 3 is actually serving"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from words import get_words_for_week, get_group_words

def check_group3_words():
    print("=== GROUP 3 WORD ANALYSIS ===")
    print()
    
    # Check all Group 3 words
    easy_words = get_group_words("group3", "easy")
    medium_words = get_group_words("group3", "medium") 
    hard_words = get_group_words("group3", "hard")
    
    print(f"Total Group 3 words:")
    print(f"  Easy: {len(easy_words)} words")
    print(f"  Medium: {len(medium_words)} words")
    print(f"  Hard: {len(hard_words)} words")
    print()
    
    # Check Week 1 words
    easy_week1 = get_words_for_week("easy", 1, "group3")
    medium_week1 = get_words_for_week("medium", 1, "group3")
    hard_week1 = get_words_for_week("hard", 1, "group3")
    
    print(f"Week 1 words (currently being served):")
    print(f"  Easy: {easy_week1}")
    print(f"  Medium: {medium_week1}")
    print(f"  Hard: {hard_week1}")
    print()
    
    # Check if workaholic is in Week 1
    if "workaholic" in hard_week1:
        print("❌ ISSUE: 'workaholic' is in Week 1 hard words!")
        print("   This explains why you're seeing it repeatedly.")
        print("   'workaholic' should be in a later week.")
    else:
        print("✅ 'workaholic' is NOT in Week 1 hard words")
    
    # Find which week workaholic is actually in
    for week in range(1, 32):  # Check up to 31 weeks
        week_words = get_words_for_week("hard", week, "group3")
        if "workaholic" in week_words:
            print(f"📍 'workaholic' is actually in Week {week}")
            break
    
    print()
    print("=== AUDIO FILES CHECK ===")
    
    # Check if workaholic audio exists
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    workaholic_files = [
        "workaholic.mp3",
        "workaholic_slow.mp3", 
        "workaholic_spell.mp3",
        "workaholic_sentence.mp3"
    ]
    
    for filename in workaholic_files:
        filepath = os.path.join(audio_dir, filename)
        if os.path.exists(filepath):
            size_kb = os.path.getsize(filepath) / 1024
            mtime = os.path.getmtime(filepath)
            import datetime
            dt = datetime.datetime.fromtimestamp(mtime)
            print(f"  {filename}: {size_kb:.1f} KB, updated {dt.strftime('%Y-%m-%d %H:%M')}")
        else:
            print(f"  {filename}: MISSING")

if __name__ == "__main__":
    check_group3_words()
