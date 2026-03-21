# Implementation Strategy - User Requirements

## Overview
This document outlines the implementation approach for all 6 critical issues based on user requirements.

---

## REQUIREMENT 1: Word Deduplication with Target Counts

### User Requirements
- Remove duplicates within same group/difficulty
- Groups can share words (part of standard spelling lists)
- Target word counts:
  - **Group 1:** 240 words
  - **Group 2:** 200 words
  - **Group 3:** 240 words
  - **Group 4:** 300 words
  - **Tournament:** 200 words
- If after deduplication count is lower, keep close to target (acceptable variance)

### Current State Analysis

**Group 1 (Global Lists):**
- Easy: ~80 words
- Medium: ~100 words
- Hard: ~150 words (after dedup)
- **Total:** ~330 words ✅ (exceeds 240, acceptable)

**Group 2:**
- Easy: 40 words
- Medium: 83 words (with duplicates)
- Hard: 194 words (with duplicates)
- **Current total:** 317 words
- **After dedup estimate:** ~200-220 words ✅ (target 200)

**Group 3:**
- Easy: 40 words (with internal duplicates)
- Medium: 100+ words (with duplicates)
- Hard: 140+ words (with duplicates)
- **Current total:** 280+ words
- **After dedup estimate:** ~220-240 words ✅ (target 240)

**Group 4:**
- Easy: 30 words
- Medium: 69 words (with duplicates)
- Hard: 67 words (with duplicates)
- **Current total:** 166 words
- **After dedup estimate:** ~140-160 words ❌ (target 300, will be short)
- **Action:** Need to add ~140-160 more words to reach target

**Tournament:**
- Easy: 51 words
- Medium: 53 words (with duplicates)
- Hard: 44 words (with duplicates)
- **Current total:** 148 words
- **After dedup estimate:** ~120-130 words ❌ (target 200, will be short)
- **Action:** Need to add ~70-80 more words to reach target

### Implementation Approach

#### Phase 1: Deduplicate Existing Words
```python
def deduplicate_group_words(group_name):
    """Remove duplicates within group, maintain cross-difficulty separation."""
    cfg = GROUP_CONFIG.get(group_name)
    if not cfg or "words" not in cfg:
        return  # Uses global lists
    
    words = cfg["words"]
    
    # Step 1: Remove internal duplicates (preserve order)
    for difficulty in ["easy", "medium", "hard"]:
        word_list = words.get(difficulty, [])
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for w in word_list:
            if w.lower() not in seen:
                seen.add(w.lower())
                unique.append(w)
        words[difficulty] = unique
    
    # Step 2: Remove cross-difficulty duplicates
    # Hard should not contain easy or medium words
    # Medium should not contain easy words
    easy_set = set(w.lower() for w in words.get("easy", []))
    medium_set = set(w.lower() for w in words.get("medium", []))
    hard_set = set(w.lower() for w in words.get("hard", []))
    
    # Filter medium: remove easy words
    words["medium"] = [w for w in words["medium"] if w.lower() not in easy_set]
    
    # Filter hard: remove easy and medium words
    words["hard"] = [w for w in words["hard"] 
                     if w.lower() not in easy_set and w.lower() not in medium_set]
    
    return words
```

#### Phase 2: Audit Word Counts
```python
def audit_group_word_counts():
    """Check if groups meet target word counts."""
    targets = {
        "group1": 240,
        "group2": 200,
        "group3": 240,
        "group4": 300,
        "tournament": 200,
    }
    
    for group_name, target in targets.items():
        cfg = GROUP_CONFIG.get(group_name)
        if not cfg or "words" not in cfg:
            continue
        
        words = cfg["words"]
        total = sum(len(words.get(d, [])) for d in ["easy", "medium", "hard"])
        
        status = "✅" if total >= target * 0.9 else "❌"
        print(f"{status} {group_name}: {total}/{target} words")
        
        if total < target * 0.9:
            deficit = target - total
            print(f"   Need ~{deficit} more words")
```

#### Phase 3: Add Missing Words (Groups 4 & Tournament)

**For Group 4 (need ~140-160 more words):**
- Source from Group 1 global lists (words not already in Group 4)
- Source from Group 2/3 (if appropriate difficulty level)
- Add common spelling bee words from standard lists

**For Tournament (need ~70-80 more words):**
- Source from Group 1 global lists
- Source from Group 2/3 (if appropriate difficulty level)
- Add competition-level words

### Implementation Code

```python
# In words.py, after GROUP_CONFIG definition:

def deduplicate_all_groups():
    """Deduplicate all group word lists."""
    for group_name in ["group2", "group3", "group4", "tournament"]:
        deduplicate_group_words(group_name)

def validate_word_counts():
    """Validate all groups meet minimum word requirements."""
    targets = {
        "group1": 240,
        "group2": 200,
        "group3": 240,
        "group4": 300,
        "tournament": 200,
    }
    
    for group_name, target in targets.items():
        cfg = GROUP_CONFIG.get(group_name)
        if not cfg or "words" not in cfg:
            continue
        
        words = cfg["words"]
        total = sum(len(words.get(d, [])) for d in ["easy", "medium", "hard"])
        
        if total < target * 0.9:
            print(f"WARNING: {group_name} has {total} words, target is {target}")

# Call on module load
deduplicate_all_groups()
validate_word_counts()
```

---

## REQUIREMENT 2: Leaderboard Separation (Ranked vs Regular)

### User Requirements
- **Regular Mode Leaderboard:** Individual scores in easy, medium, hard
- **Ranked Mode Leaderboard:** Team scores, click team to see individual ranked scores
- Completely separate collections in Firebase

### Architecture

#### Regular Mode Leaderboard Structure
```
leaderboard/
├── easy/
│   └── scores/
│       ├── player1: {name, score, streak, avatar, team_name, timestamp}
│       ├── player2: {...}
│       └── ...
├── medium/
│   └── scores/
│       └── ...
└── hard/
    └── scores/
        └── ...
```

#### Ranked Mode Leaderboard Structure
```
leaderboard_ranked/
├── easy/
│   └── team_scores/
│       ├── team1: {team_name, team_emoji, total_score, member_count, timestamp}
│       ├── team2: {...}
│       └── ...
├── medium/
│   └── team_scores/
│       └── ...
├── hard/
│   └── team_scores/
│       └── ...
└── individual_scores/  # For viewing individual ranked scores
    ├── player1: {name, team_id, team_name, ranked_score, difficulty, timestamp}
    └── ...
```

### Implementation Code

```python
# In app.py, update leaderboard functions:

def save_leaderboard_entry(name, score, streak, difficulty, group, 
                          avatar="", team_name="", team_emoji="", team_id="", 
                          is_ranked=False):
    """Save leaderboard entry with ranked/regular distinction."""
    if USE_FIRESTORE:
        def _save():
            if is_ranked:
                # Save to ranked individual scores
                ref = gcol(group, "leaderboard_ranked").document("individual_scores").collection("scores").document(name)
                ref.set({
                    "name": name,
                    "score": score,
                    "difficulty": difficulty,
                    "team_id": team_id,
                    "team_name": team_name,
                    "avatar": avatar,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                }, merge=True)
            else:
                # Save to regular leaderboard
                ref = gcol(group, "leaderboard").document(difficulty).collection("scores").document()
                ref.set({
                    "name": name,
                    "score": score,
                    "streak": streak,
                    "avatar": avatar,
                    "team_name": team_name,
                    "team_emoji": team_emoji,
                    "team_id": team_id,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                })
        _fs_write(_save)

def save_team_ranked_score(team_id, team_name, team_emoji, total_score, member_count, difficulty, group):
    """Save team ranked score."""
    if USE_FIRESTORE:
        def _save():
            ref = gcol(group, "leaderboard_ranked").document(difficulty).collection("team_scores").document(team_id)
            ref.set({
                "team_id": team_id,
                "team_name": team_name,
                "team_emoji": team_emoji,
                "total_score": total_score,
                "member_count": member_count,
                "timestamp": firestore.SERVER_TIMESTAMP,
            }, merge=True)
        _fs_write(_save)

def load_leaderboard(group="group1", is_ranked=False, difficulty="easy"):
    """Load leaderboard entries."""
    ck = f"leaderboard:{group}:{difficulty}:{'ranked' if is_ranked else 'regular'}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    
    if USE_FIRESTORE:
        def _load():
            if is_ranked:
                # Load team scores for ranked
                scores = []
                docs = gcol(group, "leaderboard_ranked").document(difficulty).collection("team_scores").stream()
                for d in docs:
                    scores.append(d.to_dict())
                scores.sort(key=lambda x: x.get("total_score", 0), reverse=True)
                return scores[:15]
            else:
                # Load individual scores for regular
                scores = []
                docs = gcol(group, "leaderboard").document(difficulty).collection("scores").stream()
                for d in docs:
                    scores.append(d.to_dict())
                scores.sort(key=lambda x: x.get("score", 0), reverse=True)
                return scores[:15]
        
        result = _fs_call(_load, default=[], timeout=5) or []
    else:
        result = []
    
    cache_set(ck, result, CACHE_TTL_LEADERBOARD)
    return result

def load_team_ranked_members(team_id, group="group1"):
    """Load individual ranked scores for a team."""
    ck = f"team_ranked:{group}:{team_id}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    
    if USE_FIRESTORE:
        def _load():
            members = []
            docs = gcol(group, "leaderboard_ranked").document("individual_scores").collection("scores").where("team_id", "==", team_id).stream()
            for d in docs:
                members.append(d.to_dict())
            members.sort(key=lambda x: x.get("score", 0), reverse=True)
            return members
        
        result = _fs_call(_load, default=[], timeout=5) or []
    else:
        result = []
    
    cache_set(ck, result, CACHE_TTL_LEADERBOARD)
    return result
```

---

## REQUIREMENT 3: Week Distribution Strategy

### User Requirements
- Minimum 10 words per difficulty (30 total per week)
- Ranked mode uses ALL words from selected week (except bombs)
- Should not have many weeks
- Need to calculate optimal weeks per group

### Analysis & Calculation

**Optimal Week Count Formula:**
```
weeks = total_words / (words_per_difficulty * 3)
weeks = total_words / 30
```

**By Group:**
- **Group 1:** 330 words ÷ 30 = 11 weeks ✅
- **Group 2:** 200 words ÷ 30 = 6-7 weeks ✅
- **Group 3:** 240 words ÷ 30 = 8 weeks ✅
- **Group 4:** 300 words ÷ 30 = 10 weeks ✅
- **Tournament:** 200 words ÷ 30 = 6-7 weeks ✅

**Week Distribution Algorithm:**
```python
def calculate_optimal_weeks(total_easy, total_medium, total_hard):
    """Calculate optimal weeks ensuring min 10 words per difficulty."""
    # Find maximum weeks where all difficulties have >= 10 words
    max_weeks = min(
        total_easy // 10,
        total_medium // 10,
        total_hard // 10
    )
    return max_weeks

# Example for Group 2:
# Easy: 40 words → 40/10 = 4 weeks max
# Medium: 50 words → 50/10 = 5 weeks max
# Hard: 120 words → 120/10 = 12 weeks max
# Optimal: min(4, 5, 12) = 4 weeks
# Distribution: Easy 10/week, Medium 10-13/week, Hard 30/week
```

### Implementation Code

```python
def _chunk_balanced(easy, medium, hard, min_per_difficulty=10):
    """Divide words into weeks ensuring min words per difficulty."""
    # Calculate max weeks
    max_weeks = min(
        len(easy) // min_per_difficulty,
        len(medium) // min_per_difficulty,
        len(hard) // min_per_difficulty
    )
    
    if max_weeks == 0:
        max_weeks = 1
    
    # Distribute words evenly across weeks
    weeks = []
    for week_num in range(max_weeks):
        easy_start = week_num * (len(easy) // max_weeks)
        easy_end = (week_num + 1) * (len(easy) // max_weeks)
        if week_num == max_weeks - 1:
            easy_end = len(easy)
        
        medium_start = week_num * (len(medium) // max_weeks)
        medium_end = (week_num + 1) * (len(medium) // max_weeks)
        if week_num == max_weeks - 1:
            medium_end = len(medium)
        
        hard_start = week_num * (len(hard) // max_weeks)
        hard_end = (week_num + 1) * (len(hard) // max_weeks)
        if week_num == max_weeks - 1:
            hard_end = len(hard)
        
        weeks.append({
            "week": week_num + 1,
            "easy": easy[easy_start:easy_end],
            "medium": medium[medium_start:medium_end],
            "hard": hard[hard_start:hard_end],
        })
    
    return weeks, max_weeks

# Update GROUP_CONFIG to use balanced chunking
for group_name in ["group2", "group3", "group4", "tournament"]:
    cfg = GROUP_CONFIG[group_name]
    if "words" in cfg:
        easy = cfg["words"].get("easy", [])
        medium = cfg["words"].get("medium", [])
        hard = cfg["words"].get("hard", [])
        
        weeks, week_count = _chunk_balanced(easy, medium, hard)
        cfg["weeks"] = week_count
        cfg["week_distribution"] = weeks
```

### Ranked Mode Week Selection

```python
def get_ranked_week_words(group="group1", week=None):
    """Get all words from a specific week for ranked mode."""
    if week is None:
        week = get_week_key()
    
    cfg = GROUP_CONFIG.get(group)
    if not cfg:
        return []
    
    # Get words from specified week
    easy = get_group_words(group, "easy", week)
    medium = get_group_words(group, "medium", week)
    hard = get_group_words(group, "hard", week)
    
    # Combine all words (except bombs will be filtered in game logic)
    all_words = easy + medium + hard
    return all_words
```

---

## REQUIREMENT 4: Tournament Bomb Words (Hard Only)

### Implementation
```python
# In words.py, fix bomb word function:

def get_bomb_words_by_difficulty(group="group1", difficulty="hard"):
    """Return hard words only for bomb word selection (all groups)."""
    # ALL groups use hard words for bombs, regardless of difficulty parameter
    return get_bomb_words(group)
```

---

## REQUIREMENT 5: Audio Generation & Caching Strategy

### User Requirements
- On-demand TTS generation (not pre-cached)
- Cache generated audio for fast loading
- Smooth game performance

### Recommended Approach

**Strategy: Lazy Loading with Progressive Caching**

1. **On First Play:** Generate audio on-demand using TTS API
2. **Cache Locally:** Save generated audio to `audio/` directory
3. **On Subsequent Plays:** Load from cache (instant)
4. **Fallback:** If generation fails, use silent playback

### Implementation Code

```python
# In app.py, update TTS generation:

AUDIO_CACHE_DIR = os.path.join(BASE_DIR, "audio")
AUDIO_CACHE_TIMEOUT = 3600  # 1 hour before re-generating

def get_or_generate_audio(word, voice="en-US-AriaNeural", suffix=""):
    """Get cached audio or generate on-demand."""
    safe_name = word.replace(" ", "_").lower()
    cache_path = os.path.join(AUDIO_CACHE_DIR, f"{safe_name}{suffix}.mp3")
    
    # Check if cached and recent
    if os.path.exists(cache_path):
        file_age = time.time() - os.path.getmtime(cache_path)
        if file_age < AUDIO_CACHE_TIMEOUT and os.path.getsize(cache_path) > 100:
            return cache_path  # Return cached file
    
    # Generate new audio
    try:
        audio_data = generate_tts_audio(word, voice)
        if audio_data:
            # Save to cache
            os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
            with open(cache_path, 'wb') as f:
                f.write(audio_data)
            return cache_path
    except Exception as e:
        print(f"[Audio] Generation failed for '{word}': {e}")
    
    return None

def generate_tts_audio(word, voice="en-US-AriaNeural"):
    """Generate audio using TTS API (ElevenLabs or Edge TTS)."""
    try:
        # Try ElevenLabs first
        if ELEVENLABS_API_KEY:
            audio_data = generate_elevenlabs_audio(word, voice)
            if audio_data:
                return audio_data
    except Exception as e:
        print(f"[ElevenLabs] Error: {e}")
    
    try:
        # Fallback to Edge TTS
        audio_data = generate_edge_tts_audio(word, voice)
        if audio_data:
            return audio_data
    except Exception as e:
        print(f"[EdgeTTS] Error: {e}")
    
    return None

def generate_elevenlabs_audio(word, voice_id="21m00Tcm4TlvDq8ikWAM"):
    """Generate audio using ElevenLabs API."""
    import requests
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": word,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    response = requests.post(url, json=data, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.content
    return None

def generate_edge_tts_audio(word, voice="en-US-AriaNeural"):
    """Generate audio using Edge TTS."""
    import asyncio
    from edge_tts import Communicate
    
    async def _generate():
        communicate = Communicate(text=word, voice=voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_data = loop.run_until_complete(_generate())
        loop.close()
        return audio_data
    except Exception as e:
        print(f"[EdgeTTS] Generation error: {e}")
        return None
```

### Frontend Audio Loading

```javascript
// In script.js, update audio playback:

function playWordAudio(word) {
    var safeName = word.replace(/ /g, "_").toLowerCase();
    var audioUrl = "/audio/" + safeName + ".mp3";
    
    // Try to load from cache first
    fetch(audioUrl, {cache: "force-cache"})
        .then(response => {
            if (response.ok) {
                return response.blob();
            }
            // If not in cache, request generation
            return fetch("/api/generate-audio?word=" + encodeURIComponent(word))
                .then(r => r.blob());
        })
        .then(blob => {
            var audio = new Audio(URL.createObjectURL(blob));
            audio.play();
        })
        .catch(err => {
            console.log("Audio playback failed:", err);
            // Continue game without audio
        });
}
```

### Backend Audio Generation Endpoint

```python
@app.route("/api/generate-audio")
def api_generate_audio():
    """Generate and cache audio on-demand."""
    word = request.args.get("word", "").strip()
    if not word:
        return jsonify({"error": "No word provided"}), 400
    
    # Generate or get cached audio
    audio_path = get_or_generate_audio(word)
    
    if audio_path and os.path.exists(audio_path):
        return send_file(audio_path, mimetype="audio/mpeg")
    
    return jsonify({"error": "Audio generation failed"}), 500
```

### Performance Optimization

```python
# Implement audio pre-warming for current week
def prewarm_week_audio(group="group1", week=None):
    """Pre-generate audio for current week in background."""
    if week is None:
        week = get_week_key()
    
    words = []
    for difficulty in ["easy", "medium", "hard"]:
        words.extend(get_group_words(group, difficulty, week))
    
    # Queue audio generation in background
    for word in words:
        # Don't block, just queue
        threading.Thread(target=get_or_generate_audio, args=(word,), daemon=True).start()

# Call on game start
@app.route("/game/start")
def game_start():
    group = get_group()
    # Pre-warm audio in background
    threading.Thread(target=prewarm_week_audio, args=(group,), daemon=True).start()
    return jsonify({"ok": True})
```

---

## REQUIREMENT 6: Image Validation (Verified/Local Only)

### Implementation Code

```python
# In app.py, update image retrieval:

def get_word_image(word, group="group1"):
    """Get image for word, using verified/local sources only."""
    
    # Check WORD_IMAGES (verified mappings)
    if word in WORD_IMAGES:
        return WORD_IMAGES[word]
    
    # Check PIXABAY_IMAGES (local verified images)
    if word in PIXABAY_IMAGES:
        return PIXABAY_IMAGES[word]
    
    # No fallback to Wikipedia - return placeholder or default
    return "/static/images/placeholder.png"

def validate_image_url(url):
    """Validate image URL is from verified source."""
    if not url:
        return False
    
    url_lower = url.lower()
    
    # Allow only verified sources
    allowed_sources = [
        "pixabay.com",
        "pexels.com",
        "unsplash.com",
        "/static/images/",
    ]
    
    for source in allowed_sources:
        if source in url_lower:
            return True
    
    return False
```

---

## Summary: Implementation Timeline

| Phase | Issues | Duration | Priority |
|-------|--------|----------|----------|
| Phase 1 | Word deduplication + add missing words | 6-8 hours | 🔴 CRITICAL |
| Phase 2 | Week distribution optimization | 2-3 hours | 🔴 CRITICAL |
| Phase 3 | Leaderboard separation (ranked/regular) | 4-5 hours | 🔴 CRITICAL |
| Phase 4 | Audio on-demand generation + caching | 3-4 hours | 🟡 MEDIUM |
| Phase 5 | Image validation (verified only) | 1-2 hours | 🟡 MEDIUM |
| Phase 6 | Tournament bomb word restriction | 30 min | 🟠 HIGH |

**Total estimated time:** 17-23 hours

---

## Testing Checklist

- [ ] All groups have target word counts (or within 10% variance)
- [ ] No duplicate words within same group/difficulty
- [ ] Week distribution: min 10 words per difficulty
- [ ] Ranked leaderboard shows team scores
- [ ] Regular leaderboard shows individual scores
- [ ] Clicking team shows individual ranked scores
- [ ] Tournament bomb words are hard difficulty only
- [ ] Audio generates on-demand and caches
- [ ] Images are from verified sources only
- [ ] Game runs smoothly without audio delays
- [ ] Ranked mode uses all words from selected week

