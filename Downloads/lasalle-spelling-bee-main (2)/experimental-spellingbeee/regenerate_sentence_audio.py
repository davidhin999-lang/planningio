#!/usr/bin/env python3
"""
Regenerate sentence audio for all 369 valid words using ElevenLabs (primary) or Edge TTS (fallback)
"""
import os
import sys
import time
import asyncio
import edge_tts
import io
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS, WORD_SENTENCES

VALID_WORDS = EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")

# ElevenLabs config
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

# Edge TTS voice
EDGE_VOICE = "en-US-JennyNeural"

def generate_elevenlabs_audio(text):
    """Generate audio using ElevenLabs API"""
    if not ELEVENLABS_API_KEY:
        return None
    
    try:
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        response = requests.post(ELEVENLABS_URL, json=data, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            print(f"    [ElevenLabs] Error {response.status_code}")
            return None
    except Exception as e:
        print(f"    [ElevenLabs] Error: {e}")
        return None

async def generate_edge_tts_audio(text):
    """Generate audio using Edge TTS"""
    try:
        communicate = edge_tts.Communicate(text, EDGE_VOICE, rate="-30%")
        audio_data = io.BytesIO()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        return audio_data.getvalue()
    except Exception as e:
        print(f"    [Edge TTS] Error: {e}")
        return None

def run_async(coro):
    """Run async function"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

def generate_sentence_audio(word, sentence_text):
    """Generate sentence audio using ElevenLabs (primary) or Edge TTS (fallback)"""
    # Try ElevenLabs first
    if ELEVENLABS_API_KEY:
        audio_data = generate_elevenlabs_audio(sentence_text)
        if audio_data:
            return audio_data
    
    # Fallback to Edge TTS
    audio_data = run_async(generate_edge_tts_audio(sentence_text))
    if audio_data:
        return audio_data
    
    return None

def main():
    print("=" * 80)
    print("REGENERATING SENTENCE AUDIO FOR ALL VALID WORDS")
    print("=" * 80)
    print(f"\nTotal words: {len(VALID_WORDS)}")
    print(f"Audio directory: {AUDIO_DIR}")
    print(f"ElevenLabs available: {bool(ELEVENLABS_API_KEY)}")
    
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)
    
    generated = 0
    failed = 0
    
    for i, word in enumerate(VALID_WORDS, 1):
        # Get sentence text
        if word in WORD_SENTENCES:
            sentence_text = WORD_SENTENCES[word]
        else:
            # Fallback sentence (shouldn't happen for valid words)
            if len(word) <= 4:
                sentence_text = f"Can you spell the word {word}?"
            elif len(word) <= 7:
                sentence_text = f"The word {word} is commonly used in everyday language."
            else:
                sentence_text = f"Learning to spell the word {word} requires practice and patience."
        
        # Generate audio
        word_filename = word.replace(" ", "_").lower()
        output_path = os.path.join(AUDIO_DIR, f"{word_filename}_sentence.mp3")
        
        # Skip if already exists
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
            print(f"[{i:3d}/{len(VALID_WORDS)}] {word:30s} - SKIPPED (already exists)")
            continue
        
        print(f"[{i:3d}/{len(VALID_WORDS)}] {word:30s} - Generating...", end="", flush=True)
        
        audio_data = generate_sentence_audio(word, sentence_text)
        
        if audio_data:
            try:
                with open(output_path, "wb") as f:
                    f.write(audio_data)
                print(" OK")
                generated += 1
            except Exception as e:
                print(f" FAILED: {e}")
                failed += 1
        else:
            print(" FAILED (no audio generated)")
            failed += 1
        
        # Rate limiting
        if i % 10 == 0:
            time.sleep(1)
    
    print("\n" + "=" * 80)
    print(f"REGENERATION COMPLETE")
    print(f"Generated: {generated}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(generated/(generated+failed)*100):.1f}%" if (generated+failed) > 0 else "N/A")
    print("=" * 80)

if __name__ == "__main__":
    main()
