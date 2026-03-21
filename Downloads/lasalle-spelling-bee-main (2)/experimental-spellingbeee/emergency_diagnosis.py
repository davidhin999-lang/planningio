#!/usr/bin/env python3
"""
Emergency fix for mixed up tournament words/images/audio
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words, GROUP_CONFIG

def emergency_tournament_check():
    print("=" * 80)
    print("EMERGENCY TOURNAMENT DIAGNOSIS")
    print("=" * 80)
    
    # Check tournament group configuration
    print("TOURNAMENT GROUP CONFIG:")
    tournament_config = GROUP_CONFIG.get("tournament", {})
    print(f"  Label: {tournament_config.get('label', 'NOT FOUND')}")
    print(f"  Ranked Week: {tournament_config.get('ranked_week', 'NOT FOUND')}")
    
    tournament_words = tournament_config.get("words", {})
    total_words = 0
    for difficulty, words in tournament_words.items():
        print(f"  {difficulty.capitalize()}: {len(words)} words")
        total_words += len(words)
        if words:
            print(f"    Sample: {words[0]}, {words[1] if len(words) > 1 else 'N/A'}")
    
    print(f"  Total: {total_words} words")
    
    # Check grouptournament group
    print(f"\nGROUPTOURNAMENT GROUP CONFIG:")
    grouptournament_config = GROUP_CONFIG.get("grouptournament", {})
    print(f"  Label: {grouptournament_config.get('label', 'NOT FOUND')}")
    print(f"  Ranked Week: {grouptournament_config.get('ranked_week', 'NOT FOUND')}")
    
    grouptournament_words = grouptournament_config.get("words", {})
    total_gt_words = 0
    for difficulty, words in grouptournament_words.items():
        print(f"  {difficulty.capitalize()}: {len(words)} words")
        total_gt_words += len(words)
        if words:
            print(f"    Sample: {words[0]}, {words[1] if len(words) > 1 else 'N/A'}")
    
    print(f"  Total: {total_gt_words} words")
    
    # Check if they match
    print(f"\nCONSISTENCY CHECK:")
    if total_words == total_gt_words:
        print(f"  Word counts match: {total_words} each")
    else:
        print(f"  WORD COUNT MISMATCH: tournament={total_words}, grouptournament={total_gt_words}")
    
    # Check specific words from your list
    expected_words = ["balloon", "airplane", "amazing", "american", "badminton"]
    print(f"\nEXPECTED WORDS CHECK:")
    
    for group_name in ["tournament", "grouptournament"]:
        print(f"  {group_name.upper()}:")
        config = GROUP_CONFIG.get(group_name, {}).get("words", {})
        all_words = set()
        for difficulty_words in config.values():
            all_words.update(difficulty_words)
        
        for word in expected_words:
            status = "FOUND" if word in all_words else "MISSING"
            print(f"    {word}: {status}")
    
    # Check for any obvious issues
    print(f"\nISSUE DETECTION:")
    issues = []
    
    if total_words != 194:
        issues.append(f"Tournament has {total_words} words, expected 194")
    
    if total_gt_words != 194:
        issues.append(f"Grouptournament has {total_gt_words} words, expected 194")
    
    if not issues:
        print("  No obvious configuration issues detected")
        print("  Problem might be in app.py caching or API responses")
    else:
        for issue in issues:
            print(f"  ERROR: {issue}")
    
    return issues

if __name__ == "__main__":
    issues = emergency_tournament_check()
    
    if issues:
        print(f"\n{'='*80}")
        print("CRITICAL ISSUES FOUND - NEED IMMEDIATE FIX")
        print("="*80)
    else:
        print(f"\n{'='*80}")
        print("CONFIGURATION OK - ISSUE ELSEWHERE")
        print("="*80)
