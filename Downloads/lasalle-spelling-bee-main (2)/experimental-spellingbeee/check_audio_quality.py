#!/usr/bin/env python3

"""Quality check existing audio files to identify which ones need replacement"""
import os
import random

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

def check_audio_quality():
    """Check a sample of audio files to assess quality"""
    print("=== AUDIO QUALITY CHECK ===")
    print(f"Audio directory: {AUDIO_DIR}")
    
    # Get all audio files
    audio_files = []
    if os.path.exists(AUDIO_DIR):
        for filename in os.listdir(AUDIO_DIR):
            if filename.endswith('.mp3'):
                audio_files.append(filename)
    
    print(f"Total audio files found: {len(audio_files)}")
    
    # Group files by base word
    word_groups = {}
    for filename in audio_files:
        base = filename.replace('.mp3', '')
        base = base.replace('_sentence', '').replace('_slow', '').replace('_spell', '')
        word_groups[base] = word_groups.get(base, []) + [filename]
    
    print(f"Unique words found: {len(word_groups)}")
    
    # Sample some words to check
    sample_size = min(20, len(word_groups))
    sample_words = random.sample(list(word_groups.keys()), sample_size)
    
    print(f"\n=== SAMPLE WORDS TO CHECK ===")
    print("Listen to these files and rate their quality:")
    print("1 = Excellent (natural, clear)")
    print("2 = Good (acceptable)")  
    print("3 = Poor (robotic, muffled, bad quality)")
    print("4 = Very Bad (unusable)")
    
    quality_scores = {}
    
    for i, word in enumerate(sample_words, 1):
        print(f"\n[{i}/{sample_size}] Word: {word}")
        files = word_groups[word]
        
        for filename in sorted(files):
            filepath = os.path.join(AUDIO_DIR, filename)
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  - {filename} ({size_kb:.1f} KB)")
        
        # Ask for quality rating
        while True:
            try:
                rating = input(f"  Quality rating (1-4): ").strip()
                if rating in ['1', '2', '3', '4']:
                    quality_scores[word] = int(rating)
                    break
                else:
                    print("  Please enter 1, 2, 3, or 4")
            except KeyboardInterrupt:
                print("\nQuality check interrupted.")
                return quality_scores
    
    # Analyze results
    print(f"\n=== QUALITY ANALYSIS ===")
    poor_words = [word for word, score in quality_scores.items() if score >= 3]
    good_words = [word for word, score in quality_scores.items() if score <= 2]
    
    print(f"Words needing replacement (score 3-4): {len(poor_words)}")
    print(f"Words acceptable (score 1-2): {len(good_words)}")
    
    if poor_words:
        print(f"\nWords to regenerate: {poor_words}")
    
    # Estimate total words needing replacement
    poor_percentage = len(poor_words) / len(quality_scores) if quality_scores else 0
    estimated_total = int(len(word_groups) * poor_percentage)
    
    print(f"\nEstimated total words needing replacement: ~{estimated_total}")
    print(f"Estimated total audio files to regenerate: ~{estimated_total * 4}")
    
    return quality_scores, poor_words

def main():
    print("Starting audio quality check...")
    print("This will help us identify which files actually need replacement.")
    print()
    
    quality_scores, poor_words = check_audio_quality()
    
    if poor_words:
        print(f"\n=== RECOMMENDATION ===")
        print(f"Regenerate {len(poor_words)} words ({len(poor_words)*4} audio files)")
        print("This is much more efficient than regenerating all files!")
        
        proceed = input("\nProceed with selective regeneration? (y/n): ").strip().lower()
        if proceed == 'y':
            return poor_words
    
    print("\nQuality check complete!")
    return []

if __name__ == "__main__":
    words_to_regenerate = main()
    if words_to_regenerate:
        print(f"Words to regenerate: {words_to_regenerate}")
