#!/usr/bin/env python3
"""
Generate just the student sentence audio file
"""

import os
import sys
from words import WORD_SENTENCES

# Audio directory
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

def generate_student_sentence():
    """Generate student sentence audio file"""
    
    word = "student"
    sentence_text = WORD_SENTENCES[word]
    
    print(f"Generating {word}_sentence.mp3...")
    print(f"Text: {sentence_text}")
    
    # Import the TTS functions from app.py
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from app import generate_tts_with_fallback
        
        # Generate audio
        result = generate_tts_with_fallback(
            sentence_text, 
            elevenlabs_speed=0.6, 
            edge_rate="-30%"
        )
        
        if result:
            print(f"TTS generated file: {result}")
            
            # Read the audio content
            try:
                with open(result, 'rb') as f:
                    audio_data = f.read()
                
                print(f"Read {len(audio_data)} bytes of audio data")
                
                # Save the audio file
                output_file = os.path.join(AUDIO_DIR, f"{word}_sentence.mp3")
                with open(output_file, 'wb') as f:
                    f.write(audio_data)
                
                print(f"Successfully generated {word}_sentence.mp3 ({len(audio_data)} bytes)")
            except Exception as file_error:
                print(f"ERROR: Failed to read audio file: {file_error}")
        else:
            print("ERROR: TTS generation failed")
            
    except ImportError as e:
        print(f"ERROR: Importing TTS functions: {e}")

if __name__ == "__main__":
    generate_student_sentence()
