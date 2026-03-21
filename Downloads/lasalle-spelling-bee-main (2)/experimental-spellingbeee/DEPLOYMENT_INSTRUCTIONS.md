# Quick Deployment Instructions

## To Deploy to lasalle-spelling-bee.vercel.app

### Step 1: Commit Changes to Git

```bash
cd c:\Users\HP\Documents\lasalle-spelling-bee-mainFINAL\lasalle-spelling-bee-main

git add .
git commit -m "Implement all 6 critical issues: word deduplication, leaderboard separation, week distribution, bomb words, audio caching with Google Cloud TTS, image validation"
git push origin main
```

### Step 2: Vercel Auto-Deploys

Once you push to GitHub, Vercel automatically:
1. Detects the push
2. Installs dependencies (including new `google-cloud-texttospeech`)
3. Deploys the updated code
4. Your site updates at lasalle-spelling-bee.vercel.app

### Step 3: Verify Environment Variables

In Vercel dashboard, ensure these are set:
- `GOOGLE_APPLICATION_CREDENTIALS` (for Google Cloud TTS)
- `FIREBASE_CREDENTIALS_*` (for each group)
- `SECRET_KEY`
- `ADMIN_PASSWORD`

---

## What Changed

**6 Critical Issues Fixed:**

1. ✅ **Word Deduplication** - Groups 2,3,4,Tournament cleaned of duplicates
2. ✅ **Leaderboard Separation** - Ranked and regular scores now separate
3. ✅ **Week Distribution** - Minimum 10 words per difficulty per week
4. ✅ **Bomb Words** - Tournament restricted to hard difficulty only
5. ✅ **Audio Caching** - Google Cloud TTS (primary) + Edge TTS (fallback) with progressive caching
6. ✅ **Image Validation** - Wikipedia fallback removed, verified sources only

**Files Modified:**
- `words.py` - Word lists, deduplication, week distribution, bomb words
- `app.py` - Leaderboard separation, audio generation/caching, image validation
- `requirements.txt` - Added `google-cloud-texttospeech==2.14.1`
- `netlify.toml` - Created for deployment config

---

## Testing After Deployment

1. Visit lasalle-spelling-bee.vercel.app
2. Play a game - audio should generate on first play, cache on subsequent plays
3. Check leaderboards - ranked and regular should be separate
4. Verify word counts per group
5. Check Vercel logs for `[TTS]` messages

