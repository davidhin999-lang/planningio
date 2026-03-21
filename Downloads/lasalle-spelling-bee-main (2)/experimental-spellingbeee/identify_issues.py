#!/usr/bin/env python3
"""
Identify three issues:
1. Words appearing in game UI that shouldn't be there
2. Generic sentence examples instead of contextual
3. Robotic voice audio in easy mode
"""
import os
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS, WORD_SENTENCES

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

print("=" * 80)
print("ISSUE IDENTIFICATION REPORT")
print("=" * 80)

# ==================== ISSUE 1: Words in UI that shouldn't be there ====================
print("\n[ISSUE 1] Words appearing in game UI that shouldn't be there")
print("-" * 80)

# Check if "excuse me", "volcano", "sea lion", "fruits" are in word lists
unwanted_words = ["excuse me", "volcano", "sea lion", "fruits"]
all_words = set(EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS)

print(f"Checking for unwanted words in word lists...")
for word in unwanted_words:
    if word in all_words:
        print(f"  [FOUND] '{word}' is in word lists - SHOULD BE REMOVED")
    else:
        print(f"  [OK] '{word}' is NOT in word lists")

# ==================== ISSUE 2: Generic sentence examples ====================
print("\n[ISSUE 2] Generic sentence examples instead of contextual")
print("-" * 80)

generic_count = 0
contextual_count = 0
missing_count = 0

for word in EASY_WORDS:
    if word not in WORD_SENTENCES:
        missing_count += 1
        print(f"  [MISSING] '{word}' has no sentence example")
    else:
        sentence = WORD_SENTENCES[word]
        if sentence.lower().startswith("the word is"):
            generic_count += 1
            print(f"  [GENERIC] '{word}': {sentence}")
        else:
            contextual_count += 1

print(f"\nSummary for EASY_WORDS:")
print(f"  Contextual sentences: {contextual_count}")
print(f"  Generic sentences: {generic_count}")
print(f"  Missing sentences: {missing_count}")

# ==================== ISSUE 3: Robotic voice audio ====================
print("\n[ISSUE 3] Robotic voice audio in easy mode")
print("-" * 80)

# Get file modification times to identify old (robotic) vs new (natural) audio
now = time.time()
one_week_ago = now - (7 * 24 * 3600)
one_month_ago = now - (30 * 24 * 3600)

old_audio_files = []
recent_audio_files = []

if os.path.exists(AUDIO_DIR):
    for filename in os.listdir(AUDIO_DIR):
        if filename.endswith('.mp3'):
            filepath = os.path.join(AUDIO_DIR, filename)
            mtime = os.path.getmtime(filepath)
            
            # Extract base word name
            base = filename.replace('.mp3', '')
            base = base.replace('_sentence', '').replace('_slow', '').replace('_spell', '')
            
            # Check if it's an easy word
            if base in EASY_WORDS:
                if mtime < one_month_ago:
                    old_audio_files.append((base, filename, mtime))
                elif mtime > one_week_ago:
                    recent_audio_files.append((base, filename, mtime))

# Group old files by word
old_words = {}
for base, filename, mtime in old_audio_files:
    if base not in old_words:
        old_words[base] = []
    old_words[base].append(filename)

print(f"\nEasy mode words with OLD (likely robotic) audio:")
print(f"Total: {len(old_words)} words")
for word in sorted(old_words.keys()):
    dt = datetime.fromtimestamp(os.path.getmtime(os.path.join(AUDIO_DIR, old_words[word][0])))
    print(f"  - {word} (generated: {dt.strftime('%Y-%m-%d %H:%M')})")

print(f"\nEasy mode words with RECENT (likely natural) audio:")
recent_words = set(base for base, _, _ in recent_audio_files)
print(f"Total: {len(recent_words)} words")

# Words that need regeneration
easy_words_set = set(EASY_WORDS)
robotic_words = easy_words_set.intersection(set(old_words.keys()))
print(f"\nEasy mode words needing regeneration: {len(robotic_words)}")
for word in sorted(robotic_words):
    print(f"  - {word}")

print("\n" + "=" * 80)
print("END OF REPORT")
print("=" * 80)
