#!/usr/bin/env python3
"""
Check which tournament words have existing audio files
"""

import os
import sys

# Tournament words that need checking
TOURNAMENT_WORDS = [
    "balloon", "airplane", "amazing", "american", "badminton",
    "bathroom", "bedroom", "boring", "bowling", "brown",
    "castle", "children", "church", "climbing", "clumsy",
    "colors", "cupboard", "cycling", "daughter", "dishes",
    "dolphin", "eagle", "easily", "factory", "february",
    "fence", "fishing", "flood", "fruits", "handles",
    "jacket", "jungle", "keyboard", "library", "loudly",
    "monkey", "museum", "noodles", "often", "pharmacy",
    "property", "quickly", "rainbow", "sailing", "scissors",
    "sea lion", "shopping", "shoulder", "skirt", "sneakers",
    "speaking", "stand up", "sweater", "swimming", "thailand",
    "theater", "thursday", "tiring", "waitress", "warming",
    "warning", "weather", "whistle", "white"
]

def check_tournament_audio():
    print("=" * 80)
    print("TOURNAMENT WORDS AUDIO STATUS")
    print("=" * 80)
    
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    
    have_audio = []
    missing_audio = []
    
    for word in TOURNAMENT_WORDS:
        safe_name = word.replace(" ", "_").lower()
        audio_path = os.path.join(audio_dir, f"{safe_name}.mp3")
        
        if os.path.exists(audio_path) and os.path.getsize(audio_path) > 500:
            have_audio.append(word)
        else:
            missing_audio.append(word)
    
    print(f"Words with audio: {len(have_audio)}")
    print(f"Words missing audio: {len(missing_audio)}")
    
    print(f"\nWORDS WITH AUDIO (will work):")
    for word in have_audio[:10]:  # Show first 10
        print(f"  {word}")
    if len(have_audio) > 10:
        print(f"  ... and {len(have_audio) - 10} more")
    
    print(f"\nWORDS MISSING AUDIO (will show error):")
    for word in missing_audio[:10]:  # Show first 10
        print(f"  {word}")
    if len(missing_audio) > 10:
        print(f"  ... and {len(missing_audio) - 10} more")
    
    print(f"\nSUMMARY:")
    print(f"- {len(have_audio)} words will work with natural audio")
    print(f"- {len(missing_audio)} words will show error (better than robotic)")
    print(f"- Total tournament words: {len(TOURNAMENT_WORDS)}")
    
    if len(have_audio) > len(missing_audio):
        print(f"\nGOOD: More words have audio than missing!")
        print(f"Tournament should be mostly functional with natural audio.")
    else:
        print(f"\nNEEDS WORK: More words missing audio than have audio.")
    
    return have_audio, missing_audio

if __name__ == "__main__":
    check_tournament_audio()
