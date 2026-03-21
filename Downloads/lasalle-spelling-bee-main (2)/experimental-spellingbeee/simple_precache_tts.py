#!/usr/bin/env python3
"""
Simple TTS pre-caching using existing app functions.
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

# Import app TTS functions
from app import cache_and_return_edge, generate_tts_with_fallback

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

# Directories
audio_dir = os.path.join(os.path.dirname(__file__), "audio")
os.makedirs(audio_dir, exist_ok=True)

success_count = 0
error_count = 0
start_time = time.time()

for i, word in enumerate(missing_words, 1):
    print(f"\n[{i}/{len(missing_words)}] Processing: {word}")
    
    try:
        # Generate normal speed audio
        result = cache_and_return_edge(word, "en-US-JennyNeural", "-30%")
        if result:
            print(f"  OK {word} - normal speed cached")
            success_count += 1
        else:
            print(f"  ERROR {word} - failed to cache normal speed")
            error_count += 1
            continue
        
        # Generate slow speed audio
        result = cache_and_return_edge(word, "en-US-JennyNeural", "-55%")
        if result:
            print(f"  OK {word} - slow speed cached")
        else:
            print(f"  ERROR {word} - failed to cache slow speed")
        
        # Small delay to avoid overwhelming Edge TTS
        time.sleep(0.1)
        
    except Exception as e:
        print(f"  ERROR {word} - {e}")
        error_count += 1

elapsed = time.time() - start_time
print("\n" + "=" * 80)
print("PRE-CACHING COMPLETE")
print("=" * 80)
print(f"Total words processed: {len(missing_words)}")
print(f"Successfully cached: {success_count}")
print(f"Errors: {error_count}")
print(f"Time elapsed: {elapsed:.1f} seconds")
print(f"Average time per word: {elapsed/len(missing_words):.2f} seconds")
