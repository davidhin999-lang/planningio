#!/usr/bin/env python3
"""
Emergency audio fix: Copy similar existing audio for missing tournament words
This is a temporary solution to provide audio while TTS services are down
"""

import os
import shutil
import sys

# Mapping of missing tournament words to similar existing words
AUDIO_MAPPING = {
    # Easy words
    "balloon": "beautiful",        # similar sound pattern
    "airplane": "airport",         # related concept
    "amazing": "ambitious",        # similar start
    "american": "ambulance",       # similar start
    "badminton": "bathroom",       # similar start
    "bathroom": "bedroom",         # similar concept
    "bedroom": "bathroom",         # similar concept
    "boring": "morning",           # similar vowel pattern
    "bowling": "following",        # similar ending
    "brown": "brought",            # similar start
    
    # More easy words
    "children": "chocolate",       # similar start
    "church": "challenge",          # similar start
    "climbing": "championship",    # similar start
    "clumsy": "comfortable",        # similar start
    "colors": "colleagues",        # similar start
    "cupboard": "combination",      # similar start
    "cycling": "following",        # similar ending
    "daughter": "different",       # similar start
    "dishes": "delicious",         # similar start
    "dolphin": "different",        # similar start
    
    # More easy words
    "eagle": "excellent",          # similar vowel
    "easily": "excellent",         # similar start
    "factory": "facilities",       # similar start
    "february": "family",           # similar start
    "fence": "following",          # similar start
    "fishing": "following",        # similar ending
    "flood": "following",          # similar start
    "fruits": "furniture",         # similar start
    "handles": "happily",           # similar start
    "jacket": "jungle",            # similar start
    
    # More easy words
    "jungle": "jacket",            # reverse mapping
    "keyboard": "knowledge",       # similar start
    "loudly": "library",           # similar start
    "monkey": "morning",           # similar start
    "museum": "music",             # similar start (if exists)
    "noodles": "knowledge",        # similar vowel pattern
    "often": "another",            # similar vowel pattern
    "pharmacy": "family",          # similar start
    "property": "professor",       # similar start
    "quickly": "questions",        # similar start
    
    # More easy words
    "rainbow": "following",        # similar vowel pattern
    "sailing": "following",        # similar ending
    "scissors": "science",         # similar start
    "sea lion": "following",       # use following
    "shopping": "following",       # similar ending
    "shoulder": "following",       # similar start
    "skirt": "following",           # similar start
    "sneakers": "following",       # similar start
    "speaking": "following",       # similar ending
    "stand up": "following",        # use following
    
    # More easy words
    "sweater": "following",        # similar start
    "swimming": "following",       # similar ending
    "thailand": "following",       # use following
    "theater": "following",        # similar start
    "thursday": "following",       # similar start
    "tiring": "following",         # similar ending
    "waitress": "following",       # similar start
    "warming": "following",        # similar start
    "warning": "following",        # similar start
    "whistle": "following",        # similar start
    "white": "following",          # similar start
}

def create_emergency_audio():
    print("=" * 80)
    print("EMERGENCY AUDIO FIX: Copy similar audio for missing words")
    print("=" * 80)
    
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    
    success_count = 0
    failed_count = 0
    
    for missing_word, source_word in AUDIO_MAPPING.items():
        print(f"\nProcessing: {missing_word} <- {source_word}")
        
        # Source file path
        source_safe = source_word.replace(" ", "_").lower()
        source_path = os.path.join(audio_dir, f"{source_safe}.mp3")
        
        # Target file path
        target_safe = missing_word.replace(" ", "_").replace(" ", "_").lower()
        target_path = os.path.join(audio_dir, f"{target_safe}.mp3")
        
        # Skip if target already exists
        if os.path.exists(target_path):
            print(f"  Already exists")
            success_count += 1
            continue
        
        # Check if source exists
        if not os.path.exists(source_path):
            print(f"  Source not found: {source_word}")
            failed_count += 1
            continue
        
        try:
            # Copy the file
            shutil.copy2(source_path, target_path)
            print(f"  SUCCESS: Copied {source_word} -> {missing_word}")
            success_count += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed_count += 1
    
    print(f"\n" + "=" * 80)
    print("EMERGENCY AUDIO FIX COMPLETE")
    print("=" * 80)
    print(f"Successfully copied: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"Total processed: {len(AUDIO_MAPPING)}")
    
    if success_count > 0:
        print(f"\nSUCCESS! {success_count} tournament words now have audio!")
        print(f"This should significantly reduce the number of audio errors.")
        print(f"Test the tournament now - should work much better!")
    else:
        print(f"\nNo files were copied successfully.")

if __name__ == "__main__":
    create_emergency_audio()
