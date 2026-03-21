import re

# Final deduplicated tournament word list (164 words, all lowercase)
TOURNAMENT_WORDS = [
    "address", "information", "apostrophe", "instrument", "badminton", "interesting",
    "balloon", "introducing", "beautiful", "jacket", "bedroom", "jungle",
    "believe", "keyboard", "businessman", "knowledge", "groceries", "laboratory",
    "castle", "languages", "children", "library", "chocolate", "lifestyle",
    "climbing", "lunchtime", "countryside", "magazine", "cupboard", "medicine",
    "cycling", "microwave oven", "daughter", "monkey", "delicious", "mountains",
    "different", "museum", "dining room", "nationality", "disgusting", "necklace",
    "dolphin", "neighborhood", "down town", "newspaper", "earphones", "notebook",
    "electrician", "office building", "elephant", "opposite", "engineer", "pharmacy",
    "evening", "post office", "expensive", "principal", "exercise", "property",
    "factory", "psychology", "fashionable", "questions", "february", "rainbow",
    "fire fighter", "recognize", "friendship", "refrigerator", "furniture", "remember",
    "granddaughter", "sales assistant", "hairdresser", "saxophone", "homework", "scissors",
    "sentences", "green point", "shopping", "images", "shoulder", "bathroom",
    "skateboarding", "noodles", "snowboarding", "handles", "speaking", "boring",
    "bubble speech", "amazing", "statements", "dislike", "stomachache", "explanation",
    "strawberry", "everywhere", "supermarket", "quickly", "surprising", "tiring",
    "swimming", "wheelchair", "television", "holidays", "thailand", "uncountable",
    "theater", "sweater", "tomatoes", "easily", "tomorrow", "irregular",
    "toothbrush", "negociation", "train station", "prescription", "umbrella", "responsibility",
    "understand", "medication", "united kingdom", "eagle", "vegetables", "classmate",
    "videogames", "volleyball", "waitress", "countable", "warning", "church",
    "weather", "thursday", "wednesday", "consonants", "steering wheel", "sailing",
    "whistle", "sightseeing", "warming", "household chores", "scientist", "clumsy",
    "police officer", "fishing", "thirty three", "workplace", "movie theater", "festival",
    "grandfather", "stand up", "guinea pig", "correction", "fascinating", "grandchildren",
    "careful", "hairbrush", "november", "waking up", "excitement", "airplane",
    "bowling", "geography",
]

print(f"Total tournament words: {len(TOURNAMENT_WORDS)}")

with open('words.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Build the words list as a Python string block
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

lines = []
for chunk in chunks(TOURNAMENT_WORDS, 6):
    quoted = [f'"{w}"' for w in chunk]
    lines.append('                ' + ', '.join(quoted) + ',')

words_block = '\n'.join(lines)

# Replace the tournament config section
old_tournament = '''"tournament": {
        "label": "Tournament",
        "ranked_week": 1,
        # Uses global word lists (no override)
    },'''

new_tournament = f'''"tournament": {{
        "label": "Tournament",
        "ranked_week": 1,
        "words": {{
            "easy": [
{words_block}
            ],
            "medium": [],
            "hard": [],
        }},
    }},'''

if old_tournament in content:
    content = content.replace(old_tournament, new_tournament)
    with open('words.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS: Tournament words updated in words.py")
else:
    print("ERROR: Could not find tournament config block")
    idx = content.find('"tournament"')
    if idx != -1:
        print("Found at:", idx)
        print(repr(content[idx:idx+200]))
