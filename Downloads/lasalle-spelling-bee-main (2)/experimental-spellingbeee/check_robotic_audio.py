#!/usr/bin/env python3

"""Check which audio files were generated with robotic TTS vs Edge TTS"""
import os
import edge_tts
import io
import time

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

# Edge TTS voices - natural sounding Microsoft voices
VOICE_NORMAL = "en-US-AriaNeural"
VOICE_SLOW = "en-US-GuyNeural"
VOICE_SPELL = "en-US-JennyNeural"

def check_recent_files():
    """Check which files were recently generated (likely Edge TTS)"""
    print("=== CHECKING RECENT AUDIO FILES ===")
    print("Files generated recently are likely Edge TTS (natural)")
    print("Older files are likely robotic TTS")
    print()
    
    audio_files = []
    if os.path.exists(AUDIO_DIR):
        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith('.mp3'):
                filepath = os.path.join(AUDIO_DIR, filename)
                mtime = os.path.getmtime(filepath)
                size_kb = os.path.getsize(filepath) / 1024
                audio_files.append((filename, mtime, size_kb))
    
    # Sort by modification time (newest first)
    audio_files.sort(key=lambda x: x[1], reverse=True)
    
    # Show recent files
    print("Most recently generated files (likely Edge TTS):")
    recent_files = audio_files[:20]
    
    for filename, mtime, size_kb in recent_files:
        import datetime
        dt = datetime.datetime.fromtimestamp(mtime)
        print(f"  {dt.strftime('%Y-%m-%d %H:%M')} - {filename} ({size_kb:.1f} KB)")
    
    # Show old files
    print(f"\nOldest files (likely robotic TTS):")
    old_files = audio_files[-20:]
    
    for filename, mtime, size_kb in old_files:
        import datetime
        dt = datetime.datetime.fromtimestamp(mtime)
        print(f"  {dt.strftime('%Y-%m-%d %H:%M')} - {filename} ({size_kb:.1f} KB)")
    
    # Group by age
    now = time.time()
    one_day_ago = now - 24 * 3600
    
    recent_words = set()
    old_words = set()
    
    for filename, mtime, _ in audio_files:
        base = filename.replace('.mp3', '')
        base = base.replace('_sentence', '').replace('_slow', '').replace('_spell', '')
        
        if mtime > one_day_ago:
            recent_words.add(base)
        else:
            old_words.add(base)
    
    print(f"\n=== SUMMARY ===")
    print(f"Words with recent (likely natural) audio: {len(recent_words)}")
    print(f"Words with old (likely robotic) audio: {len(old_words)}")
    
    # Words that were in our Group 3 update (should be natural)
    group3_words = {
        'apartment', 'birthday_party', 'breakfast', 'butterfly', 'chicken_wings',
        'childhood', 'christmas_tree', 'continuous', 'creation', 'crocodile',
        'decorations', 'effectively', 'feelings', 'friendship', 'grandparents',
        'hard-working', 'important', 'kindness', 'knuckles', 'messages',
        'musician', 'resilience', 'skyscrapers', 'speaking', 'studying',
        'sustainability', 'swimming', 'thematical', 'under_pressure', 'weather'
    }
    
    natural_group3 = recent_words.intersection(group3_words)
    robotic_group3 = old_words.intersection(group3_words)
    
    print(f"\nGroup 3 words:")
    print(f"  Natural (Edge TTS): {len(natural_group3)}")
    print(f"  Robotic (old TTS): {len(robotic_group3)}")
    
    if robotic_group3:
        print(f"  Robotic Group 3 words: {sorted(robotic_group3)}")
    
    return old_words, recent_words

def main():
    print("Checking which audio files use robotic vs natural TTS...")
    print()
    
    old_words, recent_words = check_recent_files()
    
    if old_words:
        print(f"\n=== RECOMMENDATION ===")
        print(f"Consider regenerating {len(old_words)} words that likely use robotic TTS")
        print(f"This would replace old robotic audio with natural Edge TTS")
        
        # Show a sample
        old_word_list = sorted(list(old_words))
        print(f"\nSample words with likely robotic audio:")
        for word in old_word_list[:30]:
            print(f"  - {word}")
        if len(old_word_list) > 30:
            print(f"  ... and {len(old_word_list) - 30} more")
        
        return old_words
    
    return []

if __name__ == "__main__":
    robotic_words = main()
    if robotic_words:
        print(f"\nWords with likely robotic audio: {len(robotic_words)}")
