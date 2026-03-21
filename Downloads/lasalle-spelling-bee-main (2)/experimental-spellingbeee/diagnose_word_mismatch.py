#!/usr/bin/env python3
"""
Diagnose word-audio mismatches in tournament group
Check if displayed words match audio files and verify ranked mode uses tournament list
"""

import os
import sys
import requests
import json

# Add the project directory to path
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words, GROUP_CONFIG

def check_word_audio_matching():
    print("=" * 80)
    print("TOURNAMENT WORD-AUDIO MATCHING DIAGNOSTIC")
    print("=" * 80)
    
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    # Get tournament words from configuration
    try:
        tournament_config = GROUP_CONFIG.get("tournament", {})
        tournament_words = tournament_config.get("words", {})
        
        easy_words = tournament_words.get("easy", [])
        medium_words = tournament_words.get("medium", [])
        hard_words = tournament_words.get("hard", [])
        
        all_tournament_words = easy_words + medium_words + hard_words
        
        print(f"Tournament words from config:")
        print(f"  Easy: {len(easy_words)} words")
        print(f"  Medium: {len(medium_words)} words") 
        print(f"  Hard: {len(hard_words)} words")
        print(f"  Total: {len(all_tournament_words)} words")
        
    except Exception as e:
        print(f"Error reading tournament config: {e}")
        return
    
    # Test a sample of words for audio matching
    print(f"\nTesting word-audio matching (sample):")
    
    test_words = all_tournament_words[:10]  # Test first 10 words
    
    mismatch_count = 0
    for word in test_words:
        print(f"\nTesting word: '{word}'")
        
        # Test the speak endpoint
        url = f"{base_url}/speak/{word}"
        print(f"  Audio URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                if 'audio' in response.headers.get('content-type', ''):
                    print(f"  OK Audio file returned")
                    
                    # Check if the audio file exists locally
                    safe_name = word.replace(" ", "_").lower()
                    audio_path = os.path.join(os.path.dirname(__file__), "audio", f"{safe_name}.mp3")
                    
                    if os.path.exists(audio_path):
                        print(f"  OK Local audio file exists")
                    else:
                        print(f"  X Local audio file missing")
                        mismatch_count += 1
                else:
                    print(f"  X Not audio content")
                    mismatch_count += 1
            else:
                print(f"  X HTTP {response.status_code}")
                mismatch_count += 1
                
        except Exception as e:
            print(f"  X Request failed: {e}")
            mismatch_count += 1
    
    print(f"\nWord-audio matching summary:")
    print(f"  Tested: {len(test_words)} words")
    print(f"  Mismatches: {mismatch_count}")
    
    # Check ranked mode configuration
    print(f"\nChecking ranked mode configuration:")
    
    try:
        ranked_week = tournament_config.get("ranked_week", 1)
        print(f"  Tournament ranked_week: {ranked_week}")
        
        # Get ranked words for tournament group
        ranked_words = get_group_words("tournament", "easy", week=ranked_week)
        print(f"  Ranked easy words count: {len(ranked_words)}")
        
        # Check if ranked words are from tournament list
        ranked_from_tournament = [w for w in ranked_words if w in easy_words]
        print(f"  Ranked words from tournament list: {len(ranked_from_tournament)}/{len(ranked_words)}")
        
        if len(ranked_from_tournament) == len(ranked_words):
            print(f"  OK Ranked mode uses tournament words correctly")
        else:
            print(f"  X Ranked mode may be using non-tournament words")
            
            # Show which ranked words are not in tournament list
            non_tournament = [w for w in ranked_words if w not in easy_words]
            if non_tournament:
                print(f"  Non-tournament ranked words: {non_tournament[:5]}")
        
    except Exception as e:
        print(f"  Error checking ranked mode: {e}")
    
    # Check grouptournament configuration
    print(f"\nChecking grouptournament configuration:")
    
    try:
        gt_config = GROUP_CONFIG.get("grouptournament", {})
        gt_words = gt_config.get("words", {})
        
        gt_easy = gt_words.get("easy", [])
        gt_medium = gt_words.get("medium", [])
        gt_hard = gt_words.get("hard", [])
        
        print(f"  Grouptournament easy: {len(gt_easy)} words")
        print(f"  Grouptournament medium: {len(gt_medium)} words")
        print(f"  Grouptournament hard: {len(gt_hard)} words")
        
        # Check if grouptournament matches tournament
        if gt_easy == easy_words and gt_medium == medium_words and gt_hard == hard_words:
            print(f"  OK Grouptournament matches tournament configuration")
        else:
            print(f"  X Grouptournament differs from tournament")
            
    except Exception as e:
        print(f"  Error checking grouptournament: {e}")
    
    print(f"\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    check_word_audio_matching()
