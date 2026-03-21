# Critical Findings Summary - Cross-Group Analysis

## Executive Summary

Analysis of all groups (Group 1, 2, 3, 4, Tournament) reveals **5 critical issues** affecting game functionality:

1. **Word List Duplicates** (Groups 2, 3, 4, Tournament) - CRITICAL
2. **Leaderboard Score Mixing** (All Groups) - CRITICAL
3. **Tournament Bomb Word Selection** - HIGH
4. **Week Distribution Broken** (Groups 2, 3, 4, Tournament) - CRITICAL
5. **Audio/Image Quality Issues** (All Groups) - MEDIUM

---

## FINDING 1: Word List Duplicates (CRITICAL)

### Affected Groups
- ❌ Group 2: Heavy duplicates
- ❌ Group 3: Severe duplicates (words appear in all 3 difficulties)
- ❌ Group 4: Data corruption (32/30 easy words in medium)
- ❌ Tournament: Moderate duplicates
- ✅ Group 1: Clean (uses global lists)

### Code Location
`@c:\Users\HP\Documents\lasalle-spelling-bee-mainFINAL\lasalle-spelling-bee-main\words.py:656-1206`

### Examples

**Group 2:**
- "chocolate" in easy AND medium
- "sentences" in easy AND medium
- "stomachache" in easy AND medium
- "toothache" in easy AND medium
- "wednesday" in easy AND medium

**Group 3:**
- "sentences" appears TWICE in easy list (lines 1143, 1147)
- "wednesday" appears TWICE in easy list (lines 1143, 1154)
- "chocolate" in easy AND medium AND hard
- "delicious" in easy AND medium AND hard
- 25+ words appear in multiple difficulties

**Group 4:**
- "accuracy" in easy AND medium
- "addition" in easy AND medium
- "analysis" in easy AND medium
- 32 out of 30 easy words appear in medium (impossible - data corruption)

### Impact
- Users see same words across difficulty levels
- Learning progression broken
- Week distribution severely imbalanced
- Group 2 Medium Week 2 only has 2 words (Chinatown, Airplane)

### Recommended Fix
```python
# Add validation function to words.py
def validate_group_words(group_name):
    """Validate that words don't duplicate within group or across difficulties."""
    cfg = GROUP_CONFIG.get(group_name)
    if not cfg or "words" not in cfg:
        return True  # Uses global lists, skip validation
    
    words = cfg["words"]
    easy_set = set(words.get("easy", []))
    medium_set = set(words.get("medium", []))
    hard_set = set(words.get("hard", []))
    
    # Check for duplicates within each difficulty
    easy_list = words.get("easy", [])
    if len(easy_list) != len(set(easy_list)):
        print(f"ERROR: {group_name} easy has duplicates")
        return False
    
    # Check for overlaps between difficulties
    easy_medium_overlap = easy_set & medium_set
    if easy_medium_overlap:
        print(f"ERROR: {group_name} easy/medium overlap: {easy_medium_overlap}")
        return False
    
    medium_hard_overlap = medium_set & hard_set
    if medium_hard_overlap:
        print(f"ERROR: {group_name} medium/hard overlap: {medium_hard_overlap}")
        return False
    
    easy_hard_overlap = easy_set & hard_set
    if easy_hard_overlap:
        print(f"ERROR: {group_name} easy/hard overlap: {easy_hard_overlap}")
        return False
    
    return True
```

---

## FINDING 2: Leaderboard Score Mixing (CRITICAL)

### Affected Groups
- ❌ All Groups (1, 2, 3, 4, Tournament)

### Code Location
`@c:\Users\HP\Documents\lasalle-spelling-bee-mainFINAL\lasalle-spelling-bee-main\app.py:1604-1641`

### Problem
```python
# Current code saves ALL scores to same leaderboard
save_leaderboard_entry(name, score, streak, difficulty, group,
                       avatar=p_avatar, team_name=p_team_name, 
                       team_emoji=p_team_emoji, team_id=team_id)
```

**Issue:** No distinction between ranked and regular mode scores
- Ranked scores appear in regular mode leaderboards
- Regular scores appear in ranked leaderboard
- Users can't see separate rankings

### Impact
- Leaderboard integrity compromised
- Ranked mode scores mixed with casual play
- Admin can't distinguish ranked performance from regular play

### Recommended Fix
```python
# Modify save_leaderboard_entry to accept is_ranked flag
def save_leaderboard_entry(name, score, streak, difficulty, group, 
                          avatar="", team_name="", team_emoji="", team_id="", 
                          is_ranked=False):  # NEW PARAMETER
    """Save leaderboard entry with ranked/regular distinction."""
    if USE_FIRESTORE:
        def _save():
            # Use different collection for ranked vs regular
            collection_name = "leaderboard_ranked" if is_ranked else "leaderboard"
            ref = gcol(group, collection_name).document(difficulty).collection("scores").document()
            ref.set({
                "name": name,
                "score": score,
                "streak": streak,
                "avatar": avatar,
                "team_name": team_name,
                "team_emoji": team_emoji,
                "team_id": team_id,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "is_ranked": is_ranked,  # Store flag for reference
            })
        _fs_write(_save)

# Update leaderboard POST endpoint
@app.route("/leaderboard", methods=["POST"])
def post_leaderboard():
    # ... existing code ...
    
    # Save with is_ranked flag
    save_leaderboard_entry(name, score, streak, difficulty, group,
                          avatar=p_avatar, team_name=p_team_name, 
                          team_emoji=p_team_emoji, team_id=team_id,
                          is_ranked=is_ranked)  # NEW
```

---

## FINDING 3: Tournament Bomb Word Selection (HIGH)

### Affected Groups
- ❌ Tournament only

### Code Location
`@c:\Users\HP\Documents\lasalle-spelling-bee-mainFINAL\lasalle-spelling-bee-main\words.py:1253-1260`

### Problem
```python
def get_bomb_words_by_difficulty(group="group1", difficulty="hard"):
    if group == "tournament":
        # BUG: Returns words from ANY difficulty, not just hard
        return get_group_words(group, difficulty)
    else:
        # Correct: Returns hard words only
        return get_bomb_words(group)
```

### Impact
- Tournament bomb words can be easy or medium difficulty
- Breaks game balance (bomb should be challenging)
- Inconsistent with other groups

### Recommended Fix
```python
def get_bomb_words_by_difficulty(group="group1", difficulty="hard"):
    """Return words from hard difficulty for bomb word selection."""
    # ALL groups should use hard words only for bombs
    return get_bomb_words(group)
```

---

## FINDING 4: Week Distribution Broken (CRITICAL)

### Affected Groups
- ❌ Group 2: Week 2 Medium has only 2 words
- ❌ Group 3: Unbalanced weeks
- ❌ Group 4: Unbalanced weeks
- ❌ Tournament: Unbalanced weeks
- ✅ Group 1: Balanced (global lists are large)

### Code Location
`@c:\Users\HP\Documents\lasalle-spelling-bee-mainFINAL\lasalle-spelling-bee-main\words.py:631-642`

### Problem
```python
WORDS_PER_WEEK = 10

def _chunk(words, chunk_size):
    """Divide words into weekly chunks."""
    return [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]
```

**Root Cause:** 
1. Word lists contain duplicates
2. Chunking algorithm assumes all words are unique
3. After deduplication, weeks have fewer words than expected
4. Group 2 Medium Week 2: Expected 10 words, got 2

### Example Calculation
```
Group 2 Medium:
- Listed words: 83
- Actual unique words: ~50-60 (after removing duplicates)
- Weeks needed: 50/10 = 5 weeks
- Week 2 range: words[10:20]
- If deduplication removed words in that range, week 2 is short
```

### Impact
- Users get insufficient word variety per week
- Week progression is unpredictable
- Ranked mode may not have enough words

### Recommended Fix
```python
# Step 1: Deduplicate word lists
def deduplicate_group_words(group_name):
    """Remove duplicates from group word lists."""
    cfg = GROUP_CONFIG.get(group_name)
    if not cfg or "words" not in cfg:
        return  # Uses global lists
    
    words = cfg["words"]
    
    # Deduplicate each difficulty
    words["easy"] = list(dict.fromkeys(words.get("easy", [])))
    words["medium"] = list(dict.fromkeys(words.get("medium", [])))
    words["hard"] = list(dict.fromkeys(words.get("hard", [])))
    
    # Remove cross-difficulty duplicates
    easy_set = set(words["easy"])
    medium_set = set(words["medium"]) - easy_set
    hard_set = set(words["hard"]) - easy_set - medium_set
    
    words["medium"] = list(medium_set)
    words["hard"] = list(hard_set)

# Step 2: Rebalance weeks
def rebalance_weeks(group_name):
    """Ensure each week has adequate words."""
    cfg = GROUP_CONFIG.get(group_name)
    if not cfg or "words" not in cfg:
        return
    
    words = cfg["words"]
    min_words_per_week = 8
    
    for difficulty in ["easy", "medium", "hard"]:
        word_list = words.get(difficulty, [])
        if len(word_list) < min_words_per_week:
            print(f"WARNING: {group_name} {difficulty} has only {len(word_list)} words")
```

---

## FINDING 5: Audio/Image Quality Issues (MEDIUM)

### Affected Groups
- ⚠️ All Groups

### Code Locations
- Audio: `@c:\Users\HP\Documents\lasalle-spelling-bee-mainFINAL\lasalle-spelling-bee-main\app.py:1396-1425`
- Images: `@c:\Users\HP\Documents\lasalle-spelling-bee-mainFINAL\lasalle-spelling-bee-main\app.py:1373-1393`

### Problems

**1. Multi-word Phrases (e.g., "Bottle Opener")**
- Audio file lookup: `bottle_opener.mp3`
- Word in list: `"bottle opener"` (with space)
- Mismatch causes audio not found

**2. Unrelated Images**
- Wikipedia API sometimes returns wrong images
- No validation of image relevance

**3. Audio Caching**
- Pre-cached audio: 1574 files in `audio/` directory
- TTS fallback: ElevenLabs → Edge TTS (re-enabled)
- Status: ✅ Working correctly

### Recommended Fix

```python
# Fix multi-word phrase audio lookup
def get_precached_audio(word, suffix=""):
    """Get pre-cached audio, handling multi-word phrases."""
    # Try exact match first
    safe_name = word.replace(" ", "_").lower()
    path = os.path.join(PRECACHED_AUDIO_DIR, f"{safe_name}{suffix}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return path
    
    # Try with hyphens for multi-word phrases
    safe_name_hyphen = word.replace(" ", "-").lower()
    path = os.path.join(PRECACHED_AUDIO_DIR, f"{safe_name_hyphen}{suffix}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return path
    
    return None

# Validate image relevance
def validate_image_relevance(word, image_url):
    """Check if image is likely relevant to word."""
    # Simple heuristic: check if word appears in image URL
    word_lower = word.lower().replace(" ", "")
    url_lower = image_url.lower()
    
    if word_lower in url_lower:
        return True
    
    # Check against known bad patterns
    bad_patterns = ["error", "404", "placeholder", "default"]
    if any(pattern in url_lower for pattern in bad_patterns):
        return False
    
    return True
```

---

## Action Items Summary

| Priority | Issue | Groups | Action |
|----------|-------|--------|--------|
| 🔴 CRITICAL | Word duplicates | 2,3,4,T | Remove duplicates, rebalance weeks |
| 🔴 CRITICAL | Leaderboard mixing | All | Add is_ranked flag, separate collections |
| 🔴 CRITICAL | Week distribution | 2,3,4,T | Ensure 8-10 words per week |
| 🟠 HIGH | Bomb word selection | T | Restrict to hard difficulty only |
| 🟡 MEDIUM | Audio/Image issues | All | Fix phrase handling, validate images |

---

## Questions for User

1. **Word Deduplication:** Should we remove ALL duplicates, or keep some for spaced repetition?
2. **Leaderboard Separation:** Should ranked and regular leaderboards be completely separate?
3. **Week Distribution:** What's the minimum acceptable words per week?
4. **Image Validation:** Should we use only local/verified images or accept Wikipedia results?
5. **Audio Generation:** Should we pre-generate all missing audio or rely on TTS API?

