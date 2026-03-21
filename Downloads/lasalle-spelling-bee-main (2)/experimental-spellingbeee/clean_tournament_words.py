#!/usr/bin/env python3
"""
Clean tournament group word list:
1. Keep ONLY the 200 official words
2. Remove duplicates
3. Remove any extra words
"""

# Official 200-word list from user
OFFICIAL_WORDS = [
    "ADDRESS", "APOSTROPHE", "BADMINTON", "BALLOON", "BEAUTIFUL", "BEDROOM",
    "BELIEVE", "BUSINESSMAN", "GROCERIES", "CASTLE", "CHILDREN", "CHOCOLATE",
    "CLIMBING", "COUNTRYSIDE", "CUPBOARD", "CYCLING", "DAUGHTER", "DELICIOUS",
    "DIFFERENT", "DINING ROOM", "DISGUSTING", "DOLPHIN", "DOWN TOWN", "EARPHONES",
    "ELECTRICIAN", "ELEPHANT", "ENGINEER", "EVENING", "EXPENSIVE", "EXERCISE",
    "FACTORY", "FASHIONABLE", "FEBRUARY", "FIRE FIGHTER", "FRIENDSHIP", "FURNITURE",
    "GRANDDAUGHTER", "HAIRDRESSER", "HOMEWORK", "INFORMATION", "INSTRUMENT", "INTERESTING",
    "INTRODUCING", "JACKET", "JUNGLE", "KEYBOARD", "KNOWLEDGE", "LABORATORY",
    "LANGUAGES", "LIBRARY", "LIFESTYLE", "LUNCHTIME", "MAGAZINE", "MEDICINE",
    "MICROWAVE OVEN", "MONKEY", "MOUNTAINS", "MUSEUM", "NATIONALITY", "NECKLACE",
    "NEIGHBORHOOD", "NEWSPAPER", "NOTEBOOK", "OFFICE BUILDING", "OPPOSITE", "PHARMACY",
    "POST OFFICE", "PRINCIPAL", "PROPERTY", "PSYCHOLOGY", "QUESTIONS", "RAINBOW",
    "RECOGNIZE", "REFRIGERATOR", "REMEMBER", "SALES ASSISTANT", "SAXOPHONE", "SCISSORS",
    "SENTENCES", "SHOPPING", "SHOULDER", "SKATEBOARDING", "SNOWBOARDING", "SPEAKING",
    "BUBBLE SPEECH", "STATEMENTS", "STOMACHACHE", "STRAWBERRY", "SUPERMARKET", "SURPRISING",
    "SWIMMING", "TELEVISION", "THAILAND", "THEATER", "TOMATOES", "TOMORROW",
    "TOOTHBRUSH", "TRAIN STATION", "UMBRELLA", "UNDERSTAND", "UNITED KINGDOM", "VEGETABLES",
    "VIDEOGAMES", "WAITRESS", "WARNING", "WEATHER", "WEDNESDAY", "STEERING WHEEL",
    "WHISTLE", "BUSINESSMAN", "WARMING", "SCIENTIST", "POLICE OFFICER", "THIRTY THREE", "MOVIE THEATER",
    "GRANDFATHER", "GUINEA PIG", "FASCINATING", "GRANDCHILDREN", "HAIRBRUSH", "WAKING UP",
    "AIRPLANE", "GREEN POINT", "IMAGES", "BATHROOM", "NOODLES", "HANDLES",
    "BORING", "AMAZING", "DISLIKE", "EXPLANATION", "EVERYWHERE", "QUICKLY",
    "TIRING", "WHEELCHAIR", "HOLIDAYS", "UNCOUNTABLE", "SWEATER", "EASILY",
    "IRREGULAR", "NEGOCIATION", "PRESCRIPTION", "RESPONSIBILITY", "MEDICATION", "EAGLE",
    "CLASSMATE", "VOLLEYBALL", "COUNTABLE", "CHURCH", "THURSDAY", "CONSONANTS",
    "SAILING", "SIGHTSEEING", "HOUSEHOLD CHORES", "CLUMSY", "FISHING", "WORKPLACE",
    "FESTIVAL", "STAND UP", "CORRECTION", "CAREFUL", "NOVEMBER", "EXCITEMENT",
    "BOWLING", "GEOGRAPHY", "LOUDLY", "GARAGE", "LIBRARY", "FENCE",
    "AFTERNOON", "FRUITS", "BORING", "WHITE", "SEA LION", "OCTOPUS",
    "JELLY FISH", "BROWN", "PAINTINGS", "ENTHUSIASTIC", "SANDCASTLE", "OFTEN",
    "CLASSICAL", "SATURDAY", "CELEBRITY", "MATERIAL", "EXCUSE ME", "AMERICAN",
    "DISHES", "HAPPINESS", "LAUNDROMAT", "SKIRT", "SNEAKERS", "COLORS",
    "ERASER", "RAINFOREST", "FLOOD", "VOLCANO",
]

# Remove duplicates and normalize
official_set = set()
for word in OFFICIAL_WORDS:
    official_set.add(word.lower())

print(f"Official word count (before dedup): {len(OFFICIAL_WORDS)}")
print(f"Official word count (after dedup): {len(official_set)}")

# Find duplicates in the original list
from collections import Counter
word_counts = Counter(w.lower() for w in OFFICIAL_WORDS)
duplicates = {w: c for w, c in word_counts.items() if c > 1}

if duplicates:
    print(f"\nDuplicates found in official list:")
    for word, count in sorted(duplicates.items()):
        print(f"  - {word}: {count} times")
else:
    print("\nNo duplicates in official list")

# Create the cleaned list (lowercase, sorted)
cleaned_list = sorted(list(official_set))

print(f"\nCleaned list ({len(cleaned_list)} unique words):")
print("=" * 60)

# Format as Python list for easy copy-paste
print("\nPython list format:")
print("[")
for i, word in enumerate(cleaned_list):
    if (i + 1) % 6 == 0:
        print(f'    "{word}",')
    else:
        print(f'    "{word}",', end=" ")
print("]")

# Write to file for reference
with open("tournament_words_cleaned.txt", "w") as f:
    f.write("CLEANED TOURNAMENT WORDS\n")
    f.write("=" * 60 + "\n")
    f.write(f"Total unique words: {len(cleaned_list)}\n\n")
    for i, word in enumerate(cleaned_list, 1):
        f.write(f"{i:3d}. {word}\n")
    if duplicates:
        f.write("\n\nDUPLICATES REMOVED:\n")
        for word, count in sorted(duplicates.items()):
            f.write(f"  - {word}: appeared {count} times\n")

print("\n✓ Cleaned list saved to tournament_words_cleaned.txt")
