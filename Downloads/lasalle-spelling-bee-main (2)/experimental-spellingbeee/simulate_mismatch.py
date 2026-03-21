#!/usr/bin/env python3
"""
Comprehensive test to reproduce the word-audio mismatch issue
"""

import os
import sys
import requests
import json

def test_game_flow_simulation():
    print("=" * 80)
    print("GAME FLOW SIMULATION - REPRODUCING MISMATCH")
    print("=" * 80)
    
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    # Simulate the exact flow that happens in the game
    print("\n1. Get tournament words (like JavaScript does)")
    
    try:
        # Get words for tournament group
        words_url = f"{base_url}/words?group=tournament&difficulty=easy&week=0"
        response = requests.get(words_url, timeout=10)
        
        if response.status_code == 200:
            words_data = response.json()
            available_words = words_data.get("words", [])
            print(f"   Available tournament words: {len(available_words)}")
            
            if available_words:
                # Simulate pickWord() - select first word
                selected_word = available_words[0]
                print(f"   Selected word (pickWord): '{selected_word}'")
                
                # Get bomb words (like JavaScript does)
                print(f"\n2. Get bomb words for tournament")
                bombs_url = f"{base_url}/words_bombs?group=tournament"
                bombs_response = requests.get(bombs_url, timeout=10)
                
                if bombs_response.status_code == 200:
                    bomb_words = bombs_response.json()
                    print(f"   Bomb words available: {len(bomb_words)}")
                    
                    if bomb_words:
                        # Simulate bomb word selection (first bomb word for testing)
                        bomb_word = bomb_words[0]
                        print(f"   Potential bomb word: '{bomb_word}'")
                        
                        # Check if bomb word is different from selected word
                        if bomb_word != selected_word:
                            print(f"   BOMB MISMATCH: Bomb word is different!")
                            print(f"   Display word: '{selected_word}'")
                            print(f"   Bomb word: '{bomb_word}'")
                            
                            # Test audio for both words
                            print(f"\n3. Test audio for both words")
                            
                            # Audio for selected word
                            audio1_url = f"{base_url}/speak/{selected_word}"
                            audio1_response = requests.get(audio1_url, timeout=5)
                            
                            # Audio for bomb word  
                            audio2_url = f"{base_url}/speak/{bomb_word}"
                            audio2_response = requests.get(audio2_url, timeout=5)
                            
                            print(f"   Audio for '{selected_word}': HTTP {audio1_response.status_code}")
                            print(f"   Audio for '{bomb_word}': HTTP {audio2_response.status_code}")
                            
                            if audio1_response.status_code == 200 and audio2_response.status_code == 200:
                                print(f"   Both audio files exist - this could cause mismatch!")
                                print(f"   If bomb word overrides display word, audio won't match!")
                            else:
                                print(f"   Audio status differs - check which one plays")
                        else:
                            print(f"   Words match - no bomb override in this case")
                    else:
                        print(f"   No bomb words available")
                else:
                    print(f"   Bomb words request failed: HTTP {bombs_response.status_code}")
            else:
                print(f"   No tournament words available")
        else:
            print(f"   Tournament words request failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   Request failed: {e}")
    
    # Test different difficulty levels
    print(f"\n4. Test different difficulty levels for bomb mismatches")
    
    for difficulty in ["easy", "medium", "hard"]:
        print(f"\n   Testing {difficulty}:")
        
        try:
            # Get tournament words
            words_url = f"{base_url}/words?group=tournament&difficulty={difficulty}&week=0"
            words_response = requests.get(words_url, timeout=5)
            
            # Get bomb words
            bombs_url = f"{base_url}/words_bombs?group=tournament"
            bombs_response = requests.get(bombs_url, timeout=5)
            
            if words_response.status_code == 200 and bombs_response.status_code == 200:
                words_data = words_response.json()
                bomb_words = bombs_response.json()
                
                available_words = words_data.get("words", [])
                
                if available_words and bomb_words:
                    # Check if any bomb word is different from available words
                    non_tournament_bombs = [w for w in bomb_words if w not in available_words]
                    
                    if non_tournament_bombs:
                        print(f"      Found {len(non_tournament_bombs)} bomb words not in {difficulty} list")
                        print(f"      Sample: {non_tournament_bombs[:3]}")
                        print(f"      THIS COULD CAUSE MISMATCH!")
                    else:
                        print(f"      All bomb words are in {difficulty} list")
                else:
                    print(f"      No words or bomb words available")
            else:
                print(f"      Request failed")
                
        except Exception as e:
            print(f"      Error: {e}")
    
    print(f"\n" + "=" * 80)
    print("SIMULATION COMPLETE")
    print("=" * 80)
    print(f"\nIf you're experiencing word-audio mismatches:")
    print(f"1. The issue is likely that bomb words come from HARD difficulty")
    print(f"2. But the game might be in EASY or MEDIUM mode")
    print(f"3. So a hard bomb word overrides an easy/medium word")
    print(f"4. The display shows the bomb word but the user expects easy/medium")
    print(f"5. This creates a perceived mismatch")

if __name__ == "__main__":
    test_game_flow_simulation()
