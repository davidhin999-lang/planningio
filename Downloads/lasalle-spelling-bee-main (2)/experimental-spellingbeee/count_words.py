#!/usr/bin/env python3

# Count the words I actually added to Group 3
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

print("=== WORD COUNT ANALYSIS ===")
print(f"Easy: {len(group3_easy)} words")
print(f"Medium: {len(group3_medium)} words") 
print(f"Hard: {len(group3_hard)} words")
print(f"Total: {len(group3_easy) + len(group3_medium) + len(group3_hard)} words")

# Check for duplicates across levels
all_words = group3_easy + group3_medium + group3_hard
unique_words = set(all_words)
duplicates = len(all_words) - len(unique_words)

print(f"\nUnique words: {len(unique_words)}")
print(f"Duplicates across levels: {duplicates}")

if duplicates > 0:
    print("\nDuplicate words found:")
    from collections import Counter
    word_counts = Counter(all_words)
    for word, count in word_counts.items():
        if count > 1:
            print(f"  '{word}' appears {count} times")
