// ================================================================
//  online_duel.js  —  Online 1v1 Spelling Duel client
//  Add to index.html just before </body>, AFTER script.js:
//  <script src="/static/online_duel.js"></script>
// ================================================================

// ==================== STATE ====================

var odSocket       = null;
var odRoomCode     = "";
var odMyName       = "";
var odOppName      = "";
var odOppSid       = "";
var odWord         = "";
var odMaxTime      = 30;
var odTimeLeft     = 30;
var odClientTimer  = null;
var odActive       = false;      // round is live

var odInput        = [];         // typed chars, same length as odWord
var odCursor       = 0;
var odFrozen       = false;
var odShieldOn     = false;
var odX2On         = false;
var odComplete     = false;      // I finished this round's word
var odRoundsToWin  = 3;
var odRound        = 0;

var odMyScore      = 0;
var odMyWins       = 0;
var odOppScore     = 0;
var odOppWins      = 0;
var odOppPct       = 0;          // opponent progress 0-100

// Throttle for progress emit (not every keystroke)
var _odProgThrottle = null;

var OD_POWERUPS = {
  freeze:     { emoji: "❄️",  label: "Freeze",     cost: 50, desc: "Lock opponent's keys for 3s" },
  scramble:   { emoji: "💣",  label: "Scramble",   cost: 40, desc: "Wipes their typed letters"   },
  time_steal: { emoji: "⏱️",  label: "Time Steal", cost: 35, desc: "+5s you, -5s them"           },
  x2:         { emoji: "⚡",  label: "Double pts", cost: 30, desc: "2× points for this word"     },
  shield:     { emoji: "🛡️",  label: "Shield",     cost: 45, desc: "Block next attack"           },
  reveal:     { emoji: "🔤",  label: "Reveal",     cost: 25, desc: "Hear the word spelled out"   },
};

// ==================== SOCKET ====================

function odConnect() {
  if (odSocket && odSocket.connected) return;
  console.log("[duel] odConnect called, io available:", typeof io);
  odSocket = io({ transports: ["polling"] });
  console.log("[duel] socket created:", odSocket);

  odSocket.on("connect", function() {
    console.log("[duel] connected sid:", odSocket.id);
  });

  odSocket.on("duel_room_created", function(d) {
    odRoomCode = d.code;
    document.getElementById("od-waiting-code").textContent = d.code;
    document.getElementById("od-waiting-msg").textContent = "Waiting for opponent to join…";
    showScreen("od-waiting-screen");
  });

  odSocket.on("duel_error", function(d) {
    var el = document.getElementById("od-join-error") || document.getElementById("od-create-error");
    if (el) el.textContent = d.message;
  });

  odSocket.on("duel_room_joined", function(d) {
    odRoomCode    = d.code;
    odRoundsToWin = d.rounds_to_win;
    for (var sid in d.players) {
      if (sid !== odSocket.id) { odOppName = d.players[sid]; odOppSid = sid; }
    }
    document.getElementById("od-waiting-code").textContent = d.code;
    document.getElementById("od-waiting-msg").textContent = "Joined! Starting soon…";
    showScreen("od-waiting-screen");
  });

  odSocket.on("duel_opponent_joined", function(d) {
    odOppName = d.opponent_name;
    document.getElementById("od-waiting-msg").textContent = d.opponent_name + " joined! Starting…";
  });

  odSocket.on("duel_countdown", function(d) { odShowCountdown(d.seconds); });

  odSocket.on("duel_round_start", function(d) {
    odWord        = d.word;
    odMaxTime     = d.max_time || 30;
    odRound       = d.round;
    odRoundsToWin = d.rounds_to_win || odRoundsToWin;
    _syncScores(d.players);
    odBeginRound();
  });

  odSocket.on("duel_player_complete", function(d) {
    _syncScores(d.players);
    if (d.sid === odSocket.id) {
      odComplete = true;
      odShowMyComplete(d.position, d.score_earned, d.time);
    } else {
      odOppName = d.name;
      odShowOppComplete(d.position, d.name);
    }
    odRenderPowerups();
  });

  odSocket.on("duel_round_over", function(d) {
    clearInterval(odClientTimer);
    odActive = false;
    _syncScores(d.players);
    odShowRoundResult(d);
  });

  odSocket.on("duel_match_over", function(d) {
    clearInterval(odClientTimer);
    odActive = false;
    _syncScores(d.players);
    odShowMatchOver(d.winner_sid === odSocket.id, d.winner_name, d.players);
  });

  odSocket.on("duel_opponent_progress", function(d) {
    odOppPct = d.pct || 0;
    odUpdateOppBar();
  });

  odSocket.on("duel_powerup_effect",  odApplyEffect);

  odSocket.on("duel_unfreeze", function(d) {
    if (d.sid === odSocket.id) { odFrozen = false; _hideFreezeOverlay(); }
  });

  odSocket.on("duel_shield_blocked", function(d) {
    odShowToast("🛡️ Shield blocked " + d.attacker_name + "'s " + d.powerup + "!");
  });

  odSocket.on("duel_score_update", function(d) {
    _syncScores(d.players);
    odUpdateScores();
    odRenderPowerups();
  });

  odSocket.on("duel_opponent_left", function(d) {
    clearInterval(odClientTimer);
    odActive = false;
    odShowToast("😬 " + (d.name || "Opponent") + " left the arena");
    setTimeout(returnToMenu, 2800);
  });

  odSocket.on("duel_invalid_word", function() {
    odShowToast("⚠️ Word not accepted — try again");
  });

  odSocket.on("disconnect", function(reason) {
    console.log("[duel] disconnected:", reason);
    if (odActive) odShowToast("⚡ Connection lost — reconnecting…");
  });

  odSocket.on("connect_error", function(err) {
    console.log("[duel] connect error:", err.message);
  });
}

function _syncScores(players) {
  if (!players) return;
  for (var sid in players) {
    var p = players[sid];
    if (sid === odSocket.id) { odMyScore = p.score; odMyWins = p.wins; }
    else                     { odOppSid = sid; odOppName = p.name || odOppName;
                               odOppScore = p.score; odOppWins = p.wins; }
  }
}

// ==================== LOBBY — CREATE ====================

function odCreateRoom() {
  var name  = (document.getElementById("od-create-name").value || "").trim();
  var rnd   = parseInt(document.getElementById("od-create-rounds").value) || 3;
  var errEl = document.getElementById("od-create-error");
  if (!name) { if (errEl) errEl.textContent = "Enter your name"; return; }
  if (errEl) errEl.textContent = "";
  odMyName = name;
  // Pick a random difficulty each match for variety
  var diffs = ["easy", "medium", "hard"];
  var diff  = diffs[Math.floor(Math.random() * diffs.length)];
  odConnect();
  if (odSocket.connected) {
    odSocket.emit("duel_create_room", { name: name, difficulty: diff, week: 0, rounds_to_win: rnd });
  } else {
    odSocket.once("connect", function() {
      odSocket.emit("duel_create_room", { name: name, difficulty: diff, week: 0, rounds_to_win: rnd });
    });
  }
}

// ==================== LOBBY — JOIN ====================

function odJoinRoom() {
  var name  = (document.getElementById("od-join-name").value || "").trim();
  var code  = (document.getElementById("od-join-code").value || "").trim().toUpperCase();
  var errEl = document.getElementById("od-join-error");
  if (!name) { if (errEl) errEl.textContent = "Enter your name"; return; }
  if (!code) { if (errEl) errEl.textContent = "Enter the 4-letter room code"; return; }
  if (errEl) errEl.textContent = "";
  odMyName = name;
  odConnect();
  if (odSocket.connected) {
    odSocket.emit("duel_join_room", { name: name, code: code });
  } else {
    odSocket.once("connect", function() {
      odSocket.emit("duel_join_room", { name: name, code: code });
    });
  }
}

// ==================== LOBBY — COPY CODE ====================

function odCopyCode() {
  if (!odRoomCode) return;
  navigator.clipboard.writeText(odRoomCode).catch(function() {});
  odShowToast("📋 Code copied: " + odRoomCode);
}

// ==================== COUNTDOWN ====================

function odShowCountdown(secs) {
  var overlay = document.getElementById("od-countdown-overlay");
  var num     = document.getElementById("od-countdown-num");
  if (!overlay) return;
  overlay.classList.remove("hidden");
  var count = secs;
  num.textContent = count;
  // Countdown sound
  if (typeof ArenaSounds !== 'undefined') ArenaSounds.countdown(count);
  var t = setInterval(function() {
    count--;
    if (count <= 0) {
      clearInterval(t);
      num.textContent = "🎮";
      setTimeout(function() { overlay.classList.add("hidden"); }, 700);
    } else {
      num.textContent = count;
      // Sound for each countdown number
      if (typeof ArenaSounds !== 'undefined') ArenaSounds.countdown(count);
    }
  }, 1000);
}

// ==================== ROUND START ====================

function odBeginRound() {
  // Reset local state
  odInput    = new Array(odWord.length).fill("");
  odCursor   = 0;
  odComplete = false;
  odFrozen   = false;
  odX2On     = false;
  odOppPct   = 0;
  odTimeLeft = odMaxTime;

  _hideFreezeOverlay();
  var cm = document.getElementById("od-complete-msg");
  if (cm) { cm.className = "od-complete-msg hidden"; cm.textContent = ""; }
  var om = document.getElementById("od-opp-complete-msg");
  if (om) { om.className = "od-opp-msg hidden"; om.textContent = ""; }
  var ro = document.getElementById("od-round-overlay");
  if (ro) ro.classList.add("hidden");

  showScreen("od-game-screen");
  document.getElementById("od-my-name-hdr").textContent  = odMyName;
  document.getElementById("od-opp-name-hdr").textContent = odOppName;
  odUpdateScores();
  odUpdateRoundLabel();
  odRenderBoxes();
  odUpdateOppBar();
  odRenderPowerups();
  odUpdateTimer();

  // Play word audio and fetch image
  if (typeof playTTS === "function") {
    playTTS("/speak/" + encodeURIComponent(odWord), null, null);
  }
  odFetchWordImage();
  // Round start magical sound
  if (typeof ArenaSounds !== 'undefined') ArenaSounds.roundStart();

  // Client-side visual timer (server is authoritative for scoring)
  clearInterval(odClientTimer);
  odActive = true;
  odClientTimer = setInterval(function() {
    if (!odActive) { clearInterval(odClientTimer); return; }
    odTimeLeft--;
    odUpdateTimer();
    if (odTimeLeft <= 0) clearInterval(odClientTimer);
  }, 1000);
}

// ==================== TYPING ENGINE ====================

document.addEventListener("keydown", function(e) {
  if (!odActive) return;
  var screen = document.getElementById("od-game-screen");
  if (!screen || screen.classList.contains("hidden")) return;
  if (odFrozen) return;
  if (e.key === "Backspace") { e.preventDefault(); odBackspace(); }
  else if (/^[a-zA-Z]$/.test(e.key)) { e.preventDefault(); odType(e.key.toLowerCase()); }
}, true);

function odType(letter) {
  if (!odActive || odFrozen || odComplete) return;
  // Magical typing sound
  if (typeof ArenaSounds !== 'undefined') ArenaSounds.type();
  // Advance cursor past spaces
  while (odCursor < odWord.length && odWord[odCursor] === " ") {
    odInput[odCursor] = " "; odCursor++;
  }
  if (odCursor >= odWord.length) return;
  odInput[odCursor] = letter;
  odCursor++;
  while (odCursor < odWord.length && odWord[odCursor] === " ") {
    odInput[odCursor] = " "; odCursor++;
  }
  odRenderBoxes();
  _scheduleProgress();
  odCheckComplete();
}

function odBackspace() {
  if (!odActive || odFrozen || odComplete) return;
  if (odCursor <= 0) return;
  // Backspace sound
  if (typeof ArenaSounds !== 'undefined') ArenaSounds.backspace();
  odCursor--;
  while (odCursor > 0 && odWord[odCursor] === " ") odCursor--;
  odInput[odCursor] = "";
  odRenderBoxes();
  _scheduleProgress();
}

function odCheckComplete() {
  for (var i = 0; i < odWord.length; i++) {
    if (odWord[i] === " ") continue;
    if (!odInput[i] || odInput[i] !== odWord[i]) return;
  }
  // All letters correct — submit to server
  var typed = odInput.join("");
  odSocket.emit("duel_word_complete", { code: odRoomCode, word: typed });
}

function _scheduleProgress() {
  if (_odProgThrottle) return;
  _odProgThrottle = setTimeout(function() {
    _odProgThrottle = null;
    _emitProgress();
  }, 120);
}

function _emitProgress() {
  if (!odSocket || !odRoomCode) return;
  var correct = 0, total = 0;
  for (var i = 0; i < odWord.length; i++) {
    if (odWord[i] === " ") continue;
    total++;
    if (odInput[i] === odWord[i]) correct++;
  }
  var pct = total > 0 ? Math.round((correct / total) * 100) : 0;
  odSocket.emit("duel_progress", { code: odRoomCode, correct: correct, total: total, pct: pct });
}

// ==================== BOXES ====================

function odRenderBoxes() {
  var container = document.getElementById("od-word-boxes");
  if (!container) return;
  container.innerHTML = "";

  // Scale box size based on word length
  var letterCount = odWord.replace(/ /g, "").length;
  var boxSize = letterCount <= 6 ? 58 : letterCount <= 9 ? 50 : letterCount <= 12 ? 42 : 36;

  for (var i = 0; i < odWord.length; i++) {
    if (odWord[i] === " ") {
      var sp = document.createElement("div");
      sp.className = "od-spacer";
      sp.style.width = "18px";
      container.appendChild(sp);
      continue;
    }
    var box = document.createElement("div");
    box.className = "od-box";
    box.style.width = box.style.height = boxSize + "px";
    box.style.fontSize = Math.round(boxSize * 0.52) + "px";

    var ch = odInput[i];
    if (ch && ch !== " ") {
      box.textContent = ch.toUpperCase();
      box.classList.add(ch === odWord[i] ? "od-correct" : "od-wrong");
    }
    if (i === odCursor && !odComplete) box.classList.add("od-cursor");

    // Tap to move cursor (mobile)
    (function(idx) {
      box.addEventListener("click", function() { odCursor = idx; odRenderBoxes(); });
    })(i);

    container.appendChild(box);
  }
}

// ==================== SOFT KEYBOARD (mobile) ====================

function odBuildSoftKb() {
  var kb = document.getElementById("od-soft-kb");
  if (!kb) return;
  kb.innerHTML = "";
  [["q","w","e","r","t","y","u","i","o","p"],
   ["a","s","d","f","g","h","j","k","l"],
   ["z","x","c","v","b","n","m","⌫"]].forEach(function(row) {
    var rowDiv = document.createElement("div");
    rowDiv.className = "od-soft-row";
    row.forEach(function(ch) {
      var btn = document.createElement("button");
      btn.className = "od-soft-key" + (ch === "⌫" ? " od-soft-bs" : "");
      btn.textContent = ch;
      btn.setAttribute("tabindex", "-1");
      btn.addEventListener("mousedown", function(e) { e.preventDefault(); });
      btn.addEventListener("touchstart", function(e) {
        e.preventDefault();
        if (ch === "⌫") odBackspace(); else odType(ch);
        btn.classList.add("od-key-tap");
        setTimeout(function() { btn.classList.remove("od-key-tap"); }, 100);
      }, { passive: false });
      btn.addEventListener("click", function() {
        if (ch === "⌫") odBackspace(); else odType(ch);
      });
      rowDiv.appendChild(btn);
    });
    kb.appendChild(rowDiv);
  });
}

document.addEventListener("DOMContentLoaded", odBuildSoftKb);

// ==================== POWER-UPS ====================

function odRenderPowerups() {
  var left  = document.getElementById("od-pu-left");
  var right = document.getElementById("od-pu-right");
  if (!left || !right) return;
  left.innerHTML = "";
  right.innerHTML = "";
  var keys = Object.keys(OD_POWERUPS);
  keys.forEach(function(key, idx) {
    var pu     = OD_POWERUPS[key];
    var afford = odMyScore >= pu.cost;
    var btn    = document.createElement("button");
    btn.className = "od-pu" + (afford ? "" : " od-pu-broke");
    btn.disabled  = !afford;
    btn.title     = pu.desc + " (" + pu.cost + " pts)";
    btn.innerHTML = '<span class="od-pu-em">' + pu.emoji + '</span>'
                  + '<span class="od-pu-co">' + pu.cost + '</span>';
    btn.addEventListener("click", function() { odUsePowerup(key); });
    // First half on left, second half on right
    if (idx < Math.ceil(keys.length / 2)) left.appendChild(btn);
    else right.appendChild(btn);
  });
}

function odUsePowerup(type) {
  if (!odSocket || !odRoomCode || !odActive) return;
  if (odMyScore < OD_POWERUPS[type].cost) return;
  // Power-up activation sound
  if (typeof ArenaSounds !== 'undefined') {
    if (type === 'freeze') ArenaSounds.freeze();
    else if (type === 'shield') ArenaSounds.shield();
    else ArenaSounds.powerUp();
  }
  odSocket.emit("duel_use_powerup", { code: odRoomCode, type: type });
}

function odApplyEffect(d) {
  var type   = d.type;
  var iAmTarget = d.target_sid === odSocket.id;

  if (type === "freeze") {
    if (iAmTarget) {
      odFrozen = true;
      var ov = document.getElementById("od-frozen-overlay");
      if (ov) {
        ov.querySelector(".od-frozen-msg").textContent = "❄️ " + (d.attacker_name || "Opponent") + " froze you!";
        ov.classList.remove("hidden");
      }
    } else { odShowToast("❄️ Frozen " + odOppName + " for 3s!"); }

  } else if (type === "scramble") {
    if (iAmTarget) {
      odInput  = new Array(odWord.length).fill("");
      odCursor = 0;
      odRenderBoxes();
      odShowToast("💣 " + (d.attacker_name || "Opponent") + " wiped your input!");
    } else { odShowToast("💣 Scrambled " + odOppName + "'s letters!"); }

  } else if (type === "time_steal") {
    if (iAmTarget) {
      odTimeLeft = Math.max(0, odTimeLeft - 5);
      odShowToast("⏱️ −5 seconds!");
    } else {
      odTimeLeft = Math.min(odMaxTime + 10, odTimeLeft + 5);
      odShowToast("⏱️ +5 seconds!");
    }
    odUpdateTimer();

  } else if (type === "x2") {
    odX2On = true;
    var badge = document.getElementById("od-x2-badge");
    if (badge) badge.classList.remove("hidden");
    odShowToast("⚡ Double points active this word!");

  } else if (type === "shield") {
    odShieldOn = true;
    var sbadge = document.getElementById("od-shield-badge");
    if (sbadge) sbadge.classList.remove("hidden");
    odShowToast("🛡️ Shield active — next attack blocked!");

  } else if (type === "reveal") {
    if (typeof playTTS === "function") {
      playTTS("/spell/" + encodeURIComponent(odWord), null, null);
    }
    odShowToast("🔤 Word spelled out!");
  }
}

function _hideFreezeOverlay() {
  var ov = document.getElementById("od-frozen-overlay");
  if (ov) ov.classList.add("hidden");
}

// ==================== UI HELPERS ====================

function odUpdateTimer() {
  var el = document.getElementById("od-timer");
  if (!el) return;
  var t = Math.max(0, odTimeLeft);
  el.textContent = t;
  el.className = "od-timer";
  var pct = t / odMaxTime;
  if (pct <= 0.2) el.classList.add("od-timer-urgent");
  else if (pct <= 0.4) el.classList.add("od-timer-warn");
}

function odUpdateScores() {
  var mySc  = document.getElementById("od-my-score");
  var oppSc = document.getElementById("od-opp-score");
  var myWin = document.getElementById("od-my-wins");
  var oppWin= document.getElementById("od-opp-wins");
  if (mySc)  mySc.textContent  = odMyScore;
  if (oppSc) oppSc.textContent = odOppScore;
  if (myWin) myWin.innerHTML   = _pipHtml(odMyWins,  odRoundsToWin);
  if (oppWin)oppWin.innerHTML  = _pipHtml(odOppWins, odRoundsToWin);
}

function _pipHtml(wins, total) {
  var html = "";
  for (var i = 0; i < total; i++) {
    html += '<span class="od-pip' + (i < wins ? " od-pip-on" : "") + '"></span>';
  }
  return html;
}

function odUpdateRoundLabel() {
  var el = document.getElementById("od-round-label");
  if (el) el.textContent = "ROUND " + odRound;
}

function odFetchWordImage() {
  var img = document.getElementById("od-word-img");
  if (!img || !odWord) return;
  // Use existing image endpoint
  fetch("/image/" + encodeURIComponent(odWord))
    .then(r => r.json())
    .then(d => {
      if (d.url) {
        img.onload  = function() { img.classList.add("visible"); };
        img.onerror = function() { img.classList.remove("visible"); };
        img.classList.remove("visible");
        img.src = d.url;
      } else if (d.emoji) {
        // Show emoji as text overlay if no image
        var emojiDiv = document.getElementById("od-word-emoji");
        if (!emojiDiv) {
          emojiDiv = document.createElement("div");
          emojiDiv.id = "od-word-emoji";
          emojiDiv.style.cssText = "font-size:48px;text-align:center;line-height:68px;";
          img.parentNode.insertBefore(emojiDiv, img);
        }
        emojiDiv.textContent = d.emoji;
        emojiDiv.style.display = "block";
        img.style.display = "none";
      }
    })
    .catch(() => {
      img.classList.remove("visible");
    });
}

function odUpdateOppBar() {
  var bar = document.getElementById("od-opp-bar-fill");
  var lbl = document.getElementById("od-opp-bar-pct");
  if (bar) bar.style.width = odOppPct + "%";
  if (lbl) lbl.textContent = odOppPct + "%";
}

function odShowMyComplete(pos, earned, secs) {
  odComplete = true;
  var el = document.getElementById("od-complete-msg");
  if (!el) return;
  el.className = "od-complete-msg od-complete-" + (pos === 1 ? "first" : "second");
  el.innerHTML = pos === 1
    ? "🏆 First! +" + earned + " pts"
    : "✓ Done! +" + earned + " pts";
  // Magical completion sound
  if (typeof ArenaSounds !== 'undefined') ArenaSounds.correct();
  // Victory particles
  if (typeof ArenaParticles !== 'undefined') {
    var rect = el.getBoundingClientRect();
    ArenaParticles.burst(rect.left + rect.width/2, rect.top + rect.height/2, 6, '✨', '#d4a017');
  }
  // Clear x2 badge
  var badge = document.getElementById("od-x2-badge");
  if (badge) badge.classList.add("hidden");
  if (typeof sfxComplete === "function") sfxComplete();
  if (pos === 1 && typeof launchConfetti === "function") launchConfetti(55);
}

function odShowOppComplete(pos, name) {
  var el = document.getElementById("od-opp-complete-msg");
  if (!el) return;
  el.className = "od-opp-msg" + (pos === 1 ? " od-opp-first" : "");
  el.textContent = pos === 1 ? "🏆 " + name + " finished first!" : name + " also finished!";
}

function odShowRoundResult(d) {
  var overlay = document.getElementById("od-round-overlay");
  if (!overlay) return;

  var iWon   = d.winner_sid === odSocket.id;
  var noWin  = !d.winner_sid;
  var emoji  = noWin ? "⌛" : (iWon ? "🏆" : "😤");
  var title  = noWin
    ? "Time's up! No one finished."
    : (iWon ? "You won this round!" : odOppName + " won this round!");

  document.getElementById("od-result-emoji").textContent = emoji;
  document.getElementById("od-result-title").textContent = title;
  document.getElementById("od-result-word").textContent  = "Word: " + odWord.toUpperCase();

  var html = "";
  for (var sid in d.players) {
    var p    = d.players[sid];
    var isMe = sid === odSocket.id;
    html += '<div class="od-result-row' + (isMe ? " od-result-me" : "") + '">'
          + '<span>' + escapeHtml(p.name) + (isMe ? " (you)" : "") + '</span>'
          + '<span>' + p.wins + " wins · " + p.score + " pts</span>"
          + '</div>';
  }
  document.getElementById("od-result-scores").innerHTML = html;
  overlay.classList.remove("hidden");
  // Hides automatically when next duel_round_start arrives
}

function odShowMatchOver(iWon, winnerName, players) {
  showScreen("od-over-screen");
  document.getElementById("od-over-title").textContent = iWon ? "🏆 You win!" : "😔 " + escapeHtml(winnerName) + " wins!";
  // Victory/defeat sound
  if (typeof ArenaSounds !== 'undefined') {
    if (iWon) ArenaSounds.victory();
    else ArenaSounds.defeat();
  }
  var html = "";
  for (var sid in players) {
    var p    = players[sid];
    var isMe = sid === odSocket.id;
    html += '<div class="od-final-row' + (isMe ? " od-final-me" : "") + '">'
          + '<span>' + escapeHtml(p.name) + (isMe ? " 👈" : "") + '</span>'
          + '<span>' + p.wins + " rounds · " + p.score + " pts</span>"
          + '</div>';
  }
  document.getElementById("od-final-scores").innerHTML = html;
  if (iWon && typeof launchConfetti === "function") launchConfetti(200);
  // Victory particles
  if (iWon && typeof ArenaParticles !== 'undefined') {
    var title = document.getElementById("od-over-title");
    var rect = title.getBoundingClientRect();
    ArenaParticles.burst(rect.left + rect.width/2, rect.top + rect.height/2, 12, '🏆', '#d4a017');
  }
}

// ==================== TOAST ====================

function odShowToast(msg) {
  var t = document.getElementById("od-toast");
  if (!t) return;
  t.textContent = msg;
  t.className = "od-toast";
  clearTimeout(t._tid);
  t._tid = setTimeout(function() {
    t.classList.add("od-toast-out");
    setTimeout(function() { t.className = "od-toast hidden"; }, 380);
  }, 2400);
}

// ==================== QUIT ====================

function odConfirmQuit() {
  odActive = false;
  clearInterval(odClientTimer);
  if (confirm("Leave the duel? Your opponent wins by default.")) {
    if (odSocket) odSocket.disconnect();
    returnToMenu();
  } else {
    odActive = true;
  }
}

// ==================== PLAY AGAIN ====================

function odPlayAgain() {
  if (odSocket) odSocket.disconnect();
  odSocket = null;
  showScreen("od-lobby-screen");
}
