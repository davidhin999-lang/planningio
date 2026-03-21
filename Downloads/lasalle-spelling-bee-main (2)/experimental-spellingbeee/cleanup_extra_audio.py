#!/usr/bin/env python3
"""
Remove all audio files for words that are NOT in words.py
Keep only audio for valid words
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS

VALID_WORDS = set(EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS)
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")

print("=" * 80)
print("CLEANING UP EXTRA AUDIO FILES")
print("=" * 80)

# Get all unique base words from audio files
audio_words = {}
if os.path.exists(AUDIO_DIR):
    for filename in os.listdir(AUDIO_DIR):
        if filename.endswith('.mp3'):
            base = filename.replace('.mp3', '')
            base = base.replace('_sentence', '').replace('_slow', '').replace('_spell', '')
            
            if base not in audio_words:
                audio_words[base] = []
            audio_words[base].append(filename)

# Find words in audio that are NOT in words.py
extra_words = set(audio_words.keys()) - VALID_WORDS

print(f"\nTotal audio files: {sum(len(files) for files in audio_words.values())}")
print(f"Valid words in words.py: {len(VALID_WORDS)}")
print(f"Words with audio: {len(audio_words)}")
print(f"Extra words to remove: {len(extra_words)}")

if extra_words:
    print(f"\nRemoving {len(extra_words)} extra words...")
    
    deleted_count = 0
    for word in sorted(extra_words):
        files_to_delete = audio_words[word]
        for filename in files_to_delete:
            filepath = os.path.join(AUDIO_DIR, filename)
            try:
                os.remove(filepath)
                deleted_count += 1
                print(f"  Deleted: {filename}")
            except Exception as e:
                print(f"  ERROR deleting {filename}: {e}")
    
    print(f"\nTotal files deleted: {deleted_count}")
else:
    print("\nNo extra words found. Audio directory is clean!")

print("\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)
