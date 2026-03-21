#!/usr/bin/env python3

# Extract words from the original lists
original_easy = [
    "queue", "email", "autumn", "minute", "castle",
    "doctor", "family", "bakery", "centre", "believe",
    "airport", "camping", "already", "foreign", "further",
    "library", "luggage", "address", "biscuit", "business",
    "grateful", "freezing", "features", "headache", "medicine",
    "accident", "ambitious", "ambulance", "animation", "adventure",
    "agreement", "attention", "authority", "beautiful", "beginning",
    "challenge", "character", "chocolate", "certainly", "confusing",
    "correctly", "dangerous", "decisions", "delicious", "desserts",
    "education", "equipment", "eternity", "excellent", "expensive",
    "following", "furniture", "geography", "knowledge", "languages",
    "lightning", "marathon", "necessary", "opposite", "sentences",
    "stressful", "thrilling", "toothache", "wednesday",
    "involving", "acquiring", "applying", "paperless", "terrifying",
    "contained", "corkscrew", "extremely", "hopefully", "sightseeing",
    "throughout", "vegetables", "vocabulary", "girlfriend", "headphones",
]

original_medium = [
    "achieving", "apparently", "appreciate", "belongings", "beautifully",
    "businessman", "catastrophic", "championship", "cheesecake", "chinatown",
    "colleagues", "combination", "comfortable", "commitment", "comparative",
    "competition", "completely", "conditions", "containing", "countryside",
    "definition", "difference", "distraction", "earthquake", "employment",
    "expression", "experience", "exhibition", "excitement", "facilities",
    "hardworking", "harmonious", "housewares", "imagination", "immigration",
    "importance", "indirectly", "interesting", "introducing", "jewellery",
    "kilometre", "literature", "management", "medication", "monitoring",
    "mountainous", "mischievous", "modernization", "phenomenon", "philosophy",
    "politician", "possessions", "potentially", "predictions", "rainforest",
    "ridiculous", "salesperson", "snorkeling", "statements", "stomachache",
    "strawberry", "suggestions", "technician", "technology", "temperature",
    "university", "unstoppable", "windsurfing", "workaholic", "application",
    "appointment", "advertising", "aeroplane", "afterwards", "alcoholism",
    "arrangements", "association", "availability", "civilization", "documentary",
    "exploration", "information", "kitesurfing", "linguistics", "paragliding",
    "questioning", "romanticism", "satisfaction", "screwdriver", "significance",
]

original_hard = [
    "necessary", "occurrence", "accommodation", "embarrassment", "exaggerate",
    "conscience", "conscientious", "bureaucracy", "millennium", "questionnaire",
    "surveillance", "lieutenant", "miscellaneous", "perseverance", "privilege",
    "pronunciation", "rhythm", "silhouette", "supersede", "threshold",
    "acquaintance", "acknowledge", "colleague", "committee", "correspondence",
    "definitely", "dilemma", "disappear", "disappoint", "discipline",
    "environment", "especially", "exhilarate", "fluorescent", "foreign",
    "guarantee", "harass", "hierarchy", "immediately", "independent",
    "intelligence", "irrelevant", "knowledge", "maintenance", "manoeuvre",
    "miniature", "mischievous", "misspell", "neighbour",
    "noticeable", "occasion", "occurred", "parliament", "particularly",
    "perceive", "permanent", "personnel", "playwright", "possession",
    "precede", "prejudice", "principal", "procedure",
    "professor", "publicly", "receive", "recommend", "referred",
    "relevant", "restaurant", "rhyme", "schedule", "secretary",
    "separate", "sergeant", "sincerely", "successful", "sufficient",
    "surprise", "technique", "temperature", "thorough",
    "tomorrow", "transferred", "truly", "unfortunately", "unnecessary",
    "until", "usually", "vacuum", "vegetable", "Wednesday",
    "accomplishments", "achievements", "acknowledgement", "administration",
    "advertisement", "appreciation", "apprehensive", "appropriate",
    "architecture", "astronomical", "communication", "comprehension",
    "comprehensive", "circumstances", "consecutively",
    "consideration", "consolidation", "courageously", "continuously",
    "dermatologist", "disappointing", "distribution",
    "economically", "encyclopedia", "engineering",
    "entertainment", "enthusiastic", "examination",
    "extraordinary", "independently", "international",
    "interruption", "investigation", "neighborhood", "nevertheless",
    "overwhelming", "possibilities", "prescription",
    "presentations", "refrigerator", "relationship", "resolutions",
    "revolutionary", "scientifically", "successfully", "surprisingly",
    "transnational", "understandable", "understanding", "unforgettable",
    "mediterranean", "methodology",
]

original_phrases = [
    "food court", "ice hockey", "computer room", "movie theater",
    "shopping bag", "shopping center", "bottle opener", "bungee jumping",
    "chopping board", "microwave oven", "household chores", "united states",
    "washing machine", "weekly planner", "wooden spoon", "admiration mark",
]

# Group 3 words from the file
group3_easy = [
    "adventure", "education", "challenge", "excellent", "important",
    "headache", "marathon", "stomachache", "sentences", "chocolate",
    "statements", "luggage", "apartment", "delicious", "suggestions",
    "corkscrew", "strawberry", "championship", "headphones", "friendship",
    "neighborhood", "chopping board", "screwdriver", "wooden spoon", "bottle opener",
    "wednesday", "conditions", "feelings", "interesting", "knuckles",
    "lightning", "beginning", "disappointing", "toothache", "freezing",
    "thrilling", "further", "birthday party", "decorations", "desserts",
    "refrigerator", "decisions", "weather", "excitement", "messages",
    "predictions", "childhood", "breakfast", "butterfly", "grateful",
    "following", "christmas tree", "creation", "dictionary", "agreement",
    "attention", "availability", "authority", "ridiculous", "employment",
    "consolidation", "computer room", "indirectly"
]

group3_medium = [
    "comprehension", "character", "continuous", "speaking", "acknowledgement",
    "possibilities", "achievements", "entertainment", "beautifully", "expensive",
    "enthusiastic", "courageously", "kindness", "swimming", "vocabulary",
    "completely", "immediately", "descriptions", "difference", "mountainous",
    "engineering", "application", "surprisingly", "stressful", "confusing",
    "effectively", "methodology", "distraction", "temperature", "resolutions",
    "appointment", "prescription", "facilities", "information", "vegetables",
    "philosophy", "presentations", "distribution", "relationship", "unstoppable",
    "revolutionary", "effectiveness", "monitoring", "eternity", "equality",
    "unforgettable", "scientifically", "comparative", "dangerous", "rainforest",
    "grandparents", "civilization", "questioning", "hypervitaminosis", "apprehensive",
    "comprehensive", "catastrophic", "communication", "extraordinary", "windsurfing",
    "nevertheless", "sightseeing", "throughout", "washing machine", "paragliding",
    "countryside", "geography", "snorkeling", "cheesecake", "exhibition",
    "documentary", "comfortable", "architecture", "consecutively", "knowledge",
    "encyclopedia", "skyscrapers", "hyperthyroidism", "investigation", "earthquake",
    "mischievous", "weekly planner", "movie theater", "chinatown", "independently",
    "bungee jumping", "household chores", "housewares", "international", "transnational",
    "introducing", "studying", "kitesurfing", "participles", "under pressure",
    "shopping bag", "paperless", "chicken wings", "internationally", "sustainability",
    "ice hockey", "apparently", "hard-working", "examination", "correctly",
    "management", "shopping center", "experience", "features", "acquiring",
    "equipment", "successfully", "understandable", "food court", "technician",
    "technology", "consciously", "interruption", "possessions", "belongings",
    "expression", "containing", "appreciation", "significance", "involving",
    "consideration", "accomplishments", "admiration mark", "astronomical", "economically",
    "exploration", "harmonious", "satisfaction", "association", "potentially",
    "circumstances", "overwhelming", "appropriate", "phenomenon", "imagination",
    "literature", "combination", "extremely", "administration", "linguistics",
    "terrifying", "microwave oven", "languages", "colleagues", "arrangements",
    "mediterranean", "girlfriend", "medication", "hopefully", "competition",
    "animation", "workaholic", "alcoholism", "resilience", "musician",
    "ambitious", "crocodile", "university", "applying", "thematical",
    "definition", "businessman", "salesperson", "commitment", "immigration",
    "united states", "dermatologist", "politician", "modernization", "hypertension"
]

group3_hard = [
    "understanding", "romanticism", "effectiveness", "monitoring", "eternity",
    "equality", "unforgettable", "scientifically", "comparative", "dangerous",
    "rainforest", "grandparents", "civilization", "questioning", "hypervitaminosis",
    "apprehensive", "comprehensive", "catastrophic", "communication", "extraordinary",
    "windsurfing", "nevertheless", "sightseeing", "throughout", "beginning",
    "disappointing", "toothache", "washing machine", "freezing", "paragliding",
    "countryside", "geography", "snorkeling", "cheesecake", "exhibition",
    "documentary", "comfortable", "architecture", "consecutively", "knowledge",
    "encyclopedia", "skyscrapers", "hyperthyroidism", "investigation", "earthquake",
    "mischievous", "weekly planner", "movie theater", "thrilling", "chinatown",
    "independently", "further", "bungee jumping", "household chores", "housewares",
    "birthday party", "international", "transnational", "introducing", "studying",
    "kitesurfing", "participles", "under pressure", "shopping bag", "paperless",
    "chicken wings", "decorations", "internationally", "sustainability", "ice hockey",
    "desserts", "refrigerator", "decisions", "weather", "excitement",
    "messages", "predictions", "childhood", "apparently", "hard-working",
    "examination", "correctly", "management", "shopping center", "experience",
    "features", "acquiring", "equipment", "successfully", "understandable",
    "food court", "technician", "technology", "consciously", "interruption",
    "possessions", "belongings", "expression", "containing", "appreciation",
    "significance", "involving", "consideration", "accomplishments", "admiration mark",
    "astronomical", "economically", "exploration", "harmonious", "satisfaction",
    "association", "potentially", "circumstances", "overwhelming", "appropriate",
    "phenomenon", "imagination", "literature", "combination", "extremely",
    "administration", "linguistics", "terrifying", "microwave oven", "languages",
    "colleagues", "breakfast", "arrangements", "mediterranean", "girlfriend",
    "medication", "hopefully", "competition", "animation", "workaholic",
    "alcoholism", "resilience", "musician", "ambitious", "crocodile",
    "christmas tree", "creation", "university", "applying", "thematical",
    "dictionary", "definition", "agreement", "attention", "availability",
    "authority", "businessman", "salesperson", "employment", "ridiculous",
    "commitment", "immigration", "united states", "consolidation", "dermatologist",
    "politician", "modernization", "hypertension", "computer room", "butterfly",
    "grateful", "following", "indirectly"
]

def compare_lists(group_words, original_easy, original_medium, original_hard, original_phrases):
    """Compare group words with all original lists"""
    all_original = set(original_easy + original_medium + original_hard + original_phrases)
    group_set = set(group_words)
    
    # Words in group but not in original
    new_words = group_set - all_original
    # Words in both
    common_words = group_set & all_original
    
    return {
        'total_group_words': len(group_words),
        'new_words': sorted(list(new_words)),
        'common_words': sorted(list(common_words)),
        'new_count': len(new_words),
        'common_count': len(common_words)
    }

# Compare each difficulty level
easy_results = compare_lists(group3_easy, original_easy, original_medium, original_hard, original_phrases)
medium_results = compare_lists(group3_medium, original_easy, original_medium, original_hard, original_phrases)
hard_results = compare_lists(group3_hard, original_easy, original_medium, original_hard, original_phrases)

print("=== GROUP 3 WORDS COMPARISON ===\n")
print(f"EASY LEVEL:")
print(f"  Total words: {easy_results['total_group_words']}")
print(f"  New words (not in original): {easy_results['new_count']}")
print(f"  Common words (in original): {easy_results['common_count']}")
if easy_results['new_words']:
    print(f"  New words: {', '.join(easy_results['new_words'][:10])}{'...' if len(easy_results['new_words']) > 10 else ''}")
print()

print(f"MEDIUM LEVEL:")
print(f"  Total words: {medium_results['total_group_words']}")
print(f"  New words (not in original): {medium_results['new_count']}")
print(f"  Common words (in original): {medium_results['common_count']}")
if medium_results['new_words']:
    print(f"  New words: {', '.join(medium_results['new_words'][:10])}{'...' if len(medium_results['new_words']) > 10 else ''}")
print()

print(f"HARD LEVEL:")
print(f"  Total words: {hard_results['total_group_words']}")
print(f"  New words (not in original): {hard_results['new_count']}")
print(f"  Common words (in original): {hard_results['common_count']}")
if hard_results['new_words']:
    print(f"  New words: {', '.join(hard_results['new_words'][:10])}{'...' if len(hard_results['new_words']) > 10 else ''}")
print()

# Overall totals
total_group = easy_results['total_group_words'] + medium_results['total_group_words'] + hard_results['total_group_words']
total_new = easy_results['new_count'] + medium_results['new_count'] + hard_results['new_count']
total_common = easy_results['common_count'] + medium_results['common_count'] + hard_results['common_count']

print("=== OVERALL TOTALS ===")
print(f"Total words in Group 3: {total_group}")
print(f"Words NOT in original lists: {total_new}")
print(f"Words that were already in original: {total_common}")
print(f"Percentage of new words: {(total_new/total_group)*100:.1f}%")
