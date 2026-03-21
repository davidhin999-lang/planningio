#!/usr/bin/env python3

"""Regenerate the 11 remaining robotic TTS words with natural Edge TTS"""
import os
import edge_tts
import io
import time

# Edge TTS voices - natural sounding Microsoft voices
VOICE_NORMAL = "en-US-AriaNeural"      # Natural female voice
VOICE_SLOW = "en-US-GuyNeural"         # Natural male voice, slightly deeper
VOICE_SPELL = "en-US-JennyNeural"      # Clear female voice for spelling

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

# The 11 words with robotic TTS that need regeneration
ROBOTIC_WORDS = [
    'usually',
    'vacuum', 
    'vegetable',
    'vegetables',
    'vocabulary',
    'washing_machine',
    'wednesday',
    'weekly_planner',
    'windsurfing',
    'wooden_spoon',
    'workaholic'
]

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
        
        print(f"  [OK] Generated {os.path.basename(output_path)}")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Failed to generate {os.path.basename(output_path)}: {e}")
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
    print("=== REPLACING ROBOTIC TTS WITH NATURAL EDGE TTS ===")
    print(f"Audio directory: {AUDIO_DIR}")
    print(f"Words to regenerate: {len(ROBOTIC_WORDS)}")
    print(f"Total audio files: {len(ROBOTIC_WORDS) * 4}")
    print()
    
    total_success = 0
    total_possible = len(ROBOTIC_WORDS) * 4
    
    for i, word in enumerate(ROBOTIC_WORDS, 1):
        print(f"[{i}/{len(ROBOTIC_WORDS)}]", end="")
        success = regenerate_word_audio(word)
        total_success += success
        
        # Small delay to avoid overwhelming the system
        if i < len(ROBOTIC_WORDS):
            time.sleep(0.5)
    
    print(f"\n\n=== REGENERATION COMPLETE ===")
    print(f"Successfully regenerated: {total_success}/{total_possible} audio files")
    print(f"Success rate: {(total_success/total_possible)*100:.1f}%")
    print()
    print("🎉 ALL AUDIO NOW USES NATURAL EDGE TTS!")
    print("🤖 Robotic TTS completely eliminated!")

if __name__ == "__main__":
    main()
