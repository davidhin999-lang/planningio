# Sentence Audio Playback Issue

## Problem Description

Sentence examples are not being played correctly. The issue involves a mismatch between:
1. What sentence text is being used
2. How it's being generated
3. What audio is being served

## Root Cause Analysis

### The Sentence Endpoint (`/sentence/<word>`)

**Current Implementation (app.py:1401-1426):**

```python
@app.route("/sentence/<path:word>")
def sentence(word):
    w = unquote(word).lower().strip()
    precached = get_precached_audio(w, suffix="_sentence")
    if precached:
        return send_file(precached, mimetype="audio/mpeg")
    
    # Use contextual sentence if available, otherwise create helpful fallback
    if w in WORD_SENTENCES:
        text = WORD_SENTENCES[w]
    else:
        # Create helpful contextual sentences by word type/length
        if len(w) <= 4:
            text = f"Can you spell the word {w}?"
        elif len(w) <= 7:
            text = f"The word {w} is commonly used in everyday language."
        else:
            text = f"Learning to spell the word {w} requires practice and patience."
    
    # Play sentence slowly for better comprehension
    result = generate_tts_with_fallback(text, elevenlabs_speed=0.6, edge_rate="-30%")
    return serve_tts(result)
```

### The Issue

**Problem 1: Precached Audio Mismatch**
- The endpoint looks for precached audio with `suffix="_sentence"`
- But the precached audio files are named based on the WORD_SENTENCES text
- Example: For word "geography", it looks for `geography_sentence.mp3`
- But the actual file might be `geography_sentence.mp3` with audio for "In geography class, we learned about volcanoes."

**Problem 2: Dynamic Fallback Sentences**
- If a word is NOT in WORD_SENTENCES, it generates a fallback sentence
- These fallback sentences are generic and not contextual
- They're generated on-the-fly, so they're never cached
- This causes performance issues and inconsistent playback

**Problem 3: Deleted Audio Files**
- We just deleted 1,231 audio files for extra words
- Some of those deleted files may have been sentence audio for valid words
- This could cause 404 errors when trying to play sentence audio

## Examples of the Issue

### Example 1: Word with Contextual Sentence
```
Word: "geography"
WORD_SENTENCES["geography"] = "In geography class, we learned about volcanoes."
Expected: Play audio of that sentence
Actual: Looks for geography_sentence.mp3, plays it if found
Status: ✅ Works if precached file exists
```

### Example 2: Word WITHOUT Sentence (if any)
```
Word: "example"
WORD_SENTENCES["example"] = (missing)
Fallback: "The word example is commonly used in everyday language."
Expected: Generate and play fallback sentence
Actual: Generates on-the-fly, no caching
Status: ⚠️ Works but inefficient, no caching
```

### Example 3: Deleted Extra Words
```
Word: "often" (was deleted from audio directory)
Precached: often_sentence.mp3 (DELETED)
Fallback: "The word often is commonly used in everyday language."
Expected: Play fallback
Actual: Tries precached first, fails, then generates fallback
Status: ❌ Slow, causes delay
```

## The Real Problem

**Sentence audio is not being cached properly because:**

1. **Precached files were deleted** - We removed 1,231 files including sentence audio
2. **Fallback sentences are not cached** - Generated on-the-fly each time
3. **No consistency** - Some words use precached audio, others generate on-the-fly
4. **Performance issue** - TTS generation adds latency to sentence playback

## Solution

### Option 1: Regenerate All Sentence Audio (Recommended)
- Generate sentence audio for all 369 valid words
- Cache all sentence audio in `/audio/` directory
- Ensure consistency across all words
- Improves performance significantly

### Option 2: Improve Fallback Handling
- Cache fallback sentences in memory
- Use consistent, contextual fallback sentences
- Still slower than precached audio

### Option 3: Hybrid Approach
- Keep precached audio for words with contextual sentences
- Generate and cache fallback sentences for others
- Best of both worlds

## Recommended Fix

**Regenerate sentence audio for all 369 valid words:**

1. For each word in EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS:
   - Get the contextual sentence from WORD_SENTENCES
   - Generate audio using ElevenLabs (primary) or Edge TTS (fallback)
   - Save as `{word}_sentence.mp3`
   - Cache in `/audio/` directory

2. This ensures:
   - All sentences are contextual (not generic)
   - All audio is precached (no on-the-fly generation)
   - Consistent playback experience
   - Better performance

## Implementation

Create a script to regenerate all sentence audio:

```python
#!/usr/bin/env python3
import os
from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS, WORD_SENTENCES

VALID_WORDS = EASY_WORDS + MEDIUM_WORDS + HARD_WORDS + PHRASE_WORDS
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "audio")

for word in VALID_WORDS:
    if word in WORD_SENTENCES:
        sentence = WORD_SENTENCES[word]
        # Generate audio for sentence
        # Save as {word}_sentence.mp3
```

## Summary

**Current Status:**
- ❌ Sentence audio playback is inconsistent
- ❌ Some sentences are not cached
- ❌ Performance is degraded due to on-the-fly generation
- ❌ Deleted extra word audio may have included valid sentence audio

**After Fix:**
- ✅ All sentences are contextual
- ✅ All sentences are precached
- ✅ Consistent, fast playback
- ✅ Better user experience
