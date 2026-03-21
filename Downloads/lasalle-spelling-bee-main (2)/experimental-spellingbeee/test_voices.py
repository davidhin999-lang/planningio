#!/usr/bin/env python3

"""Test different Edge TTS voices for creation and feelings"""
import os
import edge_tts
import io

AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

# Test different voices
TEST_VOICES = [
    ("en-US-AriaNeural", "Aria (Natural Female)"),
    ("en-US-JennyNeural", "Jenny (Clear Female)"), 
    ("en-US-GuyNeural", "Guy (Natural Male)"),
    ("en-US-EricNeural", "Eric (Natural Male)"),
    ("en-US-AriaNeural", "Aria (Natural Female) - Slower"),
]

def test_voice_generation():
    """Test different voices for creation and feelings"""
    test_words = ["creation", "feelings"]
    
    print("=== TESTING EDGE TTS VOICES ===")
    print("Testing different voices for 'creation' and 'feelings'")
    print()
    
    for word in test_words:
        print(f"Testing word: {word}")
        
        for i, (voice, description) in enumerate(TEST_VOICES):
            # Adjust rate for last test
            rate = "+0%" if i < len(TEST_VOICES) - 1 else "-10%"
            
            try:
                communicate = edge_tts.Communicate(word, voice, rate=rate)
                audio_data = io.BytesIO()
                
                for chunk in communicate.stream_sync():
                    if chunk["type"] == "audio":
                        audio_data.write(chunk["data"])
                
                # Save test file
                test_filename = f"test_{word}_{voice.replace('-', '_')}.mp3"
                test_path = os.path.join(AUDIO_DIR, test_filename)
                
                with open(test_path, "wb") as f:
                    f.write(audio_data.getvalue())
                
                size_kb = os.path.getsize(test_path) / 1024
                print(f"  [OK] {description}: {test_filename} ({size_kb:.1f} KB)")
                
            except Exception as e:
                print(f"  [FAIL] {description}: {e}")
        
        print()

if __name__ == "__main__":
    test_voice_generation()
    print("Test files created! Listen to them to compare voice quality.")
    print("Files are named: test_creation_voice.mp3, test_feelings_voice.mp3")
    print("Delete the ones you don't like and keep the best ones.")
