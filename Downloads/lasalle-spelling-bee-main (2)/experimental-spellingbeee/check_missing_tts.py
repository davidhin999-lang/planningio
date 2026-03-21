#!/usr/bin/env python3
"""
Check which tournament words are missing from pre-cached audio.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words

# Get all tournament words
tournament_words = set()
for difficulty in ["easy", "medium", "hard"]:
    words = get_group_words("tournament", difficulty)
    tournament_words.update(words)

# Get all pre-cached audio files
audio_dir = os.path.join(os.path.dirname(__file__), "audio")
cached_files = set()
if os.path.exists(audio_dir):
    for filename in os.listdir(audio_dir):
        if filename.endswith(".mp3") and not any(suffix in filename for suffix in ["_sentence", "_slow", "_spell"]):
            # Extract word name from filename (remove .mp3)
            word = filename[:-4]
            # Convert underscores back to spaces
            word = word.replace("_", " ")
            cached_files.add(word.lower())

print("=" * 80)
print("TOURNAMENT WORDS MISSING FROM PRE-CACHED AUDIO")
print("=" * 80)

missing_words = []
for word in sorted(tournament_words):
    if word.lower() not in cached_files:
        missing_words.append(word)

print(f"Total tournament words: {len(tournament_words)}")
print(f"Pre-cached audio files: {len(cached_files)}")
print(f"Missing audio files: {len(missing_words)}")

if missing_words:
    print(f"\nMissing words ({len(missing_words)}):")
    for i, word in enumerate(missing_words, 1):
        print(f"  {i:3d}. {word}")
    
    # Save missing words list
    with open("tournament_missing_tts.txt", "w") as f:
        f.write("Tournament words missing from pre-cached audio:\n")
        f.write("=" * 50 + "\n")
        for word in missing_words:
            f.write(f"{word}\n")
    
    print(f"\nSaved missing words list to tournament_missing_tts.txt")
else:
    print("\nAll tournament words have pre-cached audio!")

print("\n" + "=" * 80)
print("TTS CONFIGURATION")
print("=" * 80)

# Check TTS configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
print(f"ElevenLabs API Key available: {'Yes' if ELEVENLABS_API_KEY else 'No'}")
print(f"Audio cache directory: {audio_dir}")
print(f"Cache directory exists: {os.path.exists(audio_dir)}")
