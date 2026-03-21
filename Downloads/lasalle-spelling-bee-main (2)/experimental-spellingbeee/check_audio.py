#!/usr/bin/env python3

import os

# Get all existing audio files (base names without extensions)
audio_dir = "audio"
existing_audio = set()

if os.path.exists(audio_dir):
    for filename in os.listdir(audio_dir):
        if filename.endswith('.mp3'):
            # Remove the _sentence, _slow, _spell suffixes to get base word
            base = filename.replace('.mp3', '')
            base = base.replace('_sentence', '').replace('_slow', '').replace('_spell', '')
            existing_audio.add(base)

# Group 3 words that need audio
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

def find_missing_audio(words, difficulty):
    """Find words that need audio generation"""
    missing = []
    existing = []
    
    for word in words:
        # Convert spaces to underscores for filename matching
        word_filename = word.replace(' ', '_').lower()
        if word_filename in existing_audio:
            existing.append(word)
        else:
            missing.append(word)
    
    return missing, existing

# Check each difficulty level
easy_missing, easy_existing = find_missing_audio(group3_easy, "easy")
medium_missing, medium_existing = find_missing_audio(group3_medium, "medium")  
hard_missing, hard_existing = find_missing_audio(group3_hard, "hard")

print("=== GROUP 3 AUDIO ANALYSIS ===\n")
print(f"EASY LEVEL:")
print(f"  Words needing audio: {len(easy_missing)}")
print(f"  Words with existing audio: {len(easy_existing)}")
if easy_missing:
    print(f"  Missing audio: {', '.join(easy_missing[:10])}{'...' if len(easy_missing) > 10 else ''}")
print()

print(f"MEDIUM LEVEL:")
print(f"  Words needing audio: {len(medium_missing)}")
print(f"  Words with existing audio: {len(medium_existing)}")
if medium_missing:
    print(f"  Missing audio: {', '.join(medium_missing[:10])}{'...' if len(medium_missing) > 10 else ''}")
print()

print(f"HARD LEVEL:")
print(f"  Words needing audio: {len(hard_missing)}")
print(f"  Words with existing audio: {len(hard_existing)}")
if hard_missing:
    print(f"  Missing audio: {', '.join(hard_missing[:10])}{'...' if len(hard_missing) > 10 else ''}")
print()

# Overall totals
total_missing = len(easy_missing) + len(medium_missing) + len(hard_missing)
total_existing = len(easy_existing) + len(medium_existing) + len(hard_existing)
total_words = total_missing + total_existing

print("=== OVERALL TOTALS ===")
print(f"Total words in Group 3: {total_words}")
print(f"Words needing new audio: {total_missing}")
print(f"Words with existing audio: {total_existing}")
print(f"Percentage with existing audio: {(total_existing/total_words)*100:.1f}%")

# Generate list of all words needing audio
all_missing = easy_missing + medium_missing + hard_missing
if all_missing:
    print(f"\n=== ALL WORDS NEEDING AUDIO ===")
    for word in sorted(all_missing):
        print(f"  {word}")
