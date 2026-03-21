# Ranked Attempts Counting Analysis

## 🚨 **CRITICAL ISSUE FOUND: Unfair Attempt Consumption**

### **Current Attempt Consumption Logic**

#### **🔴 Problem 1: Attempt Consumed After 3 Correct Words**
```javascript
// Located in compHandleCorrect() function
if (isRankedMode && !rankedAttemptConsumed) {
  rankedWordsPlayed++;
  if (rankedWordsPlayed >= 3) {
    rankedAttemptConsumed = true;
    // Consume attempt in backend NOW
    fetch("/leaderboard", {
      method: "POST",
      body: JSON.stringify({_consume_only: true})
    });
  }
}
```

**ISSUE**: Attempt is consumed after 3 correct words, even if player hasn't finished the game!

#### **🔴 Problem 2: Game Exit Doesn't Check Attempt Status**
```javascript
function quitGame() {
  document.getElementById("quit-modal").classList.add("hidden");
  gamePausedForQuit = false;
  returnToMenu();  // No attempt protection!
}
```

**ISSUE**: Player loses attempt even if they exit before attempt was consumed.

#### **🔴 Problem 3: System Errors Can Consume Attempts**
- **Network failures** during attempt consumption
- **Tab switching** detection consuming attempts
- **Game crashes** leaving attempts consumed
- **Backend errors** during submission

---

## 🛠️ **SOLUTION: Robust Attempt Protection System**

### **📋 Required Changes**

#### **1. Safe Exit Mechanism**
```javascript
function quitGame() {
  // Only consume attempt if game was meaningful
  if (isRankedMode && rankedAttemptConsumed) {
    // Attempt already consumed - fair to exit
    returnToMenu();
  } else if (isRankedMode && !rankedAttemptConsumed) {
    // Attempt not consumed yet - safe exit
    rankedAttemptConsumed = true; // Mark as consumed to prevent re-entry
    returnToMenu();
  }
  returnToMenu();
}
```

#### **2. Attempt Consumption on Game Completion Only**
```javascript
// Move attempt consumption from compHandleCorrect to compEndGame
function compEndGame() {
  // ... existing logic ...
  
  // Only consume attempt if game was completed meaningfully
  if (isRankedMode && !rankedAttemptConsumed && wordScores.length >= 3) {
    // Consume attempt only after meaningful game completion
    rankedAttemptConsumed = true;
    fetch("/leaderboard", {
      method: "POST",
      body: JSON.stringify({_consume_only: true})
    });
  }
}
```

#### **3. Error Recovery Mechanism**
```javascript
function handleRankedError(error) {
  if (isRankedMode && !rankedAttemptConsumed) {
    // Don't consume attempt on system error
    console.error("Ranked game error - attempt not consumed:", error);
    showErrorMessage("System error occurred. Your attempt was not consumed.");
    returnToMenu();
  }
}
```

#### **4. Tab Switching Protection**
```javascript
// Current tab switching logic needs fixing
function handleTabSwitch() {
  if (isRankedMode && !rankedAttemptConsumed) {
    // Don't consume attempt on first tab switch
    tabSwitchCount++;
    if (tabSwitchCount >= 3) {
      // Only invalidate game, don't consume attempt
      showErrorMessage("Game invalidated due to tab switching. Attempt not consumed.");
      endGame();
    }
  }
}
```

---

## 🎯 **Recommended Implementation Priority**

### **🚨 Critical (Fix Immediately)**
1. **Move attempt consumption** from `compHandleCorrect` to `compEndGame`
2. **Add attempt protection** for quit game functionality
3. **Fix tab switching** to not consume attempts

### **⚠️ Important (Fix Soon)**
4. **Add error recovery** for network failures
5. **Implement attempt rollback** mechanism
6. **Add attempt status logging** for debugging

### **📝 Nice to Have**
7. **Attempt restoration** after system errors
8. **Attempt protection UI** showing attempt status
9. **Grace period** for rejoining after accidental exit

---

## 🔍 **Specific Bugs to Fix**

### **Bug 1: Early Attempt Consumption**
**Location**: `compHandleCorrect()` line ~1338
**Fix**: Move to `compEndGame()` with minimum game completion check

### **Bug 2: Unsafe Quit Mechanism**
**Location**: `quitGame()` function
**Fix**: Check `rankedAttemptConsumed` status before allowing exit

### **Bug 3: Tab Switching Penalty**
**Location**: Tab switching detection logic
**Fix**: Invalidate game instead of consuming attempt

### **Bug 4: No Error Recovery**
**Location**: Network error handling
**Fix**: Add try-catch with attempt protection

---

## 🛡️ **Protection Mechanisms**

### **Before Attempt Consumption**
- **Minimum 3 correct words** required
- **Game must be completed** (not exited)
- **No system errors** occurred
- **No tab switching violations**

### **Safe Exit Conditions**
- **Player clicks quit** before attempt consumption
- **System errors** occur during gameplay
- **Network failures** prevent submission
- **Tab switching** detected early

### **Attempt Status Tracking**
- **rankedAttemptConsumed** flag
- **Backend attempt validation**
- **Frontend-backend sync**
- **Error logging** for debugging

---

## 🎮 **User Experience Improvements**

### **Clear Attempt Status**
- Show "Attempt protected" when safe to exit
- Display "Attempt consumed" when locked in
- Warn before actions that might consume attempts

### **Error Messages**
- "System error - attempt not consumed"
- "Game ended safely - attempt not consumed"
- "Tab switching detected - game invalidated"

### **Grace Period**
- Allow rejoining within 30 seconds of accidental exit
- Restore attempt state for legitimate disconnections
- Provide attempt recovery options
