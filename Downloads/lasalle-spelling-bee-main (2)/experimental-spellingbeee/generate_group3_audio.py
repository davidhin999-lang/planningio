"""Generate audio files for missing Group 3 words using Edge TTS (Microsoft natural voices).
Run locally: python generate_group3_audio.py
Saves MP3 files to audio/ directory with naming convention:
  audio/{word}.mp3           - normal speed speak
  audio/{word}_slow.mp3      - slow speed speak
  audio/{word}_spell.mp3     - letter-by-letter spelling
  audio/{word}_sentence.mp3  - word used in a sentence
"""
import asyncio
import os
import sys
import edge_tts
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Edge TTS voices - natural sounding Microsoft voices
VOICE_NORMAL = "en-US-AriaNeural"      # Natural female voice
VOICE_SLOW = "en-US-GuyNeural"         # Natural male voice, slightly deeper
VOICE_SPELL = "en-US-JennyNeural"      # Clear female voice for spelling

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

# Group 3 words that need audio (from our analysis)
MISSING_WORDS = [
    "apartment", "birthday party", "breakfast", "butterfly", "chicken wings",
    "childhood", "christmas tree", "continuous", "creation", "crocodile",
    "decorations", "effectively", "feelings", "friendship", "grandparents",
    "hard-working", "important", "kindness", "knuckles", "messages",
    "musician", "resilience", "skyscrapers", "speaking", "studying",
    "sustainability", "swimming", "thematical", "under pressure", "weather"
]

# Simple sentences for context
SENTENCES = {
    "apartment": "I live in a small apartment downtown.",
    "birthday party": "We're having a birthday party this weekend.",
    "breakfast": "I eat breakfast every morning at 7 AM.",
    "butterfly": "A beautiful butterfly landed on the flower.",
    "chicken wings": "The restaurant serves delicious chicken wings.",
    "childhood": "I have fond memories of my childhood.",
    "christmas tree": "We decorated the christmas tree with lights.",
    "continuous": "The continuous rain lasted for three days.",
    "creation": "The artist's latest creation was amazing.",
    "crocodile": "A crocodile swam slowly across the river.",
    "decorations": "We put up decorations for the holiday.",
    "effectively": "She effectively managed the entire project.",
    "feelings": "It's important to share your feelings with others.",
    "friendship": "Their friendship lasted for many years.",
    "grandparents": "My grandparents live in the countryside.",
    "hard-working": "The hard-working student earned top marks.",
    "important": "It's important to finish your homework.",
    "kindness": "Kindness costs nothing but means everything.",
    "knuckles": "He cracked his knuckles before typing.",
    "messages": "I have several messages to check.",
    "musician": "The musician played beautifully at the concert.",
    "resilience": "Her resilience helped her overcome challenges.",
    "skyscrapers": "The city has many tall skyscrapers.",
    "speaking": "Speaking in public requires confidence.",
    "studying": "Studying regularly improves your grades.",
    "sustainability": "Sustainability is crucial for our planet.",
    "swimming": "Swimming is great exercise for the whole body.",
    "thematical": "The movie had a strong thematical element.",
    "under pressure": "He performs well under pressure.",
    "weather": "The weather today is perfect for a picnic."
}

def format_spelling_text(word):
    """Format word for spelling with pauses between letters"""
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
    """Generate audio for one text using Edge TTS"""
    if os.path.exists(output_path) and os.path.getsize(output_path) > 100:
        print(f"  [OK] {os.path.basename(output_path)} already exists")
        return True
    
    try:
        # Select voice based on speed/type
        if speed == "slow":
            voice = VOICE_SLOW
            rate = "-15%"  # Slightly slower for clarity
        elif speed == "spell":
            voice = VOICE_SPELL
            text = format_spelling_text(text)
            rate = "-20%"  # Slower for spelling
        else:
            voice = VOICE_NORMAL
            rate = "+0%"   # Normal speed
        
        # Generate audio using Edge TTS (synchronous)
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        audio_data = io.BytesIO()
        
        # Use synchronous approach
        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        
        # Save to file
        with open(output_path, "wb") as f:
            f.write(audio_data.getvalue())
        
        print(f"  [OK] Generated {os.path.basename(output_path)}")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Failed to generate {os.path.basename(output_path)}: {e}")
        return False

def generate_word_audio(word):
    """Generate all audio variants for a single word"""
    word_filename = word.replace(' ', '_').lower()
    
    print(f"\nGenerating audio for: {word}")
    
    tasks = [
        ("normal", f"{word_filename}.mp3", word),
        ("slow", f"{word_filename}_slow.mp3", word),
        ("spell", f"{word_filename}_spell.mp3", word),
        ("sentence", f"{word_filename}_sentence.mp3", SENTENCES.get(word, f"The word is {word}."))
    ]
    
    success_count = 0
    for speed, filename, text in tasks:
        output_path = os.path.join(AUDIO_DIR, filename)
        if generate_one(text, speed, output_path):
            success_count += 1
    
    return success_count

def main():
    print(f"Generating audio for {len(MISSING_WORDS)} Group 3 words using Edge TTS...")
    print(f"Output directory: {AUDIO_DIR}")
    print(f"Voices: {VOICE_NORMAL} (normal), {VOICE_SLOW} (slow), {VOICE_SPELL} (spelling)")
    
    total_success = 0
    total_possible = len(MISSING_WORDS) * 4  # 4 audio files per word
    
    for i, word in enumerate(MISSING_WORDS, 1):
        print(f"\n[{i}/{len(MISSING_WORDS)}]", end="")
        success = generate_word_audio(word)
        total_success += success
        
        # Small delay to avoid overwhelming the system
        if i < len(MISSING_WORDS):
            time.sleep(0.5)
    
    print(f"\n\nGeneration complete!")
    print(f"Successfully generated: {total_success}/{total_possible} audio files")
    print(f"Success rate: {(total_success/total_possible)*100:.1f}%")

if __name__ == "__main__":
    import time
    main()
