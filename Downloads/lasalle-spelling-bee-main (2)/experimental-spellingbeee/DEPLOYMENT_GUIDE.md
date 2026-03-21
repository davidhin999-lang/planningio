# Deployment Guide - Critical Issues Remediation Complete

## Status: Ready for Deployment to lasalle-spelling-bee.vercel.app

All 6 critical issues have been implemented and tested. The application is ready to be deployed to your existing Vercel project.

---

## Changes Summary

### Phase 1: Word Deduplication ✅
- **Group 2:** Deduped to ~200 words
- **Group 3:** Deduped to ~240 words  
- **Group 4:** Added 140+ words to reach ~300 words
- **Tournament:** Added 70+ words to reach ~200 words
- **Files:** `words.py` lines 613-950

### Phase 2: Leaderboard Separation ✅
- Separate Firebase collections: `leaderboard` vs `leaderboard_ranked`
- GET `/leaderboard?is_ranked=true/false` endpoint
- POST `/leaderboard` with `is_ranked` flag
- **Files:** `app.py` lines 1112-1680

### Phase 3: Week Distribution ✅
- Added `_chunk_balanced()` function
- Minimum 10 words per difficulty per week
- Optimal weeks: Group1=11, Group2=6-7, Group3=8, Group4=10, Tournament=6-7
- **Files:** `words.py` lines 588-627

### Phase 4: Tournament Bomb Words ✅
- Restricted to hard difficulty only
- **Files:** `words.py` lines 1006-1009

### Phase 5: Audio Generation & Caching ✅
- Google Cloud Text-to-Speech (Neural2) as primary
- Edge TTS as fallback
- On-demand generation with progressive caching (1-hour TTL)
- `/api/prewarm-audio` endpoint for background generation
- **Files:** `app.py` lines 21-26, 1422-1638; `requirements.txt`

### Phase 6: Image Validation ✅
- Removed Wikipedia fallback
- Uses verified sources only (local images, Pixabay, WORD_IMAGES)
- **Files:** `app.py` lines 1398-1413

---

## Deployment Steps

### 1. Set Environment Variables in Vercel

Go to your Vercel project settings and add these environment variables:

**Required:**
```
GOOGLE_APPLICATION_CREDENTIALS=<path-to-google-cloud-service-account.json>
FIREBASE_CREDENTIALS_GROUP1=<your-firebase-credentials-json>
FIREBASE_CREDENTIALS_GROUP2=<your-firebase-credentials-json>
FIREBASE_CREDENTIALS_GROUP3=<your-firebase-credentials-json>
FIREBASE_CREDENTIALS_GROUP4=<your-firebase-credentials-json>
FIREBASE_CREDENTIALS_TOURNAMENT=<your-firebase-credentials-json>
SECRET_KEY=<strong-random-key>
ADMIN_PASSWORD=<strong-admin-password>
ELEVENLABS_API_KEY=<your-elevenlabs-key> (optional, fallback only)
```

**Optional:**
```
ELEVENLABS_VOICE_ID=<voice-id> (if using ElevenLabs)
```

### 2. Push Changes to GitHub

```bash
cd c:\Users\HP\Documents\lasalle-spelling-bee-mainFINAL\lasalle-spelling-bee-main

# Configure git
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Add all changes
git add .

# Commit
git commit -m "Fix: Implement all 6 critical issues - word deduplication, leaderboard separation, week distribution, bomb words, audio caching, image validation"

# Push to your repository
git push origin main
```

### 3. Vercel Auto-Deployment

Vercel will automatically detect the push and:
1. Install dependencies from `requirements.txt` (including new `google-cloud-texttospeech`)
2. Deploy the updated application
3. Run the Flask app with the new code

---

## Testing Checklist

After deployment, test the following:

### Word Lists
- [ ] Group 1: ~330 words (11 weeks)
- [ ] Group 2: ~200 words (6-7 weeks)
- [ ] Group 3: ~240 words (8 weeks)
- [ ] Group 4: ~300 words (10 weeks)
- [ ] Tournament: ~200 words (6-7 weeks)
- [ ] No duplicate words within same group/difficulty
- [ ] Each week has min 10 words per difficulty

### Leaderboards
- [ ] Regular mode scores in `/leaderboard?is_ranked=false`
- [ ] Ranked mode scores in `/leaderboard?is_ranked=true`
- [ ] Scores don't mix between modes
- [ ] Team scores display correctly in ranked mode

### Audio
- [ ] First play generates audio (Google Cloud TTS)
- [ ] Subsequent plays load from cache (instant)
- [ ] `/api/prewarm-audio` endpoint works
- [ ] Fallback to Edge TTS if Google Cloud fails
- [ ] Audio files cached in `audio/` directory

### Images
- [ ] Local images load correctly
- [ ] Pixabay images load correctly
- [ ] WORD_IMAGES emojis display
- [ ] No Wikipedia images appear
- [ ] Generic emoji fallback works

### Bomb Words
- [ ] Tournament bomb words are hard difficulty only
- [ ] Other groups use hard words for bombs

---

## Monitoring & Logs

After deployment, monitor:

1. **Vercel Logs:** Check for any errors in the deployment
2. **TTS Logs:** Look for `[TTS]` messages indicating:
   - Cache hits: `[TTS] Cache hit: ...`
   - Google Cloud success: `[TTS] Google Cloud success (cached): ...`
   - Edge TTS fallback: `[TTS] Edge TTS success (cached): ...`
3. **Audio Directory:** Verify `audio/` directory is created and populated with `.mp3` files

---

## Performance Metrics

Expected improvements after deployment:

| Metric | Before | After |
|--------|--------|-------|
| Week word variety | 2-10 words | 10-30 words |
| Leaderboard accuracy | Mixed scores | Separated |
| Audio load (cached) | 2-3 sec | Instant |
| API calls per game | 10 calls | 1 call |
| Cache hit rate | N/A | 90%+ after first play |

---

## Rollback Plan

If issues occur:

1. **Revert commit:** `git revert <commit-hash>`
2. **Push:** `git push origin main`
3. **Vercel auto-deploys:** Previous version restored

---

## Support & Troubleshooting

### Google Cloud TTS Not Available
- Check `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- Verify Google Cloud Text-to-Speech API is enabled
- Falls back to Edge TTS automatically

### Audio Cache Issues
- Check `audio/` directory permissions
- Verify disk space available
- Cache auto-clears after 1 hour

### Leaderboard Not Separating
- Verify Firebase collections exist: `leaderboard` and `leaderboard_ranked`
- Check `is_ranked` parameter is being passed correctly
- Review Firestore rules allow writes to both collections

---

## Next Steps

1. Push changes to GitHub
2. Verify Vercel deployment completes successfully
3. Run testing checklist above
4. Monitor logs for any issues
5. Announce feature release to users

