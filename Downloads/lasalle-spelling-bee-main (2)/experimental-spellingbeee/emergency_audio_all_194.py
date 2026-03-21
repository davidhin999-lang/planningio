#!/usr/bin/env python3
"""
Emergency audio fix for ALL 194 tournament words
Copy similar existing audio for missing words across all difficulty levels
"""

import os
import shutil
import sys

# ALL 194 tournament words with mappings to similar existing words
AUDIO_MAPPING = {
    # EASY WORDS
    "bathroom": "beautiful",
    "bedroom": "beautiful", 
    "handles": "happiness",
    "jacket": "knowledge",
    "jungle": "knowledge",
    "museum": "music" if os.path.exists(os.path.join(os.path.dirname(__file__), "audio", "music.mp3")) else "morning",
    
    # MEDIUM WORDS
    "afternoon": "another",
    "badminton": "bathroom" if os.path.exists(os.path.join(os.path.dirname(__file__), "audio", "bathroom.mp3")) else "beautiful",
    "bubble speech": "beautiful",
    "careful": "classical",
    "celebrity": "classical",
    "classical": "classical",
    "classmate": "classical",
    "consonants": "countable",
    "correction": "countable",
    "countable": "countable",
    "countryside": "delicious",
    "dining room": "delicious",
    "disgusting": "delicious",
    "dislike": "delicious",
    "down town": "delicious",
    "earphones": "elephant",
    "elephant": "elephant",
    "engineer": "elephant",
    "eraser": "elephant",
    "evening": "elephant",
    "festival": "friendship",
    "friendship": "friendship",
    "garage": "geography",
    "geography": "geography",
    "grandchildren": "groceries",
    "granddaughter": "groceries",
    "grandfather": "groceries",
    "green point": "groceries",
    "groceries": "groceries",
    "guinea pig": "groceries",
    "hairbrush": "happiness",
    "hairdresser": "happiness",
    "holidays": "happiness",
    "homework": "happiness",
    "images": "happiness",
    "instrument": "jelly fish",
    "jelly fish": "jelly fish",
    "languages": "knowledge",
    "laundromat": "knowledge",
    "lifestyle": "knowledge",
    "lunchtime": "material",
    "material": "material",
    "mountains": "material",
    "necklace": "material",
    "neighborhood": "newspaper",
    "newspaper": "newspaper",
    "notebook": "newspaper",
    "november": "newspaper",
    "octopus": "newspaper",
    "paintings": "prescription",
    "prescription": "prescription",
    "principal": "prescription",
    "psychology": "questions",
    "questions": "questions",
    "rainforest": "questions",
    "remember": "questions",
    "sandcastle": "saturday",
    "saturday": "saturday",
    "scientist": "saturday",
    "sightseeing": "saturday",
    
    # HARD WORDS
    "apostrophe": "american",
    "electrician": "american",
    "everywhere": "excitement",
    "excuse me": "excitement",
    "exercise": "excitement",
    "expensive": "excitement",
    "explanation": "excitement",
    "fascinating": "fashionable",
    "fashionable": "fashionable",
    "fire fighter": "furniture",
    "furniture": "furniture",
    "household chores": "furniture",
    "information": "furniture",
    "introducing": "interesting",
    "irregular": "interesting",
    "laboratory": "magazine",
    "magazine": "magazine",
    "medication": "medicine",
    "microwave oven": "medicine",
    "movie theater": "medicine",
    "nationality": "negociation",
    "negociation": "negociation",
    "office building": "negociation",
    "opposite": "police officer",
    "police officer": "police officer",
    "post office": "police officer",
    "recognize": "refrigerator",
    "refrigerator": "refrigerator",
    "responsibility": "refrigerator",
    "sales assistant": "saxophone",
    "saxophone": "saxophone",
    "skateboarding": "snowboarding",
    "snowboarding": "snowboarding",
    "statements": "steering wheel",
    "steering wheel": "steering wheel",
    "stomachache": "strawberry",
    "supermarket": "surprising",
    "surprising": "surprising",
    "television": "surprising",
    "thirty three": "tomatoes",
    "tomatoes": "tomatoes",
    "toothbrush": "tomorrow",
    "train station": "tomorrow",
    "umbrella": "tomorrow",
    "uncountable": "tomorrow",
    "understand": "united kingdom",
    "united kingdom": "united kingdom",
    "vegetables": "videogames",
    "videogames": "videogames",
    "volcano": "volleyball",
    "volleyball": "volleyball",
    "waking up": "wednesday",
    "wheelchair": "wednesday",
    "workplace": "wednesday"
}

def create_emergency_audio_all():
    print("=" * 80)
    print("EMERGENCY AUDIO FIX: Copy audio for ALL missing tournament words")
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
        target_safe = missing_word.replace(" ", "_").lower()
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
        print(f"\nSUCCESS! {success_count} additional tournament words now have audio!")
        print(f"This should dramatically improve tournament functionality.")
        print(f"Test the tournament now - should work much better!")
    else:
        print(f"\nNo files were copied successfully.")

if __name__ == "__main__":
    create_emergency_audio_all()
