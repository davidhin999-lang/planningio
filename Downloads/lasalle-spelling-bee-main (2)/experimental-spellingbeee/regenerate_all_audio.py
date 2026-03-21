#!/usr/bin/env python3

"""Delete old robotic TTS files and regenerate with natural Edge TTS voices"""
import os
import edge_tts
import io
import time

# Edge TTS voices - natural sounding Microsoft voices
VOICE_NORMAL = "en-US-AriaNeural"      # Natural female voice
VOICE_SLOW = "en-US-GuyNeural"         # Natural male voice, slightly deeper
VOICE_SPELL = "en-US-JennyNeural"      # Clear female voice for spelling

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

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
        
        print(f"  [OK] Regenerated {os.path.basename(output_path)}")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Failed to regenerate {os.path.basename(output_path)}: {e}")
        return False

def regenerate_word_audio(word):
    """Regenerate all audio variants for a single word"""
    word_filename = word.replace(' ', '_').lower()
    
    print(f"\nRegenerating audio for: {word}")
    
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
    print("Scanning for old robotic TTS files to replace with Edge TTS...")
    print(f"Audio directory: {AUDIO_DIR}")
    
    # Get all audio files
    audio_files = []
    if os.path.exists(AUDIO_DIR):
        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith('.mp3'):
                audio_files.append(filename)
    
    print(f"Found {len(audio_files)} audio files")
    
    # Group files by base word
    word_groups = {}
    for filename in audio_files:
        # Remove suffixes to get base word
        base = filename.replace('.mp3', '')
        base = base.replace('_sentence', '').replace('_slow', '').replace('_spell', '')
        word_groups[base] = word_groups.get(base, []) + [filename]
    
    print(f"Found {len(word_groups)} unique words")
    
    # Words to regenerate (all of them for consistency)
    words_to_regenerate = list(word_groups.keys())
    
    total_success = 0
    total_possible = len(words_to_regenerate) * 4  # 4 audio files per word
    
    for i, word in enumerate(words_to_regenerate, 1):
        print(f"\n[{i}/{len(words_to_regenerate)}]", end="")
        success = regenerate_word_audio(word)
        total_success += success
        
        # Small delay to avoid overwhelming the system
        if i < len(words_to_regenerate):
            time.sleep(0.5)
    
    print(f"\n\nRegeneration complete!")
    print(f"Successfully regenerated: {total_success}/{total_possible} audio files")
    print(f"Success rate: {(total_success/total_possible)*100:.1f}%")

if __name__ == "__main__":
    main()
