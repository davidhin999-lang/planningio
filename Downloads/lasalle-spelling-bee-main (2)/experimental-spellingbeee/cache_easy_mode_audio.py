#!/usr/bin/env python3
"""
Pre-cache audio for easy mode words that don't have cached audio.
This script identifies missing audio files and generates them using Edge TTS.
Run this to improve audio quality in easy mode.
"""
import os
import asyncio
import edge_tts
from words import get_group_words, format_spelling_text, VALID_GROUPS

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
VOICE = "en-US-JennyNeural"

def safe_filename(word, suffix=""):
    """Convert word to safe filename."""
    return word.replace(" ", "_").lower() + suffix + ".mp3"

def audio_exists(word, suffix=""):
    """Check if audio file exists and has reasonable size."""
    path = os.path.join(AUDIO_DIR, safe_filename(word, suffix))
    return os.path.exists(path) and os.path.getsize(path) > 100

async def generate_audio(word, suffix=""):
    """Generate audio for a word using Edge TTS."""
    if audio_exists(word, suffix):
        return False  # Already exists
    
    output_path = os.path.join(AUDIO_DIR, safe_filename(word, suffix))
    
    try:
        if suffix == "_spell":
            text = format_spelling_text(word)
            rate = "-30%"
        elif suffix == "_slow":
            text = word
            rate = "-55%"
        else:
            text = word
            rate = "-30%"
        
        communicate = edge_tts.Communicate(text, VOICE, rate=rate)
        await communicate.save(output_path)
        print(f"[OK] Generated {word}{suffix}")
        return True
    except Exception as e:
        print(f"[FAIL] {word}{suffix}: {e}")
        return False

async def main():
    print("=" * 60)
    print("Easy Mode Audio Pre-Loader")
    print("=" * 60)
    
    # Get all easy mode words across all groups
    easy_words = set()
    for group in VALID_GROUPS:
        words = get_group_words(group, "easy")
        easy_words.update(words)
        print(f"[{group}] Found {len(words)} easy mode words")
    
    print(f"\nTotal unique easy mode words: {len(easy_words)}")
    
    # Find missing audio
    missing = []
    for word in sorted(easy_words):
        if not audio_exists(word, ""):
            missing.append((word, ""))
        if not audio_exists(word, "_slow"):
            missing.append((word, "_slow"))
        if not audio_exists(word, "_spell"):
            missing.append((word, "_spell"))
    
    if not missing:
        print("\n[OK] All easy mode words have cached audio!")
        return
    
    print(f"\n[INFO] Found {len(missing)} missing audio files")
    print("Starting generation...\n")
    
    # Generate missing audio
    generated = 0
    failed = 0
    for word, suffix in missing:
        if await generate_audio(word, suffix):
            generated += 1
        else:
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Generated: {generated} files")
    print(f"Failed: {failed} files")
    print(f"Already cached: {len(easy_words) * 3 - len(missing)}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
