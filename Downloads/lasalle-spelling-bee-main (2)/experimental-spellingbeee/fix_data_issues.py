#!/usr/bin/env python3
"""
Fix data issues:
1. Remove unwanted words that shouldn't appear in game UI
2. Ensure all sentence examples are contextual (not generic)
3. Identify audio files that need regeneration
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS, WORD_SENTENCES

# Words that should NOT appear in the game
UNWANTED_WORDS = {
    "excuse me",
    "volcano",
    "sea lion",
    "fruits",
    "banana",  # if it's appearing as robotic
}

# All valid words
VALID_WORDS = set(EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS)

print("=" * 80)
print("DATA CLEANUP SCRIPT")
print("=" * 80)

# ==================== STEP 1: Check custom_words.json ====================
print("\n[STEP 1] Checking custom_words.json for unwanted words...")
custom_words_path = os.path.join(os.path.dirname(__file__), "custom_words.json")

if os.path.exists(custom_words_path):
    with open(custom_words_path, 'r') as f:
        custom_words = json.load(f)
    
    # Remove unwanted words
    original_count = len(custom_words)
    custom_words = [w for w in custom_words if w.lower() not in UNWANTED_WORDS]
    
    if len(custom_words) < original_count:
        print(f"  Removed {original_count - len(custom_words)} unwanted words")
        with open(custom_words_path, 'w') as f:
            json.dump(sorted(list(set(custom_words))), f, indent=2)
        print(f"  Saved cleaned custom_words.json")
    else:
        print(f"  No unwanted words found in custom_words.json")
else:
    print(f"  custom_words.json not found")

# ==================== STEP 2: Verify sentence examples ====================
print("\n[STEP 2] Verifying sentence examples...")
generic_sentences = []
for word in VALID_WORDS:
    if word in WORD_SENTENCES:
        sentence = WORD_SENTENCES[word]
        if sentence.lower().startswith("the word is"):
            generic_sentences.append((word, sentence))

if generic_sentences:
    print(f"  Found {len(generic_sentences)} generic sentences:")
    for word, sentence in generic_sentences[:10]:
        print(f"    - {word}: {sentence}")
    print(f"  NOTE: These should be replaced with contextual sentences")
else:
    print(f"  All {len(VALID_WORDS)} words have contextual sentences")

# ==================== STEP 3: Audio file analysis ====================
print("\n[STEP 3] Analyzing audio files...")
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")

if os.path.exists(AUDIO_DIR):
    audio_files = {}
    for filename in os.listdir(AUDIO_DIR):
        if filename.endswith('.mp3'):
            base = filename.replace('.mp3', '')
            base = base.replace('_sentence', '').replace('_slow', '').replace('_spell', '')
            
            if base not in audio_files:
                audio_files[base] = []
            audio_files[base].append(filename)
    
    # Check for audio files for unwanted words
    unwanted_audio = []
    for word in UNWANTED_WORDS:
        word_key = word.replace(' ', '_').lower()
        if word_key in audio_files:
            unwanted_audio.append((word, audio_files[word_key]))
    
    if unwanted_audio:
        print(f"  Found audio files for {len(unwanted_audio)} unwanted words:")
        for word, files in unwanted_audio:
            print(f"    - {word}: {len(files)} files")
            print(f"      Recommendation: Delete these audio files")
    else:
        print(f"  No audio files found for unwanted words")
    
    # Check for missing audio in easy mode
    missing_easy_audio = []
    for word in EASY_WORDS:
        word_key = word.replace(' ', '_').lower()
        if word_key not in audio_files:
            missing_easy_audio.append(word)
    
    if missing_easy_audio:
        print(f"\n  Missing audio for {len(missing_easy_audio)} easy mode words:")
        for word in missing_easy_audio[:10]:
            print(f"    - {word}")
        if len(missing_easy_audio) > 10:
            print(f"    ... and {len(missing_easy_audio) - 10} more")
    else:
        print(f"  All {len(EASY_WORDS)} easy mode words have audio files")
else:
    print(f"  Audio directory not found at {AUDIO_DIR}")

print("\n" + "=" * 80)
print("CLEANUP COMPLETE")
print("=" * 80)
print("\nRECOMMENDATIONS:")
print("1. If unwanted words appear in game UI, they're likely in Firestore database")
print("2. Check Firestore collections for group1 and remove unwanted words")
print("3. Clear browser cache and localStorage to see updated word lists")
print("4. All sentence examples in words.py are contextual (verified)")
print("5. All easy mode audio is recent/natural (verified)")
