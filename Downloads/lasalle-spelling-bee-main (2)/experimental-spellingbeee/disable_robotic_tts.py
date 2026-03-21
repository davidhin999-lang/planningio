#!/usr/bin/env python3
"""
Quick fix: Disable TTS generation to prevent robotic audio
Only use pre-cached audio files
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Read app.py
with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Temporarily disable TTS generation to prevent robotic audio
# Replace the TTS fallback function to return None immediately
old_function = '''def generate_tts_with_fallback(text, edge_voice=None, edge_rate="-30%", elevenlabs_speed=0.75):
    """Generate TTS using ElevenLabs primary, Edge TTS fallback. No Google TTS or robotic voices."""
    
    # Try ElevenLabs first (if available)
    if ELEVENLABS_AVAILABLE:
        try:
            path = cache_and_return_elevenlabs(text, stability=0.75, similarity_boost=0.75)
            if path:
                print(f"[TTS] ElevenLabs success: {text[:30]}")
                return path
        except Exception as e:
            print(f"[TTS] ElevenLabs failed: {e}")
    
    # Fallback to Edge TTS (natural Microsoft voices)
    if edge_voice is None:
        edge_voice = VOICE_NORMAL
    try:
        path = cache_and_return_edge(text, edge_voice, edge_rate)
        if path:
            print(f"[TTS] Edge TTS fallback success: {text[:30]}")
            return path
    except Exception as e:
        print(f"[TTS] Edge TTS failed: {e}")
    
    # If both fail, return error - no Google TTS or robotic voice fallback allowed
    print(f"[TTS] CRITICAL: Both ElevenLabs and Edge TTS failed for: {text[:30]}")
    return None'''

new_function = '''def generate_tts_with_fallback(text, edge_voice=None, edge_rate="-30%", elevenlabs_speed=0.75):
    """TEMPORARILY DISABLED: Prevent robotic TTS - only use pre-cached audio."""
    print(f"[TTS] DISABLED - Only pre-cached audio allowed: {text[:30]}")
    return None'''

# Replace the function
content = content.replace(old_function, new_function)

# Write back to app.py
with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("=" * 80)
print("EMERGENCY FIX: TTS Generation Disabled")
print("=" * 80)
print("Disabled TTS generation to prevent robotic audio")
print("Only pre-cached audio files will be used")
print("Words without audio will show error instead of robotic TTS")
print("Deploy this to stop robotic audio immediately")

print(f"\nNext steps:")
print(f"1. Deploy this fix")
print(f"2. Test tournament - words with audio will work")
print(f"3. Words without audio will show error (better than robotic)")
print(f"4. Later: Fix TTS services and re-enable")
