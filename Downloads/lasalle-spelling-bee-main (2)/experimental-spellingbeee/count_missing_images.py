#!/usr/bin/env python3

"""Count words without images across all 4 groups"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from words import get_group_words

def count_words_without_images():
    print("=== WORDS WITHOUT IMAGES ANALYSIS ===")
    print()
    
    # Load image data
    WORD_IMAGES = {}
    WORD_SENTENCES = {}
    PIXABAY_IMAGES = {}
    
    # Load WORD_IMAGES from words.py
    try:
        with open(os.path.join(os.path.dirname(__file__), "words.py"), "r", encoding="utf-8") as f:
            content = f.read()
            # Simple extraction - not perfect but works for counting
            import re
            word_images_matches = re.findall(r'"([^"]+)":\s*"([^"]+)"', content)
            for word, emoji in word_images_matches:
                if len(emoji) <= 5 and any(c in emoji for c in "🎯📚⚡🎪🎭🎨🎬🎮🎯🎲🎸🎺🎻🎹🥁🎤🎧🎬📷📹📱💻⌨️🖥️🖱️🖨️📠📞📟📱☎️📞"):
                    WORD_IMAGES[word] = emoji
    except Exception as e:
        print(f"Error loading WORD_IMAGES: {e}")
    
    # Load PIXABAY_IMAGES
    pixabay_path = os.path.join(os.path.dirname(__file__), "word_images.json")
    if os.path.exists(pixabay_path):
        import json
        with open(pixabay_path, "r", encoding="utf-8") as f:
            PIXABAY_IMAGES = json.load(f)
    
    groups = ["default", "english6", "group3", "group4"]
    total_words = 0
    total_with_images = 0
    
    for group in groups:
        print(f"=== {group.upper()} GROUP ===")
        
        group_total = 0
        group_with_images = 0
        group_without_images = []
        
        for difficulty in ["easy", "medium", "hard"]:
            words = get_group_words(group, difficulty)
            group_total += len(words)
            
            for word in words:
                word_lower = word.lower()
                has_image = False
                
                # Check Pixabay images
                if word_lower in PIXABAY_IMAGES:
                    has_image = True
                
                # Check WORD_IMAGES (emojis)
                if word_lower in WORD_IMAGES:
                    has_image = True
                
                # Check if word has local image file
                if word_lower.replace(" ", "_") + ".jpg" in os.listdir("static/img/words") if os.path.exists("static/img/words") else False:
                    has_image = True
                
                if has_image:
                    group_with_images += 1
                else:
                    group_without_images.append(word)
        
        print(f"  Total words: {group_total}")
        print(f"  With images: {group_with_images}")
        print(f"  Without images: {group_total - group_with_images}")
        print(f"  Coverage: {(group_with_images/group_total)*100:.1f}%")
        
        if group_without_images:
            print(f"  First 10 without images: {', '.join(group_without_images[:10])}")
        
        print()
        
        total_words += group_total
        total_with_images += group_with_images
    
    print("=== OVERALL SUMMARY ===")
    print(f"Total words across all groups: {total_words}")
    print(f"With images: {total_with_images}")
    print(f"Without images: {total_words - total_with_images}")
    print(f"Overall coverage: {(total_with_images/total_words)*100:.1f}%")

if __name__ == "__main__":
    count_words_without_images()
