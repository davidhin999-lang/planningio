#!/usr/bin/env python3
"""
Check audio status for ALL 194 tournament words (easy, medium, hard)
"""

import os
import sys

# ALL 194 tournament words from words.py
TOURNAMENT_WORDS = {
    "easy": [
        "address", "balloon", "bathroom", "bedroom", "boring", "bowling",
        "brown", "castle", "children", "church", "climbing", "clumsy",
        "colors", "cupboard", "cycling", "daughter", "dishes", "dolphin",
        "eagle", "easily", "factory", "february", "fence", "fishing",
        "flood", "fruits", "handles", "jacket", "jungle", "keyboard",
        "library", "loudly", "monkey", "museum", "noodles", "often",
        "pharmacy", "property", "quickly", "rainbow", "sailing", "scissors",
        "sea lion", "shopping", "shoulder", "skirt", "sneakers", "speaking",
        "stand up", "sweater", "swimming", "thailand", "theater", "thursday",
        "tiring", "waitress", "warming", "warning", "weather", "whistle",
        "white",
    ],
    "medium": [
        "afternoon", "airplane", "amazing", "badminton", "beautiful", "believe",
        "bubble speech", "careful", "celebrity", "classical", "classmate", "consonants",
        "correction", "countable", "countryside", "delicious", "different", "dining room",
        "disgusting", "dislike", "down town", "earphones", "elephant", "engineer",
        "eraser", "evening", "festival", "friendship", "garage", "geography",
        "grandchildren", "granddaughter", "grandfather", "green point", "groceries", "guinea pig",
        "hairbrush", "hairdresser", "happiness", "holidays", "homework", "images",
        "instrument", "jelly fish", "knowledge", "languages", "laundromat", "lifestyle",
        "lunchtime", "material", "mountains", "necklace", "neighborhood", "newspaper",
        "notebook", "november", "octopus", "paintings", "prescription", "principal",
        "psychology", "questions", "rainforest", "remember", "sandcastle", "saturday",
        "scientist", "sentences", "sightseeing",
    ],
    "hard": [
        "american", "apostrophe", "businessman", "chocolate", "electrician", "enthusiastic",
        "everywhere", "excitement", "excuse me", "exercise", "expensive", "explanation",
        "fascinating", "fashionable", "fire fighter", "furniture", "household chores", "information",
        "interesting", "introducing", "irregular", "laboratory", "magazine", "medication",
        "medicine", "microwave oven", "movie theater", "nationality", "negociation", "office building",
        "opposite", "police officer", "post office", "recognize", "refrigerator", "responsibility",
        "sales assistant", "saxophone", "skateboarding", "snowboarding", "statements", "steering wheel",
        "stomachache", "strawberry", "supermarket", "surprising", "television", "thirty three",
        "tomatoes", "tomorrow", "toothbrush", "train station", "umbrella", "uncountable",
        "understand", "united kingdom", "vegetables", "videogames", "volcano", "volleyball",
        "waking up", "wednesday", "wheelchair", "workplace",
    ]
}

def check_all_tournament_audio():
    print("=" * 80)
    print("COMPLETE TOURNAMENT AUDIO STATUS - ALL 194 WORDS")
    print("=" * 80)
    
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    
    total_words = 0
    total_have_audio = 0
    total_missing_audio = 0
    
    for difficulty, words in TOURNAMENT_WORDS.items():
        have_audio = []
        missing_audio = []
        
        for word in words:
            total_words += 1
            safe_name = word.replace(" ", "_").lower()
            audio_path = os.path.join(audio_dir, f"{safe_name}.mp3")
            
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 500:
                have_audio.append(word)
                total_have_audio += 1
            else:
                missing_audio.append(word)
                total_missing_audio += 1
        
        print(f"\n{difficulty.upper()} LEVEL:")
        print(f"  Words with audio: {len(have_audio)}/{len(words)}")
        print(f"  Words missing audio: {len(missing_audio)}/{len(words)}")
        
        if have_audio:
            print(f"  Working: {', '.join(have_audio[:5])}")
            if len(have_audio) > 5:
                print(f"    ... and {len(have_audio) - 5} more")
        
        if missing_audio:
            print(f"  Missing: {', '.join(missing_audio[:5])}")
            if len(missing_audio) > 5:
                print(f"    ... and {len(missing_audio) - 5} more")
    
    print(f"\n" + "=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)
    print(f"Total tournament words: {total_words}")
    print(f"Words with audio: {total_have_audio} ({total_have_audio/total_words*100:.1f}%)")
    print(f"Words missing audio: {total_missing_audio} ({total_missing_audio/total_words*100:.1f}%)")
    
    if total_have_audio > total_missing_audio:
        print(f"\nGOOD: More words have audio than missing!")
    else:
        print(f"\nNEEDS WORK: More words missing audio than have audio.")
    
    print(f"\nWith robotic TTS disabled:")
    print(f"- {total_have_audio} words will work perfectly")
    print(f"- {total_missing_audio} words will be silent (no robotic audio)")
    
    return total_have_audio, total_missing_audio

if __name__ == "__main__":
    check_all_tournament_audio()
