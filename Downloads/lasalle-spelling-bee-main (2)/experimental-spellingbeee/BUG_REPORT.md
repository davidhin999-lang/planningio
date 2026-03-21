# Bug Report - Spelling Bee Application

## Executive Summary
**27 HIGH-SEVERITY BUGS** found in `app.py`:
- All are **duplicate nested function definitions**
- These cause function shadowing and unpredictable behavior
- Need immediate refactoring to fix

## Critical Issues Found

### 1. Duplicate `_load` Functions (8 instances)
Lines: 411, 515, 560, 635, 1031, 1049, 2460, 2509

**Problem:** Multiple `_load()` nested functions defined in different outer functions. When called, Python uses the last defined version, causing logic errors.

**Example Pattern:**
```python
def function_a():
    def _load():
        # Implementation A
    return _fs_call(_load)

def function_b():
    def _load():
        # Implementation B
    return _fs_call(_load)
```

**Impact:** If both functions are called in sequence, the second `_load` overwrites the first, causing function_a to use function_b's logic.

---

### 2. Duplicate `_save` Functions (3 instances)
Lines: 433, 1012, 1112

**Problem:** Multiple `_save()` implementations in different contexts. Last definition wins.

**Impact:** Score saving, profile updates, and other critical operations may use wrong implementation.

---

### 3. Duplicate `_reset` Functions (2 instances)
Lines: 536, 2214

**Problem:** Two `_reset()` functions with different purposes overwrite each other.

**Impact:** Week reset or attempt reset might not work correctly.

---

### 4. Duplicate `_update` Functions (3 instances)
Lines: 749, 908, 926

**Problem:** Profile update logic defined multiple times.

**Impact:** Player profile updates may not persist correctly.

---

### 5. Duplicate `_get` Functions (3 instances)
Lines: 672, 735, 880

**Problem:** Data retrieval functions defined multiple times.

**Impact:** Fetching player data, team data, or other info may return wrong data.

---

### 6. Duplicate `_del` Functions (2 instances)
Lines: 459, 1863

**Problem:** Deletion logic defined twice.

**Impact:** Deleting players or data may fail or delete wrong items.

---

### 7. Duplicate `_test` Functions (2 instances)
Lines: 1206, 1255

**Problem:** Test/validation logic duplicated.

**Impact:** Unpredictable validation behavior.

---

### 8. Duplicate `target` Functions (2 instances)
Lines: 201, 220

**Problem:** Target function defined twice.

**Impact:** Firestore operations may target wrong database.

---

### 9. Duplicate `save_weekly_snapshot` Functions (2 instances)
Lines: 657, 1003

**Problem:** Two completely different implementations of weekly snapshot saving.

**Impact:** Week-end archiving may not work correctly or may use wrong logic.

---

## Additional Issues

### Warnings (212 total)
- **Potential None dereference** - Missing default values in `.get()` calls
- **Using print() instead of logging** - Should use proper logging module
- **File operations without `with` statement** - Risk of resource leaks

### Info Items (46 total)
- **Debug console.log statements** in script.js that should be removed for production

---

## Recommended Fixes

### Priority 1: CRITICAL
1. **Rename nested functions** to be unique:
   - `_load` → `_load_profiles`, `_load_leaderboard`, `_load_week_history`, etc.
   - `_save` → `_save_profile`, `_save_leaderboard`, etc.
   - `_get` → `_get_team`, `_get_profile`, `_get_ranked_attempts`, etc.

### Priority 2: HIGH
2. **Remove duplicate `save_weekly_snapshot`** - Keep only one implementation
3. **Consolidate `_reset` functions** - Merge into single function with parameters
4. **Consolidate `_update` functions** - Merge into single function with parameters

### Priority 3: MEDIUM
5. **Add default values** to all `.get()` calls
6. **Replace print() with logging** module
7. **Use `with` statement** for all file operations
8. **Remove debug console.log** statements from production code

---

## Example Fix

**Before (Problematic):**
```python
def get_profile(name, group):
    def _get():
        return gcol(group, "player_profiles").document(name).get()
    return _fs_call(_get)

def get_team(team_id, group):
    def _get():  # DUPLICATE NAME!
        return gcol(group, "teams").document(team_id).get()
    return _fs_call(_get)
```

**After (Fixed):**
```python
def get_profile(name, group):
    def _get_profile():
        return gcol(group, "player_profiles").document(name).get()
    return _fs_call(_get_profile)

def get_team(team_id, group):
    def _get_team():  # UNIQUE NAME
        return gcol(group, "teams").document(team_id).get()
    return _fs_call(_get_team)
```

---

## Testing Recommendations

After fixes:
1. Test all score saving operations
2. Test player profile updates
3. Test week reset functionality
4. Test team data retrieval
5. Test player deletion
6. Test leaderboard loading

---

## Severity Assessment

| Issue | Count | Severity | Impact |
|-------|-------|----------|--------|
| Duplicate functions | 27 | HIGH | Logic errors, data corruption |
| None dereference | 50+ | MEDIUM | Potential crashes |
| Print statements | 100+ | LOW | Performance, logging |
| Debug logs | 46 | LOW | Code cleanliness |

**Overall Risk Level: HIGH** - These bugs could cause data loss or incorrect game state.
