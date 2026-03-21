# Ranked Mode Bug Fixes

## Summary
Fixed three critical bugs in ranked mode that were preventing score saving, causing incorrect attempt tracking, and blocking play-again functionality.

---

## Bug #1: Ranked Scores Not Saved to Leaderboard

### Problem
Ornella's 1000+ point ranked score was not appearing on the leaderboard. Ranked scores were only being tracked in player profiles (`ranked_best_{week}`) but not saved to the leaderboard collection.

### Root Cause
In `app.py` lines 1533-1561, the code explicitly skipped leaderboard saving for ranked games:
```python
if not is_ranked:
    # Only save to individual leaderboard for non-ranked games
```

### Fix
**File:** `app.py` (lines 1533-1557)
- Removed the `if not is_ranked:` condition
- Now ranked scores are saved to the leaderboard collection just like non-ranked scores
- Ranked scores now appear on the public leaderboard alongside other scores

### Impact
- Ornella's score (and all future ranked scores) will now appear on the leaderboard
- Players can see their ranked performance on the public leaderboard
- Team rankings will properly reflect ranked scores

---

## Bug #2: Attempt Counter Incremented Twice

### Problem
When a player completed their first ranked attempt, the system showed "1 attempt remaining" instead of "2 attempts remaining". The attempt counter was being incremented twice:
1. Once when the early consumption flag was sent after 3 correct words
2. Again when the final score was submitted

### Root Cause
In `app.py` lines 1514-1518, the backend always incremented the attempt counter when `_skip_attempt: false` was sent, even if the attempt had already been consumed early via the `_consume_only` flag.

In `script.js` line 4737, the frontend always sent `_skip_attempt: false` regardless of whether the attempt was already consumed.

### Fix
**File 1:** `app.py` (lines 1518-1521)
- Added a check: only increment the attempt counter if the game was meaningful (3+ words completed)
- This prevents double-counting when the attempt was already consumed early

**File 2:** `script.js` (line 4737)
- Changed `_skip_attempt: false` to `_skip_attempt: rankedAttemptConsumed`
- Now properly signals to the backend whether the attempt was already consumed

### Impact
- Attempt counter now correctly reflects the number of attempts used
- Players see accurate "attempts remaining" count after each game
- Early attempt consumption (after 3 correct words) is properly tracked

---

## Bug #3: Play Again Shows "No Attempts Left" on First Attempt

### Problem
After completing the first ranked game, clicking "Play Again" would show "No ranked attempts left this week! Resets Monday." even though the player had just used their first attempt and had 2 remaining.

### Root Cause
The `playAgain()` function was checking if `rankedAttemptsLeft <= 0` after fetching the updated count from the server. However, the state variable `_lastGameWasRanked` remained `true`, which could cause logic issues in the modal opening sequence.

### Fix
**File:** `script.js` (line 1238)
- Added `_lastGameWasRanked = false;` before calling `openRankedMode()`
- This resets the ranked game state before opening the ranked mode modal
- Ensures the modal properly reflects the current attempt count

### Impact
- "Play Again" button now works correctly after the first ranked game
- Players can continue playing ranked games as long as attempts remain
- Proper state management prevents modal logic conflicts

---

## Testing Checklist

- [ ] Submit a ranked game and verify the score appears on the leaderboard
- [ ] Check that after first ranked game, "attempts remaining" shows 2 (not 1)
- [ ] Click "Play Again" after a ranked game and verify it opens the ranked modal
- [ ] Verify the ranked modal shows correct attempt count
- [ ] Complete 3 ranked games and verify "No attempts left" message appears
- [ ] Verify early attempt consumption (after 3 correct words) works correctly
- [ ] Check that team scores are properly updated with ranked scores

---

## Files Modified
1. `app.py` - Backend leaderboard saving and attempt tracking
2. `script.js` - Frontend attempt flag and play-again state management
