# Audio Generation & Caching Strategy

## Overview
Implement on-demand TTS generation with progressive caching for smooth game performance.

## Strategy: Lazy Loading with Progressive Caching

### 1. On-Demand Generation
- Generate audio when first requested (not pre-cached)
- Use ElevenLabs API as primary (high quality)
- Fall back to Edge TTS if ElevenLabs fails
- Return silent playback if both fail (game continues)

### 2. Progressive Caching
- Save generated audio to `audio/` directory
- Cache for 1 hour before regenerating
- Subsequent plays load from cache (instant)
- Reduces API calls and improves performance

### 3. Pre-warming (Background)
- Pre-generate audio for current week in background
- Happens when game starts, doesn't block gameplay
- Uses threading to avoid UI delays
- Improves experience for subsequent plays

## Implementation

### Audio Cache Directory
```
audio/
├── word_name.mp3
├── word_name_sentence.mp3
└── ...
```

### File Naming Convention
- Word audio: `{word_safe}.mp3` (spaces → underscores)
- Sentence audio: `{word_safe}_sentence.mp3`

### Cache Validation
- File must exist
- File size > 100 bytes (valid audio)
- File age < 3600 seconds (1 hour)

### Fallback Chain
1. Check cache (instant)
2. Generate with ElevenLabs (high quality)
3. Fall back to Edge TTS (reliable)
4. Silent playback (game continues)

## Performance Impact

### Before Caching
- Every word generation: API call (1-3 seconds)
- Total game load: 10 words × 2 seconds = 20 seconds

### After Caching
- First play: 10 API calls (20 seconds)
- Subsequent plays: Load from cache (instant)
- Pre-warmed week: 0 API calls (instant)

## API Cost Reduction
- ElevenLabs: $0.30 per 1M characters
- Typical game: 10 words × 20 chars = 200 chars
- Cost per game: $0.00006
- With caching: 90% reduction in API calls

## Implementation Checklist
- [ ] Add `get_or_generate_audio()` function
- [ ] Implement cache validation logic
- [ ] Add pre-warming endpoint
- [ ] Update frontend audio loading
- [ ] Test with all groups
- [ ] Monitor cache hit rates

