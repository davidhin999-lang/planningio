// ==================== STATE ====================
var words = [];
var currentWord = "";
var currentIndex = 0;
var score = 0;
var timer = null;
var timeLeft = 60;
var maxTime = 60;
var currentDifficulty = "easy";
var gameActive = false;
var usedWords = [];
var reviewWords = [];
var streak = 0;
var bestStreak = 0;
var totalBonusTime = 0;
var wordsCompleted = 0;
var audioPlayCount = 0;
var spellPlayCount = 0;
var hiddenKeys = [];
var lives = 3;
var maxLives = 3;
var keyFadeTimer = null;
var playerName = "";
var leaderboardData = {};
var isPracticeMode = false;

// Round system
var currentRound = 1;
var totalRounds = 3;
var wordsPerRound = 6;
var wordInRound = 0;

// Per-word scoring
var wrongLetters = 0;
var wordStartTime = 0;
var wordScores = [];

var RADIUS = 50;
var CIRCUMFERENCE = 2 * Math.PI * RADIUS;
var ALL_KEYS = "qwertyuiopasdfghjklzxcvbnm";

// Difficulty settings: time, bonus, penalty, hint
var DIFF_CONFIG = {
  easy:   { wordTime: 20, letterBonus: 3, penalty: 0, fadeSpeed: 1.0, hintDelay: 5 },
  medium: { wordTime: 15, letterBonus: 2, penalty: 1, fadeSpeed: 0.7, hintDelay: 4 },
  hard:   { wordTime: 10, letterBonus: 1, penalty: 1, fadeSpeed: 0.5, hintDelay: 3 }
};

// Group system — read from ?group= URL param
var currentGroup = (function() {
  var params = new URLSearchParams(window.location.search);
  return (params.get("group") || "group1").toLowerCase();
})();
var currentGroupLabel = "";

// ==================== DOM ELEMENT CACHE ====================
// Cache frequently accessed DOM elements to reduce query overhead
var domCache = {};
function getEl(id) {
  if (!domCache[id]) {
    domCache[id] = document.getElementById(id);
  }
  return domCache[id];
}

function groupQS(url) {
  // Append ?group= or &group= to a URL
  return url + (url.indexOf("?") === -1 ? "?" : "&") + "group=" + encodeURIComponent(currentGroup);
}

function groupBody(obj) {
  // Inject group into a POST body object
  if (!obj) obj = {};
  obj.group = currentGroup;
  return obj;
}

function lsKey(key) {
  // Namespace localStorage keys per group to avoid cross-group conflicts
  if (currentGroup === "group1") return key;
  return currentGroup + "_" + key;
}

// Week system
var weekCounts = { easy: 1, medium: 1, hard: 1 };
var selectedWeek = 0; // 0 = all words

// Hint system state
var hintTimer = null;
var hintActive = false;
var hintGlowingKey = null;
var skippedWords = 0;

// Speaking mode
var gameMode = "type";         // "type" or "speak"
var speakSubmode = "say";      // "say" or "spell"
var recognition = null;
var micListening = false;
var micAttempts = 0;
var MAX_MIC_ATTEMPTS = 3;
var audioPlaying = false;
var processingResult = false;
var speechWordTarget = "";
var spellMicTimer = null;
var spellAccumulated = "";

// ==================== COMPETITION MODE STATE ====================
var isCompetitionMode = false;
var compTeamId = null;
var compTeamName = "";
var compTeamColor = "#f59e0b";
var compTeamEmoji = "";
var compWordPool = [];          // mixed pool of all difficulties
var compCorrect = 0;            // correct answers this session
var compWrong = 0;              // wrong answers this session
var compWordTime = 20;          // current per-word time (shrinks adaptively)
var COMP_TIME_MIN = 10;         // floor for per-word time
var COMP_TIME_START = 20;       // starting per-word time
var COMP_SHRINK_EVERY = 3;      // shrink timer every N correct answers
var COMP_SHRINK_BY = 0.5;       // seconds to shrink per step
var compStreakBonus = { 3: 20, 5: 50, 7: 100 }; // streak → bonus pts
var compAllWords = [];          // all words loaded for competition

// NOTE: Ranked mode state and bomb word variables are declared
// in their respective sections below (lines ~3680 and ~4030)

// ==================== MAP of spoken letter names to actual letters ====================
// Enhanced map with more variations and common speech recognition errors
var LETTER_NAME_MAP = {
  // Single letters (direct recognition)
  "a": "a", "b": "b", "c": "c", "d": "d", "e": "e", "f": "f", "g": "g",
  "h": "h", "i": "i", "j": "j", "k": "k", "l": "l", "m": "m", "n": "n",
  "o": "o", "p": "p", "q": "q", "r": "r", "s": "s", "t": "t", "u": "u",
  "v": "v", "w": "w", "x": "x", "y": "y", "z": "z",
  
  // Standard phonetic names
  "ay": "a", "eh": "a", "bee": "b", "be": "b", "see": "c", "sea": "c", "cee": "c",
  "dee": "d", "de": "d", "ee": "e", "ef": "f", "eff": "f", "gee": "g", "ge": "g",
  "aitch": "h", "ach": "h", "eye": "i", "ai": "i", "jay": "j", "jy": "j",
  "kay": "k", "ka": "k", "el": "l", "elle": "l", "em": "m", "en": "n",
  "oh": "o", "pee": "p", "pe": "p", "cue": "q", "queue": "q", "cu": "q", "kew": "q",
  "are": "r", "ar": "r", "es": "s", "ess": "s", "ass": "s", "tee": "t", "te": "t",
  "you": "u", "yu": "u", "vee": "v", "ve": "v", "double you": "w", "double u": "w",
  "doubleyou": "w", "ex": "x", "eggs": "x", "why": "y", "wy": "y", "wye": "y",
  "zee": "z", "zed": "z", "ze": "z",
  
  // Common variations and mistakes
  "seea": "c", "seeh": "c", "seac": "c",  // C variations
  "dey": "d",                           // D variations
  "ell": "l", "ellee": "l",             // L variations
  "enn": "n", "enne": "n",              // N variations
  "youu": "u", "yuu": "u",              // U variations
  "doubleyou": "w", "double-u": "w",     // W variations
  "exx": "x", "eks": "x",               // X variations
  
  // Common speech recognition errors
  "bea": "b", "cea": "c", "dea": "d", "gea": "g", "jea": "j", "kea": "k", "pea": "p", "tea": "t", "vea": "v", "zea": "z",
  
  // Merged letters (common speech API issue)
  "ab": "ab", "bc": "bc", "cd": "cd", "de": "de", "ef": "ef", "fg": "fg", "gh": "gh", "hi": "hi", "ij": "ij", "jk": "jk", "kl": "kl", "lm": "lm", "mn": "mn", "no": "no", "op": "op", "pq": "pq", "qr": "qr", "rs": "rs", "st": "st", "tu": "tu", "uv": "uv", "vw": "vw", "wx": "wx", "xy": "xy", "yz": "yz"
};

function extractLettersFromSpeech(text) {
  var lower = text.toLowerCase().trim();
  console.log("[Extract] Input: '" + text + "'");
  
  // Method 1: Direct merged letter extraction
  var mergedResult = extractMergedLetters(lower);
  if (mergedResult) {
    console.log("[Extract] Merged letters: '" + mergedResult + "'");
    return mergedResult;
  }
  
  // Method 2: Phonetic name extraction
  var parts = lower.split(/[\s,.\/\-]+/).filter(function(p) { return p.length > 0; });
  var letters = [];
  
  for (var i = 0; i < parts.length; i++) {
    var p = parts[i];
    console.log("[Extract] Processing part: '" + p + "'");
    
    // Single letter
    if (p.length === 1 && /[a-z]/.test(p)) {
      letters.push(p);
      console.log("[Extract] Single letter: " + p);
    // Known letter name
    } else if (LETTER_NAME_MAP[p]) {
      var mapped = LETTER_NAME_MAP[p];
      // Handle merged letters from map
      if (mapped.length > 1) {
        letters.push(...mapped.split(''));
      } else {
        letters.push(mapped);
      }
      console.log("[Extract] Letter name: '" + p + "' → " + mapped);
    // Check multi-word combos
    } else if (i + 1 < parts.length && LETTER_NAME_MAP[p + " " + parts[i+1]]) {
      var mapped = LETTER_NAME_MAP[p + " " + parts[i+1]];
      if (mapped.length > 1) {
        letters.push(...mapped.split(''));
      } else {
        letters.push(mapped);
      }
      console.log("[Extract] Multi-word: '" + p + " " + parts[i+1] + "' → " + mapped);
      i++; // skip next part
    } else {
      console.log("[Extract] Unrecognized: '" + p + "'");
    }
  }
  
  var result = letters.join("");
  console.log("[Extract] Final result: '" + result + "'");
  return result;
}

function extractMergedLetters(text) {
  // Handle common speech API merged letters (like "ABC" instead of "A B C")
  var mergedPatterns = {
    "ab": "ab", "bc": "bc", "cd": "cd", "de": "de", "ef": "ef", "fg": "fg",
    "gh": "gh", "hi": "hi", "ij": "ij", "jk": "jk", "kl": "kl", "lm": "lm",
    "mn": "mn", "no": "no", "op": "op", "pq": "pq", "qr": "qr", "rs": "rs",
    "st": "st", "tu": "tu", "uv": "uv", "vw": "vw", "wx": "wx", "xy": "xy", "yz": "yz"
  };
  
  // Check for exact matches
  for (var pattern in mergedPatterns) {
    if (text === pattern) {
      return mergedPatterns[pattern];
    }
  }
  
  // Check if text contains merged pattern
  for (var pattern in mergedPatterns) {
    if (text.includes(pattern)) {
      return mergedPatterns[pattern];
    }
  }
  
  return null;
}

function fuzzyMatch(str1, str2, maxErrors) {
  // Allow minor speech recognition errors
  if (Math.abs(str1.length - str2.length) > maxErrors) return false;
  
  var errors = 0;
  var len = Math.min(str1.length, str2.length);
  
  for (var i = 0; i < len; i++) {
    if (str1[i] !== str2[i]) {
      errors++;
      if (errors > maxErrors) return false;
    }
  }
  
  return true;
}

// ==================== SOUND EFFECTS (Web Audio API) ====================
var audioCtx = null;
function getAudioCtx() {
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  if (audioCtx.state === "suspended") {
    audioCtx.resume().catch(function() {});
  }
  return audioCtx;
}

function playTone(freq, duration, type, vol) {
  if (sfxMuted) return;
  try {
    var ctx = getAudioCtx();
    if (ctx.state === "suspended") return;
    var osc = ctx.createOscillator();
    var gain = ctx.createGain();
    osc.type = type || "sine";
    osc.frequency.value = freq;
    gain.gain.value = vol || 0.15;
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    osc.stop(ctx.currentTime + duration);
  } catch(e) {}
}

function sfxCorrect() { playTone(880, 0.1, "sine", 0.12); hapticCorrect(); }
function sfxWrong() {
  playTone(200, 0.2, "square", 0.08);
  setTimeout(function() { playTone(160, 0.2, "square", 0.06); }, 100);
  hapticWrong();
}
function sfxComplete() {
  [523, 659, 784, 1047].forEach(function(n, i) {
    setTimeout(function() { playTone(n, 0.15, "sine", 0.12); }, i * 80);
  });
}
function sfxStreak() {
  playTone(1200, 0.08, "sine", 0.1);
  setTimeout(function() { playTone(1600, 0.12, "sine", 0.12); }, 60);
  hapticStreak();
}
function sfxGameOver() {
  [523, 440, 349, 262].forEach(function(n, i) {
    setTimeout(function() { playTone(n, 0.3, "triangle", 0.1); }, i * 200);
  });
  hapticGameOver();
}
function sfxCelebration() {
  var notes = [523, 659, 784, 880, 1047, 1175, 1319, 1568];
  notes.forEach(function(n, i) {
    setTimeout(function() { playTone(n, 0.2, "sine", 0.1); }, i * 60);
  });
  setTimeout(function() {
    playTone(1568, 0.4, "sine", 0.12);
    playTone(1047, 0.4, "sine", 0.08);
  }, notes.length * 60);
}
function sfxPenalty() {
  playTone(150, 0.15, "sawtooth", 0.06);
}

// ==================== CONFETTI ====================
var confettiCanvas, confettiCtx, confettiPieces = [], confettiAnimating = false;

function initConfetti() {
  confettiCanvas = document.getElementById("confetti-canvas");
  confettiCtx = confettiCanvas.getContext("2d");
  resizeConfetti();
  window.addEventListener("resize", resizeConfetti);
}

function resizeConfetti() {
  if (!confettiCanvas) return;
  confettiCanvas.width = window.innerWidth;
  confettiCanvas.height = window.innerHeight;
}

function launchConfetti(count) {
  confettiPieces = [];
  var colors = ["#fbbf24", "#f59e0b", "#ef4444", "#10b981", "#3b82f6", "#8b5cf6"];
  for (var i = 0; i < count; i++) {
    confettiPieces.push({
      x: Math.random() * confettiCanvas.width,
      y: -20,
      vx: (Math.random() - 0.5) * 4,
      vy: Math.random() * 3 + 2,
      w: Math.random() * 8 + 6,
      h: Math.random() * 4 + 2,
      rot: Math.random() * 360,
      rotSpeed: (Math.random() - 0.5) * 10,
      color: colors[Math.floor(Math.random() * colors.length)],
      life: 1.0,
      decay: Math.random() * 0.01 + 0.005
    });
  }
  if (!confettiAnimating) { confettiAnimating = true; animateConfetti(); }
}

// Global trigger for admin winner celebration
window.triggerConfetti = function() {
  launchConfetti(100);
};

// ==================== BADGE SYSTEM ====================

function showBadgePopup(badge) {
  var popup = document.getElementById("badge-popup");
  document.getElementById("badge-popup-icon").textContent = badge.icon || "🏆";
  document.getElementById("badge-popup-name").textContent = badge.name || "Badge Earned!";
  document.getElementById("badge-popup-desc").textContent = badge.description || "";
  popup.style.display = "flex";
  
  // Trigger celebration
  launchConfetti(50);
  sfxCelebration();
}

function closeBadgePopup() {
  document.getElementById("badge-popup").style.display = "none";
}

function renderBadges(badges, containerId) {
  var container = document.getElementById(containerId);
  if (!container) return;
  
  container.innerHTML = "";
  badges.forEach(function(badge) {
    var badgeEl = document.createElement("div");
    badgeEl.className = "badge-item " + (badge.rarity || "common");
    badgeEl.innerHTML = 
      badge.icon + " " +
      '<span class="badge-tooltip">' + badge.name + ': ' + badge.description + '</span>';
    container.appendChild(badgeEl);
  });
}

function loadPlayerBadges(playerName) {
  fetch(groupQS("/api/player-badges/" + encodeURIComponent(playerName)))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var badges = data.badges || [];
      
      // Show in login screen
      if (document.getElementById("login-badges-list")) {
        if (badges.length > 0) {
          document.getElementById("login-badges").style.display = "block";
          renderBadges(badges, "login-badges-list");
        }
      }
      
      // Show in profile
      if (document.getElementById("profile-badges-grid")) {
        renderBadges(badges, "profile-badges-grid");
      }
    })
    .catch(function() {});
}

function animateConfetti() {
  confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
  var alive = false;
  for (var i = 0; i < confettiPieces.length; i++) {
    var p = confettiPieces[i];
    if (p.life <= 0) continue;
    alive = true;
    p.x += p.vx; p.y += p.vy; p.vy += 0.1; p.rot += p.rotSpeed; p.life -= 0.005;
    confettiCtx.save();
    confettiCtx.translate(p.x, p.y);
    confettiCtx.rotate(p.rot * Math.PI / 180);
    confettiCtx.globalAlpha = Math.max(0, p.life);
    confettiCtx.fillStyle = p.color;
    confettiCtx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h);
    confettiCtx.restore();
  }
  if (alive) { requestAnimationFrame(animateConfetti); }
  else { confettiAnimating = false; confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height); }
}

// ==================== LOCAL STORAGE ====================
function _statsKey() {
  return lsKey(playerName ? "spelling_bee_stats_" + playerName : "spelling_bee_stats");
}
function getStats() {
  try { return JSON.parse(localStorage.getItem(_statsKey())) || {}; }
  catch(e) { return {}; }
}
function saveStats(stats) {
  try { localStorage.setItem(_statsKey(), JSON.stringify(stats)); } catch(e) {}
}

function saveGameResult() {
  var stats = getStats();
  stats.totalGames = (stats.totalGames || 0) + 1;
  stats.totalWords = (stats.totalWords || 0) + wordsCompleted;
  if (bestStreak > (stats.bestStreak || 0)) stats.bestStreak = bestStreak;

  var key = "best" + currentDifficulty.charAt(0).toUpperCase() + currentDifficulty.slice(1);
  var isNewBest = false;
  if (score > (stats[key] || 0)) { stats[key] = score; isNewBest = true; }

  saveStats(stats);
  return isNewBest;
}

// ==================== SCREENS ====================
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(function(s) {
    s.classList.remove("active");
    s.classList.remove("screen-enter");
  });
  var screen = document.getElementById(id);
  screen.classList.add("active");
  setTimeout(function() { screen.classList.add("screen-enter"); }, 20);
}

// ==================== ATMOSPHERE (Canvas-based) ====================
var atmoCanvas, atmoCtx, atmoMode = null, atmoAnimating = false, atmoTime = 0;
var atmoParticles = [];

function initAtmo() {
  atmoCanvas = document.getElementById("atmo-canvas");
  atmoCtx = atmoCanvas.getContext("2d");
  resizeAtmo();
  window.addEventListener("resize", resizeAtmo);
}

function resizeAtmo() {
  if (!atmoCanvas) return;
  atmoCanvas.width = window.innerWidth;
  atmoCanvas.height = window.innerHeight;
}

function setAtmosphere(difficulty) {
  document.body.classList.remove("theme-easy", "theme-medium", "theme-hard", "theme-competition");
  document.body.classList.add("theme-" + difficulty);
  atmoMode = difficulty;
  atmoTime = 0;
  atmoParticles = [];
  var W = window.innerWidth, H = window.innerHeight;

  if (difficulty === "easy") {
    // Falling leaves
    var leafColors = ["#e67e22", "#d35400", "#f39c12", "#c0392b", "#27ae60", "#2ecc71"];
    for (var i = 0; i < 15; i++) {
      atmoParticles.push({
        type: "leaf",
        x: Math.random() * W,
        y: -20 - Math.random() * H,
        size: 8 + Math.random() * 12,
        speed: 0.3 + Math.random() * 0.6,
        drift: (Math.random() - 0.5) * 0.5,
        rotation: Math.random() * 360,
        rotSpeed: (Math.random() - 0.5) * 3,
        alpha: 0.5 + Math.random() * 0.4,
        phase: Math.random() * Math.PI * 2,
        color: leafColors[Math.floor(Math.random() * leafColors.length)]
      });
    }
    // Sun particle (drawn separately)
    atmoParticles.push({
      type: "sun",
      x: 60,
      y: 60
    });
  } else if (difficulty === "medium") {
    // UFO — travels full screen left to right
    atmoParticles.push({
      type: "ufo",
      x: -50,
      y: H * 0.15,
      baseY: H * 0.15,
      speed: 0.8 + Math.random() * 0.4,
      dir: 1,
      phase: 0
    });
  } else if (difficulty === "hard") {
    // Flame particles
    for (var j = 0; j < 40; j++) {
      atmoParticles.push({
        x: Math.random() * W,
        y: H - Math.random() * H * 0.5,
        r: 20 + Math.random() * 40,
        vy: 0.5 + Math.random() * 2,
        vx: (Math.random() - 0.5) * 0.3,
        hue: Math.random() * 50,
        phase: Math.random() * Math.PI * 2,
        alpha: 0.3 + Math.random() * 0.4
      });
    }
    // Rat (top-down view) running fast all over the screen
    atmoParticles.push({
      type: "rat",
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (3 + Math.random() * 3) * (Math.random() < 0.5 ? 1 : -1),
      vy: (2 + Math.random() * 2) * (Math.random() < 0.5 ? 1 : -1),
      legPhase: 0,
      turnTimer: 0
    });
  } else if (difficulty === "competition") {
    // No particle effects for competition mode
  }

  if (!atmoAnimating) { atmoAnimating = true; animateAtmo(); }
}

function clearAtmosphere() {
  atmoMode = null;
  atmoParticles = [];
  document.body.classList.remove("theme-easy", "theme-medium", "theme-hard", "theme-competition");
  if (atmoCtx && atmoCanvas) atmoCtx.clearRect(0, 0, atmoCanvas.width, atmoCanvas.height);
}

function animateAtmo() {
  if (!atmoMode) { atmoAnimating = false; return; }
  var W = atmoCanvas.width, H = atmoCanvas.height;
  atmoCtx.clearRect(0, 0, W, H);
  atmoTime += 0.016;

  if (atmoMode === "easy") {
    // Draw each particle
    for (var i = 0; i < atmoParticles.length; i++) {
      var p = atmoParticles[i];

      if (p.type === "sun") {
        // Sun in the top-left corner
        var sunPulse = 1 + 0.08 * Math.sin(atmoTime * 2);
        var sunR = 40 * sunPulse;
        var sunGrad = atmoCtx.createRadialGradient(p.x, p.y, sunR * 0.2, p.x, p.y, sunR * 2.5);
        sunGrad.addColorStop(0, "rgba(255, 230, 80, 0.9)");
        sunGrad.addColorStop(0.3, "rgba(255, 200, 50, 0.5)");
        sunGrad.addColorStop(0.6, "rgba(255, 180, 30, 0.15)");
        sunGrad.addColorStop(1, "rgba(255, 160, 0, 0)");
        atmoCtx.fillStyle = sunGrad;
        atmoCtx.beginPath();
        atmoCtx.arc(p.x, p.y, sunR * 2.5, 0, Math.PI * 2);
        atmoCtx.fill();
        // Sun core
        atmoCtx.fillStyle = "rgba(255, 240, 120, 0.95)";
        atmoCtx.beginPath();
        atmoCtx.arc(p.x, p.y, sunR * 0.6, 0, Math.PI * 2);
        atmoCtx.fill();

      } else if (p.type === "leaf") {
        // Move leaf down with sway
        p.y += p.speed;
        p.x += p.drift + Math.sin(atmoTime * 1.5 + p.phase) * 0.8;
        p.rotation += p.rotSpeed;
        if (p.y > H + 20) { p.y = -20; p.x = Math.random() * W; }

        atmoCtx.save();
        atmoCtx.translate(p.x, p.y);
        atmoCtx.rotate(p.rotation * Math.PI / 180);
        atmoCtx.globalAlpha = p.alpha;
        atmoCtx.fillStyle = p.color;
        // Leaf shape: two arcs
        atmoCtx.beginPath();
        atmoCtx.moveTo(0, -p.size);
        atmoCtx.quadraticCurveTo(p.size, 0, 0, p.size);
        atmoCtx.quadraticCurveTo(-p.size, 0, 0, -p.size);
        atmoCtx.fill();
        atmoCtx.globalAlpha = 1;
        atmoCtx.restore();
      }
    }

  } else if (atmoMode === "medium") {
    // Draw UFO
    for (var m = 0; m < atmoParticles.length; m++) {
      var sp = atmoParticles[m];

      if (sp.type === "ufo") {
        sp.phase += 0.016;
        sp.x += sp.speed * sp.dir;
        sp.y = sp.baseY + Math.sin(sp.phase * 1.2) * 25;
        // Wrap around edges
        if (sp.dir > 0 && sp.x > W + 60) { sp.x = -60; sp.baseY = H * 0.1 + Math.random() * H * 0.15; }
        if (sp.dir < 0 && sp.x < -60) { sp.x = W + 60; sp.baseY = H * 0.1 + Math.random() * H * 0.15; }
        var tilt = sp.dir * 0.1 + Math.sin(sp.phase * 0.8) * 0.08;

        atmoCtx.save();
        atmoCtx.translate(sp.x, sp.y);
        atmoCtx.rotate(tilt);

        // Beam of light
        var beamAlpha = 0.05 + 0.03 * Math.sin(atmoTime * 3);
        atmoCtx.fillStyle = "rgba(150, 255, 200, " + beamAlpha + ")";
        atmoCtx.beginPath();
        atmoCtx.moveTo(-15, 8);
        atmoCtx.lineTo(15, 8);
        atmoCtx.lineTo(60, H);
        atmoCtx.lineTo(-60, H);
        atmoCtx.fill();

        // UFO body (ellipse)
        atmoCtx.fillStyle = "rgba(180, 180, 200, 0.7)";
        atmoCtx.beginPath();
        atmoCtx.ellipse(0, 0, 35, 10, 0, 0, Math.PI * 2);
        atmoCtx.fill();
        // UFO dome
        atmoCtx.fillStyle = "rgba(150, 220, 255, 0.6)";
        atmoCtx.beginPath();
        atmoCtx.ellipse(0, -6, 15, 12, 0, Math.PI, 0);
        atmoCtx.fill();
        // UFO lights
        var colors = ["#ff4444", "#44ff44", "#4444ff", "#ffff44"];
        for (var li = 0; li < 4; li++) {
          var lx = -22 + li * 15;
          var lAlpha = 0.5 + 0.5 * Math.sin(atmoTime * 5 + li * 1.5);
          atmoCtx.fillStyle = colors[li];
          atmoCtx.globalAlpha = lAlpha;
          atmoCtx.beginPath();
          atmoCtx.arc(lx, 3, 2.5, 0, Math.PI * 2);
          atmoCtx.fill();
        }
        atmoCtx.globalAlpha = 1;
        atmoCtx.restore();
      }
    }

  } else if (atmoMode === "hard") {
    // Base glow
    var baseGrad = atmoCtx.createLinearGradient(0, H, 0, H * 0.3);
    baseGrad.addColorStop(0, "rgba(255, 40, 0, 0.6)");
    baseGrad.addColorStop(0.3, "rgba(255, 60, 5, 0.25)");
    baseGrad.addColorStop(0.6, "rgba(200, 30, 0, 0.06)");
    baseGrad.addColorStop(1, "rgba(150, 10, 0, 0)");
    atmoCtx.fillStyle = baseGrad;
    atmoCtx.fillRect(0, H * 0.3, W, H * 0.7);

    // Flame particles and fire rat
    for (var j = 0; j < atmoParticles.length; j++) {
      var f = atmoParticles[j];

      if (f.type === "rat") {
        // Fast movement in current direction
        f.x += f.vx;
        f.y += f.vy;
        f.legPhase += 0.4;
        f.turnTimer += 0.016;

        // Bounce off screen edges
        if (f.x < -20) { f.x = -20; f.vx = Math.abs(f.vx); }
        if (f.x > W + 20) { f.x = W + 20; f.vx = -Math.abs(f.vx); }
        if (f.y < -20) { f.y = -20; f.vy = Math.abs(f.vy); }
        if (f.y > H + 20) { f.y = H + 20; f.vy = -Math.abs(f.vy); }

        // Random direction change every 1-3 seconds
        if (f.turnTimer > 1 + Math.random() * 2) {
          f.turnTimer = 0;
          var spd = 3 + Math.random() * 3;
          var angle = Math.random() * Math.PI * 2;
          f.vx = Math.cos(angle) * spd;
          f.vy = Math.sin(angle) * spd;
        }

        var ratAngle = Math.atan2(f.vy, f.vx);
        var kick = Math.sin(f.legPhase) * 3;
        var ctx = atmoCtx;

        ctx.save();
        ctx.translate(f.x, f.y);
        ctx.rotate(ratAngle);

        // === SHADOW (soft, large) ===
        var shGrad = ctx.createRadialGradient(0, 3, 2, 0, 3, 22);
        shGrad.addColorStop(0, "rgba(0,0,0,0.18)");
        shGrad.addColorStop(1, "rgba(0,0,0,0)");
        ctx.fillStyle = shGrad;
        ctx.beginPath();
        ctx.ellipse(0, 3, 20, 11, 0, 0, Math.PI * 2);
        ctx.fill();

        // === TAIL (segmented, tapered, pink-brown) ===
        ctx.lineCap = "round";
        var tw = Math.sin(f.legPhase * 1.5) * 4;
        for (var ts = 0; ts < 12; ts++) {
          var tt = ts / 12;
          var tx = -16 - ts * 3.5;
          var ty = Math.sin(tt * 4 + f.legPhase * 1.2) * (3 + tt * 4);
          var tWidth = 2.5 - tt * 1.8;
          if (tWidth < 0.4) tWidth = 0.4;
          var tAlpha = 0.7 - tt * 0.3;
          var tPink = Math.round(180 + tt * 40);
          ctx.strokeStyle = "rgba(" + tPink + "," + Math.round(130 + tt * 30) + "," + Math.round(120 + tt * 30) + "," + tAlpha + ")";
          ctx.lineWidth = tWidth;
          ctx.beginPath();
          if (ts === 0) {
            ctx.moveTo(-14, 0);
          } else {
            var prevTx = -16 - (ts - 1) * 3.5;
            var prevTy = Math.sin((ts - 1) / 12 * 4 + f.legPhase * 1.2) * (3 + (ts - 1) / 12 * 4);
            ctx.moveTo(prevTx, prevTy);
          }
          ctx.lineTo(tx, ty);
          ctx.stroke();
        }

        // === BACK LEGS (with paw pads) ===
        var legColors = ["rgba(75,50,32,0.9)", "rgba(65,42,28,0.85)"];
        // Back left
        ctx.save();
        ctx.translate(-9, -9 + kick);
        ctx.rotate(-0.25);
        var blGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, 5);
        blGrad.addColorStop(0, "rgba(85,58,38,0.95)");
        blGrad.addColorStop(1, legColors[0]);
        ctx.fillStyle = blGrad;
        ctx.beginPath();
        ctx.ellipse(0, 0, 3.5, 5.5, 0, 0, Math.PI * 2);
        ctx.fill();
        // Tiny paw pads
        ctx.fillStyle = "rgba(200,150,130,0.5)";
        ctx.beginPath(); ctx.arc(-1.5, -4, 1, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(0.5, -4.5, 0.8, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(1.8, -3.8, 0.8, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
        // Back right
        ctx.save();
        ctx.translate(-9, 9 - kick);
        ctx.rotate(0.25);
        ctx.fillStyle = blGrad;
        ctx.beginPath();
        ctx.ellipse(0, 0, 3.5, 5.5, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "rgba(200,150,130,0.5)";
        ctx.beginPath(); ctx.arc(-1.5, 4, 1, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(0.5, 4.5, 0.8, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(1.8, 3.8, 0.8, 0, Math.PI * 2); ctx.fill();
        ctx.restore();

        // === BODY (gradient fur) ===
        var bodyGrad = ctx.createRadialGradient(-2, -1, 2, 0, 0, 16);
        bodyGrad.addColorStop(0, "rgba(130,95,65,0.95)");
        bodyGrad.addColorStop(0.3, "rgba(105,72,48,0.95)");
        bodyGrad.addColorStop(0.7, "rgba(80,52,32,0.9)");
        bodyGrad.addColorStop(1, "rgba(60,38,22,0.85)");
        ctx.fillStyle = bodyGrad;
        ctx.beginPath();
        ctx.ellipse(0, 0, 16, 8.5, 0, 0, Math.PI * 2);
        ctx.fill();

        // Body fur texture (subtle strokes)
        ctx.strokeStyle = "rgba(140,105,70,0.25)";
        ctx.lineWidth = 0.6;
        for (var fi = 0; fi < 18; fi++) {
          var fx = -12 + fi * 1.5 + Math.sin(fi * 1.3) * 2;
          var fy = (fi % 2 === 0 ? -1 : 1) * (2 + Math.sin(fi) * 2);
          ctx.beginPath();
          ctx.moveTo(fx, fy);
          ctx.lineTo(fx - 2.5, fy + (fi % 2 === 0 ? -1.5 : 1.5));
          ctx.stroke();
        }

        // Spine highlight
        ctx.strokeStyle = "rgba(160,120,85,0.2)";
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(-12, 0);
        ctx.quadraticCurveTo(0, -0.5, 10, 0);
        ctx.stroke();

        // === FRONT LEGS (with paw pads) ===
        // Front left
        ctx.save();
        ctx.translate(8, -9 - kick);
        ctx.rotate(0.2);
        var flGrad = ctx.createRadialGradient(0, 0, 0, 0, 0, 4.5);
        flGrad.addColorStop(0, "rgba(90,62,42,0.95)");
        flGrad.addColorStop(1, "rgba(70,48,30,0.9)");
        ctx.fillStyle = flGrad;
        ctx.beginPath();
        ctx.ellipse(0, 0, 3, 5, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "rgba(210,160,140,0.5)";
        ctx.beginPath(); ctx.arc(-1, -4, 0.9, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(0.7, -4.3, 0.7, 0, Math.PI * 2); ctx.fill();
        ctx.restore();
        // Front right
        ctx.save();
        ctx.translate(8, 9 + kick);
        ctx.rotate(-0.2);
        ctx.fillStyle = flGrad;
        ctx.beginPath();
        ctx.ellipse(0, 0, 3, 5, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "rgba(210,160,140,0.5)";
        ctx.beginPath(); ctx.arc(-1, 4, 0.9, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(0.7, 4.3, 0.7, 0, Math.PI * 2); ctx.fill();
        ctx.restore();

        // === HEAD (gradient, slightly pointed snout) ===
        var headGrad = ctx.createRadialGradient(14, 0, 1, 14, 0, 8);
        headGrad.addColorStop(0, "rgba(125,90,60,0.95)");
        headGrad.addColorStop(0.5, "rgba(100,68,44,0.95)");
        headGrad.addColorStop(1, "rgba(80,52,32,0.9)");
        ctx.fillStyle = headGrad;
        ctx.beginPath();
        ctx.ellipse(14, 0, 7.5, 6, -0.05, 0, Math.PI * 2);
        ctx.fill();

        // Head fur texture
        ctx.strokeStyle = "rgba(145,110,75,0.2)";
        ctx.lineWidth = 0.5;
        for (var hi = 0; hi < 8; hi++) {
          var hx = 10 + hi * 1.2;
          var hy = (hi % 2 === 0 ? -1 : 1) * (1.5 + Math.sin(hi) * 1);
          ctx.beginPath();
          ctx.moveTo(hx, hy);
          ctx.lineTo(hx - 1.5, hy + (hi % 2 === 0 ? -1 : 1));
          ctx.stroke();
        }

        // === EARS (detailed with inner pink) ===
        // Left ear
        ctx.fillStyle = "rgba(100,65,42,0.9)";
        ctx.beginPath();
        ctx.ellipse(11, -6.5, 4.5, 4, 0.3, 0, Math.PI * 2);
        ctx.fill();
        // Inner ear (pink)
        var earGrad = ctx.createRadialGradient(11, -6.5, 0.5, 11, -6.5, 3);
        earGrad.addColorStop(0, "rgba(210,150,140,0.7)");
        earGrad.addColorStop(1, "rgba(180,120,100,0.3)");
        ctx.fillStyle = earGrad;
        ctx.beginPath();
        ctx.ellipse(11, -6.5, 3, 2.5, 0.3, 0, Math.PI * 2);
        ctx.fill();
        // Right ear
        ctx.fillStyle = "rgba(100,65,42,0.9)";
        ctx.beginPath();
        ctx.ellipse(11, 6.5, 4.5, 4, -0.3, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = earGrad;
        ctx.beginPath();
        ctx.ellipse(11, 6.5, 3, 2.5, -0.3, 0, Math.PI * 2);
        ctx.fill();

        // === EYES (glossy, with highlight) ===
        // Left eye
        ctx.fillStyle = "rgba(15,10,8,0.95)";
        ctx.beginPath();
        ctx.ellipse(17.5, -2.5, 1.8, 1.5, 0.1, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "rgba(255,255,255,0.7)";
        ctx.beginPath();
        ctx.arc(17, -3, 0.6, 0, Math.PI * 2);
        ctx.fill();
        // Right eye
        ctx.fillStyle = "rgba(15,10,8,0.95)";
        ctx.beginPath();
        ctx.ellipse(17.5, 2.5, 1.8, 1.5, -0.1, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "rgba(255,255,255,0.7)";
        ctx.beginPath();
        ctx.arc(17, 3, 0.6, 0, Math.PI * 2);
        ctx.fill();

        // === NOSE (wet, glossy pink) ===
        var noseGrad = ctx.createRadialGradient(20.5, 0, 0.3, 20.5, 0, 2.2);
        noseGrad.addColorStop(0, "rgba(220,140,130,1)");
        noseGrad.addColorStop(0.6, "rgba(190,110,100,0.95)");
        noseGrad.addColorStop(1, "rgba(160,85,75,0.9)");
        ctx.fillStyle = noseGrad;
        ctx.beginPath();
        ctx.ellipse(20.5, 0, 2.2, 1.8, 0, 0, Math.PI * 2);
        ctx.fill();
        // Nose highlight
        ctx.fillStyle = "rgba(255,220,210,0.6)";
        ctx.beginPath();
        ctx.ellipse(20, -0.5, 0.8, 0.5, -0.3, 0, Math.PI * 2);
        ctx.fill();
        // Nostrils
        ctx.fillStyle = "rgba(100,50,40,0.7)";
        ctx.beginPath();
        ctx.ellipse(21, -0.7, 0.5, 0.4, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.beginPath();
        ctx.ellipse(21, 0.7, 0.5, 0.4, 0, 0, Math.PI * 2);
        ctx.fill();

        // === WHISKERS ===
        ctx.strokeStyle = "rgba(180,160,140,0.5)";
        ctx.lineWidth = 0.5;
        // Left whiskers
        ctx.beginPath(); ctx.moveTo(19, -2); ctx.lineTo(28, -6); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(19.5, -1.5); ctx.lineTo(29, -3); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(19, -2.5); ctx.lineTo(27, -9); ctx.stroke();
        // Right whiskers
        ctx.beginPath(); ctx.moveTo(19, 2); ctx.lineTo(28, 6); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(19.5, 1.5); ctx.lineTo(29, 3); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(19, 2.5); ctx.lineTo(27, 9); ctx.stroke();

        ctx.restore();
        continue;
      }

      // Regular flame particle
      f.y -= f.vy;
      f.x += f.vx + Math.sin(atmoTime * 3 + f.phase) * 0.6;
      if (f.y + f.r < 0) {
        f.y = H + f.r;
        f.x = Math.random() * W;
      }
      var heightRatio = 1 - (f.y / H);
      if (heightRatio < 0) heightRatio = 0;
      if (heightRatio > 1) heightRatio = 1;
      var flicker = 0.6 + 0.4 * Math.sin(atmoTime * 7 + f.phase);
      var alpha = f.alpha * (1 - heightRatio * 0.8) * flicker;
      var cr = f.r * (1 - heightRatio * 0.3);
      var rr = 255;
      var gg = Math.round(Math.max(0, 200 - heightRatio * 180 + f.hue));
      var bb = Math.round(Math.max(0, 50 - heightRatio * 50));

      var fGrad = atmoCtx.createRadialGradient(f.x, f.y, cr * 0.05, f.x, f.y, cr);
      fGrad.addColorStop(0, "rgba(" + rr + "," + gg + "," + bb + "," + alpha + ")");
      fGrad.addColorStop(0.4, "rgba(" + rr + "," + Math.round(gg * 0.5) + "," + Math.round(bb * 0.3) + "," + (alpha * 0.5) + ")");
      fGrad.addColorStop(1, "rgba(150,10,0,0)");
      atmoCtx.fillStyle = fGrad;
      atmoCtx.beginPath();
      atmoCtx.arc(f.x, f.y, cr, 0, Math.PI * 2);
      atmoCtx.fill();
    }
  }

  if (atmoMode === "competition") {
    for (var ci = 0; ci < atmoParticles.length; ci++) {
      var cp = atmoParticles[ci];
      if (cp.type === "spark") {
        cp.y -= cp.vy;
        cp.x += cp.vx + Math.sin(atmoTime * 3 + cp.phase) * 0.4;
        if (cp.y < -10) { cp.y = H + 10; cp.x = Math.random() * W; }
        var heightR = cp.y / H;
        var cAlpha = cp.alpha * heightR * (0.7 + 0.3 * Math.sin(atmoTime * 5 + cp.phase));
        var gold = Math.round(200 + cp.hue);
        var sparkGrad = atmoCtx.createRadialGradient(cp.x, cp.y, 0, cp.x, cp.y, cp.r * 2);
        sparkGrad.addColorStop(0, "rgba(255," + gold + ",50," + cAlpha + ")");
        sparkGrad.addColorStop(1, "rgba(255," + gold + ",0,0)");
        atmoCtx.fillStyle = sparkGrad;
        atmoCtx.beginPath();
        atmoCtx.arc(cp.x, cp.y, cp.r * 2, 0, Math.PI * 2);
        atmoCtx.fill();
      } else if (cp.type === "trophy") {
        var pulse = 0.85 + 0.15 * Math.sin(atmoTime * 2);
        var tGrad = atmoCtx.createRadialGradient(cp.x, cp.y, 10, cp.x, cp.y, 80 * pulse);
        tGrad.addColorStop(0, "rgba(255,215,0,0.18)");
        tGrad.addColorStop(1, "rgba(255,180,0,0)");
        atmoCtx.fillStyle = tGrad;
        atmoCtx.beginPath();
        atmoCtx.arc(cp.x, cp.y, 80 * pulse, 0, Math.PI * 2);
        atmoCtx.fill();
      }
    }
  }

  requestAnimationFrame(animateAtmo);
}

// ==================== PICK WORD ====================
function pickWord() {
  var available = words.filter(function(w) { return usedWords.indexOf(w) === -1; });
  
  // In ranked mode, don't reset usedWords - end game when all words are used
  if (available.length === 0) {
    if (isRankedMode || isPracticeMode) {
      // End the game gracefully instead of repeating words
      endGame();
      return null;
    } else {
      // In regular modes, allow word reuse
      usedWords = [];
      available = words.slice();
    }
  }

  // Remove preloadedAudio preference to prevent word repetition
  // Just pick randomly from available words
  var word = available[Math.floor(Math.random() * available.length)];

  usedWords.push(word);
  currentWord = word;
  return word;
}

// ==================== REFERENCE IMAGE ====================
function updateRefImage(word) {
  var emojiEl = document.getElementById("ref-image");
  var photoEl = document.getElementById("ref-image-photo");
  emojiEl.textContent = "";
  emojiEl.classList.remove("ref-image-enter");
  photoEl.classList.add("hidden");
  photoEl.src = "";

  fetch("/image/" + encodeURIComponent(word))
    .then(function(res) { return res.json(); })
    .then(function(data) {
      if (data.url) {
        photoEl.src = data.url;
        photoEl.classList.remove("hidden");
        photoEl.classList.remove("ref-image-enter");
        void photoEl.offsetWidth;
        photoEl.classList.add("ref-image-enter");
        emojiEl.textContent = "";
      } else {
        emojiEl.textContent = data.emoji || "";
        emojiEl.classList.remove("ref-image-enter");
        void emojiEl.offsetWidth;
        emojiEl.classList.add("ref-image-enter");
        photoEl.classList.add("hidden");
      }
    })
    .catch(function() {
      emojiEl.textContent = "";
      photoEl.classList.add("hidden");
    });
}

// ==================== KEYBOARD FADE SYSTEM ====================
function getLettersNotInWord(word) {
  var clean = word.replace(/ /g, "");
  var wordLetters = {};
  for (var i = 0; i < clean.length; i++) wordLetters[clean[i]] = true;
  var others = [];
  for (var j = 0; j < ALL_KEYS.length; j++) {
    if (!wordLetters[ALL_KEYS[j]]) others.push(ALL_KEYS[j]);
  }
  return others;
}

function shuffleArray(arr) {
  for (var i = arr.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
  }
  return arr;
}

function resetKeyboardVisibility() {
  hiddenKeys = [];
  var keys = document.querySelectorAll(".key");
  for (var i = 0; i < keys.length; i++) {
    keys[i].classList.remove("key-faded");
    keys[i].style.opacity = "";
    keys[i].style.pointerEvents = "";
  }
  clearInterval(keyFadeTimer);
  keyFadeTimer = null;
}

function startKeyFading() {
  resetKeyboardVisibility();
  var config = DIFF_CONFIG[currentDifficulty] || DIFF_CONFIG.easy;
  var lettersToHide = shuffleArray(getLettersNotInWord(currentWord));
  var fadeIndex = 0;
  var totalToHide = lettersToHide.length;
  var fadeInterval = Math.max(800, Math.floor((config.wordTime * 1000 * config.fadeSpeed) / (totalToHide + 2)));

  keyFadeTimer = setInterval(function() {
    if (!gameActive || fadeIndex >= totalToHide) { clearInterval(keyFadeTimer); return; }
    var letter = lettersToHide[fadeIndex];
    var keyEl = document.querySelector('.key[data-letter="' + letter + '"]');
    if (keyEl) { keyEl.classList.add("key-faded"); hiddenKeys.push(letter); }
    fadeIndex++;
  }, fadeInterval);
}

// ==================== GAME START ====================
function startGame(difficulty) {
  playerName = document.getElementById("player-name").value.trim();
  if (!playerName) {
    document.getElementById("player-name").focus();
    document.getElementById("player-name").classList.add("input-shake");
    setTimeout(function() { document.getElementById("player-name").classList.remove("input-shake"); }, 500);
    return;
  }

  localStorage.setItem(lsKey("spelling_bee_name"), playerName);

  var config = DIFF_CONFIG[difficulty] || DIFF_CONFIG.easy;
  currentDifficulty = difficulty;
  maxTime = gameMode === "speak" ? Math.round(config.wordTime * 2.5) : config.wordTime;
  timeLeft = maxTime;
  skippedWords = 0;
  score = 0;
  usedWords = [];
  reviewWords = [];
  streak = 0;
  bestStreak = 0;
  totalBonusTime = 0;
  wordsCompleted = 0;
  audioPlayCount = 0;
  spellPlayCount = 0;
  currentRound = 1;
  wordInRound = 0;
  wrongLetters = 0;
  wordScores = [];
  lives = maxLives;
  updateScore();
  updateStreak();
  updateRoundIndicator();
  updateLivesDisplay();

  var badge = document.getElementById("difficulty-badge");
  badge.textContent = difficulty.toUpperCase();
  badge.className = "difficulty-badge " + difficulty;

  document.getElementById("player-tag").textContent = playerName;

  setAtmosphere(difficulty);

  // Show game screen with loading state while words are fetched
  showScreen("game-screen");
  showLoadingState();

  fetch(groupQS("/words?difficulty=" + difficulty + "&week=" + selectedWeek))
    .then(function(res) { return res.json(); })
    .then(function(data) {
      words = data.words;
      var word = pickWord();
      renderBoxes(word);
      updateRefImage(word);
      if (gameMode === "speak") {
        buildKeyboard();
        showSpeakingUI();
      } else {
        hideSpeakingUI();
        buildKeyboard();
        startKeyFading();
      }
      setupNativeKeyboardDetection();
      playAudio();
      wordStartTime = Date.now();
      wrongLetters = 0;
      startTimer();
      gameActive = true;
      // Preload next word's audio immediately
      preloadNextWordAudio();
    })
    .catch(function(err) {
      console.error("Failed to load words:", err);
      alert("Could not load words. Is the server running?");
    });
}

function playAgain() {
  // If this was a ranked game, check attempts before allowing replay
  if (_lastGameWasRanked) {
    // Re-fetch attempts from server
    fetch(groupQS("/api/ranked-check?name=" + encodeURIComponent(playerName)))
      .then(function(r) { return r.json(); })
      .then(function(data) {
        rankedAttemptsLeft = data.attempts_left || 0;
        updateRankedBadge();
        if (rankedAttemptsLeft <= 0) {
          alert("No ranked attempts left this week! Resets Monday.");
          returnToMenu();
        } else {
          // Reset ranked state before opening modal
          _lastGameWasRanked = false;
          openRankedMode();
        }
      })
      .catch(function() { returnToMenu(); });
    return;
  }
  if (isCompetitionMode) { startCompetition(); return; }
  startGame(currentDifficulty);
}
var _lastGameWasRanked = false;
var _skipCompEndGameSubmit = false;

// ==================== COMPETITION MODE ====================
var selectedTeamId = null;
var selectedTeamName = "";
var selectedTeamColor = "#f59e0b";
var selectedTeamEmoji = "";
var teamsData = [];

function startCompetition() {
  if (!selectedTeamId) return;

  isCompetitionMode = true;
  compTeamId = selectedTeamId;
  compTeamName = selectedTeamName;
  compTeamColor = selectedTeamColor;
  compTeamEmoji = selectedTeamEmoji;
  compCorrect = 0;
  compWrong = 0;
  compWordTime = COMP_TIME_START;

  // Reset game state
  score = 0;
  usedWords = [];
  reviewWords = [];
  streak = 0;
  bestStreak = 0;
  totalBonusTime = 0;
  wordsCompleted = 0;
  audioPlayCount = 0;
  spellPlayCount = 0;
  currentRound = 1;
  wordInRound = 0;
  wrongLetters = 0;
  wordScores = [];
  lives = 3;
  maxLives = 3;
  currentDifficulty = "competition";

  // NEW: Reset streak bank and shield
  streakBank = 0;
  streakShield = false;

  updateScore();
  updateStreak();
  updateLivesDisplay();

  var badge = document.getElementById("difficulty-badge");
  badge.textContent = "COMPETITION";
  badge.className = "difficulty-badge competition";

  var compBadge = document.getElementById("comp-team-badge");
  compBadge.textContent = "🏅 " + compTeamName;
  compBadge.style.background = compTeamColor;
  compBadge.classList.remove("hidden");

  document.getElementById("player-tag").textContent = playerName;
  document.getElementById("round-indicator").textContent = "Competition Mode";

  setAtmosphere("competition");
  showScreen("game-screen");
  showLoadingState();

  // Load all words for competition pool
  fetch(groupQS("/words_all"))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      // Mix: 30% easy, 40% medium, 30% hard — shuffled
      var easy = (data.easy || []).slice();
      var medium = (data.medium || []).slice();
      var hard = (data.hard || []).slice();
      shuffleArray(easy); shuffleArray(medium); shuffleArray(hard);
      var easyN = Math.ceil(easy.length * 0.3);
      var medN = Math.ceil(medium.length * 0.4);
      var hardN = Math.ceil(hard.length * 0.3);
      compAllWords = easy.slice(0, easyN).concat(medium.slice(0, medN)).concat(hard.slice(0, hardN));
      shuffleArray(compAllWords);
      words = compAllWords.slice();

      maxTime = compWordTime;
      timeLeft = maxTime;

      pickWord(); // sets currentWord
      renderBoxes(currentWord);
      updateRefImage(currentWord);
      hideSpeakingUI();
      buildKeyboard();
      resetKeyboardVisibility();
      setupNativeKeyboardDetection();
      playAudio();
      wordStartTime = Date.now();
      wrongLetters = 0;
      startTimer();
      gameActive = true;
      preloadNextWordAudio();
    })
    .catch(function(err) {
      console.error("Competition words load error:", err);
      alert("Could not load words. Is the server running?");
    });
}

function compPickNextWord() {
  // Ranked/practice: use ranked shrink constants + anti-snowball scaling
  if (isRankedMode || isPracticeMode) {
    var shrinkAmt = getAntiSnowballShrink(compCorrect);
    var minTime = getAntiSnowballMinTime(compCorrect);
    var steps = Math.floor(compCorrect / RANKED_SHRINK_EVERY);
    compWordTime = Math.max(minTime, RANKED_TIME_START - steps * shrinkAmt);
  } else {
    var steps2 = Math.floor(compCorrect / COMP_SHRINK_EVERY);
    compWordTime = Math.max(COMP_TIME_MIN, COMP_TIME_START - steps2 * COMP_SHRINK_BY);
  }
  maxTime = compWordTime;
  timeLeft = compWordTime;
}

// ==================== SCORE CALCULATION UTILITY ====================
function calculateScoreComponents(word, timeTaken, errors, wordTime, isBomb, streakMult) {
  var wordLen = word.replace(/ /g, "");
  wordLen = Math.max(1, wordLen.length);
  var base = wordLen * 10;
  
  var safeWordTime = Math.max(1, wordTime || 20);
  var speedRatio = Math.max(0, 1 - timeTaken / safeWordTime);
  var accuracyRatio = Math.max(0, 1 - errors / wordLen);
  
  var speedBonus = Math.round(base * speedRatio * 0.3);
  var accuracyBonus = Math.round(base * accuracyRatio * 0.2);
  var comboBonus = (speedRatio >= 0.6 && accuracyRatio >= 0.8) ? Math.round(base * 0.1) : 0;
  var errorPenalty = Math.round(base * errors * 0.15);
  
  var total = Math.max(0, base + speedBonus + accuracyBonus + comboBonus - errorPenalty);
  var isPerfect = (errors === 0 && speedRatio >= 0.4);
  if (isPerfect) total = Math.round(total * 1.2);
  if (isBomb) total = Math.round(total * 2);
  total = Math.round(total * streakMult);
  
  return { base: base, speedBonus: speedBonus, accuracyBonus: accuracyBonus, comboBonus: comboBonus, errorPenalty: errorPenalty, total: total, isPerfect: isPerfect, isBomb: isBomb };
}

function compCalcScore(word, timeTaken, errors) {
  var streakMult = getBalancedStreakMultiplier();
  var result = calculateScoreComponents(word, timeTaken, errors, compWordTime, isBombWord, streakMult);
  if (isBombWord && isRankedMode) rankedBombsCorrect++;
  return result;
}

function compHandleCorrect() {
  stopAllAudio();
  compCorrect++;
  wordsCompleted++;
  wordInRound++;
  streak++;
  if (streak > bestStreak) bestStreak = streak;

  // NEW: Update streak bank and shield
  updateStreakBank(streak);
  updateStreakShield(streak);

  var timeTaken = (Date.now() - wordStartTime) / 1000;
  var sc = compCalcScore(currentWord, timeTaken, wrongLetters);
  wordScores.push({ word: currentWord, score: sc.total, time: Math.round(timeTaken * 10) / 10, errors: wrongLetters, perfect: sc.isPerfect, bomb: sc.isBomb });
  // Always recalculate score from wordScores to ensure consistency
  score = wordScores.reduce(function(sum, w) { return sum + w.score; }, 0);

  // Popup label
  var popLabel = "+" + sc.total;
  if (sc.isBomb) popLabel = "💣 BOMB! +" + sc.total;
  else if (sc.isPerfect) popLabel = "🎯 PERFECT! +" + sc.total;
  else if (streak >= 3) popLabel = "🔥 STREAK! +" + sc.total;

  // Note: Streak multiplier is already applied in compCalcScore(), no need for additional bonuses
  showBonus(popLabel);
  sfxComplete();
  if (streak >= 3) { sfxStreak(); launchConfetti(30 + streak * 5); }

  // After bomb word, hide indicator and reset
  if (isBombWord) {
    isBombWord = false;
    var ind = document.getElementById("bomb-indicator");
    if (ind) { ind.classList.add("hidden"); ind.classList.remove("bomb-pulse"); }
  }

  updateScore();
  updateStreak();

  // Fill boxes
  var boxes = document.querySelectorAll(".letter-box");
  var wordChars = currentWord.split("");
  var bi = 0;
  for (var w = 0; w < wordChars.length; w++) {
    if (wordChars[w] === " ") continue;
    if (boxes[bi]) { boxes[bi].textContent = wordChars[w]; boxes[bi].classList.add("correct"); }
    bi++;
  }
  for (var c = 0; c < boxes.length; c++) {
    (function(b, delay) { setTimeout(function() { b.classList.add("celebrate"); }, delay); })(boxes[c], c * 60);
  }

  gameActive = false;
  clearInterval(timer);

  // Adaptive: update time for next word
  compPickNextWord();

  setTimeout(function() { nextWord(); }, 900);
}

function compHandleWrong() {
  compWrong++;
  wrongLetters++;
  
  // NEW: Check streak shield before breaking
  if (streakShield) {
    streakShield = false;  // Consume shield, keep streak
    showBonus("🛡️ Shield Protected Streak!");
  } else {
    if (streak >= 3) streakBreakEffect();
    breakStreak();  // Use new breakStreak function with bank recovery
  }
  
  updateStreak();
  sfxWrong();
  showPenalty("-2s");
  timeLeft = Math.max(1, timeLeft - 2);
  if (reviewWords.indexOf(currentWord) === -1) reviewWords.push(currentWord);

  // Screen shake
  document.getElementById("game-screen").classList.add("screen-shake");
  setTimeout(function() { document.getElementById("game-screen").classList.remove("screen-shake"); }, 300);
}

function compEndGame() {
  gameActive = false;
  clearInterval(timer);
  stopAllAudio();
  clearHint();
  resetKeyboardVisibility();

  var compBadge = document.getElementById("comp-team-badge");
  compBadge.classList.add("hidden");

  var isNewBest = saveGameResult();

  var scoreEl = document.getElementById("final-score-number");
  animateNumber(scoreEl, 0, score, 800);
  document.getElementById("final-streak").textContent = bestStreak;
  document.getElementById("final-words-completed").textContent = wordsCompleted + " words";

  var breakdownEl = document.getElementById("score-breakdown");
  if (breakdownEl) {
    var html = "<table class='breakdown-table'><tr><th>Word</th><th>Time</th><th>Errors</th><th>Score</th></tr>";
    for (var i = 0; i < wordScores.length; i++) {
      var ws = wordScores[i];
      var rowClass = ws.errors === 0 ? " class='perfect'" : "";
      html += "<tr" + rowClass + "><td>" + ws.word + "</td><td>" + ws.time + "s</td><td>" + ws.errors + "</td><td>" + ws.score + "</td></tr>";
    }
    html += "</table>";
    breakdownEl.innerHTML = html;
  }

  if (isNewBest && score > 0) {
    document.getElementById("new-best").classList.remove("hidden");
    launchConfetti(150);
    sfxCelebration();
  } else {
    document.getElementById("new-best").classList.add("hidden");
    if (score > 0) { launchConfetti(60); sfxCelebration(); }
    else { sfxGameOver(); }
  }

  document.getElementById("review-section").classList.add("hidden");
  document.getElementById("final-rank").classList.add("hidden");

  // Submit score to individual leaderboard + team score
  var finalScore = score;
  document.getElementById("game-over-leaderboard").innerHTML =
    '<div class="go-lb-section"><h3 class="go-lb-title">🏆 Competition — Team ' + escapeHtml(compTeamName) + '</h3><p class="lb-empty" style="opacity:0.5">Submitting...</p></div>';

  var submitDone = false;
  function afterSubmit() {
    if (submitDone) return;
    submitDone = true;
    // Show team leaderboard on game over (delay to allow backend to aggregate scores)
    setTimeout(function() {
      fetch(groupQS("/api/team-leaderboard"))
        .then(function(r) { return r.json(); })
        .then(function(data) {
          renderCompGameOverLeaderboard(data.teams || [], finalScore);
          buildReviewWithAudio();
        })
        .catch(function() { buildReviewWithAudio(); });
    }, 1500); // 1.5 second delay for backend processing
  }

  if (playerName && finalScore > 0 && !_skipCompEndGameSubmit) {
    // Submit individual score tagged as competition
    fetch("/leaderboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(groupBody({ name: playerName, score: finalScore, difficulty: currentDifficulty || "medium", streak: bestStreak, team_id: compTeamId, team_name: compTeamName, team_emoji: compTeamEmoji, is_competition: true, is_ranked: isRankedMode, accuracy: wordsCompleted > 0 ? wordsCompleted / (wordsCompleted + skippedWords) : 0, words_completed: wordsCompleted + skippedWords, bombs_correct: rankedBombsCorrect || 0, reached_x3: rankedReachedX3 || false }))
    }).then(function(response) {
      if (!response.ok) {
        throw new Error("HTTP " + response.status + ": " + response.statusText);
      }
      afterSubmit();
    }).catch(function(error) {
      console.error("[SCORE] Competition score submission failed:", error);
      if (finalScore > 0) {
        setTimeout(function() {
          fetch("/leaderboard", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(groupBody({ name: playerName, score: finalScore, difficulty: currentDifficulty || "medium", streak: bestStreak, team_id: compTeamId, team_name: compTeamName, team_emoji: compTeamEmoji, is_competition: true, is_ranked: isRankedMode, accuracy: wordsCompleted > 0 ? wordsCompleted / (wordsCompleted + skippedWords) : 0, words_completed: wordsCompleted + skippedWords, bombs_correct: rankedBombsCorrect || 0, reached_x3: rankedReachedX3 || false }))
          }).then(function(response) {
            if (response.ok) {
              console.log("[SCORE] Competition retry successful");
              afterSubmit();
            } else {
              console.error("[SCORE] Competition retry failed:", response.status);
              afterSubmit();
            }
          }).catch(function(retryError) {
            console.error("[SCORE] Competition retry failed:", retryError);
            afterSubmit();
          });
        }, 2000);
      } else {
        afterSubmit();
      }
    });
  } else {
    afterSubmit();
  }

  showScreen("game-over-screen");
}

function renderCompGameOverLeaderboard(teams, myScore) {
  var container = document.getElementById("game-over-leaderboard");
  var html = '<div class="go-lb-section">';
  html += '<h3 class="go-lb-title">🏆 Weekly Team Standings</h3>';
  if (teams.length === 0) {
    html += '<p class="lb-empty">No team scores yet this week.</p>';
  } else {
    var medals = ["🥇", "🥈", "🥉"];
    html += '<div class="comp-podium-mini">';
    teams.forEach(function(t, i) {
      var isMyTeam = (t.id === compTeamId);
      // Calculate actual team score as sum of all members' best scores
      var actualTeamScore = 0;
      if (t.members && Array.isArray(t.members)) {
        actualTeamScore = t.members.reduce(function(sum, m) {
          return sum + (m.best_score || 0);
        }, 0);
      }
      html += '<div class="podium-mini-row' + (isMyTeam ? " podium-my-team" : "") + '">';
      html += '<span class="podium-mini-rank">' + (i < 3 ? medals[i] : (i + 1) + ".") + '</span>';
      html += '<span class="podium-mini-dot" style="background:' + (t.color || "#f59e0b") + '"></span>';
      html += '<span class="podium-mini-name">' + escapeHtml(t.name) + (isMyTeam ? " ← You" : "") + '</span>';
      html += '<span class="podium-mini-score">' + actualTeamScore + ' pts</span>';
      html += '</div>';
    });
    html += '</div>';
  }
  html += '</div>';
  container.innerHTML = html;
}

function returnToMenu() {
  gameActive = false;
  clearInterval(timer);
  resetKeyboardVisibility();
  hideSpeakingUI();
  clearAtmosphere();
  isCompetitionMode = false;
  var compBadge = document.getElementById("comp-team-badge");
  if (compBadge) compBadge.classList.add("hidden");
  // Reset native keyboard state
  teardownNativeKeyboardDetection();
  useNativeKeyboard = false;
  var toggle = document.getElementById("kb-toggle");
  if (toggle) toggle.classList.remove("active");
  var kbLabel = document.getElementById("kb-toggle-label");
  if (kbLabel) kbLabel.textContent = "Device Keyboard";
  var nativeInput = document.getElementById("native-input");
  if (nativeInput) { nativeInput.classList.add("hidden"); nativeInput.classList.remove("active"); nativeInput.blur(); nativeInput.value = ""; }
  var bank = document.getElementById("letter-bank");
  if (bank) bank.classList.remove("hidden");
  document.body.classList.remove("native-keyboard-active");
  showScreen("menu-screen");
}

// ==================== QUIT CONFIRMATION ====================
var gamePausedForQuit = false;

function confirmQuit() {
  gamePausedForQuit = gameActive;
  gameActive = false;
  clearInterval(timer);
  document.getElementById("quit-modal").classList.remove("hidden");
}

function closeQuitModal() {
  document.getElementById("quit-modal").classList.add("hidden");
  if (gamePausedForQuit) { gameActive = true; startTimer(); }
}

function quitGame() {
  document.getElementById("quit-modal").classList.add("hidden");
  gamePausedForQuit = false;
  
  // User choice - consume attempt if game was meaningful
  if (isRankedMode && !rankedAttemptConsumed && wordScores.length >= 3) {
    console.log("[ATTEMPT] User quit after meaningful progress - consuming attempt");
    rankedAttemptConsumed = true;
    fetch("/leaderboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(groupBody({ name: playerName, score: 0, difficulty: currentDifficulty,
        streak: 0, is_ranked: true, _consume_only: true }))
    }).catch(function(err) {
      console.error("[ATTEMPT] Failed to consume attempt for quit:", err);
    });
  } else if (isRankedMode && !rankedAttemptConsumed && wordScores.length < 3) {
    console.log("[ATTEMPT] User quit early - attempt not consumed");
    showBonus("✅ Attempt protected - quit early");
    rankedAttemptConsumed = true; // Mark to prevent re-entry
  } else if (isRankedMode && rankedAttemptConsumed) {
    console.log("[ATTEMPT] User quit after attempt consumption");
  }
  
  returnToMenu();
}

// ==================== LEADERBOARD ====================
var currentLbTab = "easy";

function showLeaderboard() {
  fetch(groupQS("/leaderboard"))
    .then(function(res) { return res.json(); })
    .then(function(data) {
      leaderboardData = data;
      currentLbTab = "easy";
      renderLbTab("easy");
      updateLbTabButtons();
      document.getElementById("leaderboard-modal").classList.remove("hidden");
    })
    .catch(function() {
      document.getElementById("leaderboard-modal").classList.remove("hidden");
    });
}

function closeLeaderboard() {
  document.getElementById("leaderboard-modal").classList.add("hidden");
}

function switchLbTab(tab) {
  currentLbTab = tab;
  renderLbTab(tab);
  updateLbTabButtons();
}

function updateLbTabButtons() {
  var tabs = document.querySelectorAll("#leaderboard-modal .lb-tab");
  tabs.forEach(function(t) { t.classList.remove("active"); });
  tabs.forEach(function(t) {
    var txt = t.textContent.trim();
    if (currentLbTab === "teams" && txt.indexOf("Teams") !== -1) t.classList.add("active");
    else if (currentLbTab === "easy" && txt === "Easy") t.classList.add("active");
    else if (currentLbTab === "medium" && txt === "Medium") t.classList.add("active");
    else if (currentLbTab === "hard" && txt === "Hard") t.classList.add("active");
  });
}

function renderLbTab(tab) {
  var list = document.getElementById("lb-list");

  if (tab === "teams") {
    list.innerHTML = '<p class="lb-empty" style="opacity:0.5">Loading team standings...</p>';
    fetch(groupQS("/api/team-leaderboard"))
      .then(function(r) { return r.json(); })
      .then(function(data) {
        var teams = data.teams || [];
        if (teams.length === 0) {
          list.innerHTML = '<p class="lb-empty">No team scores yet this week.<br><small>Play Ranked Mode to earn points for your team!</small></p>';
          return;
        }
        var medals = ["🥇", "🥈", "🥉"];
        var weekLabel = data.week_label || "";

        // Fetch all team members in parallel then render
        var teamFetches = teams.map(function(t) {
          return fetch(groupQS("/api/team-members?team_id=" + encodeURIComponent(t.id)))
            .then(function(r) { return r.json(); })
            .catch(function() { return {members:[]}; });
        });
        Promise.all(teamFetches).then(function(memberResults) {
          var html = '<div class="teams-lb-header">&#127942; Weekly Team Standings' + (weekLabel ? ' <small style="opacity:0.5;font-size:0.7rem">' + weekLabel + '</small>' : '') + '</div>';

          // Visual podium for top 3: arranged as 2nd | 1st | 3rd
          var top3 = teams.slice(0, 3);
          if (top3.length >= 1) {
            // Reorder: [2nd, 1st, 3rd] for podium visual
            var podiumOrder = top3.length >= 3 ? [1, 0, 2] : (top3.length === 2 ? [1, 0] : [0]);
            // Indexed by rank: 0=1st(gold), 1=2nd(silver), 2=3rd(bronze)
            var podiumHeights = ["140px", "110px", "90px"];
            var podiumColors = [
              "linear-gradient(180deg, rgba(255,215,0,0.3) 0%, rgba(255,215,0,0.08) 100%)",
              "linear-gradient(180deg, rgba(192,192,192,0.25) 0%, rgba(192,192,192,0.08) 100%)",
              "linear-gradient(180deg, rgba(205,127,50,0.2) 0%, rgba(205,127,50,0.06) 100%)"
            ];
            var podiumBorders = ["rgba(255,215,0,0.5)", "rgba(192,192,192,0.4)", "rgba(205,127,50,0.35)"];

            html += '<div class="team-podium-visual">';
            podiumOrder.forEach(function(idx) {
              var t = top3[idx];
              if (!t) return;
              var members = (memberResults[idx] && memberResults[idx].members) || [];
              var teamId = "team-expand-" + idx;
              var placeIdx = idx; // 0=1st, 1=2nd, 2=3rd
              html += '<div class="team-podium-col" onclick="toggleTeamExpand(\'' + teamId + '\')" style="cursor:pointer">';
              html += '<div class="team-podium-emoji">' + (t.emoji || '🏅') + '</div>';
              html += '<div class="team-podium-name">' + escapeHtml(t.name) + '</div>';
              // Calculate actual team score as sum of all members' best scores
              var actualTeamScore = 0;
              if (members && Array.isArray(members)) {
                actualTeamScore = members.reduce(function(sum, m) {
                  return sum + (m.best_score || 0);
                }, 0);
              }
              html += '<div class="team-podium-pts">' + actualTeamScore + '</div>';
              html += '<div class="team-podium-block" style="height:' + podiumHeights[placeIdx] + ';background:' + podiumColors[placeIdx] + ';border-color:' + podiumBorders[placeIdx] + '">';
              html += '<span class="team-podium-medal">' + medals[placeIdx] + '</span>';
              html += '</div>';
              html += '<div class="team-podium-players">' + members.length + ' players ▾</div>';
              // Expandable members
              html += '<div id="' + teamId + '" class="team-members-expand hidden">';
              if (members.length === 0) {
                html += '<div class="team-expand-empty">No scores yet</div>';
              } else {
                members.forEach(function(m, mi) {
                  var mMedal = mi < 3 ? medals[mi] : (mi + 1) + ".";
                  html += '<div class="team-expand-row">';
                  html += '<span class="team-expand-rank">' + mMedal + '</span>';
                  html += '<span class="team-expand-name">' + escapeHtml(m.name) + '</span>';
                  html += '<span class="team-expand-score">' + (m.best_score || 0) + ' pts</span>';
                  html += '</div>';
                });
              }
              html += '</div>';
              html += '</div>';
            });
            html += '</div>';
          }

          // Remaining teams (4th+) in compact list
          var rest = teams.slice(3);
          if (rest.length > 0) {
            html += '<div class="teams-rest-list">';
            rest.forEach(function(t, i) {
              var rank = i + 4;
              var members = (memberResults[i + 3] && memberResults[i + 3].members) || [];
              var teamId = "team-expand-" + (i + 3);
              html += '<div class="teams-lb-row" onclick="toggleTeamExpand(\'' + teamId + '\')" style="cursor:pointer">';
              html += '<span class="teams-lb-rank">' + rank + '.</span>';
              html += '<span class="teams-lb-emoji">' + (t.emoji || '🏅') + '</span>';
              html += '<span class="teams-lb-dot" style="background:' + (t.color || "#f59e0b") + '"></span>';
              html += '<span class="teams-lb-name">' + escapeHtml(t.name) + '</span>';
              // Calculate actual team score as sum of all members' best scores
              var actualTeamScore = 0;
              if (members && Array.isArray(members)) {
                actualTeamScore = members.reduce(function(sum, m) {
                  return sum + (m.best_score || 0);
                }, 0);
              }
              html += '<span class="teams-lb-score">' + actualTeamScore + ' pts</span>';
              html += '<span class="teams-lb-games">' + members.length + ' players ▾</span>';
              html += '</div>';
              html += '<div id="' + teamId + '" class="team-members-expand hidden">';
              if (members.length === 0) {
                html += '<div class="team-expand-empty">No scores yet</div>';
              } else {
                members.forEach(function(m, mi) {
                  var mMedal = mi < 3 ? medals[mi] : (mi + 1) + ".";
                  html += '<div class="team-expand-row">';
                  html += '<span class="team-expand-rank">' + mMedal + '</span>';
                  html += '<span class="team-expand-name">' + escapeHtml(m.name) + '</span>';
                  html += '<span class="team-expand-score">' + (m.best_score || 0) + ' pts</span>';
                  html += '</div>';
                });
              }
              html += '</div>';
            });
            html += '</div>';
          }

          list.innerHTML = html;
        });
      })
      .catch(function() {
        list.innerHTML = '<p class="lb-empty" style="color:#f87171">Could not load team standings.</p>';
      });
    return;
  }

  var entries = (leaderboardData[tab] || []).slice(0, 10);

  if (entries.length === 0) {
    list.innerHTML = '<p class="lb-empty">No scores yet. Be the first!</p>';
    return;
  }

  var medals = ["🥇", "🥈", "🥉"];
  var podiumClasses = ["lb-podium-gold", "lb-podium-silver", "lb-podium-bronze"];
  var html = '';

  // Top 3: creative podium cards
  var top3 = entries.slice(0, 3);
  if (top3.length > 0) {
    html += '<div class="lb-podium-section">';
    top3.forEach(function(e, i) {
      var isMe = e.name === playerName;
      html += '<div class="lb-podium-card ' + podiumClasses[i] + (isMe ? ' lb-podium-me' : '') + '">';
      html += '<div class="lb-podium-rank">' + medals[i] + '</div>';
      html += '<div class="lb-podium-name">' + escapeHtml(e.name) + '</div>';
      html += '<div class="lb-podium-details"><span class="lb-podium-score">' + e.score + ' pts</span></div>';
      html += '<div class="lb-podium-streak">' + (e.streak || 0) + ' streak</div>';
      html += '</div>';
    });
    html += '</div>';
  }

  // Rest: compact table
  var rest = entries.slice(3);
  if (rest.length > 0) {
    html += '<table class="lb-table"><thead><tr><th>#</th><th>Name</th><th>Score</th><th>Streak</th></tr></thead><tbody>';
    rest.forEach(function(e, i) {
      var rank = i + 4;
      var highlight = (e.name === playerName) ? ' class="lb-highlight"' : '';
      html += '<tr' + highlight + '><td>' + rank + '</td><td>' + escapeHtml(e.name) + '</td><td>' + e.score + '</td><td>' + (e.streak || 0) + '</td></tr>';
    });
    html += '</tbody></table>';
  }
  list.innerHTML = html;
  
  // Make names clickable (except current player) - non-blocking
  setTimeout(function() {
    try {
      makeLeaderboardNamesClickable();
    } catch (err) {
      console.error("Error in leaderboard clickables:", err);
    }
  }, 500);
}

function toggleTeamExpand(id) {
  var el = document.getElementById(id);
  if (el) el.classList.toggle("hidden");
}

function renderGameOverLeaderboard(board, playerScore) {
  var container = document.getElementById("game-over-leaderboard");
  if (!board || board.length === 0) {
    container.innerHTML = '<div class="go-lb-section"><h3 class="go-lb-title">🏆 Leaderboard — ' + currentDifficulty.toUpperCase() + '</h3><p class="lb-empty">No scores yet.</p></div>';
    return;
  }

  var entries = board.slice(0, 10);
  var userRank = -1;
  for (var i = 0; i < entries.length; i++) {
    if (entries[i].name === playerName && entries[i].score === playerScore) { userRank = i + 1; break; }
  }

  var html = '<div class="go-lb-section">';
  html += '<h3 class="go-lb-title">🏆 Leaderboard — ' + currentDifficulty.toUpperCase() + '</h3>';
  if (userRank > 0) {
    var rankMedals = ["🥇", "🥈", "🥉"];
    var rankText = userRank <= 3 ? rankMedals[userRank - 1] + " " : "";
    html += '<div class="go-lb-rank">' + rankText + 'You placed #' + userRank + '!</div>';
  }
  html += '<table class="lb-table lb-mini"><thead><tr><th>#</th><th>Name</th><th>Score</th><th>Streak</th></tr></thead><tbody>';
  var medals = ["🥇", "🥈", "🥉"];
  entries.forEach(function(e, i) {
    var rank = i < 3 ? medals[i] : (i + 1);
    var isUser = (e.name === playerName && e.score === playerScore);
    var highlight = isUser ? ' class="lb-highlight"' : '';
    html += '<tr' + highlight + '><td>' + rank + '</td><td>' + escapeHtml(e.name) + '</td><td>' + e.score + '</td><td>' + (e.streak || 0) + '</td></tr>';
  });
  html += '</tbody></table></div>';
  container.innerHTML = html;
}

function fetchAndShowGameOverLeaderboard(playerScore, onDone) {
  fetch(groupQS("/leaderboard"))
    .then(function(res) { return res.json(); })
    .then(function(data) {
      var board = data[currentDifficulty] || [];
      renderGameOverLeaderboard(board, playerScore);
      if (typeof onDone === "function") onDone();
    })
    .catch(function(err) {
      console.error("Game over leaderboard fetch error:", err);
      if (typeof onDone === "function") onDone();
    });
}

function escapeHtml(str) {
  var div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ==================== GAME OVER ====================
function endGame() {
  if (isCompetitionMode) { compEndGame(); return; }
  gameActive = false;
  clearInterval(timer);
  stopAllAudio();
  clearHint();
  resetKeyboardVisibility();

  var isNewBest = saveGameResult();

  var scoreEl = document.getElementById("final-score-number");
  animateNumber(scoreEl, 0, score, 600);

  document.getElementById("final-streak").textContent = bestStreak;
  document.getElementById("final-words-completed").textContent = wordsCompleted + "/" + (totalRounds * wordsPerRound);

  // Build score breakdown table
  var breakdownEl = document.getElementById("score-breakdown");
  if (breakdownEl) {
    var html = "<table class='breakdown-table'><tr><th>Word</th><th>Time</th><th>Errors</th><th>Score</th></tr>";
    for (var i = 0; i < wordScores.length; i++) {
      var ws = wordScores[i];
      var rowClass = ws.skipped ? " class='skipped'" : (ws.errors === 0 ? " class='perfect'" : "");
      html += "<tr" + rowClass + "><td>" + ws.word + "</td><td>" + ws.time + "s</td><td>" + ws.errors + "</td><td>" + ws.score + "</td></tr>";
    }
    html += "</table>";
    breakdownEl.innerHTML = html;
  }

  var newBestEl = document.getElementById("new-best");
  if (isNewBest && score > 0) {
    newBestEl.classList.remove("hidden");
    launchConfetti(120);
    sfxCelebration();
  } else {
    newBestEl.classList.add("hidden");
    if (score > 0) { launchConfetti(40); sfxCelebration(); }
    else { sfxGameOver(); }
  }

  // Hide review section until leaderboard loads
  document.getElementById("review-section").classList.add("hidden");

  // Show leaderboard loading placeholder immediately
  var finalScore = score;
  document.getElementById("final-rank").classList.add("hidden");
  document.getElementById("game-over-leaderboard").innerHTML = '<div class="go-lb-section"><h3 class="go-lb-title">🏆 Leaderboard — ' + currentDifficulty.toUpperCase() + '</h3><p class="lb-empty" style="opacity:0.5">Loading...</p></div>';

  function onLeaderboardReady() {
    // Now show review words below the leaderboard
    buildReviewWithAudio();
  }

  // Calculate accuracy from wordScores (same as compEndGame)
  var totalLetters = 0, totalErrors = 0;
  for (var i = 0; i < wordScores.length; i++) {
    var ws = wordScores[i];
    totalLetters += (ws.word ? ws.word.replace(/ /g, "").length : 1);
    totalErrors += (ws.errors || 0);
  }
  var accuracy = totalLetters > 0 ? Math.max(0, (totalLetters - totalErrors) / totalLetters) : 0;

  if (playerName && finalScore > 0) {
    fetch("/leaderboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(groupBody({ 
        name: playerName, 
        score: finalScore, 
        difficulty: currentDifficulty, 
        streak: bestStreak, 
        accuracy: accuracy,
        words_completed: wordsCompleted
      }))
    })
      .then(function(res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function(response) {
        fetchAndShowGameOverLeaderboard(finalScore, onLeaderboardReady);
      })
      .catch(function(err) {
        console.error("Score submit error:", err);
        if (finalScore > 0) {
          setTimeout(function() {
            fetch("/leaderboard", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(groupBody({ 
                name: playerName, 
                score: finalScore, 
                difficulty: currentDifficulty, 
                streak: bestStreak,
                is_ranked: false,
                accuracy: accuracy,
                words_completed: wordsCompleted,
                bombs_correct: 0,
                time_bonuses: 0,
                reached_x3: false,
              }))
            }).then(function(res) {
              if (!res.ok) throw new Error("HTTP " + res.status);
              return res.json();
            }).then(function(response) {
              console.log("[SCORE] Regular game retry successful");
              fetchAndShowGameOverLeaderboard(finalScore, onLeaderboardReady);
            }).catch(function(retryError) {
              console.error("[SCORE] Regular game retry failed:", retryError);
              fetchAndShowGameOverLeaderboard(finalScore, onLeaderboardReady);
            });
          }, 2000);
        } else {
          fetchAndShowGameOverLeaderboard(finalScore, onLeaderboardReady);
        }
      });
  } else {
    fetchAndShowGameOverLeaderboard(finalScore, onLeaderboardReady);
  }

  showScreen("game-over-screen");
}

function animateNumber(el, from, to, duration) {
  var start = performance.now();
  function update(now) {
    var progress = Math.min((now - start) / duration, 1);
    var eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(from + (to - from) * eased);
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// ==================== STREAK ====================
function updateStreak() {
  var el = document.getElementById("streak-display");
  var countEl = document.getElementById("streak-count");
  if (streak >= 2) {
    el.classList.remove("hidden");
    countEl.textContent = streak;
    el.classList.add("streak-pop");
    setTimeout(function() { el.classList.remove("streak-pop"); }, 300);
  } else { el.classList.add("hidden"); }
}

function showBonus(text) {
  var popup = document.getElementById("bonus-popup");
  popup.textContent = text;
  popup.classList.remove("hidden");
  popup.classList.add("bonus-animate");
  setTimeout(function() { popup.classList.add("hidden"); popup.classList.remove("bonus-animate"); }, 1200);
}

function showPenalty(text) {
  var popup = document.getElementById("penalty-popup");
  popup.textContent = text;
  popup.classList.remove("hidden");
  popup.classList.add("penalty-animate");
  setTimeout(function() { popup.classList.add("hidden"); popup.classList.remove("penalty-animate"); }, 1000);
}

// ==================== RENDER BOXES ====================
function renderBoxes(word) {
  var container = document.getElementById("word-display");
  container.innerHTML = "";
  currentIndex = 0;

  for (var i = 0; i < word.length; i++) {
    if (word[i] === " ") {
      var spacer = document.createElement("div");
      spacer.className = "letter-spacer";
      container.appendChild(spacer);
      continue;
    }

    var box = document.createElement("div");
    box.className = "letter-box";
    box.setAttribute("data-pos", i);

    box.style.animationDelay = (i * 0.05) + "s";
    box.classList.add("box-enter");
    // Hard mode: unfilled boxes tremble (not in ranked/competition)
    if (currentDifficulty === "hard" && !isRankedMode && !isPracticeMode) {
      box.classList.add("tremor");
    }
    container.appendChild(box);
  }

  currentIndex = 0;
  while (currentIndex < word.length && word[currentIndex] === " ") currentIndex++;
}

// ==================== KEYBOARD ====================
function buildKeyboard() {
  var bank = document.getElementById("letter-bank");
  bank.innerHTML = "";
  // Mobile QWERTY layout — keys wrapped for larger tap targets
  var rows = [
    { letters: "qwertyuiop", offset: 0 },
    { letters: "asdfghjkl", offset: 0.5 },
    { letters: "zxcvbnm", offset: 1.5 }
  ];
  rows.forEach(function(row, rowIndex) {
    var rowDiv = document.createElement("div");
    rowDiv.className = "keyboard-row";
    
    if (row.offset > 0) {
      var leftSpacer = document.createElement("div");
      leftSpacer.className = "key-spacer";
      leftSpacer.style.flex = row.offset;
      rowDiv.appendChild(leftSpacer);
    }
    
    for (var c = 0; c < row.letters.length; c++) {
      var ch = row.letters[c];
      // Wrap each key for larger invisible tap target
      var wrap = document.createElement("div");
      wrap.className = "key-wrap";
      var key = document.createElement("button");
      key.className = "key";
      key.textContent = ch;
      key.setAttribute("data-letter", ch);
      key.onclick = (function(letter) { return function() { handleLetter(letter); }; })(ch);
      key.style.animationDelay = (rowIndex * 0.04 + c * 0.015) + "s";
      key.classList.add("key-enter");
      wrap.appendChild(key);
      rowDiv.appendChild(wrap);
    }
    
    if (row.offset > 0) {
      var rightSpacer = document.createElement("div");
      rightSpacer.className = "key-spacer";
      rightSpacer.style.flex = row.offset;
      rowDiv.appendChild(rightSpacer);
    }
    
    bank.appendChild(rowDiv);
  });
}

// ==================== KEYBOARD MODE TOGGLE ====================
var useNativeKeyboard = false;

function toggleKeyboardMode() {
  useNativeKeyboard = !useNativeKeyboard;
  var toggle = document.getElementById("kb-toggle");
  var label = document.getElementById("kb-toggle-label");
  var bank = document.getElementById("letter-bank");
  var input = document.getElementById("native-input");
  
  if (useNativeKeyboard) {
    toggle.classList.add("active");
    label.textContent = "On-Screen Keyboard";
    bank.classList.add("hidden");
    input.classList.remove("hidden");
    input.classList.add("active");
    document.body.classList.add("native-keyboard-active");
    input.focus();
  } else {
    toggle.classList.remove("active");
    label.textContent = "Device Keyboard";
    bank.classList.remove("hidden");
    input.classList.add("hidden");
    input.classList.remove("active");
    document.body.classList.remove("native-keyboard-active");
    input.value = "";
  }
}

// Native input handler
document.getElementById("native-input").addEventListener("input", function(e) {
  if (!gameActive || !useNativeKeyboard) return;
  var val = e.target.value.toLowerCase();
  if (val.length > 0) {
    var lastChar = val[val.length - 1];
    if (/^[a-z]$/.test(lastChar)) {
      handleLetter(lastChar);
      e.target.value = "";
    }
  }
});

// ==================== NATIVE KEYBOARD AUTO-DETECTION ====================
var _nativeKbDetectionActive = false;
var _initialViewportHeight = 0;

function setupNativeKeyboardDetection() {
  if (_nativeKbDetectionActive) return;
  if (!window.visualViewport) return;
  _initialViewportHeight = window.visualViewport.height;
  _nativeKbDetectionActive = true;
  window.visualViewport.addEventListener("resize", _onViewportResize);
}

function teardownNativeKeyboardDetection() {
  _nativeKbDetectionActive = false;
  if (window.visualViewport) {
    window.visualViewport.removeEventListener("resize", _onViewportResize);
  }
  document.body.classList.remove("native-keyboard-active");
}

function _onViewportResize() {
  if (!_nativeKbDetectionActive || !gameActive) return;
  var currentHeight = window.visualViewport.height;
  var shrink = _initialViewportHeight - currentHeight;
  // If viewport shrank by >25% the native keyboard is likely open
  if (shrink > _initialViewportHeight * 0.25) {
    document.body.classList.add("native-keyboard-active");
  } else {
    document.body.classList.remove("native-keyboard-active");
  }
}

// Physical keyboard
document.addEventListener("keydown", function(e) {
  if (!gameActive || useNativeKeyboard) return;
  if (e.key === " ") { e.preventDefault(); return; }
  if (/^[a-zA-Z]$/.test(e.key)) {
    var letter = e.key.toLowerCase();
    handleLetter(letter);
    var keyEl = document.querySelector('.key[data-letter="' + letter + '"]');
    if (keyEl) {
      keyEl.classList.add("key-pressed");
      setTimeout(function() { keyEl.classList.remove("key-pressed"); }, 150);
    }
  }
});


// ==================== HANDLE LETTER ====================
function handleLetter(letter) {
  if (!gameActive) return;

  // Skip spaces
  while (currentIndex < currentWord.length && currentWord[currentIndex] === " ") currentIndex++;

  var boxes = document.querySelectorAll(".letter-box");
  // Find the box for current position (accounting for spacers)
  var boxIndex = 0;
  for (var p = 0; p < currentIndex; p++) {
    if (currentWord[p] !== " ") boxIndex++;
  }
  var box = boxes[boxIndex];
  if (!box) return;

  var config = DIFF_CONFIG[currentDifficulty] || DIFF_CONFIG.easy;

  if (letter === currentWord[currentIndex]) {
    sfxCorrect();
    clearHint();
    box.textContent = letter;
    box.classList.remove("tremor", "error", "error-letter");
    box.classList.add("correct");
    box.classList.add("pop");
    // Add bonus time for correct letter
    timeLeft = Math.min(timeLeft + config.letterBonus, maxTime);
    startTimer();
    currentIndex++;

    // Skip spaces after correct letter
    while (currentIndex < currentWord.length && currentWord[currentIndex] === " ") currentIndex++;

    if (currentIndex < currentWord.length) {
      // Word not done yet — schedule next hint
      scheduleHint();
    }

    if (currentIndex >= currentWord.length) {
      clearHint();
      stopAllAudio();

      // Competition mode: delegate to its own handler
      if (isCompetitionMode) {
        gameActive = false;
        clearInterval(timer);
        for (var ci = 0; ci < boxes.length; ci++) {
          (function(b, delay) { setTimeout(function() { b.classList.add("celebrate"); }, delay); })(boxes[ci], ci * 60);
        }
        compHandleCorrect();
        return;
      }

      streak++;
      if (streak > bestStreak) bestStreak = streak;
      wordsCompleted++;
      wordInRound++;

      // Calculate per-word score
      var timeTaken = (Date.now() - wordStartTime) / 1000;
      var wordLen = currentWord.replace(/ /g, "").length;
      var timeScore = Math.max(0, Math.round((maxTime - timeTaken) / maxTime * 50));
      var accuracyScore = Math.max(0, Math.round((1 - wrongLetters / wordLen) * 50));
      var wordScore = timeScore + accuracyScore;
      wordScores.push({ word: currentWord, score: wordScore, time: Math.round(timeTaken * 10) / 10, errors: wrongLetters });
      score = wordScores.reduce(function(sum, w) { return sum + w.score; }, 0);
      updateScore();
      updateStreak();
      updateRoundIndicator();

      sfxComplete();
      if (streak >= 3) { sfxStreak(); launchConfetti(30 + streak * 5); }

      gameActive = false;
      clearInterval(timer);
      for (var i = 0; i < boxes.length; i++) {
        (function(b, delay) { setTimeout(function() { b.classList.add("celebrate"); }, delay); })(boxes[i], i * 60);
      }

      // Check if round is done
      if (wordInRound >= wordsPerRound) {
        if (currentRound >= totalRounds) {
          setTimeout(function() { endGame(); }, 1000);
          return;
        }
        // Show round transition overlay, then continue
        setTimeout(function() {
          showRoundTransition(function() {
            currentRound++;
            wordInRound = 0;
            timeLeft = maxTime;
            updateRoundIndicator();
            nextWord();
          });
        }, 800);
      } else {
        // Next word in same round — time carries over
        setTimeout(function() { nextWord(); }, 800);
      }
    }
  } else {
    // Competition mode wrong letter
    if (isCompetitionMode) {
      compHandleWrong();
      box.textContent = letter;
      box.classList.add("error", "error-letter");
      if (timeLeft <= 0) { clearInterval(timer); skipWord(); }
      return;
    }

    sfxWrong();
    wrongLetters++;
    if (streak >= 3) streakBreakEffect();
    streak = 0;
    updateStreak();
    box.textContent = letter;
    box.classList.add("error", "error-letter");
    if (reviewWords.indexOf(currentWord) === -1) reviewWords.push(currentWord);

    // Time penalty for medium and hard
    if (config.penalty > 0) {
      timeLeft = Math.max(0, timeLeft - config.penalty);
      showPenalty("-" + config.penalty + "s");
      sfxPenalty();
      if (timeLeft <= 0) {
        clearInterval(timer);
        // skipWord handles life loss, game-over check, and next word
        skipWord();
        return;
      }
    }

    // Screen shake on hard mode (not in ranked/practice)
    if (currentDifficulty === "hard" && !isRankedMode && !isPracticeMode) {
      document.getElementById("game-screen").classList.add("screen-shake");
      setTimeout(function() { document.getElementById("game-screen").classList.remove("screen-shake"); }, 300);
    }
  }
}

// ==================== NEXT WORD ====================
function nextWord() {
  var picked = pickWord(); // sets currentWord, returns null if pool exhausted
  if (picked === null) return; // endGame() already called inside pickWord()

  // Check for bomb — may override currentWord with a harder word
  if (isCompetitionMode || isRankedMode) {
    checkBombWord();
  }

  // Always use currentWord — guaranteed in sync for both boxes and audio
  renderBoxes(currentWord);
  updateRefImage(currentWord);
  audioPlayCount = 0;
  spellPlayCount = 0;
  if (isCompetitionMode) {
    // Competition/Ranked: always type mode, update indicator
    resetKeyboardVisibility();
    // No key fading in competition — all keys always visible
    if (isRankedMode) {
      document.getElementById("round-indicator").textContent =
        wordsCompleted + " correct • " + skippedWords + " missed";
    } else if (isPracticeMode) {
      document.getElementById("round-indicator").textContent =
        "Practice • " + wordsCompleted + " correct • " + skippedWords + " missed";
    } else {
      document.getElementById("round-indicator").textContent =
        "Competition • " + wordsCompleted + " correct • " + skippedWords + " missed";
    }
  } else if (gameMode === "speak") {
    showSpeakingUI();
  } else {
    resetKeyboardVisibility();
    startKeyFading();
  }

  playAudio();
  wordStartTime = Date.now();
  wrongLetters = 0;
  startTimer();
  gameActive = true;
  if (!isCompetitionMode) scheduleHint();

  // Preload next word's audio immediately
  preloadNextWordAudio();
}

// ==================== ROUND INDICATOR ====================
function updateRoundIndicator() {
  var el = document.getElementById("round-indicator");
  if (el) el.textContent = "Round " + currentRound + "/" + totalRounds + "  •  Word " + (wordInRound + 1) + "/" + wordsPerRound;
}

// ==================== ROUND TRANSITION ====================
function showRoundTransition(callback) {
  clearInterval(timer);
  var overlay = document.getElementById("round-transition");
  if (!overlay) { callback(); return; }

  // Calculate round score (sum of wordScores from this round)
  var roundStart = (currentRound - 1) * wordsPerRound;
  var roundEnd = currentRound * wordsPerRound;
  var roundScore = 0;
  for (var i = roundStart; i < roundEnd && i < wordScores.length; i++) {
    roundScore += wordScores[i].score;
  }

  var emojis = ["🎉", "🔥", "⭐"];
  document.getElementById("rt-emoji").textContent = emojis[currentRound - 1] || "🎉";
  document.getElementById("rt-title").textContent = "Round " + currentRound + " Complete!";
  document.getElementById("rt-round-score").textContent = roundScore;
  document.getElementById("rt-total-score").textContent = score;
  document.getElementById("rt-streak").textContent = bestStreak;
  document.getElementById("rt-next").textContent = "⚡ Round " + (currentRound + 1) + " starting...";

  var fill = document.getElementById("rt-progress-fill");
  fill.style.transition = "none";
  fill.style.width = "0%";

  overlay.classList.remove("hidden");

  // Start progress bar after a tiny delay for CSS to reset
  setTimeout(function() {
    fill.style.transition = "width 3s linear";
    fill.style.width = "100%";
  }, 50);

  // After 3.5s, hide overlay and continue
  setTimeout(function() {
    overlay.classList.add("hidden");
    callback();
  }, 3500);
}

// ==================== SCORE ====================
function updateScore() {
  var el = document.getElementById("score");
  el.textContent = score;
  el.classList.add("score-pop");
  setTimeout(function() { el.classList.remove("score-pop"); }, 300);
}

// ==================== LIVES (HEARTS) ====================
function updateLivesDisplay() {
  var container = document.getElementById("lives-display");
  if (!container) return;
  container.innerHTML = "";
  for (var i = 0; i < maxLives; i++) {
    var heart = document.createElement("span");
    heart.className = "heart" + (i < lives ? " heart-alive" : " heart-dead");
    heart.textContent = i < lives ? "❤️" : "🖤";
    heart.setAttribute("data-index", i);
    container.appendChild(heart);
  }
}

function breakHeart() {
  var hearts = document.querySelectorAll(".heart-alive");
  if (hearts.length === 0) return;
  var last = hearts[hearts.length - 1];
  last.classList.remove("heart-alive");
  last.classList.add("heart-breaking");
  last.textContent = "💔";
  setTimeout(function() {
    last.classList.remove("heart-breaking");
    last.classList.add("heart-dead");
    last.textContent = "🖤";
  }, 800);
}

// ==================== AUTO-HINT SYSTEM ====================
function scheduleHint() {
  clearHint();
  if (!gameActive || gameMode !== "type") return;
  var config = DIFF_CONFIG[currentDifficulty] || DIFF_CONFIG.easy;
  hintTimer = setTimeout(function() {
    if (!gameActive) return;
    showHint();
  }, config.hintDelay * 1000);
}

function showHint() {
  if (!gameActive || currentIndex >= currentWord.length) return;
  var nextLetter = currentWord[currentIndex];
  if (!nextLetter || nextLetter === " ") return;

  // Find the key on the keyboard
  var keyEl = document.querySelector('.key[data-letter="' + nextLetter + '"]');
  if (!keyEl) return;

  // Apply subtle glow — no time penalty, the cost is the wait itself
  hintGlowingKey = keyEl;
  hintActive = true;
  keyEl.classList.add("key-hint-glow");
}

function clearHint() {
  clearTimeout(hintTimer);
  hintTimer = null;
  hintActive = false;
  if (hintGlowingKey) {
    hintGlowingKey.classList.remove("key-hint-glow");
    hintGlowingKey = null;
  }
}

// ==================== TIMER ====================
var _timerCircle = null;
var _timerText = null;

function startTimer() {
  if (!_timerCircle) _timerCircle = document.getElementById("timer-circle");
  if (!_timerText) _timerText = document.getElementById("timer-text");
  var circle = _timerCircle;
  var text = _timerText;
  circle.style.strokeDasharray = CIRCUMFERENCE;
  circle.classList.remove("timer-warning", "timer-critical");
  text.classList.remove("timer-critical-text");
  text.textContent = timeLeft;

  // Update circle to reflect current time vs maxTime
  var offset = CIRCUMFERENCE - (timeLeft / maxTime) * CIRCUMFERENCE;
  circle.style.strokeDashoffset = Math.min(offset, CIRCUMFERENCE);

  // Pre-compute thresholds once per word
  var warnAt = Math.ceil(maxTime * 0.4);
  var critAt = Math.ceil(maxTime * 0.2);

  clearInterval(timer);
  timer = setInterval(function() {
    timeLeft--;
    text.textContent = Math.max(timeLeft, 0);

    var offset = CIRCUMFERENCE - (timeLeft / maxTime) * CIRCUMFERENCE;
    circle.style.strokeDashoffset = Math.min(offset, CIRCUMFERENCE);

    if (timeLeft <= critAt) {
      circle.classList.add("timer-critical");
      text.classList.add("timer-critical-text");
    } else if (timeLeft <= warnAt) {
      circle.classList.add("timer-warning");
      circle.classList.remove("timer-critical");
      text.classList.remove("timer-critical-text");
    } else {
      circle.classList.remove("timer-warning", "timer-critical");
      text.classList.remove("timer-critical-text");
    }

    if (timeLeft <= 0) {
      clearInterval(timer);
      skipWord();
    }
  }, 1000);
}

function skipWord() {
  stopAllAudio();
  clearHint();
  if (gameMode === "speak") stopMic();
  skippedWords++;
  wordInRound++;
  if (streak >= 3) streakBreakEffect();
  streak = 0;
  updateStreak();
  if (reviewWords.indexOf(currentWord) === -1) reviewWords.push(currentWord);
  sfxWrong();

  // Bomb word penalty: -10% of current score
  var bombPenalty = 0;
  if (isBombWord && (isCompetitionMode || isRankedMode)) {
    bombPenalty = Math.round(score * 0.10); // lose 10% of current score
    if (bombPenalty < 10) bombPenalty = 10;  // minimum 10 pts penalty
    showPenalty("💣 BOMB FAILED! -" + bombPenalty);
    isBombWord = false;
    var ind = document.getElementById("bomb-indicator");
    if (ind) { ind.classList.add("hidden"); ind.classList.remove("bomb-pulse"); }
  }

  // Score negative for bomb penalty (stored in wordScores so reduce captures it)
  wordScores.push({ word: currentWord, score: -bombPenalty, time: maxTime, errors: wrongLetters, skipped: true, bombPenalty: bombPenalty });
  // Recalculate score from wordScores to ensure consistency
  score = Math.max(0, wordScores.reduce(function(sum, w) { return sum + w.score; }, 0));
  updateScore();

  // Flash boxes red
  var boxes = document.querySelectorAll(".letter-box");
  for (var i = 0; i < boxes.length; i++) {
    boxes[i].classList.remove("tremor");
    boxes[i].classList.add("error");
  }

  // Show the correct word briefly
  var wordChars = currentWord.split("");
  var bi = 0;
  for (var w = 0; w < wordChars.length; w++) {
    if (wordChars[w] === " ") continue;
    if (boxes[bi]) boxes[bi].textContent = wordChars[w];
    bi++;
  }

  showPenalty("TIME'S UP!");

  // Lose a life
  lives--;
  breakHeart();
  updateLivesDisplay();

  gameActive = false;

  // Game over if out of lives
  if (lives <= 0) {
    setTimeout(function() { endGame(); }, 1500);
    return;
  }

  // Competition mode: no round system — just continue with next word
  if (isCompetitionMode) {
    compPickNextWord();
    setTimeout(function() {
      if (isRankedMode) {
        document.getElementById("round-indicator").textContent =
          wordsCompleted + " correct • " + skippedWords + " missed";
      } else if (isPracticeMode) {
        document.getElementById("round-indicator").textContent =
          "Practice • " + wordsCompleted + " correct • " + skippedWords + " missed";
      } else {
        document.getElementById("round-indicator").textContent =
          "Competition • " + wordsCompleted + " correct • " + skippedWords + " missed";
      }
      nextWord();
    }, 1400);
    return;
  }

  // Check if round is done
  if (wordInRound >= wordsPerRound) {
    if (currentRound >= totalRounds) {
      setTimeout(function() { endGame(); }, 1200);
      return;
    }
    setTimeout(function() {
      showRoundTransition(function() {
        currentRound++;
        wordInRound = 0;
        timeLeft = maxTime;
        updateRoundIndicator();
        nextWord();
      });
    }, 1200);
  } else {
    setTimeout(function() {
      timeLeft = maxTime;
      updateRoundIndicator();
      nextWord();
    }, 1200);
  }
}

// ==================== TTS AUDIO ====================
var currentTTSAudio = null;

function stopAllAudio() {
  // Stop HTML5 Audio
  if (currentTTSAudio) {
    var old = currentTTSAudio;
    old.onended = null;
    old.onerror = null;
    old.oncanplaythrough = null;
    currentTTSAudio = null;
    try { old.pause(); old.removeAttribute("src"); old.load(); } catch(e) {}
  }
  // Stop browser speechSynthesis
  if (window.speechSynthesis) {
    try { window.speechSynthesis.cancel(); } catch(e) {}
  }
  audioPlaying = false;
  var allBtns = document.querySelectorAll(".sound-btn");
  for (var i = 0; i < allBtns.length; i++) allBtns[i].classList.remove("sound-playing");
}

function speakWithBrowserTTS(text, slow, onDone) {
  // DISABLED: Prevent robotic browser TTS fallback
  console.log("[BrowserTTS] DISABLED - No robotic fallback allowed");
  if (typeof onDone === "function") onDone();
  return;
}

function extractWordFromUrl(url) {
  var match = url.match(/\/(speak|speak_slow|spell|spell_slow|sentence)\/(.+?)(\?|$)/);
  return match ? decodeURIComponent(match[2]) : "";
}

function isSlowUrl(url) {
  return url.indexOf("_slow") !== -1;
}

function isSpellUrl(url) {
  return /\/(spell|spell_slow)\//.test(url);
}

function formatSpellingText(word) {
  // Mirror the server-side format_spelling_text: letters separated by pauses
  var out = "";
  for (var i = 0; i < word.length; i++) {
    var ch = word[i];
    if (/[a-zA-Z]/.test(ch)) { out += ch.toUpperCase() + "... "; }
    else if (ch === " ") { out += ", "; }
  }
  return out.trim();
}

function playTTS(url, btn, onFinished) {
  console.log("[TTS] playTTS called:", url);

  // Stop any currently playing audio
  if (currentTTSAudio) {
    console.log("[TTS] Stopping previous audio");
    var old = currentTTSAudio;
    old.onended = null;
    old.onerror = null;
    old.onloadeddata = null;
    currentTTSAudio = null;
    try { old.pause(); old.removeAttribute("src"); old.load(); } catch(e) {}
  }

  // Clear all sound-playing states
  var allBtns = document.querySelectorAll(".sound-btn");
  for (var i = 0; i < allBtns.length; i++) allBtns[i].classList.remove("sound-playing");

  if (btn) btn.classList.add("sound-playing");
  audioPlaying = true;
  updateMicDisabledState();

  var audio = new Audio();
  currentTTSAudio = audio;

  function finish() {
    console.log("[TTS] Audio finished");
    if (currentTTSAudio === audio) currentTTSAudio = null;
    audioPlaying = false;
    updateMicDisabledState();
    if (btn) btn.classList.remove("sound-playing");
    if (typeof onFinished === "function") onFinished();
  }

  function fallbackToBrowser() {
    // DISABLED: Prevent robotic browser TTS fallback
    console.log("[TTS] Browser fallback DISABLED - No robotic audio allowed");
    finish();
  }

  audio.onended = function() {
    console.log("[TTS] onended fired");
    finish();
  };

  audio.onerror = function(e) {
    console.log("[TTS] onerror fired, trying browser fallback", e);
    fallbackToBrowser();
  };

  audio.oncanplaythrough = function() {
    console.log("[TTS] canplaythrough fired, duration:", audio.duration);
    if (currentTTSAudio !== audio) { console.log("[TTS] stale audio, skipping play"); return; }
    audio.play().then(function() {
      console.log("[TTS] play() succeeded");
    }).catch(function(err) {
      console.log("[TTS] play() blocked, retrying after interaction unlock:", err);
      // Mobile retry: wait briefly and try again (audio unlock may have propagated)
      setTimeout(function() {
        if (currentTTSAudio !== audio) return;
        audio.play().then(function() {
          console.log("[TTS] play() retry succeeded");
        }).catch(function(err2) {
          console.log("[TTS] play() retry failed:", err2);
          finish();
        });
      }, 300);
    });
  };

  audio.onloadstart = function() { console.log("[TTS] loadstart"); };
  audio.onstalled = function() { console.log("[TTS] stalled"); };
  audio.onabort = function() { console.log("[TTS] abort"); };

  // Add cache-busting parameter to avoid browser caching issues
  var fullUrl = url + (url.indexOf("?") >= 0 ? "&" : "?") + "_t=" + Date.now();
  console.log("[TTS] Setting src:", fullUrl);
  audio.src = fullUrl;
  audio.load();
}

function playPreloaded(audio, btn, onFinished) {
  // Stop any currently playing audio
  if (currentTTSAudio) {
    var old = currentTTSAudio;
    old.onended = null; old.onerror = null;
    currentTTSAudio = null;
    try { old.pause(); old.removeAttribute("src"); old.load(); } catch(e) {}
  }

  var allBtns = document.querySelectorAll(".sound-btn");
  for (var i = 0; i < allBtns.length; i++) allBtns[i].classList.remove("sound-playing");
  if (btn) btn.classList.add("sound-playing");
  audioPlaying = true;
  updateMicDisabledState();
  currentTTSAudio = audio;

  function finish() {
    if (currentTTSAudio === audio) currentTTSAudio = null;
    audioPlaying = false;
    updateMicDisabledState();
    if (btn) btn.classList.remove("sound-playing");
    if (typeof onFinished === "function") onFinished();
  }

  function fallbackToBrowser() {
    // DISABLED: Prevent robotic browser TTS fallback
    console.log("[TTS] Preloaded fallback DISABLED - No robotic audio allowed");
    finish();
  }

  audio.onended = finish;
  audio.onerror = function() {
    console.log("[TTS] preloaded onerror, trying browser fallback");
    fallbackToBrowser();
  };

  // Audio is already loaded — play immediately
  audio.currentTime = 0;
  audio.play().then(function() {
    console.log("[TTS] preloaded play() succeeded");
  }).catch(function(err) {
    console.log("[TTS] preloaded play() failed, trying browser fallback:", err);
    fallbackToBrowser();
  });
}

function playAudio(onFinished) {
  audioPlayCount++;
  var btn = document.querySelector(".sound-btn");

  // First click: use preloaded audio if available for instant playback
  if (audioPlayCount <= 1 && preloadedAudio[currentWord]) {
    var preloaded = preloadedAudio[currentWord];
    delete preloadedAudio[currentWord];
    playPreloaded(preloaded, btn, onFinished);
    return;
  }

  var url = audioPlayCount > 1
    ? "/speak_slow/" + encodeURIComponent(currentWord)
    : "/speak/" + encodeURIComponent(currentWord);
  playTTS(url, btn, onFinished);
}

function playSpell() {
  spellPlayCount++;
  var url = spellPlayCount > 1
    ? "/spell_slow/" + encodeURIComponent(currentWord)
    : "/spell/" + encodeURIComponent(currentWord);
  var btns = document.querySelectorAll(".sound-btn");
  var btn = btns && btns.length > 1 ? btns[1] : null;
  playTTS(url, btn, null);
}

// ==================== SPEAKING MODE ====================
function setGameMode(mode) {
  gameMode = mode;
  document.getElementById("mode-type").classList.toggle("active", mode === "type");
  document.getElementById("mode-speak").classList.toggle("active", mode === "speak");
  var submodes = document.getElementById("speak-submodes");
  if (mode === "speak") { submodes.classList.remove("hidden"); }
  else { submodes.classList.add("hidden"); }
}

function setSpeakSubmode(sub) {
  speakSubmode = sub;
  document.getElementById("submode-say").classList.toggle("active", sub === "say");
  document.getElementById("submode-spell").classList.toggle("active", sub === "spell");
}

function initSpeechRecognition() {
  var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) {
    alert("Your browser does not support Speech Recognition. Please use Chrome or Edge.");
    return null;
  }
  var rec = new SpeechRecognition();
  rec.lang = "en-US";
  rec.interimResults = false;  // Only final results for better accuracy
  rec.maxAlternatives = 10;    // Increased alternatives for better matching
  rec.continuous = false;      // Better for individual letter recognition

  rec.onresult = function(event) {
    // In spell mode with continuous, accumulate results
    if (speakSubmode === "spell" && rec.continuous) {
      var full = "";
      for (var r = 0; r < event.results.length; r++) {
        full += event.results[r][0].transcript;
      }
      spellAccumulated = full;
      var extracted = extractLettersFromSpeech(full);
      var rawClean = full.toLowerCase().replace(/[^a-z]/g, "");
      var target = currentWord.toLowerCase().replace(/ /g, "");
      var display = rawClean.length > 0 ? rawClean.toUpperCase() : full.toUpperCase();
      if (extracted.length > 0) display = extracted.split("").join(" ").toUpperCase();
      document.getElementById("mic-status").textContent = "Hearing: " + display;
      console.log("[Spell] Raw: '" + full + "' → Extracted: '" + extracted + "' rawClean: '" + rawClean + "' Target: '" + target + "'");
      // Auto-submit: exact match, contains, or starts with target
      var spellMatch = (extracted.length > 0 && extracted === target)
        || rawClean === target
        || (rawClean.length >= target.length && rawClean.indexOf(target) !== -1);
      if (spellMatch) {
        console.log("[Spell] Auto-match! Submitting immediately.");
        if (spellMicTimer) { clearTimeout(spellMicTimer); spellMicTimer = null; }
        spellAccumulated = "";
        micListening = false;
        recognition.continuous = false;
        try { recognition.stop(); } catch(e) {}
        document.getElementById("mic-btn").classList.remove("mic-listening");
        document.getElementById("mic-status").textContent = "";
        handleSpeechResult([full.toLowerCase().trim()]);
        return;
      }
      // Reset the silence timer — give more time after each new result
      if (spellMicTimer) clearTimeout(spellMicTimer);
      spellMicTimer = setTimeout(function() {
        // Student stopped talking — finalize
        finishSpellListening();
      }, 3500);
      return;
    }

    // Normal mode (say the word) — only process FINAL results
    if (!event.results || !event.results[0]) return;
    if (!event.results[0].isFinal) {
      // Show interim feedback but don't process yet
      var interim = event.results[0][0].transcript.toLowerCase().trim();
      if (interim) document.getElementById("mic-status").textContent = 'Hearing: "' + interim + '"';
      return;
    }
    micListening = false;
    document.getElementById("mic-btn").classList.remove("mic-listening");
    document.getElementById("mic-status").textContent = "";
    if (event.results[0].length === 0) {
      document.getElementById("mic-status").textContent = "Could not understand. Try again!";
      return;
    }
    var results = event.results[0];
    var heard = [];
    for (var i = 0; i < results.length; i++) {
      var t = results[i].transcript.toLowerCase().trim();
      if (t.length > 0) heard.push(t);
    }
    if (heard.length === 0) {
      document.getElementById("mic-status").textContent = "No words detected. Tap mic and try again!";
      return;
    }
    handleSpeechResult(heard);
  };

  rec.onerror = function(event) {
    console.error("[Speech] Error:", event.error);
    micListening = false;
    document.getElementById("mic-btn").classList.remove("mic-listening");
    if (event.error === "no-speech") {
      document.getElementById("mic-status").textContent = "No speech detected. Try again!";
    } else if (event.error === "not-allowed") {
      document.getElementById("mic-status").textContent = "Microphone access denied. Please allow it.";
    } else if (event.error === "aborted") {
      // Ignore aborted — we handle this manually
    } else if (event.error === "network") {
      document.getElementById("mic-status").textContent = "Network error. Check your connection.";
    } else {
      document.getElementById("mic-status").textContent = "Error: " + event.error + ". Try again.";
    }
  };

  rec.onend = function() {
    // In spell continuous mode, restart if still listening
    if (speakSubmode === "spell" && micListening && rec.continuous) {
      try { rec.start(); } catch(e) {}
      return;
    }
    micListening = false;
    document.getElementById("mic-btn").classList.remove("mic-listening");
  };

  return rec;
}

function finishSpellListening() {
  if (spellMicTimer) { clearTimeout(spellMicTimer); spellMicTimer = null; }
  var accumulated = spellAccumulated;
  spellAccumulated = "";
  micListening = false;
  if (recognition) {
    recognition.continuous = false;
    try { recognition.stop(); } catch(e) {}
  }
  document.getElementById("mic-btn").classList.remove("mic-listening");
  document.getElementById("mic-status").textContent = "";
  if (accumulated.trim().length === 0) {
    document.getElementById("mic-status").textContent = "No letters detected. Try again!";
    return;
  }
  handleSpeechResult([accumulated.toLowerCase().trim()]);
}

function toggleMic() {
  if (!gameActive) return;
  if (audioPlaying) return;
  if (micListening) {
    stopMic();
    return;
  }
  startMic();
}

function updateMicDisabledState() {
  var micBtn = document.getElementById("mic-btn");
  if (!micBtn) return;
  if (audioPlaying) {
    micBtn.classList.add("mic-disabled");
    micBtn.setAttribute("disabled", "true");
  } else {
    micBtn.classList.remove("mic-disabled");
    micBtn.removeAttribute("disabled");
  }
}

function startMic() {
  if (!recognition) recognition = initSpeechRecognition();
  if (!recognition) return;

  // Clear previous feedback
  var transcript = document.getElementById("mic-transcript");
  var feedback = document.getElementById("mic-feedback");
  transcript.classList.add("hidden");
  transcript.textContent = "";
  feedback.classList.add("hidden");
  feedback.textContent = "";
  feedback.className = "mic-feedback hidden";

  // For spell mode: use continuous recognition with longer patience
  if (speakSubmode === "spell") {
    recognition.continuous = true;
    spellAccumulated = "";
    if (spellMicTimer) clearTimeout(spellMicTimer);
    // Give a generous total timeout (20s) in case no speech at all
    spellMicTimer = setTimeout(function() {
      finishSpellListening();
    }, 20000);
  } else {
    recognition.continuous = false;
  }

  micListening = true;
  document.getElementById("mic-btn").classList.add("mic-listening");
  document.getElementById("mic-status").textContent = speakSubmode === "spell" ? "Spell it out... take your time!" : "Listening...";

  try { recognition.start(); }
  catch(e) {
    // Already started — stop and restart
    recognition.stop();
    setTimeout(function() {
      try { recognition.start(); } catch(e2) {}
    }, 200);
  }
}

function stopMic() {
  if (spellMicTimer) { clearTimeout(spellMicTimer); spellMicTimer = null; }
  spellAccumulated = "";
  if (recognition) {
    recognition.continuous = false;
    try { recognition.stop(); } catch(e) {}
  }
  micListening = false;
  document.getElementById("mic-btn").classList.remove("mic-listening");
  document.getElementById("mic-status").textContent = "";
}

function handleSpeechResult(alternatives) {
  if (!gameActive) return;
  if (processingResult) return;
  // Ignore stale results from a previous word
  if (speechWordTarget !== currentWord) return;
  processingResult = true;
  // Double-check: filter out empty alternatives
  alternatives = alternatives.filter(function(a) { return a && a.trim().length > 0; });
  if (alternatives.length === 0) {
    processingResult = false;
    document.getElementById("mic-status").textContent = "No words detected. Tap mic and try again!";
    return;
  }

  var target = currentWord.toLowerCase().trim();
  var transcriptEl = document.getElementById("mic-transcript");
  var feedbackEl = document.getElementById("mic-feedback");
  var bestHeard = alternatives[0] || "";

  // In spell mode, show cleaned-up version instead of raw mess
  if (speakSubmode === "spell") {
    var cleanDisplay = bestHeard.toLowerCase().replace(/[^a-z]/g, "");
    transcriptEl.textContent = '"' + cleanDisplay + '"';
  } else {
    transcriptEl.textContent = '"' + bestHeard + '"';
  }
  transcriptEl.classList.remove("hidden");

  var isCorrect = false;

  if (speakSubmode === "say") {
    // "Say the Word" mode: check if any alternative matches the word
    for (var i = 0; i < alternatives.length; i++) {
      var cleaned = alternatives[i].replace(/[^a-z ]/g, "").trim();
      if (cleaned === target) { isCorrect = true; break; }
    }
  } else {
    // "Spell It Out" mode: use phonetic letter extraction + raw text matching
    var targetLetters = target.replace(/ /g, "");
    for (var j = 0; j < alternatives.length; j++) {
      // Method 1: extract via phonetic map
      var extracted = extractLettersFromSpeech(alternatives[j]);
      console.log("[Spell Match] alt" + j + ": '" + alternatives[j] + "' → extracted: '" + extracted + "' target: '" + targetLetters + "'");
      if (extracted === targetLetters) { isCorrect = true; break; }
      // Method 1b: fuzzy matching for extracted letters (allow 1 error)
      if (fuzzyMatch(extracted, targetLetters, 1)) { 
        console.log("[Spell Match] Fuzzy match on extracted!");
        isCorrect = true; break; 
      }
      // Method 2: raw text stripped of non-alpha (handles speech API merging letters into words)
      var rawClean = alternatives[j].toLowerCase().replace(/[^a-z]/g, "");
      if (rawClean === targetLetters) { isCorrect = true; break; }
      // Method 2b: fuzzy matching for raw clean (allow 1 error)
      if (fuzzyMatch(rawClean, targetLetters, 1)) { 
        console.log("[Spell Match] Fuzzy match on raw clean!");
        isCorrect = true; break; 
      }
      // Method 3: check if raw text contains the target (e.g. "medicine.edicine." contains "medicine")
      if (rawClean.indexOf(targetLetters) !== -1) { isCorrect = true; break; }
      // Method 4: single-char parts
      var parts = alternatives[j].toLowerCase().split(/[\s,.\-]+/).filter(function(p) { return p.length === 1 && /[a-z]/.test(p); });
      if (parts.join("") === targetLetters) { isCorrect = true; break; }
    }
  }

  if (isCorrect) {
    handleSpeakCorrect();
  } else {
    handleSpeakWrong(bestHeard);
  }
  processingResult = false;
}

function handleSpeakCorrect() {
  stopAllAudio();
  var feedbackEl = document.getElementById("mic-feedback");
  feedbackEl.textContent = "Correct!";
  feedbackEl.className = "mic-feedback correct";
  feedbackEl.classList.remove("hidden");

  sfxComplete();
  streak++;
  if (streak > bestStreak) bestStreak = streak;
  wordsCompleted++;
  wordInRound++;

  // Add bonus time for correct answer in speaking mode
  var config = DIFF_CONFIG[currentDifficulty] || DIFF_CONFIG.easy;
  var wordLen = currentWord.replace(/ /g, "").length;
  var bonus = config.letterBonus * wordLen;
  timeLeft = Math.min(timeLeft + bonus, maxTime);
  totalBonusTime += bonus;
  showBonus("+" + bonus + "s");

  // Per-word score
  var timeTaken = (Date.now() - wordStartTime) / 1000;
  var attemptPenalty = Math.max(0, micAttempts - 1);
  var timeScore = Math.max(0, Math.round((maxTime - timeTaken) / maxTime * 50));
  var accuracyScore = Math.max(0, Math.round((1 - attemptPenalty / wordLen) * 50));
  var wordScore = timeScore + accuracyScore;
  wordScores.push({ word: currentWord, score: wordScore, time: Math.round(timeTaken * 10) / 10, errors: attemptPenalty });
  score = wordScores.reduce(function(sum, w) { return sum + w.score; }, 0);
  updateScore();
  updateStreak();
  updateRoundIndicator();

  if (streak >= 3) { sfxStreak(); launchConfetti(30 + streak * 5); }

  // Fill in the letter boxes to show the word
  var boxes = document.querySelectorAll(".letter-box");
  var wordChars = currentWord.split("");
  var bi = 0;
  for (var w = 0; w < wordChars.length; w++) {
    if (wordChars[w] === " ") continue;
    if (boxes[bi]) {
      boxes[bi].textContent = wordChars[w];
      boxes[bi].classList.add("correct");
    }
    bi++;
  }
  for (var c = 0; c < boxes.length; c++) {
    (function(b, delay) { setTimeout(function() { b.classList.add("celebrate"); }, delay); })(boxes[c], c * 60);
  }

  gameActive = false;
  clearInterval(timer);

  // Check if round is done
  if (wordInRound >= wordsPerRound) {
    if (currentRound >= totalRounds) {
      setTimeout(function() { endGame(); }, 1000);
      return;
    }
    setTimeout(function() {
      showRoundTransition(function() {
        currentRound++;
        wordInRound = 0;
        timeLeft = maxTime;
        updateRoundIndicator();
        nextWord();
      });
    }, 800);
  } else {
    // Mobile fix: pre-create audio element in user gesture context (speech result)
    // to avoid autoplay restrictions on iOS/Android
    var silentKick = new Audio();
    silentKick.src = "data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA/+M4wAAAAAAAAAAAAEluZm8AAAAPAAAAAwAAAbAAkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0P/////////////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/jOMAAAG9JKAAAAAAANICAAAAATGF2YzU4LjEzAAAAAAAAAAAAAAAAJAAAAAAAAAAAAbCp7QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/+M4wDMaaACAAAAAAAANIAAAAAExBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV";
    silentKick.load();
    try { silentKick.play().then(function() { silentKick.pause(); }).catch(function() {}); } catch(e) {}

    setTimeout(function() {
      stopAllAudio();
      setTimeout(function() { nextWord(); }, 100);
    }, 1000);
  }
}

function handleSpeakWrong(heard) {
  var feedbackEl = document.getElementById("mic-feedback");
  micAttempts++;
  wrongLetters++;

  sfxWrong();
  if (streak >= 3) streakBreakEffect();
  streak = 0;
  updateStreak();
  if (reviewWords.indexOf(currentWord) === -1) reviewWords.push(currentWord);

  if (micAttempts >= MAX_MIC_ATTEMPTS) {
    // Too many attempts — show the word and move on
    feedbackEl.textContent = "The word was: " + currentWord;
    feedbackEl.className = "mic-feedback wrong";
    feedbackEl.classList.remove("hidden");

    // Show the answer in the boxes
    var boxes = document.querySelectorAll(".letter-box");
    var wordChars = currentWord.split("");
    var bi = 0;
    for (var w = 0; w < wordChars.length; w++) {
      if (wordChars[w] === " ") continue;
      if (boxes[bi]) {
        boxes[bi].textContent = wordChars[w];
        boxes[bi].classList.add("error");
      }
      bi++;
    }

    wordInRound++;
    wordScores.push({ word: currentWord, score: 0, time: Math.round((Date.now() - wordStartTime) / 100) / 10, errors: micAttempts, skipped: true });
    score = wordScores.reduce(function(sum, w) { return sum + w.score; }, 0);
    updateScore();
    updateRoundIndicator();

    gameActive = false;
    clearInterval(timer);

    if (wordInRound >= wordsPerRound) {
      if (currentRound >= totalRounds) {
        setTimeout(function() { endGame(); }, 1500);
        return;
      }
      setTimeout(function() {
        showRoundTransition(function() {
          currentRound++;
          wordInRound = 0;
          timeLeft = maxTime;
          updateRoundIndicator();
          nextWord();
        });
      }, 1500);
    } else {
      setTimeout(function() { nextWord(); }, 1500);
    }
  } else {
    // Wrong — give feedback and repeat word
    var remaining = MAX_MIC_ATTEMPTS - micAttempts;
    feedbackEl.textContent = "Not quite! " + remaining + " " + (remaining === 1 ? "try" : "tries") + " left. Listen again...";
    feedbackEl.className = "mic-feedback wrong";
    feedbackEl.classList.remove("hidden");

    // Replay the word after a short delay — block mic until audio finishes
    document.getElementById("mic-status").textContent = "Listen to the word...";
    // Reset audioPlayCount so replay uses normal speed, not slow
    audioPlayCount = 0;
    setTimeout(function() {
      playAudio(function() {
        // Ensure mic is re-enabled after replay
        audioPlaying = false;
        updateMicDisabledState();
        document.getElementById("mic-status").textContent = "Tap mic to try again";
      });
    }, 1000);
  }
}

function showSpeakingUI() {
  document.getElementById("letter-bank").classList.add("hidden");
  document.getElementById("mic-area").classList.remove("hidden");
  micAttempts = 0;
  processingResult = false;
  audioPlaying = false;
  updateMicDisabledState();
  speechWordTarget = currentWord;

  if (speakSubmode === "say") {
    document.getElementById("mic-instruction").textContent = "Tap the mic and say the word";
  } else {
    document.getElementById("mic-instruction").textContent = "Tap the mic and spell the word letter by letter";
  }

  document.getElementById("mic-status").textContent = "";
  document.getElementById("mic-transcript").classList.add("hidden");
  document.getElementById("mic-transcript").textContent = "";
  document.getElementById("mic-feedback").classList.add("hidden");
  document.getElementById("mic-feedback").textContent = "";
  document.getElementById("mic-feedback").className = "mic-feedback hidden";
}

function hideSpeakingUI() {
  document.getElementById("mic-area").classList.add("hidden");
  document.getElementById("letter-bank").classList.remove("hidden");
  stopMic();
}

// ==================== BEE FLIGHT ====================
var beeAngle = 0;

function initBeeFlight() {
  animateBee();
}

function animateBee() {
  requestAnimationFrame(animateBee);

  // Animate whichever bee is currently visible (login or menu screen)
  var bee = document.getElementById("flying-bee");
  var area = bee ? bee.closest(".bee-flight-area") : null;
  if (!bee || !area || area.offsetParent === null) {
    bee = document.getElementById("flying-bee-login");
    area = bee ? bee.closest(".bee-flight-area") : null;
  }
  if (!bee || !area || area.offsetParent === null) return;

  // Elliptical orbit parameters
  var radiusX = 16;
  var radiusY = 10;
  var speed = 0.015;
  beeAngle += speed;

  // Position on ellipse
  var x = Math.cos(beeAngle) * radiusX;
  var y = Math.sin(beeAngle) * radiusY;

  // Depth: when angle is near PI (back of circle), bee is "far away"
  var depth = 0.5 + 0.5 * Math.sin(beeAngle);
  var sc = 0.7 + depth * 0.3;

  // Horizontal velocity: derivative of cos(angle) = -sin(angle)
  var dx = -Math.sin(beeAngle);
  var flipX = dx >= 0 ? -1 : 1;

  // Slight tilt based on vertical movement
  var dy = Math.cos(beeAngle);
  var tilt = dy * -6;

  // Bounce wobble
  var bounce = Math.sin(beeAngle * 6) * 2 * sc;

  // Center of flight area
  var cx = 25;
  var cy = 25;
  var beeSize = 32 * sc;
  var px = cx + x - beeSize / 2;
  var py = cy + y + bounce - beeSize / 2;

  bee.style.transform = "translate(" + px + "px, " + py + "px) scale(" + sc + ") scaleX(" + flipX + ") rotate(" + tilt + "deg)";
}

// ==================== SENTENCE (Use in a sentence) ====================
function playSentence() {
  if (!currentWord) return;
  var url = "/sentence/" + encodeURIComponent(currentWord);
  var btns = document.querySelectorAll(".sound-btn");
  var btn = btns && btns.length > 2 ? btns[2] : null;
  playTTS(url, btn, null);
}

// ==================== AUDIO PRELOADING ====================
var preloadedAudio = {};

function preloadNextWordAudio() {
  // Clean up stale preloaded entries (used words)
  for (var key in preloadedAudio) {
    if (usedWords.indexOf(key) !== -1) {
      try { preloadedAudio[key].removeAttribute("src"); preloadedAudio[key].load(); } catch(e) {}
      delete preloadedAudio[key];
    }
  }

  var available = words.filter(function(w) { return usedWords.indexOf(w) === -1 && w !== currentWord && !preloadedAudio[w]; });
  if (available.length === 0) return;
  var nextW = available[Math.floor(Math.random() * available.length)];
  var url = "/speak/" + encodeURIComponent(nextW) + "?_preload=1&_t=" + Date.now();
  var audio = new Audio();
  audio.preload = "auto";
  audio.src = url;
  preloadedAudio[nextW] = audio;
}

// ==================== WORD REVIEW MODAL ====================
var reviewAllWords = {};
var currentReviewTab = "easy";
var currentReviewSort = "alphabetical";

function showWordReview() {
  var modal = document.getElementById("review-modal");
  modal.classList.remove("hidden");
  if (Object.keys(reviewAllWords).length === 0) {
    document.getElementById("review-word-list").innerHTML = '<p style="text-align:center;color:#888;padding:20px;">Loading words...</p>';
    fetch(groupQS("/words_all"))
      .then(function(res) { return res.json(); })
      .then(function(data) {
        reviewAllWords = data;
        renderReviewTab(currentReviewTab);
      })
      .catch(function() {
        document.getElementById("review-word-list").innerHTML = '<p style="text-align:center;color:#c00;">Failed to load words.</p>';
      });
  } else {
    renderReviewTab(currentReviewTab);
  }
}

function closeWordReview() {
  document.getElementById("review-modal").classList.add("hidden");
}

function switchReviewTab(tab) {
  currentReviewTab = tab;
  var tabs = document.querySelectorAll("#review-modal .lb-tab");
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].classList.toggle("active", tabs[i].textContent.toLowerCase() === tab);
  }
  renderReviewTab(tab);
}

function renderReviewTab(tab) {
  var list = document.getElementById("review-word-list");
  var words = reviewAllWords[tab] || [];
  if (words.length === 0) {
    list.innerHTML = '<p class="lb-empty">No words available.</p>';
    return;
  }
  
  // Apply sorting
  var sortedWords = applyReviewSorting(words, currentReviewSort);
  
  var html = '';
  for (var i = 0; i < sortedWords.length; i++) {
    var w = sortedWords[i];
    html += '<div class="review-word-item">';
    html += '<span class="review-word-text">' + w.word + '</span>';
    if (w.week) {
      html += '<span class="review-word-week">Week ' + w.week + '</span>';
    }
    html += '<button class="review-listen-btn" onclick="playReviewWord(\'' + w.word.replace(/'/g, "\\'") + '\')" title="Listen">';
    html += '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>';
    html += '</button>';
    html += '</div>';
  }
  list.innerHTML = html;
}

function applyReviewSorting(words, sortType) {
  var sortedWords = [];
  
  if (sortType === "alphabetical") {
    // Simple alphabetical sort
    sortedWords = words.slice().sort(function(a, b) {
      var wordA = typeof a === 'string' ? a : a.word;
      var wordB = typeof b === 'string' ? b : b.word;
      return wordA.localeCompare(wordB);
    });
  } else if (sortType === "week") {
    // Group by week and sort by week then alphabetically
    var weekGroups = {};
    words.forEach(function(item) {
      var word = typeof item === 'string' ? item : item.word;
      var week = typeof item === 'string' ? 1 : (item.week || 1);
      if (!weekGroups[week]) {
        weekGroups[week] = [];
      }
      weekGroups[week].push(item);
    });
    
    // Sort weeks numerically
    var sortedWeeks = Object.keys(weekGroups).sort(function(a, b) {
      return parseInt(a) - parseInt(b);
    });
    
    // Sort words within each week alphabetically
    sortedWeeks.forEach(function(week) {
      var weekWords = weekGroups[week].sort(function(a, b) {
        var wordA = typeof a === 'string' ? a : a.word;
        var wordB = typeof b === 'string' ? b : b.word;
        return wordA.localeCompare(wordB);
      });
      sortedWords = sortedWords.concat(weekWords);
    });
  }
  
  return sortedWords;
}

function sortReviewWords(sortType) {
  currentReviewSort = sortType;
  
  // Update button states
  document.querySelectorAll('.sort-btn').forEach(function(btn) {
    btn.classList.remove('active');
  });
  document.getElementById('sort-' + sortType).classList.add('active');
  
  // Re-render current tab with new sorting
  renderReviewTab(currentReviewTab);
}

function playReviewWord(word) {
  var url = "/speak/" + encodeURIComponent(word);
  playTTS(url, null, null);
}

// ==================== SOUND TOGGLE (Mute SFX) ====================
var sfxMuted = (function() {
  try { return localStorage.getItem(lsKey("spelling_bee_sfx_muted")) === "1"; } catch(e) { return false; }
})();

function toggleSfxMute() {
  sfxMuted = !sfxMuted;
  var btn = document.getElementById("sfx-toggle");
  if (btn) btn.textContent = sfxMuted ? "🔇" : "🔊";
  try { localStorage.setItem(lsKey("spelling_bee_sfx_muted"), sfxMuted ? "1" : "0"); } catch(e) {}
}

// ==================== LOADING STATE ====================
function showLoadingState() {
  var area = document.getElementById("word-display");
  if (area) area.innerHTML = '<div class="loading-dots"><span>.</span><span>.</span><span>.</span></div>';
}

// ==================== GAME-OVER REVIEW: TAP TO HEAR ====================
var _origBuildReview = null;

function buildReviewWithAudio() {
  var section = document.getElementById("review-section");
  var container = document.getElementById("review-words");
  if (!section || !container) return;
  if (reviewWords.length === 0) { section.classList.add("hidden"); return; }
  section.classList.remove("hidden");
  container.innerHTML = "";
  for (var i = 0; i < reviewWords.length; i++) {
    var chip = document.createElement("button");
    chip.className = "review-chip review-chip-audio";
    chip.textContent = reviewWords[i];
    chip.setAttribute("data-word", reviewWords[i]);
    chip.onclick = function() {
      var w = this.getAttribute("data-word");
      playReviewWord(w);
    };
    container.appendChild(chip);
  }
}

// ==================== RANKED MODE ====================
var isRankedMode = false;
var rankedAttemptsLeft = 3;
var rankedDifficulty = "medium";
var rankedBombsCorrect = 0;
var rankedReachedX3 = false;
var rankedWordsPlayed = 0;     // guard: only consume attempt after 3+ words
var rankedAttemptConsumed = false;

// Ranked uses competition engine variables
var rankedWordTime = 14;       // starts at 14s, shrinks
var RANKED_TIME_START = 14;
var RANKED_TIME_MIN = 6;
var RANKED_SHRINK_EVERY = 2;   // shrink every N correct words
var RANKED_SHRINK_BY = 1;      // shrink by 1s each step

function _requireName() {
  playerName = document.getElementById("player-name").value.trim();
  if (!playerName) {
    document.getElementById("player-name").focus();
    document.getElementById("player-name").classList.add("input-shake");
    setTimeout(function() { document.getElementById("player-name").classList.remove("input-shake"); }, 500);
    return false;
  }
  localStorage.setItem(lsKey("spelling_bee_name"), playerName);
  return true;
}

function openRankedMode() {
  if (!_requireName()) return;

  // Team is assigned by admin — fetch from server profile
  fetch(groupQS("/api/player-team?name=" + encodeURIComponent(playerName)))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var team = data.team;
      if (team && team.team_id) {
        selectedTeamId = team.team_id;
        selectedTeamName = team.team_name || "";
        selectedTeamColor = team.team_color || "#f59e0b";
        selectedTeamEmoji = team.team_emoji || "";
      } else {
        selectedTeamId = "";
        selectedTeamName = "";
        selectedTeamColor = "#f59e0b";
        selectedTeamEmoji = "";
      }
      _showRankedModal();
    })
    .catch(function() {
      // Offline fallback — try localStorage
      try {
        var saved = JSON.parse(localStorage.getItem(lsKey("spelling_bee_team_" + playerName)) || "null");
        if (saved && saved.team_id) {
          selectedTeamId = saved.team_id;
          selectedTeamName = saved.team_name || "";
          selectedTeamColor = saved.team_color || "#f59e0b";
          selectedTeamEmoji = saved.team_emoji || "";
        }
      } catch(e) {}
      _showRankedModal();
    });
}

function _showRankedModal() {
  // Populate team chip
  var teamRow = document.getElementById("ranked-team-row");
  var teamChip = document.getElementById("ranked-team-chip");
  if (selectedTeamId && selectedTeamName) {
    teamChip.textContent = "🏅 " + selectedTeamName;
    teamChip.style.background = selectedTeamColor || "#f59e0b";
    teamRow.classList.remove("hidden");
  } else {
    teamRow.classList.add("hidden");
  }

  // Fetch attempts + rank preview
  fetch(groupQS("/api/ranked-check?name=" + encodeURIComponent(playerName)))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      rankedAttemptsLeft = data.attempts_left !== undefined ? data.attempts_left : 3;
      renderRankedPips(rankedAttemptsLeft, "ranked-pips-modal");
      var txt = document.getElementById("ranked-attempts-text");
      if (txt) txt.textContent = rankedAttemptsLeft + " attempt" + (rankedAttemptsLeft !== 1 ? "s" : "") + " remaining this week";
    })
    .catch(function() {
      rankedAttemptsLeft = 3;
      renderRankedPips(3, "ranked-pips-modal");
    });

  // Fetch rank preview from team leaderboard
  fetch(groupQS("/api/team-leaderboard"))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var teams = data.teams || [];
      var myPos = -1;
      for (var i = 0; i < teams.length; i++) {
        if (teams[i].id === selectedTeamId) { myPos = i + 1; break; }
      }
      var previewEl = document.getElementById("ranked-rank-preview");
      var valEl = document.getElementById("rank-preview-value");
      if (previewEl && valEl && myPos > 0) {
        var medals = ["🥇","🥈","🥉"];
        valEl.textContent = (myPos <= 3 ? medals[myPos-1] + " " : "") + "#" + myPos + " of " + teams.length + " teams";
        previewEl.classList.remove("hidden");
      }
    })
    .catch(function() {});

  document.getElementById("ranked-modal").classList.remove("hidden");
}

function closeRankedModal() {
  document.getElementById("ranked-modal").classList.add("hidden");
}

function showRulesModal() {
  document.getElementById("rules-modal").classList.remove("hidden");
}

function closeRulesModal() {
  document.getElementById("rules-modal").classList.add("hidden");
}

function renderRankedPips(left, containerId) {
  var el = document.getElementById(containerId);
  if (!el) return;
  var html = "";
  for (var i = 0; i < 3; i++) {
    html += '<div class="ranked-pip ' + (i < left ? "ranked-pip-active" : "ranked-pip-used") + '"></div>';
  }
  el.innerHTML = html;
}

function updateRankedBadge() {
  if (!playerName) return;
  fetch(groupQS("/api/ranked-check?name=" + encodeURIComponent(playerName)))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var badge = document.getElementById("ranked-attempts-badge");
      if (badge) badge.textContent = (data.attempts_left || 0) + " left";
    }).catch(function() {});
}

function startRanked(difficulty) {
  if (rankedAttemptsLeft <= 0) {
    var txt = document.getElementById("ranked-attempts-text");
    if (txt) txt.textContent = "No attempts left this week! Resets Monday.";
    return;
  }
  // Double-check with server before starting
  fetch(groupQS("/api/ranked-check?name=" + encodeURIComponent(playerName)))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      rankedAttemptsLeft = data.attempts_left !== undefined ? data.attempts_left : rankedAttemptsLeft;
      updateRankedBadge();
      if (rankedAttemptsLeft <= 0) {
        var txt = document.getElementById("ranked-attempts-text");
        if (txt) txt.textContent = "No attempts left this week! Resets Monday.";
        return;
      }
      _doStartRanked(difficulty);
    })
    .catch(function() { _doStartRanked(difficulty); });
}

function _doStartRanked(difficulty) {
  var resolvedDiff = difficulty === "dynamic" ? _pickDynamicDifficulty() : difficulty;
  closeRankedModal();
  // Add ranked visual style to game screen
  var gs = document.getElementById("game-screen");
  if (gs) gs.classList.add("ranked-bg");
  // PIN already verified at login — start game directly
  _lastGameWasRanked = true;
  isRankedMode = true;
  isPracticeMode = false;
  rankedDifficulty = resolvedDiff;
  rankedBombsCorrect = 0;
  rankedReachedX3 = false;
  rankedWordsPlayed = 0;
  rankedAttemptConsumed = false;
  rankedWordTime = RANKED_TIME_START;
  startTabSwitchDetection();
  _startRankedEngine(resolvedDiff);
}

function _pickDynamicDifficulty() {
  // Pick difficulty based on player's past performance stored locally
  var stats = getStats();
  var best = Math.max(stats.bestEasy || 0, stats.bestMedium || 0, stats.bestHard || 0);
  if (best >= 80) return "hard";
  if (best >= 40) return "medium";
  return "easy";
}

// ==================== PRACTICE MODE ====================
function openPracticeMode() {
  if (!_requireName()) return;
  isPracticeMode = true;
  isRankedMode = false;
  rankedWordTime = RANKED_TIME_START;
  rankedBombsCorrect = 0;
  rankedReachedX3 = false;
  rankedWordsPlayed = 0;
  rankedAttemptConsumed = false;
  _startRankedEngine("medium"); // practice always uses mixed pool
}

// ==================== RANKED ENGINE (shared by ranked + practice) ====================
function _startRankedEngine(difficulty) {
  // Reset all game state
  isCompetitionMode = true;  // reuse competition engine
  compTeamId = selectedTeamId || "";
  compTeamName = selectedTeamName || "";
  compTeamColor = selectedTeamColor || "#f59e0b";
  compTeamEmoji = selectedTeamEmoji || "";
  compCorrect = 0;
  compWrong = 0;
  compWordTime = rankedWordTime;

  // Reset game state
  score = 0;
  usedWords = [];
  reviewWords = [];
  streak = 0;
  bestStreak = 0;
  totalBonusTime = 0;
  wordsCompleted = 0;
  audioPlayCount = 0;
  spellPlayCount = 0;
  currentRound = 1;
  wordInRound = 0;
  wrongLetters = 0;
  wordScores = [];
  lives = 3;
  maxLives = 3;
  currentDifficulty = difficulty;

  // NEW: Reset streak bank and shield
  streakBank = 0;
  streakShield = false;

  updateScore();
  updateStreak();
  updateLivesDisplay();

  var badge = document.getElementById("difficulty-badge");
  if (isPracticeMode) {
    badge.textContent = "PRACTICE";
    badge.className = "difficulty-badge competition";
  } else {
    badge.textContent = "RANKED";
    badge.className = "difficulty-badge competition";
  }

  var compBadge = document.getElementById("comp-team-badge");
  if (compTeamName && !isPracticeMode) {
    compBadge.textContent = "🏅 " + compTeamName;
    compBadge.style.background = compTeamColor;
    compBadge.classList.remove("hidden");
  } else {
    compBadge.classList.add("hidden");
  }

  var rankedBadge = document.getElementById("ranked-hud-badge");
  if (rankedBadge) {
    rankedBadge.textContent = isPracticeMode ? "🎯 PRACTICE" : "🎖️ RANKED";
    rankedBadge.classList.remove("hidden");
  }

  document.getElementById("player-tag").textContent = playerName;
  document.getElementById("round-indicator").textContent = isPracticeMode ? "Practice — no limits" : "0 correct • 0 missed";

  setAtmosphere("competition");
  showScreen("game-screen");
  showLoadingState();

  var url = (isRankedMode || isPracticeMode) ? "/words_ranked" : "/words_all";
  fetch(groupQS(url))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var easy = (data.easy || []).slice();
      var medium = (data.medium || []).slice();
      var hard = (data.hard || []).slice();
      shuffleArray(easy); shuffleArray(medium); shuffleArray(hard);

      // Build pool with equal integration across difficulties
      var pool;
      if (difficulty === "easy") {
        pool = easy.concat(medium.slice(0, Math.ceil(medium.length * 0.2)));
        shuffleArray(pool);
      } else if (difficulty === "hard") {
        pool = hard.concat(medium.slice(0, Math.ceil(medium.length * 0.4)));
        shuffleArray(pool);
      } else {
        // Equal integration: interleave easy/medium/hard evenly
        var maxLen = Math.max(easy.length, medium.length, hard.length);
        pool = [];
        for (var wi = 0; wi < maxLen; wi++) {
          if (wi < easy.length) pool.push(easy[wi]);
          if (wi < medium.length) pool.push(medium[wi]);
          if (wi < hard.length) pool.push(hard[wi]);
        }
      }
      compAllWords = pool;
      words = pool.slice();

      // Fetch bomb words for ranked/practice modes
      if (isRankedMode || isPracticeMode) {
        // Use tournament-specific endpoint for tournament group
        var bombUrl = (currentGroup === "tournament") 
          ? groupQS("/words_bombs_tournament?difficulty=" + encodeURIComponent(currentDifficulty))
          : groupQS("/words_bombs");
          
        fetch(bombUrl)
          .then(function(r) { return r.json(); })
          .then(function(bombData) {
            allBombWords = bombData || [];
          })
          .catch(function(err) {
            console.error("Bomb words load error:", err);
            allBombWords = [];
          });
      }

      maxTime = compWordTime;
      timeLeft = maxTime;

      pickWord(); // sets currentWord
      resetBombCounter();
      checkBombWord(); // may override currentWord with bomb word
      renderBoxes(currentWord);
      updateRefImage(currentWord);
      hideSpeakingUI();
      buildKeyboard();
      resetKeyboardVisibility();
      setupNativeKeyboardDetection();
      playAudio();
      wordStartTime = Date.now();
      wrongLetters = 0;
      startTimer();
      gameActive = true;
      preloadNextWordAudio();
    })
    .catch(function(err) {
      console.error("Ranked words load error:", err);
    });
}

// ==================== BOMB WORDS ====================
var isBombWord = false;
var bombWordCounter = 0;
var allBombWords = []; // All hard words from all weeks

// NEW: Fixed bomb intervals (same for all players)
var BOMB_INTERVALS = [5, 10, 15, 20, 25, 30, 35, 40]; // Maximum 8 bombs

function resetBombCounter() {
  bombWordCounter = 0;
}

function checkBombWord() {
  if (!isCompetitionMode && !isRankedMode) { isBombWord = false; return; }
  bombWordCounter++;
  
  // NEW: Check if current word should be a bomb based on fixed intervals
  if (BOMB_INTERVALS.includes(bombWordCounter)) {
    isBombWord = true;
    // Pick a random hard word from any week for bomb challenge
    if (allBombWords.length > 0) {
      var bombWord = allBombWords[Math.floor(Math.random() * allBombWords.length)];
      // Replace current word with bomb word
      currentWord = bombWord;
    }
  } else {
    isBombWord = false;
  }
  var ind = document.getElementById("bomb-indicator");
  if (ind) {
    if (isBombWord) {
      ind.classList.remove("hidden");
      ind.classList.add("bomb-pulse");
      sfxBomb();
    } else {
      ind.classList.add("hidden");
      ind.classList.remove("bomb-pulse");
    }
  }
}

function sfxBomb() {
  try {
    var ctx = getAudioCtx();
    // Low rumble + high ping
    playTone(80, 0.3, "sawtooth", 0.08);
    setTimeout(function() { playTone(1200, 0.15, "sine", 0.1); }, 200);
    setTimeout(function() { playTone(1600, 0.1, "sine", 0.12); }, 320);
  } catch(e) {}
}

// ==================== STREAK MULTIPLIER ====================
function getStreakMultiplier() {
  if (streak >= 8) return 3;
  if (streak >= 5) return 2;
  if (streak >= 3) return 1.5;
  return 1;
}

// NEW: Balanced streak multiplier with diminishing returns
function getBalancedStreakMultiplier() {
  if (streak <= 2) return 1.0;      // No bonus for low streak
  if (streak <= 4) return 1.2;      // Small bonus (was 1.5)
  if (streak <= 7) return 1.4;      // Medium bonus (was 2.0)
  if (streak <= 12) return 1.6;     // High bonus (was 3.0)
  return 1.7;                       // Maximum cap (was 3.0)
}

// NEW: Streak bank for recovery mechanics
var streakBank = 0;
var streakShield = false;

function updateStreakBank(streak) {
  if (streak === 3) { streakBank += 50; showBonus("🏆 Milestone: +50 Bank"); }
  if (streak === 5) { streakBank += 100; showBonus("🏆 Milestone: +100 Bank"); }
  if (streak === 8) { streakBank += 200; showBonus("🏆 Milestone: +200 Bank"); }
  if (streak === 12) { streakBank += 300; showBonus("🏆 Milestone: +300 Bank"); }
}

function updateStreakShield(streak) {
  if (streak >= 5 && !streakShield) {
    streakShield = true;
    showBonus("🛡️ Streak Shield Active!");
  }
}

function breakStreak() {
  if (streakBank > 0) {
    var recoveredPoints = Math.min(streakBank, 100);
    score += recoveredPoints;
    streakBank -= recoveredPoints;
    showBonus("💰 Streak Recovery: +" + recoveredPoints);
  }
  streak = 0;
  streakShield = false;
}

function updateStreakMultiplier() {
  var mult = getStreakMultiplier();
  var multEl = document.getElementById("streak-multiplier");
  var fillEl = document.getElementById("streak-fire-fill");
  var el = document.getElementById("streak-display");

  if (multEl) {
    if (mult > 1) {
      multEl.textContent = "\u00d7" + mult;
      multEl.className = "streak-multiplier mult-" + (mult >= 3 ? "3" : mult >= 2 ? "2" : "15");
    } else {
      multEl.textContent = "";
    }
  }

  // Fire bar fill: 0-3 streak = 0%, 3-5 = 33%, 5-8 = 66%, 8+ = 100%
  if (fillEl) {
    var pct = 0;
    if (streak >= 8) pct = 100;
    else if (streak >= 5) pct = 66;
    else if (streak >= 3) pct = 33;
    else pct = Math.round((streak / 3) * 33);
    fillEl.style.width = pct + "%";
    fillEl.className = "streak-fire-fill" + (streak >= 8 ? " fire-x3" : streak >= 5 ? " fire-x2" : streak >= 3 ? " fire-x15" : "");
  }

  if (mult >= 3 && (isRankedMode || isCompetitionMode)) {
    rankedReachedX3 = true;
    if (el) el.classList.add("streak-x3-glow");
  } else {
    if (el) el.classList.remove("streak-x3-glow");
  }
}

// ==================== SCORE POP-UP ====================
function showScorePopup(text, isPositive) {
  var el = document.getElementById("score-popup");
  if (!el) return;
  el.textContent = text;
  el.className = "score-popup " + (isPositive ? "score-popup-pos" : "score-popup-neg");
  el.classList.remove("hidden");
  void el.offsetWidth; // force reflow for animation restart
  el.classList.add("score-popup-animate");
  clearTimeout(el._timer);
  el._timer = setTimeout(function() {
    el.classList.add("hidden");
    el.classList.remove("score-popup-animate");
  }, 900);
}

// ==================== TAB SWITCH DETECTION ====================
var tabSwitchCount = 0;
var tabSwitchActive = false;
var _tabWarningPaused = false;

function startTabSwitchDetection() {
  tabSwitchCount = 0;
  tabSwitchActive = true;
  _tabWarningPaused = false;
}

function stopTabSwitchDetection() {
  tabSwitchActive = false;
  tabSwitchCount = 0;
  _tabWarningPaused = false;
}

function dismissTabWarning() {
  var overlay = document.getElementById("tab-switch-overlay");
  if (overlay) overlay.classList.add("hidden");
  // Resume game
  if (_tabWarningPaused) {
    _tabWarningPaused = false;
    gameActive = true;
    startTimer();
  }
}

document.addEventListener("visibilitychange", function() {
  if (!tabSwitchActive || !isRankedMode) return;
  if (document.hidden) {
    tabSwitchCount++;
    if (tabSwitchCount >= 3) {
      // PENALTY: No score + consume attempt (fair penalty for cheating)
      console.log("[ATTEMPT] Tab switching penalty - consuming attempt");
      gameActive = false;
      clearInterval(timer);
      stopTabSwitchDetection();
      
      // CONSUME ATTEMPT - this is fair penalty for cheating
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
      
      isRankedMode = false;
      var overlay = document.getElementById("tab-switch-overlay");
      var msg = document.getElementById("tab-switch-msg");
      if (msg) msg.textContent = "Ranked game invalidated — 3 tab switches detected. No score + Attempt consumed.";
      if (overlay) overlay.classList.remove("hidden");
      setTimeout(function() {
        if (overlay) overlay.classList.add("hidden");
        returnToMenu();
      }, 3000);
    } else {
      // Show warning but pause game
      gameActive = false;
      clearInterval(timer);
      _tabWarningPaused = true;
      var overlay = document.getElementById("tab-switch-overlay");
      var msg = document.getElementById("tab-switch-msg");
      if (msg) msg.textContent = "⚠️ Warning " + tabSwitchCount + "/2 — switching tabs again will invalidate your ranked game!";
      if (overlay) overlay.classList.remove("hidden");
    }
  }
});

// ==================== AVATAR PICKER ====================
var AVATAR_OPTIONS = [
  // People & roles
  "\uD83D\uDC64","\uD83D\uDC68\u200D\uD83C\uDFEB","\uD83D\uDC69\u200D\uD83C\uDFEB",
  "\uD83D\uDC77","\uD83E\uDDB8","\uD83E\uDDB9","\uD83D\uDC78","\uD83E\uDDD9",
  "\uD83E\uDDB8\u200D\u2640\uFE0F","\uD83E\uDDB9\u200D\u2642\uFE0F",
  "\uD83D\uDC68\u200D\uD83D\uDCBB","\uD83D\uDC69\u200D\uD83D\uDCBB",
  "\uD83D\uDC68\u200D\uD83C\uDFA8","\uD83D\uDC69\u200D\uD83C\uDFA8",
  "\uD83E\uDDD1\u200D\uD83D\uDE80","\uD83E\uDDD1\u200D\uD83C\uDF93",
  // Animals
  "\uD83E\uDD81","\uD83D\uDC2F","\uD83E\uDD8A","\uD83D\uDC3C","\uD83D\uDC27",
  "\uD83E\uDD89","\uD83D\uDC22","\uD83D\uDC2E","\uD83D\uDC37",
  "\uD83E\uDD96","\uD83D\uDC38","\uD83D\uDC35","\uD83E\uDD8B",
  "\uD83D\uDC09","\uD83E\uDD84","\uD83D\uDC7E","\uD83D\uDC3A",
  "\uD83E\uDD9C","\uD83D\uDC2C","\uD83E\uDD88","\uD83D\uDC3B",
  "\uD83E\uDD9D","\uD83E\uDD9A","\uD83D\uDC26","\uD83E\uDD86",
  // Fun / fantasy
  "\uD83D\uDC7B","\uD83E\uDD16","\uD83D\uDC7D","\uD83E\uDDD9\u200D\u2642\uFE0F",
  "\uD83D\uDC7C","\uD83E\uDDB9\u200D\u2640\uFE0F","\uD83D\uDC80","\uD83E\uDD21",
  // Objects / symbols
  "\uD83C\uDF1F","\uD83D\uDD25","\u26A1","\uD83C\uDFC6",
  "\uD83D\uDCA5","\uD83C\uDF08","\uD83D\uDC51","\uD83E\uDD47"
];
var playerAvatar = localStorage.getItem(lsKey("spelling_bee_avatar")) || "\uD83D\uDC64";

function openAvatarPicker() {
  var grid = document.getElementById("avatar-grid");
  if (!grid) return;
  var html = "";
  AVATAR_OPTIONS.forEach(function(av) {
    html += '<div class="avatar-option' + (av === playerAvatar ? " selected" : "") + '" onclick="selectAvatar(\'' + encodeURIComponent(av) + '\')">' + av + '</div>';
  });
  grid.innerHTML = html;
  document.getElementById("avatar-picker-overlay").classList.remove("hidden");
}

function selectAvatar(encoded) {
  playerAvatar = decodeURIComponent(encoded);
  localStorage.setItem(lsKey("spelling_bee_avatar"), playerAvatar);
  var av = document.getElementById("profile-avatar");
  if (av) av.firstChild.textContent = playerAvatar;
  // Update menu banner avatar too
  var menuAv = document.getElementById("menu-player-avatar");
  if (menuAv) menuAv.textContent = playerAvatar;
  // Refresh grid selection
  var opts = document.querySelectorAll(".avatar-option");
  opts.forEach(function(o) {
    o.classList.toggle("selected", o.textContent === playerAvatar);
  });
  // Persist avatar to server
  if (playerName) {
    fetch("/api/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(groupBody({ name: playerName, avatar: playerAvatar }))
    }).catch(function() {});
  }
}

function closeAvatarPicker() {
  document.getElementById("avatar-picker-overlay").classList.add("hidden");
  // Update avatar display
  var av = document.getElementById("profile-avatar");
  if (av) {
    av.childNodes[0].textContent = playerAvatar;
  }
}

// ==================== PIN SYSTEM ====================
var _pinBuffer = "";
var _pinMode = ""; // "set" | "verify"
var _pinCallback = null;

function getPinKey(name) {
  return lsKey("spelling_bee_pin_" + name.toLowerCase().trim());
}

function hasPin(name) {
  return !!localStorage.getItem(getPinKey(name));
}

function verifyPin(name, pin) {
  return localStorage.getItem(getPinKey(name)) === pin;
}

function savePin(name, pin) {
  localStorage.setItem(getPinKey(name), pin);
}

function openPinModal(mode, title, sub, callback) {
  _pinMode = mode;
  _pinBuffer = "";
  _pinCallback = callback;
  document.getElementById("pin-modal-title").textContent = title;
  document.getElementById("pin-modal-sub").textContent = sub;
  document.getElementById("pin-error").textContent = "";
  updatePinDots();
  document.getElementById("pin-modal-overlay").classList.remove("hidden");
}

function closePinModal() {
  document.getElementById("pin-modal-overlay").classList.add("hidden");
  _pinBuffer = "";
  // NOTE: do NOT null _pinCallback here — handlePinComplete calls closePinModal then fires callback
}

function updatePinDots() {
  for (var i = 0; i < 4; i++) {
    var dot = document.getElementById("pd" + i);
    if (dot) dot.classList.toggle("filled", i < _pinBuffer.length);
  }
}

function pinKey(digit) {
  if (_pinBuffer.length >= 4) return;
  _pinBuffer += digit;
  updatePinDots();
  if (_pinBuffer.length === 4) {
    setTimeout(function() { handlePinComplete(_pinBuffer); }, 120);
  }
}

function pinDel() {
  if (_pinBuffer.length > 0) {
    _pinBuffer = _pinBuffer.slice(0, -1);
    updatePinDots();
    document.getElementById("pin-error").textContent = "";
  }
}

function handlePinComplete(pin) {
  var name = (playerName || "").trim();
  if (_pinMode === "set") {
    savePin(name, pin);
    var cb = _pinCallback;
    _pinCallback = null;
    closePinModal();
    if (cb) cb(true);
  } else if (_pinMode === "verify") {
    if (verifyPin(name, pin)) {
      var cb = _pinCallback;
      _pinCallback = null;
      closePinModal();
      if (cb) cb(true);
    } else {
      document.getElementById("pin-error").textContent = "Wrong PIN \u2014 try again";
      _pinBuffer = "";
      updatePinDots();
    }
  }
}

// ==================== LOGOUT ====================
function logoutPlayer() {
  if (!confirm("Log out? You will need to enter your name and PIN again.")) return;
  try {
    localStorage.removeItem(lsKey("spelling_bee_name"));
    localStorage.removeItem(lsKey("spelling_bee_avatar"));
    localStorage.removeItem(lsKey("spelling_bee_authenticated"));
  } catch(e) {}
  playerName = "";
  playerAvatar = "\uD83D\uDC64";
  selectedTeamId = "";
  selectedTeamName = "";
  selectedTeamColor = "";
  selectedTeamEmoji = "";
  var nameInput = document.getElementById("player-name");
  if (nameInput) nameInput.value = "";
  // Reset login steps: show username entry, hide PIN screen
  var stepName = document.getElementById("login-step-name");
  var stepPin = document.getElementById("login-step-pin");
  if (stepName) stepName.classList.remove("hidden");
  if (stepPin) stepPin.classList.add("hidden");
  var loginInput = document.getElementById("login-name-input");
  if (loginInput) loginInput.value = "";
  showScreen("login-screen");
}

// Require PIN before ranked game — called from startRanked
function requirePinThenDo(callback) {
  // Use already-set playerName (ranked modal already validated it)
  var name = (playerName || "").trim();
  if (!name) { callback(true); return; }
  if (!hasPin(name)) {
    openPinModal("set",
      "\uD83D\uDD10 Set Your PIN",
      "Create a 4-digit PIN to protect your ranked scores. You\u2019ll need it every time you play ranked.",
      callback);
  } else {
    openPinModal("verify",
      "\uD83D\uDD10 Enter Your PIN",
      "Enter your PIN to start a ranked game as \u201c" + name + "\u201d.",
      callback);
  }
}

// ==================== PLAYER PROFILE ====================
var profileData = {};
var profileBadgeDefs = [];

function openProfile() {
  if (!playerName) {
    // Not logged in — go to login screen
    showScreen("login-screen");
    return;
  }
  localStorage.setItem(lsKey("spelling_bee_name"), playerName);
  // Update avatar display
  playerAvatar = localStorage.getItem(lsKey("spelling_bee_avatar")) || "\uD83D\uDC64";
  var avEl = document.getElementById("profile-avatar");
  if (avEl) avEl.childNodes[0].textContent = playerAvatar;
  showScreen("profile-screen");
  renderProfileLoading();
  fetch(groupQS("/api/profile?name=" + encodeURIComponent(playerName)))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      profileData = data.profile || {};
      profileBadgeDefs = data.badges || [];
      renderProfile();
    })
    .catch(function() {
      renderProfileOffline();
    });
}

function renderProfileLoading() {
  document.getElementById("profile-name-display").textContent = playerName;
  document.getElementById("pstat-games").textContent = "...";
  document.getElementById("pstat-best").textContent = "...";
  document.getElementById("pstat-streak").textContent = "...";
  document.getElementById("pstat-accuracy").textContent = "...";
  document.getElementById("profile-badges-grid").innerHTML = '<p style="opacity:0.5;font-size:0.85rem">Loading...</p>';
}

function renderProfileOffline() {
  // Fall back to localStorage stats
  var stats = getStats();
  document.getElementById("profile-name-display").textContent = playerName;
  document.getElementById("pstat-games").textContent = stats.totalGames || 0;
  var best = Math.max(stats.bestEasy || 0, stats.bestMedium || 0, stats.bestHard || 0);
  document.getElementById("pstat-best").textContent = best;
  document.getElementById("pstat-streak").textContent = stats.bestStreak || 0;
  document.getElementById("pstat-accuracy").textContent = "N/A";
  renderProfileBadges([], []);
  renderProfileAttemptPips(3);
}

function renderProfile() {
  document.getElementById("profile-name-display").textContent = playerName;

  // Team badge
  var teamBadge = document.getElementById("profile-team-badge");
  if (profileData.team_name) {
    teamBadge.textContent = (profileData.team_name);
    teamBadge.style.background = profileData.team_color || "#f59e0b";
    teamBadge.style.display = "inline-block";
  } else {
    teamBadge.style.display = "none";
  }

  // Stats — merge Firestore + localStorage
  var stats = getStats();
  var games = profileData.total_games || stats.totalGames || 0;
  var bestFs = Math.max(profileData.best_easy || 0, profileData.best_medium || 0, profileData.best_hard || 0);
  var bestLs = Math.max(stats.bestEasy || 0, stats.bestMedium || 0, stats.bestHard || 0);
  var best = Math.max(bestFs, bestLs);
  var streakBest = Math.max(profileData.best_streak || 0, stats.bestStreak || 0);
  var totalCorrect = profileData.total_correct_words || 0;
  var totalAttempted = profileData.total_attempted_words || 0;
  var acc = totalAttempted > 0 ? Math.round((totalCorrect / totalAttempted) * 100) + "%" : "N/A";

  document.getElementById("pstat-games").textContent = games;
  document.getElementById("pstat-best").textContent = best;
  document.getElementById("pstat-streak").textContent = streakBest;
  document.getElementById("pstat-accuracy").textContent = acc;

  // Ranked attempts pips
  renderProfileAttemptPips(profileData.ranked_attempts_left !== undefined ? profileData.ranked_attempts_left : 3);

  // View team button
  var teamId = profileData.team_id || selectedTeamId || "";
  var teamName = profileData.team_name || selectedTeamName || "";
  var teamColor = profileData.team_color || selectedTeamColor || "#f59e0b";
  var existingBtn = document.getElementById("view-team-btn");
  if (existingBtn) existingBtn.remove();
  if (teamId) {
    var btn = document.createElement("button");
    btn.id = "view-team-btn";
    btn.className = "menu-btn";
    btn.style.cssText = "width:100%;margin-top:4px;background:" + teamColor + ";color:#fff;border:none;font-weight:800;font-size:0.88rem;padding:10px;border-radius:12px;cursor:pointer;";
    btn.innerHTML = "\uD83D\uDC65 View Team: " + teamName;
    btn.onclick = function() { openTeamMembers(teamId, teamName, teamColor); };
    var rankedRow = document.querySelector(".profile-ranked-row");
    if (rankedRow) rankedRow.parentNode.insertBefore(btn, rankedRow);
  }

  // Badges
  renderProfileBadges(profileData.badges || [], profileBadgeDefs);
}

// ==================== TEAM MEMBERS ====================
function openTeamMembers(teamId, teamName, teamColor) {
  var badge = document.getElementById("team-members-badge");
  if (badge) {
    badge.textContent = "\uD83C\uDFC5 " + teamName;
    badge.style.background = teamColor || "#f59e0b";
  }
  var list = document.getElementById("team-members-list");
  if (list) list.innerHTML = '<p style="text-align:center;opacity:0.5;padding:20px">Loading...</p>';
  showScreen("team-members-screen");

  fetch(groupQS("/api/team-members?team_id=" + encodeURIComponent(teamId)))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var week = document.getElementById("team-members-week");
      if (week) week.textContent = "Week: " + (data.week || "");
      var members = data.members || [];
      if (!list) return;
      if (members.length === 0) {
        list.innerHTML = '<p style="text-align:center;opacity:0.5;padding:20px">No ranked scores yet this week.</p>';
        return;
      }
      var medals = ["\uD83E\uDD47", "\uD83E\uDD48", "\uD83E\uDD49"];
      var html = "";
      members.forEach(function(m, i) {
        var rankClass = i === 0 ? "top-1" : i === 1 ? "top-2" : i === 2 ? "top-3" : "";
        var rankIcon = i < 3 ? medals[i] : (i + 1);
        html += '<div class="team-member-row ' + rankClass + '">';
        html += '<div class="team-member-rank">' + rankIcon + '</div>';
        html += '<div class="team-member-info">';
        html += '<div class="team-member-name">' + m.name + '</div>';
        html += '<div class="team-member-stats">' + (m.total_games || 0) + ' games &nbsp;\u00b7&nbsp; best streak ' + (m.best_streak || 0) + '</div>';
        html += '</div>';
        html += '<div>';
        html += '<div class="team-member-score">' + (m.best_score || 0) + '</div>';
        html += '<div class="team-member-score-label">best score</div>';
        html += '</div>';
        html += '</div>';
      });
      list.innerHTML = html;
    })
    .catch(function() {
      if (list) list.innerHTML = '<p style="text-align:center;opacity:0.5;padding:20px">Could not load team data.</p>';
    });
}

function renderProfileAttemptPips(left) {
  var el = document.getElementById("profile-attempts-pips");
  if (!el) return;
  var html = "";
  for (var i = 0; i < 3; i++) {
    html += '<div class="profile-pip ' + (i < left ? "profile-pip-active" : "profile-pip-used") + '"></div>';
  }
  el.innerHTML = html;
}

function renderProfileBadges(earned, defs) {
  var grid = document.getElementById("profile-badges-grid");
  if (!grid) return;
  var allBadges = defs.length > 0 ? defs : [
    {id:"first_blood",    name:"First Blood",    emoji:"\uD83C\uDF1F", desc:"Complete your first ranked game"},
    {id:"iron_brain",     name:"Iron Brain",     emoji:"\uD83E\uDDE0", desc:"10 correct words in a row"},
    {id:"speed_runner",   name:"Speed Runner",   emoji:"\u26A1",       desc:"Answer 5 words with time to spare"},
    {id:"bomb_master",    name:"Bomb Master",    emoji:"\uD83D\uDCA3", desc:"Nail 3 bomb words correctly"},
    {id:"on_fire",        name:"On Fire",        emoji:"\uD83D\uDD25", desc:"Reach \u00d73 streak multiplier"},
    {id:"precision_king", name:"Precision",      emoji:"\uD83C\uDFAF", desc:"95%+ accuracy in a ranked game"},
    {id:"centurion",      name:"Centurion",      emoji:"\uD83C\uDFC6", desc:"Score 100+ points in ranked"},
    {id:"comeback_kid",   name:"Comeback Kid",   emoji:"\uD83D\uDCAA", desc:"Win ranked after losing a life"},
    {id:"perfect_speller",name:"Perfect Speller",emoji:"\u2728",       desc:"5 perfect words in one game"},
    {id:"team_player",    name:"Team Player",    emoji:"\uD83E\uDD1D", desc:"Contribute to your team\u2019s weekly score"},
    {id:"veteran",        name:"Veteran",        emoji:"\uD83C\uDF96\uFE0F", desc:"Use all 3 ranked attempts in a week"},
    {id:"champion",       name:"Champion",       emoji:"\uD83D\uDC51", desc:"Reach #1 on the weekly leaderboard"},
  ];
  var html = "";
  allBadges.forEach(function(b) {
    var hasIt = earned.indexOf(b.id) !== -1;
    html += '<div class="badge-card ' + (hasIt ? "badge-earned" : "badge-locked") + '" title="' + b.desc + '">';
    html += '<div class="badge-emoji">' + b.emoji + '</div>';
    html += '<div class="badge-name">' + b.name + '</div>';
    html += '<div class="badge-desc">' + b.desc + '</div>';
    if (!hasIt) html += '<div class="badge-lock">\uD83D\uDD12</div>';
    html += '</div>';
  });
  grid.innerHTML = html;
}

// ==================== HOOK RANKED + BOMB INTO GAME FLOW ====================

// Wrap updateStreak to also update multiplier
var _origUpdateStreak = updateStreak;
updateStreak = function() {
  _origUpdateStreak();
  updateStreakMultiplier();
};

// Wrap returnToMenu to clean up ranked/practice state
var _origReturnToMenu = returnToMenu;
returnToMenu = function() {
  stopTabSwitchDetection();
  _lastGameWasRanked = false;
  isRankedMode = false;
  isPracticeMode = false;
  isBombWord = false;
  var gs = document.getElementById("game-screen");
  if (gs) gs.classList.remove("ranked-bg");
  var ind = document.getElementById("bomb-indicator");
  if (ind) ind.classList.add("hidden");
  var overlay = document.getElementById("tab-switch-overlay");
  if (overlay) overlay.classList.add("hidden");
  _origReturnToMenu();
  updateRankedBadge();
};

// Wrap startGame (regular modes) to reset bomb counter
var _origStartGame = startGame;
startGame = function(difficulty) {
  resetBombCounter();
  _origStartGame(difficulty);
};

// nextWord already calls checkBombWord() internally for competition/ranked modes

// Hook score pop-ups into bonus/penalty display
// Bonus/penalty popups — use only the original popup (no duplicate score-popup)
var _origShowBonus = showBonus;
var _origShowPenalty = showPenalty;

// ==================== PATCH compEndGame FOR RANKED SUBMISSION ====================
// compEndGame is called when isCompetitionMode ends (which includes ranked/practice).
// We patch it to also handle ranked score submission and badge display.
var _origCompEndGame = compEndGame;
compEndGame = function() {
  var wasRanked = isRankedMode;
  var wasPractice = isPracticeMode;

  stopTabSwitchDetection();
  isRankedMode = false;
  isPracticeMode = false;

  var rb = document.getElementById("ranked-hud-badge");
  if (rb) rb.classList.add("hidden");
  var ind = document.getElementById("bomb-indicator");
  if (ind) ind.classList.add("hidden");

  // Calculate accuracy from wordScores
  var totalLetters = 0, totalErrors = 0;
  for (var i = 0; i < wordScores.length; i++) {
    var ws = wordScores[i];
    totalLetters += (ws.word ? ws.word.replace(/ /g, "").length : 1);
    totalErrors += (ws.errors || 0);
  }
  var accuracy = totalLetters > 0 ? Math.max(0, (totalLetters - totalErrors) / totalLetters) : 0;

  // Prevent _origCompEndGame from submitting to /leaderboard for ranked/practice games
  // (ranked submission is handled below with correct is_ranked: true)
  _skipCompEndGameSubmit = wasRanked || wasPractice;
  _origCompEndGame();
  _skipCompEndGameSubmit = false;

  // Attempt protection: games with < 3 words don't consume an attempt
  // _skip_attempt = true means "server should NOT increment attempt" (already consumed or protected)
  var shouldSkipAttempt = false;
  if (wasRanked && !rankedAttemptConsumed && wordScores.length < 3) {
    console.log("[ATTEMPT] Game ended early - attempt not consumed:", wordScores.length, "words played");
    showBonus("\u2705 Attempt protected - game ended early");
    shouldSkipAttempt = true; // Tell server: don't consume
  } else if (wasRanked && rankedAttemptConsumed) {
    console.log("[ATTEMPT] Attempt already consumed earlier (quit/tab-switch)");
    shouldSkipAttempt = true; // Tell server: already consumed, don't double-count
  } else if (wasRanked && !rankedAttemptConsumed && wordScores.length >= 3) {
    // Normal game end with meaningful play - server should consume the attempt
    rankedAttemptConsumed = true;
    shouldSkipAttempt = false; // Tell server: please consume this attempt
    console.log("[ATTEMPT] Will consume attempt via score submission:", wordScores.length, "words played");
  }

  // Show ranked result badge on game over
  var rrb = document.getElementById("ranked-result-badge");
  if (rrb) {
    if (wasRanked) {
      rrb.textContent = "\uD83C\uDF96\uFE0F Ranked Game";
      rrb.classList.remove("hidden");
    } else if (wasPractice) {
      rrb.textContent = "\uD83C\uDFAF Practice Game \u2014 not counted";
      rrb.classList.remove("hidden");
    } else {
      rrb.classList.add("hidden");
    }
  }

  // Track whether this was ranked for playAgain logic
  _lastGameWasRanked = wasRanked;

  // Submit ranked score to leaderboard + profile (single request handles attempt + score)
  if (wasRanked && playerName) {
    fetch("/leaderboard", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(groupBody({
        name: playerName,
        score: score,
        difficulty: currentDifficulty,
        streak: bestStreak,
        is_ranked: true,
        is_competition: !!(compTeamId),
        team_id: compTeamId || "",
        team_name: compTeamName || "",
        accuracy: accuracy,
        words_completed: wordsCompleted,
        bombs_correct: rankedBombsCorrect,
        time_bonuses: 0,
        reached_x3: rankedReachedX3,
        _skip_attempt: shouldSkipAttempt,
      }))
    }).then(function(response) {
      if (!response.ok) {
        throw new Error("HTTP " + response.status + ": " + response.statusText);
      }
      // Delay updates to allow backend to aggregate team scores
      setTimeout(function() {
        updateRankedBadge();
        // Update play-again button based on remaining attempts
        fetch(groupQS("/api/ranked-check?name=" + encodeURIComponent(playerName)))
          .then(function(r) { return r.json(); })
          .then(function(data) {
            rankedAttemptsLeft = data.attempts_left || 0;
            var btn = document.getElementById("play-again-btn");
            if (btn && rankedAttemptsLeft <= 0) {
              btn.innerHTML = '<span class="btn-label">No Attempts Left</span>';
              btn.disabled = true;
              btn.style.opacity = "0.5";
            }
          }).catch(function() {});
      }, 1000); // 1 second delay for backend processing
    }).catch(function(error) {
      console.error("[SCORE] Failed to submit ranked score:", error);
      // Retry logic for critical score submissions
      if (score > 0) {
        console.log("[SCORE] Retrying score submission...");
        setTimeout(function() {
          fetch("/leaderboard", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(groupBody({
              name: playerName,
              score: score,
              difficulty: currentDifficulty,
              streak: bestStreak,
              is_ranked: true,
              is_competition: !!(compTeamId),
              team_id: compTeamId || "",
              team_name: compTeamName || "",
              accuracy: accuracy,
              words_completed: wordsCompleted,
              bombs_correct: rankedBombsCorrect,
              time_bonuses: 0,
              reached_x3: rankedReachedX3,
              _skip_attempt: shouldSkipAttempt,
            }))
          }).then(function(response) {
            if (response.ok) {
              console.log("[SCORE] Retry successful");
              updateRankedBadge();
            } else {
              console.error("[SCORE] Retry failed:", response.status);
              showBonus("⚠️ Score submission failed - please contact support");
            }
          }).catch(function(retryError) {
            console.error("[SCORE] Retry failed:", retryError);
            showBonus("⚠️ Score submission failed - please check connection");
          });
        }, 2000); // Wait 2 seconds before retry
      }
    });
  }
};

// ==================== PERFORMANCE: DEBOUNCED RESIZE ====================
var _resizeTimer = null;
function debouncedResize() {
  clearTimeout(_resizeTimer);
  _resizeTimer = setTimeout(function() {
    resizeConfetti();
    resizeAtmo();
  }, 150);
}

// ==================== LOGIN SYSTEM ====================
var _loginPinBuffer = "";
var _loginMode = ""; // "login" | "register"
var _loginName = "";

var _loginChecking = false;

function loginCheckName() {
  if (_loginChecking) return;
  var name = document.getElementById("login-name-input").value.trim();
  var errEl = document.getElementById("login-name-error");
  if (!name) {
    errEl.textContent = "Please enter your name.";
    document.getElementById("login-name-input").focus();
    return;
  }
  errEl.textContent = "";
  _loginName = name;
  _loginChecking = true;
  var btn = document.querySelector("#login-step-name .primary-btn");
  if (btn) { btn.disabled = true; btn.querySelector(".btn-label").textContent = "Checking..."; }

  function resetBtn() {
    _loginChecking = false;
    if (btn) { btn.disabled = false; btn.querySelector(".btn-label").textContent = "Continue"; }
  }

  // Check server if profile exists
  fetch("/api/auth", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(groupBody({ name: name, action: "check" }))
  })
    .then(function(r) {
      if (!r.ok && r.status !== 404) throw new Error("HTTP " + r.status);
      return r.json();
    })
    .then(function(data) {
      resetBtn();
      if (data.exists) {
        _loginMode = "login";
        document.getElementById("login-pin-title").textContent = "\uD83D\uDD10 Enter Your PIN";
        document.getElementById("login-pin-sub").textContent = "Welcome back, " + name + "! Enter your 4-digit PIN.";
      } else if (data.pre_registered) {
        _loginMode = "register";
        document.getElementById("login-pin-title").textContent = "\uD83D\uDD10 Create Your PIN";
        document.getElementById("login-pin-sub").textContent = "Welcome, " + name + "! You\u2019re on " + (data.team_name || "a team") + ". Create a 4-digit PIN to get started.";
      } else {
        _loginMode = "register";
        document.getElementById("login-pin-title").textContent = "\uD83D\uDD10 Create a PIN";
        document.getElementById("login-pin-sub").textContent = "Hi " + name + "! Create a 4-digit PIN to protect your account.";
      }
      _loginPinBuffer = "";
      loginUpdateDots();
      document.getElementById("login-pin-error").textContent = "";
      document.getElementById("login-step-name").classList.add("hidden");
      document.getElementById("login-step-pin").classList.remove("hidden");
    })
    .catch(function(err) {
      resetBtn();
      errEl.textContent = "Could not connect. Please try again. (" + (err.message || "network error") + ")";
    });
}

function loginGoBack() {
  _loginPinBuffer = "";
  _loginMode = "";
  document.getElementById("login-step-pin").classList.add("hidden");
  document.getElementById("login-step-name").classList.remove("hidden");
  document.getElementById("login-name-input").focus();
}

function loginUpdateDots() {
  for (var i = 0; i < 4; i++) {
    var dot = document.getElementById("lpd" + i);
    if (dot) dot.classList.toggle("filled", i < _loginPinBuffer.length);
  }
}

function loginPinKey(digit) {
  if (_loginPinBuffer.length >= 4) return;
  _loginPinBuffer += digit;
  loginUpdateDots();
  if (_loginPinBuffer.length === 4) {
    setTimeout(function() { loginSubmitPin(_loginPinBuffer); }, 120);
  }
}

function loginPinDel() {
  if (_loginPinBuffer.length > 0) {
    _loginPinBuffer = _loginPinBuffer.slice(0, -1);
    loginUpdateDots();
    document.getElementById("login-pin-error").textContent = "";
  }
}

function loginSubmitPin(pin) {
  var errEl = document.getElementById("login-pin-error");
  fetch("/api/auth", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(groupBody({ name: _loginName, pin: pin, action: _loginMode }))
  })
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (!data.ok) {
        errEl.textContent = data.error || "Wrong PIN \u2014 try again";
        _loginPinBuffer = "";
        loginUpdateDots();
        return;
      }
      // Login successful!
      playerName = data.name || _loginName;
      localStorage.setItem(lsKey("spelling_bee_name"), playerName);
      localStorage.setItem(lsKey("spelling_bee_authenticated"), "1");
      // Clean up old shared stats key (pre per-player migration)
      try { localStorage.removeItem(lsKey("spelling_bee_stats")); } catch(e) {}
      document.getElementById("player-name").value = playerName;

      // Set team from server (admin-assigned)
      if (data.team_id) {
        selectedTeamId = data.team_id;
        selectedTeamName = data.team_name || "";
        selectedTeamColor = data.team_color || "#f59e0b";
        selectedTeamEmoji = data.team_emoji || "";
        try {
          localStorage.setItem(lsKey("spelling_bee_team_" + playerName), JSON.stringify({
            team_id: data.team_id, team_name: data.team_name, team_color: data.team_color, team_emoji: data.team_emoji
          }));
        } catch(e) {}
      }

      if (data.avatar) {
        playerAvatar = data.avatar;
        localStorage.setItem(lsKey("spelling_bee_avatar"), playerAvatar);
      }

      rankedAttemptsLeft = data.ranked_attempts_left !== undefined ? data.ranked_attempts_left : 3;

      // Update menu UI
      _updateMenuBanner(data.is_new);
      updateRankedBadge();

      showScreen("menu-screen");
    })
    .catch(function() {
      errEl.textContent = "Server error. Try again.";
      _loginPinBuffer = "";
      loginUpdateDots();
    });
}

// ==================== MENU BANNER HELPER ====================
function _updateMenuBanner(isNew) {
  var greetings = isNew
    ? ["Welcome, " + playerName + "!", "Hey " + playerName + "! Ready to spell?", "Hi " + playerName + "! Let\u2019s go!"]
    : ["Welcome back, " + playerName + "!", "Good to see you, " + playerName + "!", "Ready to spell, " + playerName + "?", "Let\u2019s go, " + playerName + "!"];
  var hello = greetings[Math.floor(Math.random() * greetings.length)];
  var helloEl = document.querySelector(".menu-player-hello");
  if (helloEl) helloEl.textContent = hello;
  var nameEl = document.getElementById("menu-player-name");
  if (nameEl) nameEl.textContent = "";
  var avEl = document.getElementById("menu-player-avatar");
  if (avEl) avEl.textContent = playerAvatar || "\uD83D\uDC64";
  updateMissionControlLite();
}

function updateMissionControlLite() {
  if (!playerName) return;
  var totalScoreEl = document.getElementById("mc-total-score");
  var accuracyEl = document.getElementById("mc-accuracy");
  var bestStreakEl = document.getElementById("mc-best-streak");
  var gamesEl = document.getElementById("mc-games-played");
  var recapEl = document.getElementById("mc-weekly-recap");
  var challengeEl = document.getElementById("mc-daily-challenge");
  if (!totalScoreEl || !accuracyEl || !bestStreakEl || !gamesEl || !recapEl || !challengeEl) return;

  totalScoreEl.textContent = "--";
  accuracyEl.textContent = "--";
  bestStreakEl.textContent = "--";
  gamesEl.textContent = "--";
  recapEl.textContent = "Weekly recap loading";
  challengeEl.textContent = "Complete one round with fewer than 3 misses.";

  fetch(groupQS("/api/profile?name=" + encodeURIComponent(playerName)))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      var profile = data.profile || {};
      var stats = getStats();
      var totalScore = Math.max(
        profile.best_easy || 0,
        profile.best_medium || 0,
        profile.best_hard || 0,
        stats.bestEasy || 0,
        stats.bestMedium || 0,
        stats.bestHard || 0
      );
      var games = profile.total_games || stats.totalGames || 0;
      var streakBest = Math.max(profile.best_streak || 0, stats.bestStreak || 0);
      var totalCorrect = profile.total_correct_words || 0;
      var totalAttempted = profile.total_attempted_words || 0;
      var accuracy = totalAttempted > 0 ? Math.round((totalCorrect / totalAttempted) * 100) + "%" : "N/A";

      totalScoreEl.textContent = String(totalScore);
      accuracyEl.textContent = accuracy;
      bestStreakEl.textContent = String(streakBest);
      gamesEl.textContent = String(games);

      if (games === 0) recapEl.textContent = "Start your first run";
      else if (streakBest >= 10) recapEl.textContent = "Streak machine this week";
      else recapEl.textContent = "Keep your streak alive";

      var attemptsLeft = profile.ranked_attempts_left;
      if (attemptsLeft === undefined || attemptsLeft === null) attemptsLeft = 3;
      if (attemptsLeft > 0) {
        challengeEl.textContent = "Ranked challenge: use " + attemptsLeft + " attempt" + (attemptsLeft === 1 ? "" : "s") + " strategically.";
      } else {
        challengeEl.textContent = "Practice challenge: review missed words and aim for 90%+ accuracy.";
      }
    })
    .catch(function() {
      recapEl.textContent = "Offline recap mode";
    });
}

// ==================== ANTI-SNOWBALL: PROGRESSIVE DIFFICULTY ====================
// As a player scores higher, the timer shrinks faster and words get harder
function getAntiSnowballShrink(wordsCorrect) {
  // After 10 words: shrink by 1.5s instead of 1s
  // After 20 words: shrink by 2s
  // After 30 words: shrink by 2.5s
  if (wordsCorrect >= 30) return 2.5;
  if (wordsCorrect >= 20) return 2.0;
  if (wordsCorrect >= 10) return 1.5;
  return RANKED_SHRINK_BY;
}

function getAntiSnowballMinTime(wordsCorrect) {
  // After 20 words: minimum timer drops to 5s
  // After 30 words: drops to 4s
  if (wordsCorrect >= 30) return 4;
  if (wordsCorrect >= 20) return 5;
  return RANKED_TIME_MIN;
}

// ==================== INIT ====================
document.addEventListener("DOMContentLoaded", function() {
  initConfetti();
  initAtmo();
  initBeeFlight();

  // Debounced resize instead of direct
  window.removeEventListener("resize", resizeConfetti);
  window.removeEventListener("resize", resizeAtmo);
  window.addEventListener("resize", debouncedResize);

  // Check if user is already authenticated
  var savedName = localStorage.getItem(lsKey("spelling_bee_name"));
  var isAuth = localStorage.getItem(lsKey("spelling_bee_authenticated")) === "1";

  if (savedName && isAuth) {
    // Already logged in — go straight to menu
    playerName = savedName;
    document.getElementById("player-name").value = savedName;
    playerAvatar = localStorage.getItem(lsKey("spelling_bee_avatar")) || "\uD83D\uDC64";

    _updateMenuBanner(false);
    showScreen("menu-screen");
    updateRankedBadge();
  } else {
    // Show login screen
    showScreen("login-screen");
  }

  // Fetch group info and show label
  fetch(groupQS("/api/group-info"))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      currentGroupLabel = data.label || currentGroup;
      var el = document.getElementById("group-label");
      if (el) { el.textContent = currentGroupLabel; el.style.display = ""; }
      document.title = "Spelling Bee — " + currentGroupLabel;
    }).catch(function() {});

  // Fetch week counts and populate dropdown
  fetch(groupQS("/weeks"))
    .then(function(res) { return res.json(); })
    .then(function(data) {
      weekCounts = data;
      var maxWeeks = Math.max(data.easy, data.medium, data.hard);
      var select = document.getElementById("week-select");
      for (var i = 1; i <= maxWeeks; i++) {
        var opt = document.createElement("option");
        opt.value = i;
        opt.textContent = "Week " + i;
        select.appendChild(opt);
      }
      try {
        var saved = localStorage.getItem(lsKey("spelling_bee_week"));
        if (saved !== null) {
          select.value = saved;
          selectedWeek = parseInt(saved, 10) || 0;
        }
      } catch(e) {}
    })
    .catch(function() {});

  document.getElementById("week-select").addEventListener("change", function() {
    selectedWeek = parseInt(this.value, 10) || 0;
    try { localStorage.setItem(lsKey("spelling_bee_week"), selectedWeek); } catch(e) {}
  });

  // Enter key on login name input
  document.getElementById("login-name-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") loginCheckName();
  });

  // Keyboard support for PIN pad on desktop
  document.addEventListener("keydown", function(e) {
    var pinStep = document.getElementById("login-step-pin");
    if (!pinStep || pinStep.classList.contains("hidden")) return;
    
    // Handle numeric keys (0-9)
    if (e.key >= "0" && e.key <= "9") {
      e.preventDefault();
      loginPinKey(e.key);
    }
    // Handle backspace
    else if (e.key === "Backspace") {
      e.preventDefault();
      loginPinDel();
    }
    // Handle Enter to submit
    else if (e.key === "Enter") {
      e.preventDefault();
      if (_loginPinBuffer.length === 4) {
        loginSubmitPin(_loginPinBuffer);
      }
    }
  });
});
// ==================== UX ENHANCEMENTS ====================

// ---- Haptic Feedback (mobile vibration) ----
function haptic(pattern) {
  try {
    if (navigator.vibrate) navigator.vibrate(pattern);
  } catch(e) {}
}

function hapticCorrect() { haptic(30); }
function hapticWrong() { haptic([50, 30, 50]); }
function hapticStreak() { haptic([20, 10, 20, 10, 40]); }
function hapticGameOver() { haptic([100, 50, 100]); }

// ---- Progressive Score Counter ----
function animateScore(element, from, to, duration) {
  if (!element || from === to) return;
  var start = performance.now();
  var diff = to - from;
  duration = duration || 400;
  
  function tick(now) {
    var elapsed = now - start;
    var progress = Math.min(elapsed / duration, 1);
    // Ease out cubic
    var eased = 1 - Math.pow(1 - progress, 3);
    var current = Math.round(from + diff * eased);
    element.textContent = current;
    
    if (progress < 1) {
      requestAnimationFrame(tick);
    } else {
      element.textContent = to;
      element.classList.add("score-pop");
      setTimeout(function() { element.classList.remove("score-pop"); }, 400);
    }
  }
  requestAnimationFrame(tick);
}

// ---- Skeleton Loader Generator ----
function skeletonRows(count, isDark) {
  var cls = isDark ? "skeleton" : "skeleton-light";
  var html = "";
  for (var i = 0; i < count; i++) {
    html += '<div class="skeleton-row">' +
      '<div class="skeleton-circle ' + cls + '"></div>' +
      '<div class="skeleton-line ' + cls + '" style="width:' + (50 + Math.random() * 40) + '%"></div>' +
      '<div class="skeleton-line-short ' + cls + '"></div>' +
    '</div>';
  }
  return html;
}

// ---- Streak Break Effect ----
function streakBreakEffect() {
  // Screen shake
  var gameScreen = document.getElementById("game-screen");
  if (gameScreen) {
    gameScreen.classList.add("shake");
    setTimeout(function() { gameScreen.classList.remove("shake"); }, 500);
  }
  
  // Red flash overlay
  var flash = document.createElement("div");
  flash.className = "streak-break-flash";
  document.body.appendChild(flash);
  setTimeout(function() { flash.remove(); }, 600);
  
  hapticWrong();
}

// ---- Button Ripple Effect ----
function addRipple(e) {
  var btn = e.currentTarget;
  var rect = btn.getBoundingClientRect();
  var size = Math.max(rect.width, rect.height);
  var x = e.clientX - rect.left - size / 2;
  var y = e.clientY - rect.top - size / 2;
  
  var ripple = document.createElement("span");
  ripple.className = "ripple-effect";
  ripple.style.width = ripple.style.height = size + "px";
  ripple.style.left = x + "px";
  ripple.style.top = y + "px";
  btn.appendChild(ripple);
  
  setTimeout(function() { ripple.remove(); }, 600);
}

// ==================== STUDENT PROFILE POPUP ====================
var classmatesCache = null;
var classmatesCacheWeek = null;

function showStudentProfile(studentName) {
  if (!studentName) return;
  
  // Load classmates data if not cached or week changed
  var currentWeek = document.getElementById("week-label")?.textContent || "";
  if (!classmatesCache || classmatesCacheWeek !== currentWeek) {
    loadClassmatesData();
    // Try again after data loads — only retry once to avoid infinite recursion on fetch failure
    if (!showStudentProfile._retrying) {
      showStudentProfile._retrying = true;
      setTimeout(function() { showStudentProfile._retrying = false; showStudentProfile(studentName); }, 500);
    }
    return;
  }
  
  // Find student in cached data
  var student = classmatesCache.find(s => s.name === studentName);
  if (!student) {
    console.log("Student not found:", studentName);
    return;
  }
  
  // Update popup content
  document.getElementById("profile-popup-avatar").textContent = student.avatar || "👤";
  document.getElementById("profile-popup-name").textContent = student.name;
  
  var teamDisplay = student.team_name || "No Team";
  if (student.team_emoji) {
    teamDisplay = student.team_emoji + " " + teamDisplay;
  }
  document.getElementById("profile-popup-team").textContent = teamDisplay;
  
  document.getElementById("profile-popup-ranked-score").textContent = student.ranked_best || 0;
  document.getElementById("profile-popup-total-games").textContent = student.total_games || 0;
  document.getElementById("profile-popup-best-streak").textContent = student.best_streak || 0;
  document.getElementById("profile-popup-badge-count").textContent = student.badge_count || 0;
  
  // Display badges
  var badgesList = document.getElementById("profile-popup-badges-list");
  if (student.badges && student.badges.length > 0) {
    badgesList.innerHTML = student.badges.map(badge => 
      '<div class="profile-badge">' +
        '<span class="profile-badge-icon">' + badge.icon + '</span>' +
        badge.name +
      '</div>'
    ).join("");
    document.getElementById("profile-popup-badges").style.display = "block";
  } else {
    badgesList.innerHTML = '<div style="color:rgba(255,255,255,0.5);font-size:12px;">No badges earned yet</div>';
    document.getElementById("profile-popup-badges").style.display = "block";
  }
  
  // Show popup
  document.getElementById("profile-popup").style.display = "flex";
}

function closeProfilePopup() {
  document.getElementById("profile-popup").style.display = "none";
}

function loadClassmatesData() {
  fetch(groupQS("/api/classmates"))
    .then(function(r) { return r.json(); })
    .then(function(data) {
      classmatesCache = data.classmates || [];
      classmatesCacheWeek = data.week || "";
    })
    .catch(function(err) {
      console.error("Failed to load classmates data:", err);
      classmatesCache = [];
    });
}

// Make names clickable in leaderboard
function makeLeaderboardNamesClickable() {
  try {
    var leaderboardNames = document.querySelectorAll(".lb-podium-name, .lb-highlight td:nth-child(2)");
    leaderboardNames.forEach(function(nameEl) {
      if (nameEl.textContent && nameEl.textContent !== playerName) {
        nameEl.style.cursor = "pointer";
        nameEl.style.textDecoration = "underline";
        nameEl.style.textDecorationStyle = "dotted";
        nameEl.style.textDecorationColor = "rgba(255,255,255,0.3)";
        nameEl.onclick = function(e) {
          e.stopPropagation();
          showStudentProfile(nameEl.textContent);
        };
      }
    });
  } catch (err) {
    console.error("Error making leaderboard names clickable:", err);
  }
}

// Attach ripple to all interactive buttons
document.addEventListener("DOMContentLoaded", function() {
  var buttons = document.querySelectorAll(".menu-btn, .pin-key, .mode-btn, .submode-btn, .menu-link-btn");
  buttons.forEach(function(btn) {
    btn.addEventListener("click", addRipple);
  });

  // Resume AudioContext AND unlock HTML5 Audio on first user gesture (required for iOS/Chrome/Android)
  var _audioUnlocked = false;
  function _unlockAudio() {
    if (_audioUnlocked) return;
    _audioUnlocked = true;
    try { getAudioCtx(); } catch(e) {}
    // Also unlock HTML5 Audio element for mobile autoplay
    try {
      var silence = new Audio("data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA/+M4wAAAAAAAAAAAAEluZm8AAAAPAAAAAwAAAbAAkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQkJCQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0NDQ0P/////////////////////////////////AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/jOMAAAG9JKAAAAAAANICAAAAATGF2YzU4LjEzAAAAAAAAAAAAAAAAJAAAAAAAAAAAAbCp7QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/+M4wDMaaACAAAAAAAANIAAAAAExBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV");
      silence.play().then(function() { silence.pause(); }).catch(function() {});
    } catch(e) {}
    document.removeEventListener("touchstart", _unlockAudio);
    document.removeEventListener("click", _unlockAudio);
  }
  document.addEventListener("touchstart", _unlockAudio, { once: true });
  document.addEventListener("click", _unlockAudio, { once: true });

  // Restore sfxMuted button state
  var sfxBtn = document.getElementById("sfx-toggle");
  if (sfxBtn) sfxBtn.textContent = sfxMuted ? "🔇" : "🔊";
});

// Cache bust 03/11/2026 17:20:00
