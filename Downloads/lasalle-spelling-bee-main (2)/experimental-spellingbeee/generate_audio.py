"""Pre-generate audio files for all spelling bee words using ElevenLabs API.
Run locally: ELEVENLABS_API_KEY=your_key python generate_audio.py
Saves MP3 files to audio/ directory with naming convention:
  audio/{word}.mp3           - normal speed speak
  audio/{word}_slow.mp3      - slow speed speak
  audio/{word}_spell.mp3     - letter-by-letter spelling
  audio/{word}_sentence.mp3  - word used in a sentence
"""
import asyncio
import os
import sys
import requests
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS, WORD_SENTENCES

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Bella
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

ALL_WORDS = list(set(EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS))
ALL_WORDS.sort()


def format_spelling_text(word):
    parts = []
    for ch in str(word):
        if ch.isalpha():
            parts.append(ch.upper())
        elif ch.isdigit():
            parts.append(ch)
        elif ch.isspace():
            parts.append(" ")
    out = []
    for p in parts:
        if p == " ":
            if out and out[-1] != ", ":
                out.append(", ")
            continue
        out.append(p)
        out.append("... ")
    return "".join(out).strip()


def generate_one(text, speed, output_path):
    if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
        return False  # Already exists
    
    if not ELEVENLABS_API_KEY:
        print(f"  ERROR: ELEVENLABS_API_KEY not set")
        return False
    
    try:
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "style": 0.0,
                "use_speaker_boost": True,
                "speed": speed
            }
        }
        
        response = requests.post(ELEVENLABS_URL, json=data, headers=headers)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"  ERROR generating {output_path}: {e}")
        return False


def main():
    total = len(ALL_WORDS)
    print(f"Generating audio for {total} words with ElevenLabs...")
    
    if not ELEVENLABS_API_KEY:
        print("ERROR: Set ELEVENLABS_API_KEY environment variable")
        return

    generated = 0
    skipped = 0

    for i, word in enumerate(ALL_WORDS):
        safe_name = word.replace(" ", "_").lower()
        print(f"[{i+1}/{total}] {word}")

        # 1) Normal speak
        path = os.path.join(AUDIO_DIR, f"{safe_name}.mp3")
        if generate_one(word, 0.65, path):
            generated += 1
        else:
            skipped += 1

        # 2) Slow speak
        path_slow = os.path.join(AUDIO_DIR, f"{safe_name}_slow.mp3")
        if generate_one(word, 0.35, path_slow):
            generated += 1
        else:
            skipped += 1

        # 3) Spell
        spell_text = format_spelling_text(word)
        path_spell = os.path.join(AUDIO_DIR, f"{safe_name}_spell.mp3")
        if generate_one(spell_text, 0.35, path_spell):
            generated += 1
        else:
            skipped += 1

        # 4) Sentence
        sentence_text = WORD_SENTENCES.get(word.lower(), f"The word is {word}.")
        path_sentence = os.path.join(AUDIO_DIR, f"{safe_name}_sentence.mp3")
        if generate_one(sentence_text, 0.75, path_sentence):
            generated += 1
        else:
            skipped += 1

    print(f"\nDone! Generated: {generated}, Skipped (already exist): {skipped}")
    print(f"Audio directory: {AUDIO_DIR}")


if __name__ == "__main__":
    main()
