#!/usr/bin/env python3

"""Regenerate creation and feelings with the best Edge TTS voice"""
import os
import edge_tts
import io

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

# Use the best voice from our tests (Jenny sounds most natural)
VOICE_NORMAL = "en-US-JennyNeural"      # Clear female voice
VOICE_SLOW = "en-US-JennyNeural"         # Same voice for consistency
VOICE_SPELL = "en-US-JennyNeural"       # Same voice for spelling

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
    try:
        # Select voice based on speed/type
        if speed == "slow":
            voice = VOICE_SLOW
            rate = "-10%"  # Slightly slower for clarity
        elif speed == "spell":
            voice = VOICE_SPELL
            text = format_spelling_text(text)
            rate = "-15%"  # Slower for spelling
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
        
        print(f"  [OK] Regenerated {os.path.basename(output_path)}")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Failed to regenerate {os.path.basename(output_path)}: {e}")
        return False

def regenerate_word_audio(word):
    """Regenerate all audio variants for a single word"""
    word_filename = word.replace(' ', '_').lower()
    
    print(f"Regenerating audio for: {word}")
    
    tasks = [
        ("normal", f"{word_filename}.mp3", word),
        ("slow", f"{word_filename}_slow.mp3", word),
        ("spell", f"{word_filename}_spell.mp3", word),
        ("sentence", f"{word_filename}_sentence.mp3", f"The word is {word}.")
    ]
    
    success_count = 0
    for speed, filename, text in tasks:
        output_path = os.path.join(AUDIO_DIR, filename)
        if generate_one(text, speed, output_path):
            success_count += 1
    
    return success_count

def main():
    print("=== REGENERATING CREATION AND FEELINGS ===")
    print("Using Jenny voice (most natural from our tests)")
    print()
    
    words_to_fix = ["creation", "feelings"]
    
    for word in words_to_fix:
        regenerate_word_audio(word)
        print()
    
    print("✅ Done! Try the word review now - should sound much more natural!")

if __name__ == "__main__":
    main()
