import sys
sys.path.insert(0, '.')
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, GROUP_CONFIG

# New word list (168 words, some duplicates in input)
new_words_raw = [
    "ADDRESS", "INFORMATION", "APOSTROPHE", "INSTRUMENT", "BADMINTON", "INTERESTING",
    "BALLOON", "INTRODUCING", "BEAUTIFUL", "JACKET", "BEDROOM", "JUNGLE",
    "BELIEVE", "KEYBOARD", "BUSINESSMAN", "KNOWLEDGE", "GROCERIES", "LABORATORY",
    "CASTLE", "LANGUAGES", "CHILDREN", "LIBRARY", "CHOCOLATE", "LIFESTYLE",
    "CLIMBING", "LUNCHTIME", "COUNTRYSIDE", "MAGAZINE", "CUPBOARD", "MEDICINE",
    "CYCLING", "MICROWAVE OVEN", "DAUGHTER", "MONKEY", "DELICIOUS", "MOUNTAINS",
    "DIFFERENT", "MUSEUM", "DINING ROOM", "NATIONALITY", "DISGUSTING", "NECKLACE",
    "DOLPHIN", "NEIGHBORHOOD", "DOWN TOWN", "NEWSPAPER", "EARPHONES", "NOTEBOOK",
    "ELECTRICIAN", "OFFICE BUILDING", "ELEPHANT", "OPPOSITE", "ENGINEER", "PHARMACY",
    "EVENING", "POST OFFICE", "EXPENSIVE", "PRINCIPAL", "EXERCISE", "PROPERTY",
    "FACTORY", "PSYCHOLOGY", "FASHIONABLE", "QUESTIONS", "FEBRUARY", "RAINBOW",
    "FIRE FIGHTER", "RECOGNIZE", "FRIENDSHIP", "REFRIGERATOR", "FURNITURE", "REMEMBER",
    "GRANDDAUGHTER", "SALES ASSISTANT", "HAIRDRESSER", "SAXOPHONE", "HOMEWORK", "SCISSORS",
    "SENTENCES", "GREEN POINT", "SHOPPING", "IMAGES", "SHOULDER", "BATHROOM",
    "SKATEBOARDING", "NOODLES", "SNOWBOARDING", "HANDLES", "SPEAKING", "BORING",
    "BUBBLE SPEECH", "AMAZING", "STATEMENTS", "DISLIKE", "STOMACHACHE", "EXPLANATION",
    "STRAWBERRY", "EVERYWHERE", "SUPERMARKET", "QUICKLY", "SURPRISING", "TIRING",
    "SWIMMING", "WHEELCHAIR", "TELEVISION", "HOLIDAYS", "THAILAND", "UNCOUNTABLE",
    "THEATER", "SWEATER", "TOMATOES", "EASILY", "TOMORROW", "IRREGULAR",
    "TOOTHBRUSH", "NEGOCIATION", "TRAIN STATION", "PRESCRIPTION", "UMBRELLA", "RESPONSIBILITY",
    "UNDERSTAND", "MEDICATION", "UNITED KINGDOM", "EAGLE", "VEGETABLES", "CLASSMATE",
    "VIDEOGAMES", "VOLLEYBALL", "WAITRESS", "COUNTABLE", "WARNING", "CHURCH",
    "WEATHER", "THURSDAY", "WEDNESDAY", "CONSONANTS", "STEERING WHEEL", "SAILING",
    "WHISTLE", "SIGHTSEEING", "WARMING", "HOUSEHOLD CHORES", "SCIENTIST", "CLUMSY",
    "POLICE OFFICER", "FISHING", "THIRTY THREE", "WORKPLACE", "MOVIE THEATER", "FESTIVAL",
    "GRANDFATHER", "STAND UP", "GUINEA PIG", "CORRECTION", "FASCINATING", "WORKPLACE",
    "GRANDCHILDREN", "CAREFUL", "HAIRBRUSH", "NOVEMBER", "WAKING UP", "EXCITEMENT",
    "AIRPLANE", "BOWLING", "LIBRARY", "GEOGRAPHY", "EXPLANATION",
]

# Deduplicate preserving order (case-insensitive)
seen = set()
new_words_deduped = []
for w in new_words_raw:
    key = w.lower().strip()
    if key not in seen:
        seen.add(key)
        new_words_deduped.append(w.lower().strip())

print(f"Raw input count: {len(new_words_raw)}")
print(f"After deduplication: {len(new_words_deduped)}")

# Build set of all existing global words (lowercase)
existing = set()
for w in EASY_WORDS + MEDIUM_WORDS + HARD_WORDS:
    existing.add(w.lower().strip())

# Also check group3 and other groups
for grp, cfg in GROUP_CONFIG.items():
    words = cfg.get('words', {})
    for tier in ['easy', 'medium', 'hard']:
        for w in words.get(tier, []):
            existing.add(w.lower().strip())

already_in = [w for w in new_words_deduped if w in existing]
brand_new = [w for w in new_words_deduped if w not in existing]

print(f"\nAlready in existing lists ({len(already_in)}):")
for w in sorted(already_in):
    print(f"  {w}")

print(f"\nBrand new words ({len(brand_new)}):")
for w in sorted(brand_new):
    print(f"  {w}")

print(f"\nTotal unique words for tournament: {len(new_words_deduped)}")
