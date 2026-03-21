#!/usr/bin/env python3
"""
Deep analysis: Find all words in tournament group that don't belong
to the official 200-word list.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from words import GROUP_CONFIG

# Official 200-word list (normalized to lowercase)
OFFICIAL_WORDS = {
    "address", "apostrophe", "badminton", "balloon", "beautiful", "bedroom",
    "believe", "businessman", "groceries", "castle", "children", "chocolate",
    "climbing", "countryside", "cupboard", "cycling", "daughter", "delicious",
    "different", "dining room", "disgusting", "dolphin", "down town", "earphones",
    "electrician", "elephant", "engineer", "evening", "expensive", "exercise",
    "factory", "fashionable", "february", "fire fighter", "friendship", "furniture",
    "granddaughter", "hairdresser", "homework", "information", "instrument", "interesting",
    "introducing", "jacket", "jungle", "keyboard", "knowledge", "laboratory",
    "languages", "library", "lifestyle", "lunchtime", "magazine", "medicine",
    "microwave oven", "monkey", "mountains", "museum", "nationality", "necklace",
    "neighborhood", "newspaper", "notebook", "office building", "opposite", "pharmacy",
    "post office", "principal", "property", "psychology", "questions", "rainbow",
    "recognize", "refrigerator", "remember", "sales assistant", "saxophone", "scissors",
    "sentences", "shopping", "shoulder", "skateboarding", "snowboarding", "speaking",
    "bubble speech", "statements", "stomachache", "strawberry", "supermarket", "surprising",
    "swimming", "television", "thailand", "theater", "tomatoes", "tomorrow",
    "toothbrush", "train station", "umbrella", "understand", "united kingdom", "vegetables",
    "videogames", "waitress", "warning", "weather", "wednesday", "steering wheel",
    "whistle", "warming", "scientist", "police officer", "thirty three", "movie theater",
    "grandfather", "guinea pig", "fascinating", "grandchildren", "hairbrush", "waking up",
    "airplane", "green point", "images", "bathroom", "noodles", "handles",
    "boring", "amazing", "dislike", "explanation", "everywhere", "quickly",
    "tiring", "wheelchair", "holidays", "uncountable", "sweater", "easily",
    "irregular", "negociation", "prescription", "responsibility", "medication", "eagle",
    "classmate", "volleyball", "countable", "church", "thursday", "consonants",
    "sailing", "sightseeing", "household chores", "clumsy", "fishing", "workplace",
    "festival", "stand up", "correction", "careful", "november", "excitement",
    "bowling", "geography", "loudly", "garage", "fence",
    "afternoon", "fruits", "white", "sea lion", "octopus",
    "jelly fish", "brown", "paintings", "enthusiastic", "sandcastle", "often",
    "classical", "saturday", "celebrity", "material", "excuse me", "american",
    "dishes", "happiness", "laundromat", "skirt", "sneakers", "colors",
    "eraser", "rainforest", "flood", "volcano",
}

# Get current tournament words
tournament_cfg = GROUP_CONFIG.get("tournament", {})
current_words = tournament_cfg.get("words", {}).get("easy", [])

# Normalize current words
current_set = set(w.lower() for w in current_words)

print("=" * 80)
print("TOURNAMENT WORD LIST ANALYSIS")
print("=" * 80)

print(f"\nOfficial word count: {len(OFFICIAL_WORDS)}")
print(f"Current tournament word count: {len(current_set)}")

# Find extra words (in current but not in official)
extra_words = current_set - OFFICIAL_WORDS
print(f"\n[EXTRA WORDS] Words in tournament but NOT in official list: {len(extra_words)}")
if extra_words:
    for word in sorted(extra_words):
        print(f"  - {word}")

# Find missing words (in official but not in current)
missing_words = OFFICIAL_WORDS - current_set
print(f"\n[MISSING WORDS] Words in official but NOT in tournament: {len(missing_words)}")
if missing_words:
    for word in sorted(missing_words):
        print(f"  - {word}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Extra words to remove: {len(extra_words)}")
print(f"Missing words to add: {len(missing_words)}")
print(f"Total issues: {len(extra_words) + len(missing_words)}")

if extra_words or missing_words:
    print("\nBUGS IDENTIFIED:")
    if extra_words:
        print(f"  1. Tournament list contains {len(extra_words)} words that don't belong")
    if missing_words:
        print(f"  2. Tournament list is missing {len(missing_words)} official words")
else:
    print("\nNo issues found - tournament list matches official list perfectly!")

# Write detailed report
with open("tournament_analysis_report.txt", "w") as f:
    f.write("TOURNAMENT WORD LIST ANALYSIS REPORT\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"Official word count: {len(OFFICIAL_WORDS)}\n")
    f.write(f"Current tournament word count: {len(current_set)}\n\n")
    
    if extra_words:
        f.write(f"EXTRA WORDS TO REMOVE ({len(extra_words)}):\n")
        f.write("-" * 80 + "\n")
        for word in sorted(extra_words):
            f.write(f"  - {word}\n")
        f.write("\n")
    
    if missing_words:
        f.write(f"MISSING WORDS TO ADD ({len(missing_words)}):\n")
        f.write("-" * 80 + "\n")
        for word in sorted(missing_words):
            f.write(f"  - {word}\n")
        f.write("\n")
    
    f.write("\nCORRECT TOURNAMENT WORD LIST (sorted):\n")
    f.write("-" * 80 + "\n")
    correct_list = sorted(list(OFFICIAL_WORDS))
    for i, word in enumerate(correct_list, 1):
        f.write(f"{i:3d}. {word}\n")

print("\nDetailed report saved to tournament_analysis_report.txt")
