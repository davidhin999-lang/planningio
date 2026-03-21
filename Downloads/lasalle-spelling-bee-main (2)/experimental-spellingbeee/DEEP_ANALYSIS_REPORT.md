# Deep Analysis Report: Cross-Group Issues

## Analysis Date: March 19, 2026

---

## ISSUE 1: Word List Integrity (Duplicates & Categorization)

### Problem Statement
Each group should have:
- Unique words (no duplicates within a group)
- Proper categorization into easy/medium/hard
- No word should appear in multiple difficulty levels within same group
- Words should not overlap between groups

### Analysis Results

#### GROUP 1 (Global Lists)
**Status:** ✅ CLEAN
- Uses global EASY_WORDS, MEDIUM_WORDS, HARD_WORDS + PHRASE_WORDS
- No custom override
- Global lists are consolidated (fixed duplicate HARD_WORDS issue)

#### GROUP 2
**Status:** ⚠️ ISSUES FOUND
- **Easy words:** 40 words
- **Medium words:** 83 words (includes duplicates from easy)
- **Hard words:** 194 words (includes duplicates from medium)
- **Duplicates found:**
  - "chocolate" appears in easy AND medium
  - "sentences" appears in easy AND medium
  - "stomachache" appears in easy AND medium
  - "toothache" appears in easy AND medium
  - "wednesday" appears in easy AND medium
  - "adventure" appears in medium AND hard
  - "beautiful" appears in medium AND hard
  - "knowledge" appears in medium AND hard
  - "language" appears in medium AND hard
  - "exercise" appears in medium AND hard
  - And more...

#### GROUP 3
**Status:** ⚠️ ISSUES FOUND
- **Easy words:** 40 words
- **Medium words:** 100+ words (heavy duplication from easy)
- **Hard words:** 140+ words (heavy duplication from medium)
- **Duplicates found:**
  - "chocolate" appears in easy AND medium AND hard
  - "sentences" appears in easy AND medium AND hard
  - "stomachache" appears in easy AND medium AND hard
  - "wednesday" appears in easy AND medium AND hard
  - "breakfast" appears in easy AND medium
  - "butterfly" appears in easy AND medium
  - "crocodile" appears in easy AND medium
  - "decisions" appears in easy AND medium
  - "delicious" appears in easy AND medium AND hard
  - "equipment" appears in easy AND medium AND hard
  - "excellent" appears in easy AND medium AND hard
  - "exciting" appears in easy AND medium
  - "following" appears in easy AND medium AND hard
  - "geography" appears in easy AND medium AND hard
  - "hopefully" appears in easy AND medium AND hard
  - "important" appears in easy AND medium AND hard
  - "knowledge" appears in easy AND medium AND hard
  - "languages" appears in easy AND medium AND hard
  - "lightning" appears in easy AND medium AND hard
  - "paperless" appears in easy AND medium AND hard
  - "sentences" appears in easy AND medium AND hard
  - "stressful" appears in easy AND medium AND hard
  - "technology" appears in easy AND medium AND hard
  - "thrilling" appears in easy AND medium AND hard
  - "wednesday" appears in easy AND medium AND hard

#### GROUP 4
**Status:** ⚠️ ISSUES FOUND
- **Easy words:** 30 words
- **Medium words:** 69 words (includes duplicates from easy)
- **Hard words:** 67 words (includes duplicates from medium)
- **Duplicates found:**
  - "accuracy" appears in easy AND medium
  - "addition" appears in easy AND medium
  - "analysis" appears in easy AND medium
  - "argument" appears in easy AND medium
  - "adventure" appears in easy AND medium
  - "agreement" appears in easy AND medium
  - "alternate" appears in easy AND medium
  - "apartment" appears in easy AND medium
  - "attention" appears in easy AND medium
  - "available" appears in easy AND medium
  - "beautiful" appears in easy AND medium
  - "calculate" appears in easy AND medium
  - And more...

#### TOURNAMENT
**Status:** ⚠️ ISSUES FOUND
- **Easy words:** 51 words
- **Medium words:** 53 words (includes duplicates from easy)
- **Hard words:** 44 words (includes duplicates from medium)
- **Duplicates found:**
  - "beautiful" appears in easy AND medium
  - "believe" appears in easy AND medium
  - "different" appears in easy AND medium
  - "delicious" appears in easy AND medium
  - "engineer" appears in easy AND medium
  - "friendship" appears in easy AND medium
  - "geography" appears in easy AND medium
  - "knowledge" appears in easy AND medium
  - "languages" appears in easy AND medium
  - "scientist" appears in easy AND medium
  - "sentences" appears in easy AND medium
  - And more...

---

## ISSUE 2: Ranked Mode Word Pool Balance

### Problem Statement
Ranked mode should:
- Use random mix of words from ALL weeks
- Keep balanced distribution (not just one difficulty)
- Provide variety across easy/medium/hard

### Analysis Results

**Current Implementation (script.js:3944-3970):**
```javascript
var easy = (data.easy || []).slice();
var medium = (data.medium || []).slice();
var hard = (data.hard || []).slice();
shuffleArray(easy); shuffleArray(medium); shuffleArray(hard);

// Equal integration: interleave easy/medium/hard evenly
var maxLen = Math.max(easy.length, medium.length, hard.length);
pool = [];
for (var wi = 0; wi < maxLen; wi++) {
  if (wi < easy.length) pool.push(easy[wi]);
  if (wi < medium.length) pool.push(medium[wi]);
  if (wi < hard.length) pool.push(hard[wi]);
}
```

**Status:** ✅ CORRECT
- Properly interleaves all three difficulty levels
- Creates balanced pool across difficulties
- Shuffles each difficulty before interleaving

---

## ISSUE 3: Bomb Word Selection

### Problem Statement
Bomb words should ONLY come from hard difficulty words.

### Analysis Results

**Current Implementation (words.py:1253-1260):**
```python
def get_bomb_words_by_difficulty(group="group1", difficulty="hard"):
    """Return words from specified difficulty for bomb word selection (used for tournament)."""
    if group == "tournament":
        # For tournament group, return words from the specified difficulty
        return get_group_words(group, difficulty)
    else:
        # For other groups, use original behavior (hard words only)
        return get_bomb_words(group)
```

**Status:** ⚠️ ISSUE FOUND
- **Tournament group:** Allows bomb words from ANY difficulty (easy, medium, hard)
- **Other groups:** Correctly use hard words only via `get_bomb_words()`
- **Problem:** Tournament group should also restrict to hard words only

---

## ISSUE 4: Leaderboard Scoring (Ranked vs Regular)

### Problem Statement
- Ranked scores should NOT appear in regular mode leaderboards
- Regular mode scores should NOT appear in ranked leaderboard
- Each mode should have separate score tracking

### Analysis Results

**Current Implementation (app.py:1604-1641):**
```python
# Update player profile
update_profile(name, {
    "score": score, "accuracy": accuracy, "streak": streak,
    "words_completed": words_completed,
    "bombs_correct": bombs_correct, "time_bonuses": time_bonuses,
    "is_ranked": is_ranked, "difficulty": difficulty,
    "team_id": team_id, "team_name": team_name,
    "reached_x3": reached_x3,
}, group)

# Save to leaderboard for both ranked and non-ranked games
if USE_FIRESTORE:
    save_leaderboard_entry(name, score, streak, difficulty, group,
                           avatar=p_avatar, team_name=p_team_name, team_emoji=p_team_emoji, team_id=team_id)
```

**Status:** ⚠️ ISSUE FOUND
- **Problem:** All scores (ranked AND regular) are saved to same leaderboard collection
- **Missing:** Separate collection or flag to distinguish ranked vs regular scores
- **Impact:** Ranked scores appear in regular mode leaderboards and vice versa

---

## ISSUE 5: Week Word Count Distribution

### Problem Statement
Each week should have adequate number of words (not just 2 words like Group 2 Medium Week 2).

### Analysis Results

**Group 2 Medium Difficulty:**
- Total medium words: 83
- WORDS_PER_WEEK: 10 (default)
- Expected weeks: 8-9
- **Week 2 actual words:** Only 2 words (Chinatown, Airplane)

**Root Cause:** 
- Group 2 medium list has heavy duplication
- After deduplication, actual unique words are much fewer
- Word chunking algorithm doesn't account for duplicates

**Status:** 🔴 CRITICAL
- Week distribution is broken due to duplicates in word lists
- Users get insufficient word variety per week

---

## ISSUE 6: Audio & Image Issues

### Problem Statement
- Some words have missing audio (e.g., "Bottle Opener")
- Some images don't relate to words
- Audio should be pre-cached for performance

### Analysis Results

**Audio Status:**
- Pre-cached audio directory: `audio/` (1574 items)
- TTS fallback: ElevenLabs → Edge TTS (re-enabled)
- **Missing audio words:** Need to check against actual word lists
- **Bottle Opener issue:** Multi-word phrase, may have underscore/space mismatch

**Image Status:**
- WORD_IMAGES dict: Contains emoji mappings
- PIXABAY_IMAGES: Local image references
- Wikipedia fallback: For words without local images
- **Unrelated images:** Likely from Wikipedia API returning wrong results

**Status:** ⚠️ NEEDS INVESTIGATION
- Audio caching is working (TTS re-enabled)
- Image quality depends on Wikipedia API accuracy
- Multi-word phrases need special handling (spaces vs underscores)

---

## Summary of Findings

| Issue | Group1 | Group2 | Group3 | Group4 | Tournament | Severity |
|-------|--------|--------|--------|--------|-----------|----------|
| Word duplicates | ✅ | 🔴 | 🔴 | 🔴 | 🔴 | CRITICAL |
| Ranked pool balance | ✅ | ✅ | ✅ | ✅ | ✅ | OK |
| Bomb word selection | ✅ | ✅ | ✅ | ✅ | 🔴 | HIGH |
| Leaderboard mixing | 🔴 | 🔴 | 🔴 | 🔴 | 🔴 | CRITICAL |
| Week word counts | ✅ | 🔴 | 🔴 | 🔴 | 🔴 | CRITICAL |
| Audio/Image issues | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | MEDIUM |

---

## Recommended Actions (Priority Order)

### 1. CRITICAL: Fix Word List Duplicates (Groups 2, 3, 4, Tournament)
- Remove all duplicate words within each difficulty level
- Ensure words don't appear in multiple difficulties
- Rebalance week distribution after deduplication

### 2. CRITICAL: Fix Leaderboard Score Separation
- Add `is_ranked` flag to leaderboard entries
- Create separate ranked leaderboard view
- Filter regular mode leaderboard to exclude ranked scores

### 3. HIGH: Fix Tournament Bomb Words
- Restrict bomb words to hard difficulty only
- Update `get_bomb_words_by_difficulty()` for tournament group

### 4. MEDIUM: Fix Audio/Image Issues
- Audit missing audio files for multi-word phrases
- Verify image mappings are correct
- Consider pre-generating all missing audio

### 5. MEDIUM: Improve Week Distribution
- After fixing duplicates, rebalance weeks
- Ensure minimum words per week (e.g., 8-10)

---

## Questions for Clarification

1. **Word List Source:** Are the duplicate words intentional (for spaced repetition) or accidental?
2. **Ranked Leaderboard:** Should ranked scores be completely separate from regular mode leaderboards?
3. **Audio Generation:** Should we pre-generate all audio or rely on TTS API?
4. **Image Quality:** Are incorrect images acceptable or should we use only local/verified images?
5. **Week Distribution:** What's the minimum acceptable words per week?

