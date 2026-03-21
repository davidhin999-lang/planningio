#!/usr/bin/env python3

"""Regenerate ALL precached audio files.
Primary: ElevenLabs API (high quality)
Fallback: Edge TTS (JennyNeural)

Fixes:
- Multi-word phrases: convert filename underscores back to spaces for TTS text
- Slow audio: use -50% rate (was -10% which was barely noticeable)
- Uses word lists as source of truth, not just existing filenames
"""
import os
import sys
import io
import time
import hashlib
import argparse

try:
    import requests as http_requests
except ImportError:
    http_requests = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

# Edge TTS voice
EDGE_VOICE = "en-US-JennyNeural"

# ElevenLabs config (set ELEVENLABS_API_KEY env var)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Bella


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


def generate_elevenlabs(text, output_path):
    """Generate audio using ElevenLabs API. Returns True on success."""
    if not ELEVENLABS_API_KEY or not http_requests:
        return False
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY,
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        }
        resp = http_requests.post(url, json=data, headers=headers, timeout=30)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return True
    except Exception as e:
        print(f"    [ElevenLabs] Failed: {e}")
        return False


def generate_edge(text, output_path, rate="+0%"):
    """Generate audio using Edge TTS. Returns True on success."""
    if not edge_tts:
        return False
    try:
        communicate = edge_tts.Communicate(text, EDGE_VOICE, rate=rate)
        audio_data = io.BytesIO()
        for chunk in communicate.stream_sync():
            if chunk["type"] == "audio":
                audio_data.write(chunk["data"])
        with open(output_path, "wb") as f:
            f.write(audio_data.getvalue())
        return True
    except Exception as e:
        print(f"    [EdgeTTS] Failed: {e}")
        return False


def generate_audio(text, output_path, rate="+0%", use_elevenlabs=True):
    """Generate audio with ElevenLabs primary, Edge TTS fallback."""
    if use_elevenlabs and generate_elevenlabs(text, output_path):
        return "elevenlabs"
    if generate_edge(text, output_path, rate=rate):
        return "edge"
    return None


def get_all_words():
    """Get all unique words from all groups and word lists."""
    sys.path.insert(0, BASE_DIR)
    from words import (
        EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS,
        GROUP_CONFIG, WORD_SENTENCES,
    )

    all_words = set()
    # Global lists
    for w in EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS:
        all_words.add(w.lower())
    # Group-specific lists
    for grp, cfg in GROUP_CONFIG.items():
        for diff, wlist in cfg.get("words", {}).items():
            for w in wlist:
                all_words.add(w.lower())

    return sorted(all_words), WORD_SENTENCES


def regenerate_word(word, sentences, use_elevenlabs=True, force=False):
    """Regenerate all 4 audio variants for a word. Returns count of successes."""
    safe_name = word.replace(" ", "_").lower()
    sentence_text = sentences.get(word, f"The word is {word}.")

    variants = [
        (f"{safe_name}.mp3", word, "+0%"),
        (f"{safe_name}_slow.mp3", word, "-50%"),
        (f"{safe_name}_spell.mp3", format_spelling_text(word), "-15%"),
        (f"{safe_name}_sentence.mp3", sentence_text, "+0%"),
    ]

    ok = 0
    for filename, text, rate in variants:
        path = os.path.join(AUDIO_DIR, filename)
        if not force and os.path.exists(path) and os.path.getsize(path) > 500:
            ok += 1
            continue
        result = generate_audio(text, path, rate=rate, use_elevenlabs=use_elevenlabs)
        if result:
            ok += 1
        else:
            print(f"    FAILED: {filename}")
    return ok


def main():
    parser = argparse.ArgumentParser(description="Regenerate precached audio")
    parser.add_argument("--force", action="store_true", help="Regenerate even if file exists")
    parser.add_argument("--slow-only", action="store_true", help="Only regenerate _slow files")
    parser.add_argument("--multi-word-only", action="store_true", help="Only regenerate multi-word phrases")
    parser.add_argument("--missing-only", action="store_true", help="Only generate missing files")
    parser.add_argument("--no-elevenlabs", action="store_true", help="Skip ElevenLabs, use Edge TTS only")
    args = parser.parse_args()

    os.makedirs(AUDIO_DIR, exist_ok=True)

    use_el = not args.no_elevenlabs and bool(ELEVENLABS_API_KEY)
    print("=== AUDIO REGENERATION ===")
    print(f"ElevenLabs: {'YES' if use_el else 'NO (Edge TTS only)'}")
    print(f"Audio dir:  {AUDIO_DIR}")
    print()

    words, sentences = get_all_words()

    # Apply filters
    if args.multi_word_only:
        words = [w for w in words if " " in w]
        print(f"Multi-word filter: {len(words)} phrases")
    if args.slow_only:
        # Just regenerate _slow files
        print(f"Slow-only mode: regenerating _slow variants")
        ok = 0
        for i, word in enumerate(words, 1):
            safe = word.replace(" ", "_").lower()
            path = os.path.join(AUDIO_DIR, f"{safe}_slow.mp3")
            if not args.force and os.path.exists(path) and os.path.getsize(path) > 500:
                continue
            result = generate_audio(word, path, rate="-50%", use_elevenlabs=use_el)
            if result:
                ok += 1
                print(f"  [{i}/{len(words)}] {word} -> {result}")
            if i % 5 == 0:
                time.sleep(0.3)
        print(f"\nDone! Regenerated {ok} slow files.")
        return

    total = len(words)
    total_ok = 0
    total_files = 0

    for i, word in enumerate(words, 1):
        safe = word.replace(" ", "_").lower()
        if args.missing_only:
            # Check if all 4 variants exist
            all_exist = all(
                os.path.exists(os.path.join(AUDIO_DIR, f"{safe}{s}.mp3"))
                and os.path.getsize(os.path.join(AUDIO_DIR, f"{safe}{s}.mp3")) > 500
                for s in ["", "_slow", "_spell", "_sentence"]
            )
            if all_exist:
                total_ok += 4
                continue

        print(f"[{i}/{total}] {word}")
        ok = regenerate_word(word, sentences, use_elevenlabs=use_el, force=args.force)
        total_ok += ok
        total_files += 4

        # Rate limiting
        if use_el and i % 3 == 0:
            time.sleep(1)
        elif i % 5 == 0:
            time.sleep(0.2)

    print(f"\n=== DONE ===")
    print(f"Audio files OK: {total_ok}/{total * 4}")


if __name__ == "__main__":
    main()
