#!/usr/bin/env python3
"""
Test the words_bombs endpoint for tournament group
"""

import requests
import json

def test_bombs_endpoint():
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    print("Testing words_bombs endpoint for tournament group...")
    
    try:
        response = requests.get(f"{base_url}/words_bombs?group=tournament", timeout=10)
        
        if response.status_code == 200:
            bomb_words = response.json()
            print(f"Status: {response.status_code}")
            print(f"Bomb words count: {len(bomb_words)}")
            
            if bomb_words:
                print(f"First 5 bomb words: {bomb_words[:5]}")
                
                # Check if bomb words are from tournament list
                # Add words.py to path to check
                import sys
                import os
                sys.path.insert(0, os.path.dirname(__file__))
                
                from words import get_group_words
                
                tournament_hard_words = get_group_words("tournament", "hard")
                print(f"Tournament hard words count: {len(tournament_hard_words)}")
                
                # Check if bomb words are from tournament
                from_tournament = [w for w in bomb_words if w in tournament_hard_words]
                print(f"Bomb words from tournament: {len(from_tournament)}/{len(bomb_words)}")
                
                if len(from_tournament) != len(bomb_words):
                    non_tournament = [w for w in bomb_words if w not in tournament_hard_words]
                    print(f"Non-tournament bomb words: {non_tournament[:5]}")
                    print(f"THIS IS THE BUG! Bomb words are not from tournament list!")
                else:
                    print(f"OK: All bomb words are from tournament list")
            else:
                print("No bomb words returned")
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_bombs_endpoint()
