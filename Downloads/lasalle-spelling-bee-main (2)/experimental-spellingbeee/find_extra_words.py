#!/usr/bin/env python3
"""
Find all extra words that are appearing in the game but not in words.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS

# All valid words from source
VALID_WORDS = set(EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS)

# Words reported as appearing but shouldn't
REPORTED_EXTRA_WORDS = {
    "excuse me",
    "volcano",
    "sea lion",
    "fruits",
    "banana",
    "often",
    "octopus",
}

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")

print("=" * 80)
print("FINDING EXTRA WORDS IN AUDIO DIRECTORY")
print("=" * 80)

# Get all unique base words from audio files
audio_words = set()
if os.path.exists(AUDIO_DIR):
    for filename in os.listdir(AUDIO_DIR):
        if filename.endswith('.mp3'):
            base = filename.replace('.mp3', '')
            base = base.replace('_sentence', '').replace('_slow', '').replace('_spell', '')
            audio_words.add(base)

print(f"\nTotal unique words with audio files: {len(audio_words)}")
print(f"Total valid words in words.py: {len(VALID_WORDS)}")

# Find words in audio that are NOT in words.py
extra_words_in_audio = audio_words - VALID_WORDS

print(f"\nWords with audio files but NOT in words.py: {len(extra_words_in_audio)}")
if extra_words_in_audio:
    for word in sorted(extra_words_in_audio):
        # Count how many audio variants
        variants = [f for f in os.listdir(AUDIO_DIR) if f.startswith(word + '.') or f.startswith(word + '_')]
        print(f"  - {word} ({len(variants)} audio files)")

# Check reported words specifically
print(f"\nStatus of reported extra words:")
for word in sorted(REPORTED_EXTRA_WORDS):
    word_key = word.replace(' ', '_').lower()
    has_audio = word_key in audio_words
    in_valid = word in VALID_WORDS
    print(f"  {word:20} | In words.py: {str(in_valid):5} | Has audio: {str(has_audio):5}")

print("\n" + "=" * 80)
