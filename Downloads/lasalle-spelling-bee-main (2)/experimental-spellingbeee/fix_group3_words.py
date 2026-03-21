#!/usr/bin/env python3

# Original list provided by user - about 240 unique words
user_words = [
    "ADVENTURE", "EDUCATION", "CHALLENGE", "EXCELLENT", "IMPORTANT",
    "COMPREHENSION", "CHARACTER", "CONTINUOUS", "SPEAKING", "ACKNOWLEDGEMENT",
    "HEADACHE", "MARATHON", "STOMACHACHE", "SENTENCES", "CHOCOLATE",
    "STATEMENTS", "POSSIBILITIES", "ACHIEVEMENTS", "ENTERTAINMENT", "BEAUTIFULLY",
    "EXPENSIVE", "ENTHUSIASTIC", "COURAGEOUSLY", "KINDNESS", "SWIMMING",
    "VOCABULARY", "COMPLETELY", "IMMEDIATELY", "DESCRIPTIONS", "LUGGAGE",
    "APARTMENT", "DIFFERENCE", "MOUNTAINOUS", "DELICIOUS", "SUGGESTIONS",
    "ENGINEERING", "APPLICATION", "SURPRISINGLY", "STRESSFUL", "CONFUSING",
    "EFFECTIVELY", "METHODOLOGY", "DISTRACTION", "TEMPERATURE", "RESOLUTIONS",
    "CORKSCREW", "STRAWBERRY", "CHAMPIONSHIP", "HEADPHONES", "APPOINTMENT",
    "PRESCRIPTION", "FRIENDSHIP", "NEIGHBORHOOD", "CHOPPING BOARD", "SCREWDRIVER",
    "WOODEN SPOON", "ROMANTICISM", "UNDERSTANDING", "FACILITIES", "INFORMATION",
    "VEGETABLES", "BOTTLE OPENER", "PHILOSOPHY", "PRESENTATIONS", "DISTRIBUTION",
    "RELATIONSHIP", "UNSTOPPABLE", "REVOLUTIONARY", "EFFECTIVENESS", "MONITORING",
    "ETERNITY", "EQUALITY", "UNFORGETTABLE", "WEDNESDAY", "CONDITIONS",
    "FEELINGS", "INTERESTING", "SCIENTIFICALLY", "COMPARATIVE", "DANGEROUS",
    "RAINFOREST", "GRANDPARENTS", "CIVILIZATION", "KNUCKLES", "QUESTIONING",
    "HYPERVITAMINOSIS", "LIGHTNING", "APPREHENSIVE", "COMPREHENSIVE", "CATASTROPHIC",
    "COMMUNICATION", "EXTRAORDINARY", "WINDSURFING", "NEVERTHELESS", "SIGHTSEEING",
    "THROUGHOUT", "BEGINNING", "DISAPPOINTING", "TOOTHACHE", "WASHING MACHINE",
    "FREEZING", "PARAGLIDING", "COUNTRYSIDE", "GEOGRAPHY", "SNORKELING",
    "CHEESECAKE", "EXHIBITION", "DOCUMENTARY", "COMFORTABLE", "ARCHITECTURE",
    "CONSECUTIVELY", "KNOWLEDGE", "ENCYCLOPEDIA", "SKYSCRAPERS", "HYPERTHYROIDISM",
    "INVESTIGATION", "EARTHQUAKE", "MISCHIEVOUS", "WEEKLY PLANNER", "MOVIE THEATER",
    "THRILLING", "CHINATOWN", "INDEPENDENTLY", "FURTHER", "BUNGEE JUMPING",
    "HOUSEHOLD CHORES", "HOUSEWARES", "BIRTHDAY PARTY", "INTERNATIONAL", "TRANSNATIONAL",
    "INTRODUCING", "STUDYING", "KITESURFING", "PARTICIPLES", "UNDER PRESSURE",
    "SHOPPING BAG", "PAPERLESS", "CHICKEN WINGS", "DECORATIONS", "INTERNATIONALLY",
    "SUSTAINABILITY", "ICE HOCKEY", "DESSERTS", "REFRIGERATOR", "DECISIONS",
    "WEATHER", "EXCITEMENT", "MESSAGES", "PREDICTIONS", "CHILDHOOD",
    "APPARENTLY", "HARD-WORKING", "EXAMINATION", "CORRECTLY", "MANAGEMENT",
    "SHOPPING CENTER", "EXPERIENCE", "FEATURES", "ACQUIRING", "EQUIPMENT",
    "SUCCESSFULLY", "UNDERSTANDABLE", "FOOD COURT", "TECHNICIAN", "TECHNOLOGY",
    "CONSCIOUSLY", "INTERRUPTION", "POSSESSIONS", "BELONGINGS", "EXPRESSION",
    "CONTAINING", "APPRECIATION", "SIGNIFICANCE", "INVOLVING", "CONSIDERATION",
    "ACCOMPLISHMENTS", "ADMIRATION MARK", "ASTRONOMICAL", "ECONOMICALLY", "EXPLORATION",
    "HARMONIOUS", "SATISFACTION", "ASSOCIATION", "POTENTIALLY", "CIRCUMSTANCES",
    "OVERWHELMING", "APPROPRIATE", "PHENOMENON", "IMAGINATION", "LITERATURE",
    "COMBINATION", "EXTREMELY", "ADMINISTRATION", "LINGUISTICS", "TERRIFYING",
    "MICROWAVE OVEN", "LANGUAGES", "COLLEAGUES", "BREAKFAST", "ARRANGEMENTS",
    "MEDITERRANEAN", "GIRLFRIEND", "MEDICATION", "HOPEFULLY", "COMPETITION",
    "ANIMATION", "WORKAHOLIC", "ALCOHOLISM", "RESILIENCE", "MUSICIAN",
    "AMBITIOUS", "CROCODILE", "CHRISTMAS TREE", "CREATION", "UNIVERSITY",
    "APPLYING", "THEMATICAL", "DICTIONARY", "DEFINITION", "AGREEMENT",
    "ATTENTION", "AVAILABILITY", "AUTHORITY", "BUSINESSMAN", "SALESPERSON",
    "EMPLOYMENT", "RIDICULOUS", "COMMITMENT", "IMMIGRATION", "UNITED STATES",
    "CONSOLIDATION", "DERMATOLOGIST", "POLITICIAN", "MODERNIZATION", "HYPERTENSION",
    "COMPUTER ROOM", "BUTTERFLY", "GRATEFUL", "FOLLOWING", "INDIRECTLY"
]

# Convert to lowercase and remove duplicates
unique_words = list(set([word.lower().strip() for word in user_words]))
unique_words.sort()

print(f"Original words provided: {len(user_words)}")
print(f"Unique words after deduplication: {len(unique_words)}")

# Now categorize by difficulty based on word characteristics
def categorize_word(word):
    length = len(word.replace(' ', ''))
    syllables = word.count('aeiou') + word.count('y')  # rough estimate
    
    # Easy: short words (1-2 syllables, 6-8 chars)
    if length <= 8 and syllables <= 2:
        return 'easy'
    # Hard: long words (3+ syllables, 10+ chars) or complex patterns
    elif length >= 10 or syllables >= 3 or any(x in word for x in ['tion', 'sion', 'ment', 'ness', 'ity']):
        return 'hard'
    # Medium: everything else
    else:
        return 'medium'

easy_words = []
medium_words = []
hard_words = []

for word in unique_words:
    category = categorize_word(word)
    if category == 'easy':
        easy_words.append(word)
    elif category == 'medium':
        medium_words.append(word)
    else:
        hard_words.append(word)

print(f"\nCategorized as:")
print(f"Easy: {len(easy_words)} words")
print(f"Medium: {len(medium_words)} words")
print(f"Hard: {len(hard_words)} words")
print(f"Total: {len(easy_words) + len(medium_words) + len(hard_words)} words")

print(f"\n=== EASY WORDS ===")
print(', '.join(easy_words[:20]) + ('...' if len(easy_words) > 20 else ''))

print(f"\n=== MEDIUM WORDS ===")
print(', '.join(medium_words[:20]) + ('...' if len(medium_words) > 20 else ''))

print(f"\n=== HARD WORDS ===")
print(', '.join(hard_words[:20]) + ('...' if len(hard_words) > 20 else ''))
