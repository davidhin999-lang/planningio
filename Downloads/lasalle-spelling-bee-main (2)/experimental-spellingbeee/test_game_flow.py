#!/usr/bin/env python3
"""
Test the actual tournament game flow to detect word-audio mismatches
"""

import os
import sys
import requests
import json

# Add the project directory to path
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words, get_ranked_words, GROUP_CONFIG

def test_tournament_game_flow():
    print("=" * 80)
    print("TOURNAMENT GAME FLOW TEST")
    print("=" * 80)
    
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    # Test getting a tournament word
    print(f"\nTesting tournament word selection...")
    
    try:
        # Test the word endpoint
        word_url = f"{base_url}/word?group=tournament&difficulty=easy"
        response = requests.get(word_url, timeout=10)
        
        if response.status_code == 200:
            word_data = response.json()
            selected_word = word_data.get("word", "")
            print(f"  Selected word: '{selected_word}'")
            
            # Test audio for this word
            audio_url = f"{base_url}/speak/{selected_word}"
            audio_response = requests.get(audio_url, timeout=10)
            
            if audio_response.status_code == 200:
                if 'audio' in audio_response.headers.get('content-type', ''):
                    print(f"  Audio URL works: {audio_url}")
                    
                    # Check if audio file exists locally
                    safe_name = selected_word.replace(" ", "_").lower()
                    audio_path = os.path.join(os.path.dirname(__file__), "audio", f"{safe_name}.mp3")
                    
                    if os.path.exists(audio_path):
                        print(f"  Local audio file exists: {safe_name}.mp3")
                        file_size = os.path.getsize(audio_path)
                        print(f"  File size: {file_size} bytes")
                        
                        if file_size > 500:
                            print(f"  OK: Audio file seems valid")
                        else:
                            print(f"  WARNING: Audio file might be too small")
                    else:
                        print(f"  ERROR: Local audio file missing!")
                else:
                    print(f"  ERROR: Audio URL returned non-audio content")
                    print(f"  Content-Type: {audio_response.headers.get('content-type')}")
            else:
                print(f"  ERROR: Audio URL failed with HTTP {audio_response.status_code}")
        else:
            print(f"  ERROR: Word selection failed with HTTP {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"  ERROR: Request failed: {e}")
    
    # Test multiple words to check for patterns
    print(f"\nTesting multiple tournament words...")
    
    test_count = 0
    success_count = 0
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\n  Testing {difficulty} words:")
        
        for i in range(3):  # Test 3 words per difficulty
            try:
                word_url = f"{base_url}/word?group=tournament&difficulty={difficulty}"
                response = requests.get(word_url, timeout=5)
                
                if response.status_code == 200:
                    word_data = response.json()
                    selected_word = word_data.get("word", "")
                    
                    # Check if word is in tournament list
                    tournament_words = get_group_words("tournament", difficulty)
                    if selected_word in tournament_words:
                        print(f"    Word {i+1}: '{selected_word}' - OK (in tournament list)")
                        success_count += 1
                    else:
                        print(f"    Word {i+1}: '{selected_word}' - ERROR (not in tournament list)")
                        print(f"      Expected from: {tournament_words[:5]}...")
                    
                    test_count += 1
                else:
                    print(f"    Word {i+1}: ERROR - HTTP {response.status_code}")
                    test_count += 1
                    
            except Exception as e:
                print(f"    Word {i+1}: ERROR - {e}")
                test_count += 1
    
    print(f"\nGame flow test summary:")
    print(f"  Words tested: {test_count}")
    print(f"  Success: {success_count}")
    print(f"  Success rate: {success_count/test_count*100:.1f}%" if test_count > 0 else "N/A")
    
    # Check for any potential caching issues
    print(f"\nChecking for potential issues:")
    
    # 1. Check if there are duplicate audio files
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    audio_files = [f for f in os.listdir(audio_dir) if f.endswith(".mp3")]
    
    if len(audio_files) != len(set(audio_files)):
        print(f"  WARNING: Duplicate audio files detected")
    else:
        print(f"  OK: No duplicate audio files")
    
    # 2. Check if all tournament words have audio
    missing_audio = []
    for difficulty in ["easy", "medium", "hard"]:
        tournament_words = get_group_words("tournament", difficulty)
        for word in tournament_words:
            safe_name = word.replace(" ", "_").lower()
            audio_path = os.path.join(audio_dir, f"{safe_name}.mp3")
            if not os.path.exists(audio_path):
                missing_audio.append(word)
    
    if missing_audio:
        print(f"  WARNING: {len(missing_audio)} tournament words missing audio")
        print(f"    Missing: {missing_audio[:5]}{'...' if len(missing_audio) > 5 else ''}")
    else:
        print(f"  OK: All tournament words have audio")
    
    print(f"\n" + "=" * 80)
    print("GAME FLOW TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_tournament_game_flow()
