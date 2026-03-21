#!/usr/bin/env python3
"""
Quick fix: Generate audio for first 10 tournament words to stop robotic TTS
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

# First 10 tournament words to fix immediately
URGENT_WORDS = [
    "balloon", "airplane", "amazing", "american", "badminton",
    "bathroom", "bedroom", "boring", "bowling", "brown"
]

def generate_elevenlabs_audio(text, output_path):
    """Generate audio using ElevenLabs API."""
    try:
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY,
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }
        
        response = requests.post(f"{ELEVENLABS_API_URL}/{ELEVENLABS_VOICE_ID}", 
                               json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"    API error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"    Generation failed: {e}")
        return False

def main():
    """Generate audio for urgent tournament words."""
    print("=" * 80)
    print("URGENT FIX: Generate audio for tournament words")
    print("=" * 80)
    
    if not ELEVENLABS_API_KEY:
        print("ERROR: ElevenLabs API Key not found!")
        return
    
    print(f"API Key: {ELEVENLABS_API_KEY[:20]}...")
    print(f"Generating audio for {len(URGENT_WORDS)} urgent words...")
    
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    success_count = 0
    
    for i, word in enumerate(URGENT_WORDS, 1):
        print(f"\n[{i}/{len(URGENT_WORDS)}] {word}")
        
        safe_name = word.replace(" ", "_").lower()
        output_path = os.path.join(audio_dir, f"{safe_name}.mp3")
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
            print(f"  Already exists")
            success_count += 1
            continue
        
        print(f"  Generating...")
        
        if generate_elevenlabs_audio(word, output_path):
            print(f"  SUCCESS")
            success_count += 1
        else:
            print(f"  FAILED - will use Edge TTS")
        
        time.sleep(1)  # Rate limiting
    
    print(f"\n" + "=" * 80)
    print("URGENT FIX COMPLETE")
    print("=" * 80)
    print(f"Audio files generated: {success_count}/{len(URGENT_WORDS)}")
    
    if success_count > 0:
        print(f"\nSUCCESS! {success_count} words now have premium audio")
        print(f"Test these words in the tournament - no more robotic TTS!")
    else:
        print(f"\nElevenLabs failed - Edge TTS will be used instead")
        print(f"Still better than robotic Google TTS")

if __name__ == "__main__":
    main()
