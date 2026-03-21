#!/usr/bin/env python3
"""
Pre-cache TTS audio for all missing tournament words using Edge TTS.
This prevents robotic Google TTS fallback.
"""

import sys
import os
import asyncio
import edge_tts
import time
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words

# Load missing words list
missing_words = []
try:
    with open("tournament_missing_tts.txt", "r") as f:
        lines = f.readlines()
        for line in lines[2:]:  # Skip header lines
            word = line.strip()
            if word:
                missing_words.append(word)
except FileNotFoundError:
    print("Error: tournament_missing_tts.txt not found. Run check_missing_tts.py first.")
    sys.exit(1)

print("=" * 80)
print("PRE-CACHING TOURNAMENT WORDS WITH EDGE TTS")
print("=" * 80)
print(f"Words to process: {len(missing_words)}")

# Edge TTS configuration
VOICE_NORMAL = "en-US-JennyNeural"  # Clear female voice
VOICE_SLOW = "en-US-JennyNeural"   # Same voice for consistency
VOICE_SPELL = "en-US-JennyNeural"  # Same voice for spelling

# Directories
audio_dir = os.path.join(os.path.dirname(__file__), "audio")
os.makedirs(audio_dir, exist_ok=True)

async def generate_speech_edge(text, voice=VOICE_NORMAL, rate="-30%"):
    """Generate speech using Edge TTS."""
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
    return communicate.stream()

async def cache_word_audio(word):
    """Generate and cache audio for a single word."""
    safe_name = word.replace(" ", "_").lower()
    
    # Check if already exists
    existing_files = [
        os.path.join(audio_dir, f"{safe_name}.mp3"),
        os.path.join(audio_dir, f"{safe_name}_slow.mp3"),
        os.path.join(audio_dir, f"{safe_name}_spell.mp3"),
        os.path.join(audio_dir, f"{safe_name}_sentence.mp3")
    ]
    
    if all(os.path.exists(f) for f in existing_files):
        print(f"  OK {word} - already cached")
        return True
    
    try:
        # Generate normal speed audio
        if not os.path.exists(existing_files[0]):
            audio_stream = generate_speech_edge(word, VOICE_NORMAL, "-30%")
            audio_data = b""
            async for chunk in audio_stream:
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            with open(existing_files[0], "wb") as f:
                f.write(audio_data)
            print(f"  OK {word} - normal speed cached")
        
        # Generate slow speed audio
        if not os.path.exists(existing_files[1]):
            audio_stream = generate_speech_edge(word, VOICE_SLOW, "-55%")
            audio_data = b""
            async for chunk in audio_stream:
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            with open(existing_files[1], "wb") as f:
                f.write(audio_data)
            print(f"  OK {word} - slow speed cached")
        
        # Generate spelling audio
        if not os.path.exists(existing_files[2]):
            spelling_text = ""
            for i, letter in enumerate(word.upper()):
                if letter == " ":
                    spelling_text += "space. "
                else:
                    spelling_text += f"{letter}. "
            spelling_text = spelling_text.strip()
            
            audio_stream = generate_speech_edge(spelling_text, VOICE_SPELL, "-30%")
            audio_data = b""
            async for chunk in audio_stream:
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            with open(existing_files[2], "wb") as f:
                f.write(audio_data)
            print(f"  OK {word} - spelling cached")
        
        # Generate sentence audio
        if not os.path.exists(existing_files[3]):
            sentence_text = f"Can you spell the word {word}?"
            audio_stream = generate_speech_edge(sentence_text, VOICE_NORMAL, "-30%")
            audio_data = b""
            async for chunk in audio_stream:
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            with open(existing_files[3], "wb") as f:
                f.write(audio_data)
            print(f"  OK {word} - sentence cached")
        
        return True
        
    except Exception as e:
        print(f"  ERROR {word} - {e}")
        return False

async def main():
    """Process all missing words."""
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    for i, word in enumerate(missing_words, 1):
        print(f"\n[{i}/{len(missing_words)}] Processing: {word}")
        
        if await cache_word_audio(word):
            success_count += 1
        else:
            error_count += 1
        
        # Small delay to avoid overwhelming Edge TTS
        await asyncio.sleep(0.1)
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print("PRE-CACHING COMPLETE")
    print("=" * 80)
    print(f"Total words processed: {len(missing_words)}")
    print(f"Successfully cached: {success_count}")
    print(f"Errors: {error_count}")
    print(f"Time elapsed: {elapsed:.1f} seconds")
    print(f"Average time per word: {elapsed/len(missing_words):.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
