#!/usr/bin/env python3
"""
Cache all words to audio/ folder using edge-tts.
Run this once to pre-generate all audio files.
"""
import os
import asyncio
import edge_tts
from words import get_words_for_week, format_spelling_text, VALID_GROUPS, get_group_words

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")
VOICE = "en-US-JennyNeural"

async def generate_audio(word, suffix=""):
    safe_name = word.replace(" ", "_").lower()
    output_path = os.path.join(AUDIO_DIR, f"{safe_name}{suffix}.mp3")
    
    if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
        print(f"Skipping {word}{suffix} (already exists)")
        return
    
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
    print(f"Generated {word}{suffix}")

async def main():
    print("Caching all words to audio/ folder...")
    
    # Get all words across ALL groups and difficulties
    all_words = set()
    for group in VALID_GROUPS:
        for difficulty in ["easy", "medium", "hard"]:
            words = get_group_words(group, difficulty)
            all_words.update(words)
            print(f"[{group}] Found {len(words)} {difficulty} words")
    
    print(f"Total unique words across all groups: {len(all_words)}")
    
    # Generate normal and slow versions
    for word in sorted(all_words):
        await generate_audio(word, "")
        await generate_audio(word, "_slow")
        await generate_audio(word, "_spell")
    
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
