#!/usr/bin/env python3
"""
Generate missing sentence audio files for words that are in WORD_SENTENCES
but don't have corresponding _sentence.mp3 files in the audio folder.
"""

import os
import sys
import time
from words import WORD_SENTENCES

# Audio directory
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

def generate_sentence_audio():
    """Generate missing sentence audio files"""
    
    # Get all words that have sentences
    words_with_sentences = list(WORD_SENTENCES.keys())
    
    # Check which sentence files are missing
    missing_files = []
    for word in words_with_sentences:
        sentence_file = os.path.join(AUDIO_DIR, f"{word}_sentence.mp3")
        if not os.path.exists(sentence_file):
            missing_files.append(word)
    
    print(f"Found {len(missing_files)} missing sentence files to generate:")
    for i, word in enumerate(missing_files[:10], 1):
        print(f"  {i}. {word}")
    if len(missing_files) > 10:
        print(f"  ... and {len(missing_files) - 10} more")
    
    if not missing_files:
        print("All sentence files already exist!")
        return
    
    # Generate missing files
    print("\nGenerating missing sentence files...")
    
    # Import the TTS functions from app.py
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app import generate_tts_with_fallback, serve_tts
        
        for i, word in enumerate(missing_files, 1):
            try:
                print(f"[{i}/{len(missing_files)}] Generating {word}_sentence.mp3...")
                
                # Get the sentence text
                sentence_text = WORD_SENTENCES[word]
                
                # Generate audio
                result = generate_tts_with_fallback(
                    sentence_text, 
                    elevenlabs_speed=0.6, 
                    edge_rate="-30%"
                )
                
                if result:
                    # result is a file path, read the audio content
                    try:
                        with open(result, 'rb') as f:
                            audio_data = f.read()
                        
                        # Save the audio file
                        output_file = os.path.join(AUDIO_DIR, f"{word}_sentence.mp3")
                        with open(output_file, 'wb') as f:
                            f.write(audio_data)
                        
                        print(f"  OK Generated {word}_sentence.mp3")
                        time.sleep(0.1)  # Small delay to avoid overwhelming
                    except Exception as file_error:
                        print(f"  ERROR Failed to read audio file for {word}: {file_error}")
                else:
                    print(f"  ERROR Failed to generate {word}_sentence.mp3")
                    
            except Exception as e:
                print(f"  ERROR Error generating {word}_sentence.mp3: {e}")
        
        print(f"\nCompleted! Generated {len(missing_files)} sentence files.")
        
    except ImportError as e:
        print(f"Error importing TTS functions: {e}")
        print("Make sure app.py is in the same directory and all dependencies are installed.")

if __name__ == "__main__":
    generate_sentence_audio()
