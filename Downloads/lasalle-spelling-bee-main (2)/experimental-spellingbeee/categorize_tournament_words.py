#!/usr/bin/env python3
"""
Categorize 194 tournament words into easy, medium, hard difficulty levels
and divide into weeks (30 words per week).
"""

# Official 194 tournament words (already deduplicated)
TOURNAMENT_WORDS = [
    "address", "afternoon", "airplane", "amazing", "american", "apostrophe",
    "badminton", "balloon", "bathroom", "beautiful", "bedroom", "believe",
    "boring", "bowling", "brown", "bubble speech", "businessman", "careful",
    "castle", "celebrity", "children", "chocolate", "church", "classical",
    "classmate", "climbing", "clumsy", "colors", "consonants", "correction",
    "countable", "countryside", "cupboard", "cycling", "daughter", "delicious",
    "different", "dining room", "disgusting", "dishes", "dislike", "dolphin",
    "down town", "eagle", "earphones", "easily", "electrician", "elephant",
    "engineer", "enthusiastic", "eraser", "evening", "everywhere", "excitement",
    "excuse me", "exercise", "expensive", "explanation", "factory", "fascinating",
    "fashionable", "february", "fence", "festival", "fire fighter", "fishing",
    "flood", "friendship", "fruits", "furniture", "garage", "geography",
    "grandchildren", "granddaughter", "grandfather", "green point", "groceries", "guinea pig",
    "hairbrush", "hairdresser", "handles", "happiness", "holidays", "homework",
    "household chores", "images", "information", "instrument", "interesting", "introducing",
    "irregular", "jacket", "jelly fish", "jungle", "keyboard", "knowledge",
    "laboratory", "languages", "laundromat", "library", "lifestyle", "loudly",
    "lunchtime", "magazine", "material", "medication", "medicine", "microwave oven",
    "monkey", "mountains", "movie theater", "museum", "nationality", "necklace",
    "negociation", "neighborhood", "newspaper", "noodles", "notebook", "november",
    "octopus", "office building", "often", "opposite", "paintings", "pharmacy",
    "police officer", "post office", "prescription", "principal", "property", "psychology",
    "questions", "quickly", "rainbow", "rainforest", "recognize", "refrigerator",
    "remember", "responsibility", "sailing", "sales assistant", "sandcastle", "saturday",
    "saxophone", "scientist", "scissors", "sea lion", "sentences", "shopping",
    "shoulder", "sightseeing", "skateboarding", "skirt", "sneakers", "snowboarding",
    "speaking", "stand up", "statements", "steering wheel", "stomachache", "strawberry",
    "supermarket", "surprising", "sweater", "swimming", "television", "thailand",
    "theater", "thirty three", "thursday", "tiring", "tomatoes", "tomorrow",
    "toothbrush", "train station", "umbrella", "uncountable", "understand", "united kingdom",
    "vegetables", "videogames", "volcano", "volleyball", "waitress", "waking up",
    "warming", "warning", "weather", "wednesday", "wheelchair", "whistle",
    "white", "workplace",
]

print(f"Total words: {len(TOURNAMENT_WORDS)}")

# Categorize by difficulty based on word length and complexity
# Easy: shorter, simpler words (1-2 syllables, common)
# Medium: medium length, moderate complexity (2-3 syllables)
# Hard: longer, more complex words (3+ syllables, less common)

EASY = []
MEDIUM = []
HARD = []

for word in TOURNAMENT_WORDS:
    # Count syllables (rough estimate: vowel groups)
    vowels = "aeiou"
    syllable_count = sum(1 for i, c in enumerate(word.lower()) 
                        if c in vowels and (i == 0 or word.lower()[i-1] not in vowels))
    
    word_len = len(word)
    
    # Categorize based on length and syllables
    if word_len <= 8 and syllable_count <= 2:
        EASY.append(word)
    elif word_len <= 14 and syllable_count <= 3:
        MEDIUM.append(word)
    else:
        HARD.append(word)

print(f"\nInitial categorization:")
print(f"  Easy: {len(EASY)}")
print(f"  Medium: {len(MEDIUM)}")
print(f"  Hard: {len(HARD)}")

# Balance the categories to be roughly equal
# Target: ~65 words per category
target = len(TOURNAMENT_WORDS) // 3

# Move words between categories to balance
while len(EASY) > target + 5:
    word = EASY.pop()
    MEDIUM.append(word)

while len(MEDIUM) > target + 5:
    word = MEDIUM.pop()
    HARD.append(word)

while len(HARD) > target + 5:
    word = HARD.pop()
    EASY.append(word)

# Sort each category alphabetically
EASY.sort()
MEDIUM.sort()
HARD.sort()

print(f"\nBalanced categorization:")
print(f"  Easy: {len(EASY)}")
print(f"  Medium: {len(MEDIUM)}")
print(f"  Hard: {len(HARD)}")
print(f"  Total: {len(EASY) + len(MEDIUM) + len(HARD)}")

# Divide into weeks (30 words per week)
WORDS_PER_WEEK = 30

def chunk_words(words, size):
    return [words[i:i+size] for i in range(0, len(words), size)]

easy_weeks = chunk_words(EASY, WORDS_PER_WEEK)
medium_weeks = chunk_words(MEDIUM, WORDS_PER_WEEK)
hard_weeks = chunk_words(HARD, WORDS_PER_WEEK)

print(f"\nWeeks:")
print(f"  Easy weeks: {len(easy_weeks)}")
print(f"  Medium weeks: {len(medium_weeks)}")
print(f"  Hard weeks: {len(hard_weeks)}")

# Output Python code format
print("\n" + "=" * 80)
print("PYTHON CODE FOR words.py")
print("=" * 80)

print('\n"tournament": {')
print('    "label": "Tournament",')
print('    "ranked_week": 1,')
print('    "words": {')
print('        "easy": [')
for i, word in enumerate(EASY):
    if (i + 1) % 6 == 0:
        print(f'            "{word}",')
    else:
        print(f'            "{word}",', end=" ")
print('        ],')
print('        "medium": [')
for i, word in enumerate(MEDIUM):
    if (i + 1) % 6 == 0:
        print(f'            "{word}",')
    else:
        print(f'            "{word}",', end=" ")
print('        ],')
print('        "hard": [')
for i, word in enumerate(HARD):
    if (i + 1) % 6 == 0:
        print(f'            "{word}",')
    else:
        print(f'            "{word}",', end=" ")
print('        ],')
print('    },')
print('},')

# Save to file for reference
with open("tournament_categorized.txt", "w") as f:
    f.write("TOURNAMENT WORDS - CATEGORIZED BY DIFFICULTY\n")
    f.write("=" * 80 + "\n\n")
    
    f.write(f"EASY ({len(EASY)} words, {len(easy_weeks)} weeks):\n")
    f.write("-" * 80 + "\n")
    for i, word in enumerate(EASY, 1):
        f.write(f"{i:3d}. {word}\n")
    
    f.write(f"\n\nMEDIUM ({len(MEDIUM)} words, {len(medium_weeks)} weeks):\n")
    f.write("-" * 80 + "\n")
    for i, word in enumerate(MEDIUM, 1):
        f.write(f"{i:3d}. {word}\n")
    
    f.write(f"\n\nHARD ({len(HARD)} words, {len(hard_weeks)} weeks):\n")
    f.write("-" * 80 + "\n")
    for i, word in enumerate(HARD, 1):
        f.write(f"{i:3d}. {word}\n")

print("\n\nSaved categorized list to tournament_categorized.txt")
