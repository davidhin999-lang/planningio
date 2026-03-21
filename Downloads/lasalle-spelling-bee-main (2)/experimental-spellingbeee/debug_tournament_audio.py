#!/usr/bin/env python3
"""
Debug script to check what's happening with the tournament audio
"""

import os
import sys
import requests
import json

def test_tournament_words():
    print("=" * 80)
    print("TOURNAMENT AUDIO DEBUG")
    print("=" * 80)
    
    # Test a few words that should have audio
    test_words = ["castle", "balloon", "airplane", "weather", "library"]
    
    base_url = "https://lasalle-spelling-bee.vercel.app"
    
    for word in test_words:
        print(f"\nTesting word: {word}")
        
        # Test the speak endpoint
        url = f"{base_url}/speak/{word}"
        print(f"  URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            print(f"  Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"  Content-Length: {response.headers.get('content-length', 'N/A')}")
            
            if response.status_code == 200:
                if 'audio' in response.headers.get('content-type', ''):
                    print(f"  SUCCESS: Audio file returned")
                else:
                    print(f"  WARNING: Not audio content")
                    print(f"  Response preview: {response.text[:200]}")
            elif response.status_code == 503:
                print(f"  ERROR: 503 - TTS disabled (expected for missing audio)")
                try:
                    error_data = response.json()
                    print(f"  Error message: {error_data.get('error', 'Unknown')}")
                except:
                    print(f"  Error body: {response.text[:200]}")
            else:
                print(f"  ERROR: {response.status_code}")
                print(f"  Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"  FAILED: {e}")
    
    print(f"\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)
    
    print(f"\nIf you see 503 errors for words that should have audio,")
    print(f"the deployment might not have included the new audio files.")
    print(f"If you see 200 responses with audio content, the backend is working.")
    
    print(f"\nNext steps:")
    print(f"1. Check if the audio files are actually in the deployed version")
    print(f"2. Clear browser cache and hard refresh (Ctrl+F5)")
    print(f"3. Check browser console for JavaScript errors")

if __name__ == "__main__":
    test_tournament_words()
