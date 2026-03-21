#!/usr/bin/env python3
"""
Local OpenAI Edge TTS integration for tournament words
Uses the same edge-tts technology but with better error handling
"""

import os
import sys
import asyncio
import edge_tts
import io
import time
import tempfile
from pathlib import Path

# Tournament words that need audio
TOURNAMENT_WORDS = [
    "balloon", "airplane", "amazing", "american", "badminton",
    "bathroom", "bedroom", "boring", "bowling", "brown",
    "castle", "children", "church", "climbing", "clumsy",
    "colors", "cupboard", "cycling", "daughter", "dishes",
    "dolphin", "eagle", "easily", "factory", "february",
    "fence", "fishing", "flood", "fruits", "handles",
    "jacket", "jungle", "keyboard", "library", "loudly",
    "monkey", "museum", "noodles", "often", "pharmacy",
    "property", "quickly", "rainbow", "sailing", "scissors",
    "sea lion", "shopping", "shoulder", "skirt", "sneakers",
    "speaking", "stand up", "sweater", "swimming", "thailand",
    "theater", "thursday", "tiring", "waitress", "warming",
    "warning", "weather", "whistle", "white"
]

# Voice mappings from OpenAI Edge TTS
VOICE_MAPPING = {
    'alloy': 'en-US-JennyNeural',
    'ash': 'en-US-AndrewNeural',
    'ballad': 'en-GB-ThomasNeural',
    'coral': 'en-AU-NatashaNeural',
    'echo': 'en-US-GuyNeural',
    'fable': 'en-GB-SoniaNeural',
    'nova': 'en-US-AriaNeural',
    'onyx': 'en-US-EricNeural',
    'sage': 'en-US-JennyNeural',
    'shimmer': 'en-US-EmmaNeural',
    'verse': 'en-US-BrianNeural',
}

DEFAULT_VOICE = 'en-US-JennyNeural'  # Clear female voice

async def generate_edge_tts_audio(text, voice=None, output_path=None):
    """Generate audio using edge-tts with better error handling."""
    try:
        # Use provided voice or default
        if voice:
            edge_voice = VOICE_MAPPING.get(voice, voice)
        else:
            edge_voice = DEFAULT_VOICE
        
        print(f"  Generating with voice: {edge_voice}")
        
        communicate = edge_tts.Communicate(text, edge_voice)
        audio_data = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        if output_path:
            with open(output_path, "wb") as f:
                f.write(audio_data.getvalue())
            return True, output_path
        else:
            return True, audio_data.getvalue()
        
    except Exception as e:
        print(f"    Edge TTS failed: {e}")
        return False, None

async def generate_tournament_audio():
    """Generate audio for all tournament words."""
    print("=" * 80)
    print("GENERATING TOURNAMENT AUDIO WITH LOCAL EDGE TTS")
    print("=" * 80)
    
    print(f"Voice: {DEFAULT_VOICE}")
    print(f"Words to process: {len(TOURNAMENT_WORDS)}")
    
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    success_count = 0
    failed_words = []
    
    for i, word in enumerate(TOURNAMENT_WORDS, 1):
        print(f"\n[{i}/{len(TOURNAMENT_WORDS)}] {word}")
        
        safe_name = word.replace(" ", "_").lower()
        output_path = os.path.join(audio_dir, f"{safe_name}.mp3")
        
        # Skip if already exists
        if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
            print(f"  Already exists")
            success_count += 1
            continue
        
        # Try multiple voices if the first fails
        voices_to_try = [DEFAULT_VOICE, 'en-US-AriaNeural', 'en-US-EmmaNeural', 'en-US-GuyNeural']
        
        for voice in voices_to_try:
            print(f"  Trying voice: {voice}")
            success, result = await generate_edge_tts_audio(word, voice, output_path)
            
            if success:
                print(f"  SUCCESS with {voice}")
                success_count += 1
                break
            else:
                print(f"  Failed with {voice}")
                continue
        else:
            print(f"  ALL VOICES FAILED")
            failed_words.append(word)
        
        # Rate limiting to avoid 403 errors
        await asyncio.sleep(2)
    
    print(f"\n" + "=" * 80)
    print("AUDIO GENERATION COMPLETE")
    print("=" * 80)
    print(f"Successfully generated: {success_count}/{len(TOURNAMENT_WORDS)}")
    print(f"Failed words: {len(failed_words)}")
    
    if failed_words:
        print(f"\nFailed words: {', '.join(failed_words[:10])}")
        if len(failed_words) > 10:
            print(f"... and {len(failed_words) - 10} more")
    
    if success_count > 0:
        print(f"\nSUCCESS! {success_count} tournament words now have natural audio!")
        print(f"Re-enable TTS in app.py and test the tournament!")
    else:
        print(f"\nAll attempts failed - edge-tts service may be down")

if __name__ == "__main__":
    asyncio.run(generate_tournament_audio())
