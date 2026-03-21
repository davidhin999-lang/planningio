# Remediation Plan - Critical Issues

## Overview
This document provides step-by-step remediation for the 5 critical issues found across all groups.

---

## ISSUE 1: Word List Duplicates (CRITICAL)

### Scope
- **Groups affected:** 2, 3, 4, Tournament
- **Severity:** CRITICAL - Breaks game progression
- **Estimated effort:** 4-6 hours

### Root Cause
Words were manually added to multiple difficulty levels without deduplication validation.

### Remediation Steps

#### Step 1: Audit Current State
```python
# Add to words.py for validation
def audit_group_words(group_name):
    """Audit word list for duplicates and overlaps."""
    cfg = GROUP_CONFIG.get(group_name)
    if not cfg or "words" not in cfg:
        return {"status": "uses_global_lists"}
    
    words = cfg["words"]
    easy = words.get("easy", [])
    medium = words.get("medium", [])
    hard = words.get("hard", [])
    
    # Check internal duplicates
    easy_dupes = [w for w in easy if easy.count(w) > 1]
    medium_dupes = [w for w in medium if medium.count(w) > 1]
    hard_dupes = [w for w in hard if hard.count(w) > 1]
    
    # Check cross-difficulty overlaps
    easy_set = set(easy)
    medium_set = set(medium)
    hard_set = set(hard)
    
    easy_medium_overlap = easy_set & medium_set
    medium_hard_overlap = medium_set & hard_set
    easy_hard_overlap = easy_set & hard_set
    
    return {
        "group": group_name,
        "easy_count": len(easy),
        "medium_count": len(medium),
        "hard_count": len(hard),
        "easy_internal_dupes": list(set(easy_dupes)),
        "medium_internal_dupes": list(set(medium_dupes)),
        "hard_internal_dupes": list(set(hard_dupes)),
        "easy_medium_overlap": list(easy_medium_overlap),
        "medium_hard_overlap": list(medium_hard_overlap),
        "easy_hard_overlap": list(easy_hard_overlap),
    }

# Run audit
for group in ["group2", "group3", "group4", "tournament"]:
    audit = audit_group_words(group)
    print(f"\n{group}: {audit}")
```

#### Step 2: Clean Word Lists
For each group (2, 3, 4, Tournament):

**Group 2:**
1. Remove internal duplicates from easy, medium, hard
2. Remove words that appear in multiple difficulties
3. Ensure: easy < medium < hard (in difficulty)
4. Target: ~40 easy, ~80 medium, ~150+ hard

**Group 3:**
1. Remove "sentences" and "wednesday" duplicates from easy
2. Remove all words appearing in multiple difficulties
3. Redistribute words to balance difficulties
4. Target: ~40 easy, ~80 medium, ~150+ hard

**Group 4:**
1. Fix data corruption (32/30 easy words in medium)
2. Remove all overlapping words
3. Rebalance difficulties
4. Target: ~30 easy, ~60 medium, ~60+ hard

**Tournament:**
1. Remove overlapping words between difficulties
2. Maintain current word pool size
3. Ensure balanced distribution

#### Step 3: Validate & Test
```python
# Add validation to app startup
def validate_all_groups():
    """Validate all group word lists on startup."""
    for group in VALID_GROUPS:
        if group == "group1":
            continue  # Uses global lists
        
        audit = audit_group_words(group)
        
        if audit.get("easy_internal_dupes"):
            print(f"ERROR: {group} has internal easy duplicates: {audit['easy_internal_dupes']}")
        
        if audit.get("easy_medium_overlap"):
            print(f"ERROR: {group} has easy/medium overlap: {audit['easy_medium_overlap']}")
        
        if audit.get("medium_hard_overlap"):
            print(f"ERROR: {group} has medium/hard overlap: {audit['medium_hard_overlap']}")
        
        if audit.get("easy_hard_overlap"):
            print(f"ERROR: {group} has easy/hard overlap: {audit['easy_hard_overlap']}")

# Call on app startup
validate_all_groups()
```

---

## ISSUE 2: Leaderboard Score Mixing (CRITICAL)

### Scope
- **Groups affected:** All (1, 2, 3, 4, Tournament)
- **Severity:** CRITICAL - Data integrity issue
- **Estimated effort:** 3-4 hours

### Root Cause
No distinction between ranked and regular mode scores in leaderboard storage.

### Remediation Steps

#### Step 1: Modify Leaderboard Entry Function
```python
# In app.py, update save_leaderboard_entry
def save_leaderboard_entry(name, score, streak, difficulty, group, 
                          avatar="", team_name="", team_emoji="", team_id="", 
                          is_ranked=False):
    """Save leaderboard entry with ranked/regular distinction."""
    if USE_FIRESTORE:
        def _save():
            # Use different collection for ranked vs regular
            if is_ranked:
                collection_name = "leaderboard_ranked"
            else:
                collection_name = "leaderboard"
            
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
                "is_ranked": is_ranked,
            })
        _fs_write(_save)
```

#### Step 2: Update Leaderboard POST Endpoint
```python
# In app.py, update post_leaderboard function
@app.route("/leaderboard", methods=["POST"])
def post_leaderboard():
    # ... existing code ...
    
    # Save to leaderboard for both ranked and non-ranked games
    if USE_FIRESTORE:
        prof = get_profile(name, group) or {}
        p_avatar = prof.get("avatar", "")
        p_team_name = prof.get("team_name", team_name)
        p_team_emoji = team_emoji
        
        # CHANGE: Pass is_ranked flag
        save_leaderboard_entry(name, score, streak, difficulty, group,
                               avatar=p_avatar, team_name=p_team_name, 
                               team_emoji=p_team_emoji, team_id=team_id,
                               is_ranked=is_ranked)  # ADD THIS
        
        board = load_leaderboard(group, is_ranked=is_ranked)  # ADD PARAMETER
        return jsonify({"ok": True, "board": board.get(difficulty, [])})
```

#### Step 3: Update Leaderboard Loading
```python
# In app.py, update load_leaderboard
def load_leaderboard(group="group1", is_ranked=False):
    """Load leaderboard entries, optionally filtered by ranked status."""
    ck = f"leaderboard:{group}:{'ranked' if is_ranked else 'regular'}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    
    if USE_FIRESTORE:
        def _load():
            board = {}
            collection_name = "leaderboard_ranked" if is_ranked else "leaderboard"
            
            for diff in ["easy", "medium", "hard"]:
                scores = []
                docs = gcol(group, collection_name).document(diff).collection("scores").stream()
                for d in docs:
                    scores.append(d.to_dict())
                
                # Sort by score descending, limit to top 15
                scores.sort(key=lambda x: x.get("score", 0), reverse=True)
                board[diff] = scores[:15]
            
            return board
        
        board = _fs_call(_load, default={}, timeout=5) or {}
    else:
        # JSON fallback
        board = load_leaderboard_json(group)
    
    cache_set(ck, board, CACHE_TTL_LEADERBOARD)
    return board
```

#### Step 4: Update Frontend Leaderboard Display
```javascript
// In script.js, update leaderboard fetch
function loadLeaderboard(difficulty) {
    var isRanked = isRankedMode ? "true" : "false";
    fetch(groupQS("/leaderboard?difficulty=" + difficulty + "&is_ranked=" + isRanked))
        .then(r => r.json())
        .then(data => {
            displayLeaderboard(data.board, difficulty);
        });
}
```

---

## ISSUE 3: Tournament Bomb Word Selection (HIGH)

### Scope
- **Groups affected:** Tournament only
- **Severity:** HIGH - Game balance issue
- **Estimated effort:** 30 minutes

### Remediation Steps

#### Step 1: Fix Bomb Word Function
```python
# In words.py, update get_bomb_words_by_difficulty
def get_bomb_words_by_difficulty(group="group1", difficulty="hard"):
    """Return hard words only for bomb word selection (all groups)."""
    # ALL groups use hard words for bombs, regardless of difficulty parameter
    return get_bomb_words(group)
```

#### Step 2: Update Frontend Bomb Word Logic
```javascript
// In script.js, ensure bomb words always come from hard pool
function checkBombWord() {
    if (!allBombWords || allBombWords.length === 0) {
        isBombWord = false;
        return;
    }
    
    // Bomb words should always be from hard difficulty
    if (Math.random() < BOMB_CHANCE) {
        var idx = Math.floor(Math.random() * allBombWords.length);
        currentWord = allBombWords[idx];
        isBombWord = true;
        showBombIndicator();
    }
}
```

---

## ISSUE 4: Week Distribution (CRITICAL)

### Scope
- **Groups affected:** 2, 3, 4, Tournament
- **Severity:** CRITICAL - Breaks game progression
- **Estimated effort:** 2-3 hours (after Issue 1 is fixed)

### Remediation Steps

#### Step 1: Verify Minimum Words Per Week
```python
# In words.py, add validation
WORDS_PER_WEEK = 10
MIN_WORDS_PER_WEEK = 8

def validate_week_distribution(group_name):
    """Ensure each week has minimum words."""
    cfg = GROUP_CONFIG.get(group_name)
    if not cfg or "words" not in cfg:
        return True  # Uses global lists
    
    words = cfg["words"]
    
    for difficulty in ["easy", "medium", "hard"]:
        word_list = words.get(difficulty, [])
        weeks = _chunk(word_list, WORDS_PER_WEEK)
        
        for week_num, week_words in enumerate(weeks, 1):
            if len(week_words) < MIN_WORDS_PER_WEEK:
                print(f"ERROR: {group_name} {difficulty} week {week_num} has only {len(week_words)} words")
                return False
    
    return True
```

#### Step 2: Rebalance After Deduplication
After Issue 1 (word deduplication) is complete:

```python
# Recalculate weeks for affected groups
# Group 2: Redistribute 83 unique words into balanced weeks
# Group 3: Redistribute 200+ unique words into balanced weeks
# Group 4: Redistribute 150+ unique words into balanced weeks
# Tournament: Redistribute words into balanced weeks

# Example for Group 2:
# Current: 40 easy, 83 medium, 194 hard
# After dedup: ~40 easy, ~50 medium, ~120 hard
# Weeks: easy=4, medium=5, hard=12
```

---

## ISSUE 5: Audio/Image Quality (MEDIUM)

### Scope
- **Groups affected:** All
- **Severity:** MEDIUM - User experience issue
- **Estimated effort:** 2-3 hours

### Remediation Steps

#### Step 1: Fix Multi-word Phrase Audio Lookup
```python
# In app.py, update get_precached_audio
def get_precached_audio(word, suffix=""):
    """Get pre-cached audio, handling multi-word phrases."""
    # Try with underscore (current format)
    safe_name = word.replace(" ", "_").lower()
    path = os.path.join(PRECACHED_AUDIO_DIR, f"{safe_name}{suffix}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return path
    
    # Try with hyphen (alternative format)
    safe_name_hyphen = word.replace(" ", "-").lower()
    path = os.path.join(PRECACHED_AUDIO_DIR, f"{safe_name_hyphen}{suffix}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return path
    
    # Try without spaces (last resort)
    safe_name_no_space = word.replace(" ", "").lower()
    path = os.path.join(PRECACHED_AUDIO_DIR, f"{safe_name_no_space}{suffix}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 100:
        return path
    
    return None
```

#### Step 2: Generate Missing Audio
```python
# Create script to generate missing audio for multi-word phrases
# Priority: bottle opener, food court, ice hockey, movie theater, etc.

missing_audio = [
    "bottle_opener", "bungee_jumping", "chicken_wings", "chopping_board",
    "christmas_tree", "computer_room", "food_court", "household_chores",
    "ice_hockey", "microwave_oven", "movie_theater", "shopping_bag",
    "shopping_center", "under_pressure", "washing_machine", "weekly_planner",
    "wooden_spoon", "admiration_mark", "bubble_speech", "dining_room",
    "down_town", "excuse_me", "fire_fighter", "green_point", "guinea_pig",
    "jelly_fish", "office_building", "police_officer", "post_office",
    "sales_assistant", "sea_lion", "stand_up", "steering_wheel",
    "thirty_three", "train_station", "united_kingdom", "united_states",
    "waking_up"
]

# Generate using TTS API (ElevenLabs or Edge TTS)
for word in missing_audio:
    # Generate and cache audio
    pass
```

#### Step 3: Validate Image Relevance
```python
# In app.py, add image validation
def validate_image_relevance(word, image_url):
    """Check if image is likely relevant to word."""
    if not image_url:
        return False
    
    word_lower = word.lower().replace(" ", "")
    url_lower = image_url.lower()
    
    # Check if word appears in URL
    if word_lower in url_lower:
        return True
    
    # Check against known bad patterns
    bad_patterns = ["error", "404", "placeholder", "default", "notfound"]
    if any(pattern in url_lower for pattern in bad_patterns):
        return False
    
    # Accept Wikipedia images as fallback
    if "wikipedia" in url_lower or "commons.wikimedia" in url_lower:
        return True
    
    return False
```

---

## Implementation Timeline

| Phase | Issues | Duration | Priority |
|-------|--------|----------|----------|
| Phase 1 | Word duplicates (Issue 1) | 4-6 hours | 🔴 CRITICAL |
| Phase 2 | Week distribution (Issue 4) | 2-3 hours | 🔴 CRITICAL |
| Phase 3 | Leaderboard mixing (Issue 2) | 3-4 hours | 🔴 CRITICAL |
| Phase 4 | Bomb word selection (Issue 3) | 30 min | 🟠 HIGH |
| Phase 5 | Audio/Image quality (Issue 5) | 2-3 hours | 🟡 MEDIUM |

**Total estimated time:** 12-17 hours

---

## Testing Checklist

- [ ] Validate all groups have no word duplicates
- [ ] Verify each week has 8-10 words minimum
- [ ] Test ranked leaderboard is separate from regular
- [ ] Test regular leaderboard doesn't show ranked scores
- [ ] Verify tournament bomb words are hard difficulty only
- [ ] Test multi-word phrase audio loads correctly
- [ ] Verify image relevance for all words
- [ ] Test week progression for all groups
- [ ] Verify ranked mode word pool is balanced

