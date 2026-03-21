# System Failure Definition & Attempt Protection Policy

## 🚨 **CRITICAL: What Constitutes a System Failure**

### **❌ NOT System Failures (Should Consume Attempts)**
- **Tab switching** - User action, clear violation
- **Quit button** - User choice, intentional exit
- **Browser crash** - User's device issue
- **Internet disconnect** - User's network issue
- **Power outage** - User's environment issue
- **Closing browser tab** - User action
- **Device restart** - User's hardware issue

### **✅ True System Failures (Should NOT Consume Attempts)**
- **Backend API errors** (500, 503, timeout)
- **Frontend JavaScript errors** that prevent game completion
- **Word loading failures** from backend
- **Audio generation failures** from TTS services
- **Score submission failures** due to backend issues
- **Database connection errors** during attempt consumption
- **Server maintenance** during active game

---

## 🛡️ **Revised Attempt Protection Policy**

### **🔴 Attempts SHOULD Be Consumed For:**
1. **Tab switching violations** (after 2 warnings)
2. **Intentional quit** via quit button
3. **Natural game completion** (time out, words exhausted)
4. **Meaningful gameplay** (3+ words + score submission)

### **🟢 Attempts SHOULD Be Protected For:**
1. **Backend API failures** during submission
2. **Network timeouts** to server
3. **JavaScript errors** preventing completion
4. **Word loading failures** from backend
5. **TTS service failures** (both ElevenLabs and Edge TTS)
6. **Database errors** during attempt consumption

---

## 🔧 **Technical Implementation**

### **System Failure Detection**
```javascript
function isSystemFailure(error) {
  // Check for genuine system failures
  if (error.status >= 500) return true; // Server errors
  if (error.name === 'TypeError' && error.message.includes('fetch')) return true;
  if (error.message.includes('NetworkError')) return true;
  if (error.message.includes('timeout')) return true;
  
  // NOT system failures:
  // - Tab switching (user action)
  // - Quit button (user choice)
  // - Browser close (user action)
  return false;
}
```

### **Tab Switching Penalty (RESTORED)**
```javascript
document.addEventListener("visibilitychange", function() {
  if (!tabSwitchActive || !isRankedMode) return;
  if (document.hidden) {
    tabSwitchCount++;
    if (tabSwitchCount >= 3) {
      // PENALTY: No score + consume attempt
      gameActive = false;
      clearInterval(timer);
      stopTabSwitchDetection();
      
      // CONSUME ATTEMPT - this is fair penalty
      if (!rankedAttemptConsumed) {
        rankedAttemptConsumed = true;
        fetch("/leaderboard", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(groupBody({ 
            name: playerName, 
            score: 0,  // No score penalty
            difficulty: currentDifficulty,
            streak: 0, 
            is_ranked: true, 
            _consume_only: true 
          }))
        }).catch(function(err) {
          console.error("[ATTEMPT] Failed to consume attempt for tab switching:", err);
        });
      }
      
      showPenalty("⚠️ Tab switching violation - No score + Attempt consumed");
      
      // Return to menu after delay
      setTimeout(function() {
        returnToMenu();
      }, 3000);
    }
  }
});
```

### **Safe Error Handling**
```javascript
function handleRankedError(error) {
  if (isRankedMode && !rankedAttemptConsumed) {
    if (isSystemFailure(error)) {
      // PROTECT attempt for genuine system failures
      console.error("[ATTEMPT] System failure - attempt protected:", error);
      showBonus("⚠️ System error occurred. Attempt protected.");
      returnToMenu();
    } else {
      // CONSUME attempt for user errors
      console.error("[ATTEMPT] User error - attempt consumed:", error);
      rankedAttemptConsumed = true;
      returnToMenu();
    }
  }
}
```

---

## 📊 **Implementation Priority**

### **🚨 Immediate (Critical)**
1. **Restore tab switching penalty** (3 switches = no score + attempt consumed)
2. **Define system failures** strictly (backend errors, network issues)
3. **Remove attempt protection** for user actions (quit, tab switching)

### **⚠️ Important (Fix Soon)**
4. **Add system failure detection** logic
5. **Implement error classification** (system vs user)
6. **Add proper error logging** for debugging

### **📝 Nice to Have**
7. **Error recovery mechanisms** for system failures
8. **User education** about what constitutes violations
9. **Appeal process** for disputed attempt consumption

---

## 🎯 **Fairness Principles**

### **✅ Fair to Users**
- **Clear rules** about what consumes attempts
- **Consistent enforcement** of violations
- **Protection** from genuine system issues
- **Transparency** about attempt consumption

### **✅ Fair to Competition**
- **No exploit loopholes** for extra attempts
- **Equal treatment** for all players
- **Reliable attempt tracking** system
- **Prevent cheating** while protecting from errors

---

## 🚀 **User Communication**

### **Clear Messages**
- **Tab switching**: "⚠️ Tab switching violation - No score + Attempt consumed"
- **System failure**: "⚠️ System error occurred. Attempt protected."
- **Network error**: "⚠️ Network issue - Attempt protected. Try again."

### **Educational Elements**
- **Rules modal** explains attempt consumption rules
- **Warning messages** before penalties
- **Clear indication** of attempt status

---

## 🔍 **Testing Scenarios**

### **Test Tab Switching Penalty**
1. Start ranked game
2. Switch tabs 3 times
3. Verify: No score + Attempt consumed
4. Check leaderboard for attempt count

### **Test System Failure Protection**
1. Mock backend error during submission
2. Verify: Attempt not consumed
3. Check attempt count unchanged

### **Test Normal Consumption**
1. Complete ranked game normally
2. Verify: Attempt consumed properly
3. Check score submitted correctly

---

## 📋 **Checklist for Implementation**

- [ ] Restore tab switching penalty (3 switches = penalty)
- [ ] Define system failure detection logic
- [ ] Remove attempt protection for user actions
- [ ] Add proper error classification
- [ ] Test all scenarios thoroughly
- [ ] Update user documentation
- [ ] Monitor for exploit attempts
