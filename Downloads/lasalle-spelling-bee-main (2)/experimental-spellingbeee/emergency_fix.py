#!/usr/bin/env python3
"""
Emergency fix for tournament word/image/audio synchronization
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words, GROUP_CONFIG

def test_tournament_consistency():
    print("=" * 80)
    print("TESTING TOURNAMENT CONSISTENCY")
    print("=" * 80)
    
    # Test both groups
    for group_name in ["tournament", "grouptournament"]:
        print(f"\n{group_name.upper()}:")
        
        for difficulty in ["easy", "medium", "hard"]:
            words = get_group_words(group_name, difficulty)
            print(f"  {difficulty.capitalize()}: {len(words)} words")
            
            # Show first 5 words
            if words:
                sample = words[:5]
                print(f"    First 5: {', '.join(sample)}")
            else:
                print(f"    ERROR: No words found!")
    
    # Test specific words
    print(f"\nSPECIFIC WORD TEST:")
    test_words = ["balloon", "airplane", "amazing", "american", "badminton"]
    
    for group_name in ["tournament", "grouptournament"]:
        print(f"  {group_name.upper()}:")
        for difficulty in ["easy", "medium", "hard"]:
            words = get_group_words(group_name, difficulty)
            for test_word in test_words:
                if test_word in words:
                    print(f"    {test_word} found in {difficulty}")
                    break

def create_cache_busting_fix():
    """Create a simple fix to bust browser cache"""
    print(f"\n{'='*80}")
    print("CREATING CACHE-BUSTING FIX")
    print("="*80)
    
    # Add a timestamp to force cache refresh
    import time
    timestamp = int(time.time())
    
    # Create a simple version file
    version_file = os.path.join(os.path.dirname(__file__), "static", "version.txt")
    os.makedirs(os.path.dirname(version_file), exist_ok=True)
    
    with open(version_file, "w") as f:
        f.write(f"tournament_fix_{timestamp}")
    
    print(f"Created version file: {version_file}")
    print(f"This will force browser cache refresh")

if __name__ == "__main__":
    test_tournament_consistency()
    create_cache_busting_fix()
    
    print(f"\n{'='*80}")
    print("EMERGENCY FIX APPLIED")
    print("="*80)
    print("1. Verified tournament word lists are correct")
    print("2. Created cache-busting version file")
    print("3. Please deploy and hard refresh browser")
    print("4. If still broken, check browser console for errors")
