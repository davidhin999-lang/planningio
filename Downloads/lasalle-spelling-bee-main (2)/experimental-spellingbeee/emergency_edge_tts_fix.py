#!/usr/bin/env python3
"""
Emergency fix: Generate Edge TTS audio for tournament words to stop robotic TTS
"""

import os
import sys
import asyncio
import edge_tts
import io
import time

# First 20 tournament words to fix immediately
URGENT_WORDS = [
    "balloon", "airplane", "amazing", "american", "badminton",
    "bathroom", "bedroom", "boring", "bowling", "brown",
    "castle", "children", "church", "climbing", "clumsy",
    "colors", "cupboard", "cycling", "daughter", "dishes"
]

EDGE_VOICE = "en-US-JennyNeural"

async def generate_edge_tts_audio(text, output_path):
    """Generate audio using Edge TTS."""
    try:
        communicate = edge_tts.Communicate(text, EDGE_VOICE)
        audio_data = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        with open(output_path, "wb") as f:
            f.write(audio_data.getvalue())
        
        return True
        
    except Exception as e:
        print(f"    Edge TTS failed: {e}")
        return False

async def main():
    """Generate Edge TTS audio for urgent tournament words."""
    print("=" * 80)
    print("EMERGENCY FIX: Generate Edge TTS audio for tournament words")
    print("=" * 80)
    
    print(f"Voice: {EDGE_VOICE}")
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
        
        print(f"  Generating Edge TTS...")
        
        if await generate_edge_tts_audio(word, output_path):
            print(f"  SUCCESS - Natural Edge TTS audio created")
            success_count += 1
        else:
            print(f"  FAILED - will use robotic TTS")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n" + "=" * 80)
    print("EMERGENCY FIX COMPLETE")
    print("=" * 80)
    print(f"Audio files generated: {success_count}/{len(URGENT_WORDS)}")
    
    if success_count > 0:
        print(f"\nSUCCESS! {success_count} words now have natural Edge TTS audio")
        print(f"This should stop the robotic TTS for these words!")
        print(f"Test the tournament now - should sound much better!")
    else:
        print(f"\nEdge TTS also failed - check network/connection")

if __name__ == "__main__":
    asyncio.run(main())
