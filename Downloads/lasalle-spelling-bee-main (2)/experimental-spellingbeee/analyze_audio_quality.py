#!/usr/bin/env python3

"""Analyze audio files to identify which ones likely need replacement"""
import os
import statistics

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

def analyze_audio_files():
    """Analyze audio files by size and other metrics to identify problematic ones"""
    print("=== AUDIO FILE ANALYSIS ===")
    print(f"Audio directory: {AUDIO_DIR}")
    
    # Get all audio files with their sizes
    audio_files = []
    if os.path.exists(AUDIO_DIR):
        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith('.mp3'):
                filepath = os.path.join(AUDIO_DIR, filename)
                size_kb = os.path.getsize(filepath) / 1024
                audio_files.append((filename, size_kb))
    
    print(f"Total audio files found: {len(audio_files)}")
    
    # Group files by type
    normal_files = []
    slow_files = []
    spell_files = []
    sentence_files = []
    
    for filename, size_kb in audio_files:
        if '_spell.mp3' in filename:
            spell_files.append((filename, size_kb))
        elif '_slow.mp3' in filename:
            slow_files.append((filename, size_kb))
        elif '_sentence.mp3' in filename:
            sentence_files.append((filename, size_kb))
        else:
            normal_files.append((filename, size_kb))
    
    print(f"Normal files: {len(normal_files)}")
    print(f"Slow files: {len(slow_files)}")
    print(f"Spell files: {len(spell_files)}")
    print(f"Sentence files: {len(sentence_files)}")
    
    # Analyze sizes for each type
    def analyze_size(files, label):
        if not files:
            return []
        sizes = [size for _, size in files]
        avg_size = statistics.mean(sizes)
        median_size = statistics.median(sizes)
        min_size = min(sizes)
        max_size = max(sizes)
        
        print(f"\n{label} files:")
        print(f"  Average size: {avg_size:.1f} KB")
        print(f"  Median size: {median_size:.1f} KB")
        print(f"  Size range: {min_size:.1f} - {max_size:.1f} KB")
        
        # Flag unusually small or large files
        small_threshold = avg_size * 0.5
        large_threshold = avg_size * 2.0
        
        problematic = []
        for filename, size in files:
            if size < small_threshold or size > large_threshold:
                problematic.append((filename, size))
        
        if problematic:
            print(f"  Potentially problematic files: {len(problematic)}")
            for filename, size in problematic[:5]:  # Show first 5
                print(f"    - {filename} ({size:.1f} KB)")
            if len(problematic) > 5:
                print(f"    ... and {len(problematic) - 5} more")
        
        return problematic
    
    # Find problematic files
    problematic_normal = analyze_size(normal_files, "Normal")
    problematic_slow = analyze_size(slow_files, "Slow")
    problematic_spell = analyze_size(spell_files, "Spell")
    problematic_sentence = analyze_size(sentence_files, "Sentence")
    
    # Get unique words that need regeneration
    all_problematic = problematic_normal + problematic_slow + problematic_spell + problematic_sentence
    words_to_regenerate = set()
    
    for filename, _ in all_problematic:
        # Extract base word
        base = filename.replace('.mp3', '')
        base = base.replace('_sentence', '').replace('_slow', '').replace('_spell', '')
        words_to_regenerate.add(base)
    
    print(f"\n=== SUMMARY ===")
    print(f"Total problematic files: {len(all_problematic)}")
    print(f"Unique words needing regeneration: {len(words_to_regenerate)}")
    
    # Show sample of words to regenerate
    word_list = sorted(list(words_to_regenerate))
    print(f"\nSample words to regenerate:")
    for word in word_list[:20]:
        print(f"  - {word}")
    if len(word_list) > 20:
        print(f"  ... and {len(word_list) - 20} more")
    
    return word_list

def main():
    print("Analyzing audio files to identify which ones need replacement...")
    print("This uses file size analysis to detect potentially problematic audio files.")
    print()
    
    words_to_regenerate = analyze_audio_files()
    
    if words_to_regenerate:
        print(f"\n=== RECOMMENDATION ===")
        print(f"Regenerate {len(words_to_regenerate)} words ({len(words_to_regenerate)*4} audio files)")
        print("This targets only potentially problematic files instead of all files!")
        
        return words_to_regenerate
    
    return []

if __name__ == "__main__":
    words_to_regenerate = main()
    if words_to_regenerate:
        print(f"\nWords recommended for regeneration: {len(words_to_regenerate)}")
