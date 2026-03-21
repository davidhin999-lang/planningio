#!/usr/bin/env python3
"""
Check specific tournament words for audio
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import get_precached_audio, ELEVENLABS_AVAILABLE
from dotenv import load_dotenv

load_dotenv()

def check_tournament_words_audio():
    print("=" * 80)
    print("TOURNAMENT WORDS AUDIO CHECK")
    print("=" * 80)
    
    print(f"ElevenLabs Available: {ELEVENLABS_AVAILABLE}")
    
    # Check API key
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if api_key:
        print(f"ElevenLabs API Key: {api_key[:20]}...")
    else:
        print(f"ElevenLabs API Key: NOT SET - will use Edge TTS")
    
    # Test tournament words
    test_words = ["balloon", "airplane", "amazing", "american", "badminton"]
    
    print(f"\nTesting tournament words:")
    missing_audio = []
    
    for word in test_words:
        audio = get_precached_audio(word)
        if audio:
            print(f"  {word}: HAS AUDIO ✓")
        else:
            print(f"  {word}: MISSING AUDIO - will generate TTS on demand")
            missing_audio.append(word)
    
    print(f"\nSUMMARY:")
    print(f"Words with pre-cached audio: {len(test_words) - len(missing_audio)}")
    print(f"Words missing audio: {len(missing_audio)}")
    
    if missing_audio:
        print(f"\nMISSING AUDIO WORDS:")
        for word in missing_audio:
            print(f"  {word}")
        
        print(f"\nROBOTIC AUDIO RISK:")
        print(f"These words will use TTS on first request")
        print(f"If ElevenLabs fails → Edge TTS (natural)")
        print(f"If Edge TTS fails → Google TTS (ROBOTIC!)")
        
        # Check TTS fallback
        print(f"\nTTS FALLBACK CHAIN:")
        print(f"1. Check pre-cached audio")
        if ELEVENLABS_AVAILABLE and api_key:
            print(f"2. Generate with ElevenLabs (premium)")
        else:
            print(f"2. ElevenLabs not available")
        print(f"3. Fallback to Edge TTS (natural)")
        print(f"4. Last resort: Google TTS (ROBOTIC)")
    else:
        print(f"All test words have pre-cached audio - no robotic TTS!")

if __name__ == "__main__":
    check_tournament_words_audio()
