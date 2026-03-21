#!/usr/bin/env python3
"""
Test tournament game flow using correct endpoints
"""

import os
import sys
import requests
import json
import random

# Add the project directory to path
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words, get_ranked_words, GROUP_CONFIG

def test_tournament_with_correct_endpoints():
    print("=" * 80)
    print("TOURNAMENT GAME FLOW TEST (CORRECT ENDPOINTS)")
    print("=" * 80)
    
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    # Test getting tournament words using /words endpoint
    print(f"\nTesting tournament word selection...")
    
    try:
        # Get words for tournament group
        words_url = f"{base_url}/words?group=tournament&difficulty=easy&week=0"
        response = requests.get(words_url, timeout=10)
        
        if response.status_code == 200:
            words_data = response.json()
            available_words = words_data if isinstance(words_data, list) else []
            print(f"  Available easy words: {len(available_words)}")
            
            if available_words:
                # Select a random word
                selected_word = random.choice(available_words)
                print(f"  Selected word: '{selected_word}'")
                
                # Check if it's in tournament list
                tournament_words = get_group_words("tournament", "easy")
                if selected_word in tournament_words:
                    print(f"  OK: Word is in tournament list")
                else:
                    print(f"  ERROR: Word not in tournament list!")
                
                # Test audio for this word
                audio_url = f"{base_url}/speak/{selected_word}"
                audio_response = requests.get(audio_url, timeout=10)
                
                if audio_response.status_code == 200:
                    if 'audio' in audio_response.headers.get('content-type', ''):
                        print(f"  OK: Audio works for '{selected_word}'")
                        
                        # Check local audio file
                        safe_name = selected_word.replace(" ", "_").lower()
                        audio_path = os.path.join(os.path.dirname(__file__), "audio", f"{safe_name}.mp3")
                        
                        if os.path.exists(audio_path):
                            file_size = os.path.getsize(audio_path)
                            print(f"  OK: Local audio exists ({file_size} bytes)")
                        else:
                            print(f"  WARNING: Local audio file missing")
                    else:
                        print(f"  ERROR: Audio URL returned non-audio content")
                else:
                    print(f"  ERROR: Audio failed with HTTP {audio_response.status_code}")
            else:
                print(f"  ERROR: No words returned")
        else:
            print(f"  ERROR: Words endpoint failed with HTTP {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ERROR: Request failed: {e}")
    
    # Test ranked mode words
    print(f"\nTesting ranked mode words...")
    
    try:
        ranked_url = f"{base_url}/words_ranked?group=tournament"
        response = requests.get(ranked_url, timeout=10)
        
        if response.status_code == 200:
            ranked_data = response.json()
            print(f"  Ranked words received:")
            print(f"    Easy: {len(ranked_data.get('easy', []))} words")
            print(f"    Medium: {len(ranked_data.get('medium', []))} words")
            print(f"    Hard: {len(ranked_data.get('hard', []))} words")
            
            # Test a few ranked words
            for difficulty in ['easy', 'medium', 'hard']:
                ranked_words = ranked_data.get(difficulty, [])
                if ranked_words:
                    test_word = ranked_words[0]
                    print(f"  Testing {difficulty} ranked word: '{test_word}'")
                    
                    # Check if it's in tournament list
                    tournament_words = get_group_words("tournament", difficulty)
                    if test_word in tournament_words:
                        print(f"    OK: Ranked word is in tournament list")
                    else:
                        print(f"    ERROR: Ranked word not in tournament list!")
                    
                    # Test audio
                    audio_url = f"{base_url}/speak/{test_word}"
                    audio_response = requests.get(audio_url, timeout=5)
                    
                    if audio_response.status_code == 200:
                        print(f"    OK: Audio works for ranked word")
                    else:
                        print(f"    ERROR: Audio failed for ranked word")
        else:
            print(f"  ERROR: Ranked endpoint failed with HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  ERROR: Ranked request failed: {e}")
    
    # Test weekly words (week 1)
    print(f"\nTesting weekly words (week 1)...")
    
    try:
        weekly_url = f"{base_url}/words?group=tournament&difficulty=easy&week=1"
        response = requests.get(weekly_url, timeout=10)
        
        if response.status_code == 200:
            weekly_words = response.json()
            weekly_words = weekly_words if isinstance(weekly_words, list) else []
            print(f"  Week 1 easy words: {len(weekly_words)}")
            
            if weekly_words:
                print(f"  First few words: {', '.join(weekly_words[:5])}")
                
                # Test first word
                test_word = weekly_words[0]
                audio_url = f"{base_url}/speak/{test_word}"
                audio_response = requests.get(audio_url, timeout=5)
                
                if audio_response.status_code == 200:
                    print(f"  OK: Audio works for weekly word")
                else:
                    print(f"  ERROR: Audio failed for weekly word")
        else:
            print(f"  ERROR: Weekly endpoint failed with HTTP {response.status_code}")
            
    except Exception as e:
        print(f"  ERROR: Weekly request failed: {e}")
    
    print(f"\n" + "=" * 80)
    print("GAME FLOW TEST COMPLETE")
    print("=" * 80)
    print(f"\nIf you're experiencing word-audio mismatches in the actual game,")
    print(f"the issue might be:")
    print(f"1. Browser caching - try hard refresh (Ctrl+F5)")
    print(f"2. Client-side JavaScript logic - the word display vs audio might be handled differently")
    print(f"3. Session state - the game might be selecting words from a different difficulty/group")

if __name__ == "__main__":
    test_tournament_with_correct_endpoints()
