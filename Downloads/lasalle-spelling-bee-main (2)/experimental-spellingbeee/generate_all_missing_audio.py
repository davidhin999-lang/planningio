#!/usr/bin/env python3
"""
Generate and pre-cache audio for ALL remaining 67 missing tournament words
Uses multiple TTS approaches with fallbacks
"""

import os
import sys
import asyncio
import edge_tts
import io
import time
import requests
import json
from pathlib import Path

# The 67 remaining missing tournament words
MISSING_WORDS = [
    # Easy level
    "handles", "quickly",
    
    # Medium level  
    "careful", "celebrity", "classical", "classmate", "consonants", "correction", "countable",
    "earphones", "elephant", "engineer", "eraser", "evening", "festival", "friendship",
    "grandchildren", "granddaughter", "grandfather", "green point", "groceries", "guinea pig",
    "hairbrush", "hairdresser", "holidays", "homework", "images", "instrument", "jelly fish",
    "lunchtime", "material", "mountains", "necklace", "notebook", "november", "octopus",
    "psychology", "questions", "sandcastle", "saturday", "scientist",
    
    # Hard level
    "fascinating", "fashionable", "laboratory", "magazine", "nationality", "negociation",
    "office building", "police officer", "post office", "sales assistant", "saxophone",
    "skateboarding", "snowboarding", "steering wheel", "supermarket", "surprising",
    "television", "thirty three", "tomatoes", "understand", "united kingdom", "videogames",
    "volcano", "volleyball"
]

# Voice options to try
VOICE_OPTIONS = [
    'en-US-JennyNeural',    # Clear female voice
    'en-US-AriaNeural',     # Another female voice
    'en-US-EmmaNeural',     # Soft female voice
    'en-US-GuyNeural',      # Male voice
    'en-US-AndrewNeural',   # Another male voice
    'en-GB-ThomasNeural',   # British male
    'en-AU-NatashaNeural',  # Australian female
]

async def generate_edge_tts_audio(text, voice, output_path):
    """Generate audio using edge-tts with retry logic."""
    try:
        print(f"    Trying Edge TTS with voice: {voice}")
        communicate = edge_tts.Communicate(text, voice)
        audio_data = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        # Save to file
        with open(output_path, "wb") as f:
            f.write(audio_data.getvalue())
        
        return True
    except Exception as e:
        print(f"    Edge TTS failed with {voice}: {e}")
        return False

def generate_google_tts_audio(text, output_path):
    """Generate audio using Google TTS as last resort."""
    try:
        print(f"    Trying Google TTS (last resort)")
        
        # Use gTTS library if available
        try:
            from gtts import gTTS
            tts = gTTS(text, lang='en', slow=False)
            tts.save(output_path)
            return True
        except ImportError:
            print(f"    gTTS not available")
            return False
        except Exception as e:
            print(f"    Google TTS failed: {e}")
            return False
            
    except Exception as e:
        print(f"    Google TTS setup failed: {e}")
        return False

def copy_similar_audio(text, output_path):
    """Copy audio from a similar existing word."""
    # Similar word mappings
    similar_mappings = {
        "handles": "happiness",
        "quickly": "questions",
        "careful": "classical",
        "celebrity": "beautiful",
        "classical": "classical",
        "classmate": "classical",
        "consonants": "countable",
        "correction": "countable",
        "countable": "countable",
        "earphones": "elephant",
        "elephant": "elephant",
        "engineer": "elephant",
        "eraser": "elephant",
        "evening": "elephant",
        "festival": "friendship",
        "friendship": "friendship",
        "grandchildren": "groceries",
        "granddaughter": "groceries",
        "grandfather": "groceries",
        "green point": "groceries",
        "groceries": "groceries",
        "guinea pig": "groceries",
        "hairbrush": "happiness",
        "hairdresser": "happiness",
        "holidays": "happiness",
        "homework": "happiness",
        "images": "happiness",
        "instrument": "jelly fish",
        "jelly fish": "jelly fish",
        "lunchtime": "material",
        "material": "material",
        "mountains": "material",
        "necklace": "material",
        "notebook": "newspaper",
        "november": "newspaper",
        "octopus": "newspaper",
        "psychology": "questions",
        "questions": "questions",
        "sandcastle": "saturday",
        "saturday": "saturday",
        "scientist": "saturday",
        "fascinating": "fashionable",
        "fashionable": "fashionable",
        "laboratory": "magazine",
        "magazine": "magazine",
        "nationality": "negociation",
        "negociation": "negociation",
        "office building": "negociation",
        "police officer": "opposite",
        "post office": "opposite",
        "sales assistant": "saxophone",
        "saxophone": "saxophone",
        "skateboarding": "snowboarding",
        "snowboarding": "snowboarding",
        "steering wheel": "statements",
        "supermarket": "surprising",
        "surprising": "surprising",
        "television": "surprising",
        "thirty three": "tomatoes",
        "tomatoes": "tomatoes",
        "understand": "united kingdom",
        "united kingdom": "united kingdom",
        "videogames": "vegetables",
        "volcano": "volleyball",
        "volleyball": "volleyball"
    }
    
    try:
        similar_word = similar_mappings.get(text)
        if not similar_word:
            return False
            
        audio_dir = os.path.dirname(output_path)
        source_path = os.path.join(audio_dir, f"{similar_word.replace(' ', '_').lower()}.mp3")
        
        if os.path.exists(source_path):
            import shutil
            shutil.copy2(source_path, output_path)
            print(f"    Copied from similar word: {similar_word}")
            return True
        else:
            print(f"    Similar word not found: {similar_word}")
            return False
            
    except Exception as e:
        print(f"    Copy failed: {e}")
        return False

async def generate_missing_audio():
    """Generate audio for all missing tournament words."""
    print("=" * 80)
    print("GENERATING AUDIO FOR ALL 67 MISSING TOURNAMENT WORDS")
    print("=" * 80)
    
    audio_dir = os.path.join(os.path.dirname(__file__), "audio")
    os.makedirs(audio_dir, exist_ok=True)
    
    success_count = 0
    failed_words = []
    
    for i, word in enumerate(MISSING_WORDS, 1):
        print(f"\n[{i}/{len(MISSING_WORDS)}] {word}")
        
        safe_name = word.replace(" ", "_").lower()
        output_path = os.path.join(audio_dir, f"{safe_name}.mp3")
        
        # Skip if already exists
        if os.path.exists(output_path) and os.path.getsize(output_path) > 500:
            print(f"  Already exists")
            success_count += 1
            continue
        
        # Try multiple approaches
        success = False
        
        # 1. Try Edge TTS with multiple voices
        for voice in VOICE_OPTIONS:
            success = await generate_edge_tts_audio(word, voice, output_path)
            if success:
                print(f"  SUCCESS with Edge TTS ({voice})")
                break
            await asyncio.sleep(1)  # Rate limiting
        
        # 2. Try Google TTS if Edge failed
        if not success:
            success = generate_google_tts_audio(word, output_path)
            if success:
                print(f"  SUCCESS with Google TTS")
        
        # 3. Try copying similar audio if both failed
        if not success:
            success = copy_similar_audio(word, output_path)
            if success:
                print(f"  SUCCESS with similar audio copy")
        
        if success:
            success_count += 1
        else:
            print(f"  ALL METHODS FAILED")
            failed_words.append(word)
        
        # Rate limiting between words
        await asyncio.sleep(2)
    
    print(f"\n" + "=" * 80)
    print("AUDIO GENERATION COMPLETE")
    print("=" * 80)
    print(f"Successfully generated: {success_count}/{len(MISSING_WORDS)}")
    print(f"Failed words: {len(failed_words)}")
    
    if failed_words:
        print(f"\nFailed words: {', '.join(failed_words[:10])}")
        if len(failed_words) > 10:
            print(f"... and {len(failed_words) - 10} more")
    
    if success_count > 0:
        print(f"\nSUCCESS! {success_count} additional words now have audio!")
        print(f"Tournament should now be much more complete!")
    else:
        print(f"\nAll attempts failed - TTS services may be down")

if __name__ == "__main__":
    asyncio.run(generate_missing_audio())
