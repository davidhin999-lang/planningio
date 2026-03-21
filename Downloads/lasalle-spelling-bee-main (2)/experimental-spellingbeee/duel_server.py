# ================================================================
#  duel_server.py  —  Online 1v1 Spelling Duel backend
# ================================================================
#
# SETUP (once):
#   pip install flask-socketio eventlet
#
# In your app.py / __init__.py:
#
#   from flask_socketio import SocketIO
#   from duel_server import register_duel_events
#
#   socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")
#
#   # Wire in your existing word-loading function:
#   def get_duel_words(difficulty, week):
#       # return a list of word strings for this difficulty + week
#       # Example using your existing logic:
#       return load_words(difficulty, week)   # whatever your function is called
#
#   register_duel_events(socketio, get_duel_words)
#
#   # Replace app.run() with:
#   if __name__ == "__main__":
#       socketio.run(app, debug=True)
#
# In index.html <head>, add BEFORE your other scripts:
#   <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
# ================================================================

import random
import time
import threading
from flask import request
from flask_socketio import emit, join_room, leave_room

_rooms = {}   # room_code -> room dict

POWERUPS = {
    "freeze":     {"cost": 50, "type": "attack"},
    "scramble":   {"cost": 40, "type": "attack"},
    "time_steal": {"cost": 35, "type": "attack"},
    "x2":         {"cost": 30, "type": "self"},
    "shield":     {"cost": 45, "type": "self"},
    "reveal":     {"cost": 25, "type": "self"},
}

DIFF_MAX_TIME = {"easy": 35, "medium": 25, "hard": 18}

# ── helpers ──────────────────────────────────────────────────────

def _new_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    for _ in range(1000):
        c = "".join(random.choices(chars, k=4))
        if c not in _rooms:
            return c
    raise RuntimeError("Could not generate unique room code")

def _new_player(name):
    return {"name": name, "score": 0, "wins": 0,
            "shield": False, "x2": False, "frozen": False}

def _opp_sid(room, sid):
    for p in room["players"]:
        if p != sid:
            return p
    return None

def _player_summary(room):
    return {k: {"name": v["name"], "score": v["score"], "wins": v["wins"]}
            for k, v in room["players"].items()}

def _score_update_payload(room):
    return {"players": {k: {"score": v["score"], "wins": v["wins"]}
                        for k, v in room["players"].items()}}

# ── registration ─────────────────────────────────────────────────

def register_duel_events(socketio, get_words_fn):
    """
    socketio     : your Flask-SocketIO instance
    get_words_fn : callable(difficulty: str, week: int) -> list[str]
    """

    # ── Room creation ────────────────────────────────────────────

    @socketio.on("duel_create_room")
    def on_create(data):
        sid  = request.sid
        code = _new_code()
        diff = data.get("difficulty", "easy")
        _rooms[code] = {
            "code":          code,
            "host":          sid,
            "difficulty":    diff,
            "week":          data.get("week", 0),
            "rounds_to_win": int(data.get("rounds_to_win", 3)),
            "max_time":      DIFF_MAX_TIME.get(diff, 30),
            "players":       {sid: _new_player(data.get("name", "Player 1"))},
            "state":         "waiting",   # waiting | countdown | playing | round_over
            "round":         0,
            "word":          "",
            "used":          [],
            "completions":   [],          # [{sid, time, score_earned}]
            "round_start":   0.0,
            "words":         [],
        }
        join_room(code)
        emit("duel_room_created", {"code": code})

    # ── Joining ──────────────────────────────────────────────────

    @socketio.on("duel_join_room")
    def on_join(data):
        sid  = request.sid
        code = data.get("code", "").upper().strip()
        room = _rooms.get(code)

        if not room:
            emit("duel_error", {"message": "Room not found — check the code"}); return
        if room["state"] != "waiting":
            emit("duel_error", {"message": "Game already in progress"}); return
        if len(room["players"]) >= 2:
            emit("duel_error", {"message": "Room is full"}); return

        room["players"][sid] = _new_player(data.get("name", "Player 2"))
        join_room(code)

        names = {k: v["name"] for k, v in room["players"].items()}
        emit("duel_room_joined", {
            "code": code,
            "players": names,
            "difficulty": room["difficulty"],
            "rounds_to_win": room["rounds_to_win"],
        })
        socketio.emit("duel_opponent_joined", {
            "opponent_name": room["players"][sid]["name"],
            "players": names,
        }, to=room["host"])

        # Load words from your app's word source
        try:
            room["words"] = [w.lower() for w in get_words_fn(room["difficulty"], room["week"])]
        except Exception as exc:
            print(f"[duel] word load failed: {exc}")
            room["words"] = ["apple", "banana", "cherry", "dragon", "forest"]

        room["state"] = "countdown"
        socketio.emit("duel_countdown", {"seconds": 3}, to=code)

        threading.Timer(3.6, lambda: _start_round(code) if code in _rooms else None).start()

    # ── Round lifecycle ──────────────────────────────────────────

    def _pick_word(room):
        available = [w for w in room["words"] if w not in room["used"]]
        if not available:
            room["used"] = []
            available = list(room["words"])
        w = random.choice(available)
        room["used"].append(w)
        return w

    def _start_round(code):
        room = _rooms.get(code)
        if not room:
            return
        room["round"]       += 1
        room["completions"]  = []
        room["state"]        = "playing"
        room["word"]         = _pick_word(room)
        room["round_start"]  = time.time()

        for p in room["players"].values():
            p["x2"] = False   # x2 bonus resets each round

        socketio.emit("duel_round_start", {
            "round":         room["round"],
            "word":          room["word"],
            "max_time":      room["max_time"],
            "rounds_to_win": room["rounds_to_win"],
            "players":       _player_summary(room),
        }, to=code)

        # Server-side timeout
        round_num = room["round"]
        max_t     = room["max_time"]
        def _timeout(rn=round_num):
            if (code in _rooms
                    and _rooms[code]["state"] == "playing"
                    and _rooms[code]["round"] == rn):
                _end_round(code, timed_out=True)
        threading.Timer(max_t + 1, _timeout).start()

    def _end_round(code, timed_out=False):
        room = _rooms.get(code)
        if not room or room["state"] != "playing":
            return
        room["state"] = "round_over"

        winner_sid = room["completions"][0]["sid"] if room["completions"] else None
        if winner_sid and winner_sid in room["players"]:
            room["players"][winner_sid]["wins"] += 1

        socketio.emit("duel_round_over", {
            "word":        room["word"],
            "winner_sid":  winner_sid,
            "round":       room["round"],
            "timed_out":   timed_out,
            "completions": room["completions"],
            "players":     _player_summary(room),
        }, to=code)

        # Check for match winner
        for sid, p in room["players"].items():
            if p["wins"] >= room["rounds_to_win"]:
                def _match_over(wsid=sid, wname=p["name"]):
                    if code not in _rooms:
                        return
                    socketio.emit("duel_match_over", {
                        "winner_sid":  wsid,
                        "winner_name": wname,
                        "players":     _player_summary(_rooms[code]),
                    }, to=code)
                    del _rooms[code]
                threading.Timer(3.2, _match_over).start()
                return

        # Otherwise start next round after a pause
        threading.Timer(4.8, lambda: _start_round(code) if code in _rooms else None).start()

    # ── Word completion ──────────────────────────────────────────

    @socketio.on("duel_word_complete")
    def on_complete(data):
        sid  = request.sid
        code = data.get("code")
        room = _rooms.get(code)
        if not room or room["state"] != "playing":
            return
        if sid not in room["players"]:
            return
        if any(c["sid"] == sid for c in room["completions"]):
            return  # already submitted

        submitted = data.get("word", "").lower().replace(" ", "")
        actual    = room["word"].replace(" ", "")
        if submitted != actual:
            emit("duel_invalid_word")
            return

        elapsed   = time.time() - room["round_start"]
        time_left = max(0.0, room["max_time"] - elapsed)
        position  = len(room["completions"]) + 1   # 1 = first, 2 = second
        base      = 100 if position == 1 else 60
        bonus     = round((time_left / room["max_time"]) * 50)
        player    = room["players"][sid]
        earned    = (base + bonus) * (2 if player.get("x2") else 1)
        player["score"] += earned
        player["x2"]     = False

        room["completions"].append({
            "sid": sid, "time": round(elapsed, 2), "score_earned": earned, "position": position,
        })

        socketio.emit("duel_player_complete", {
            "sid":         sid,
            "name":        player["name"],
            "position":    position,
            "score_earned": earned,
            "time":        round(elapsed, 2),
            "players":     _player_summary(room),
        }, to=code)

        # End the round immediately if both players completed
        if len(room["completions"]) >= len(room["players"]):
            _end_round(code)

    # ── Live progress broadcast ──────────────────────────────────

    @socketio.on("duel_progress")
    def on_progress(data):
        sid  = request.sid
        code = data.get("code")
        room = _rooms.get(code)
        if not room:
            return
        opp = _opp_sid(room, sid)
        if opp:
            socketio.emit("duel_opponent_progress", {
                "correct": data.get("correct", 0),
                "total":   data.get("total",   0),
                "pct":     data.get("pct",     0),
            }, to=opp)

    # ── Power-ups ────────────────────────────────────────────────

    @socketio.on("duel_use_powerup")
    def on_powerup(data):
        sid  = request.sid
        code = data.get("code")
        pu   = data.get("type")
        room = _rooms.get(code)
        if not room or room["state"] != "playing":
            return
        if sid not in room["players"] or pu not in POWERUPS:
            return

        player = room["players"][sid]
        cost   = POWERUPS[pu]["cost"]
        if player["score"] < cost:
            emit("duel_powerup_fail", {"reason": "Not enough points"}); return

        opp_sid = _opp_sid(room, sid)
        opp     = room["players"].get(opp_sid)

        # Shield intercepts attack powerups
        if POWERUPS[pu]["type"] == "attack" and opp and opp.get("shield"):
            opp["shield"]    = False
            player["score"] -= cost
            socketio.emit("duel_shield_blocked", {
                "attacker_name": player["name"], "powerup": pu,
            }, to=code)
            socketio.emit("duel_score_update", _score_update_payload(room), to=code)
            return

        player["score"] -= cost

        if pu == "freeze" and opp_sid:
            socketio.emit("duel_powerup_effect", {
                "type": "freeze", "target_sid": opp_sid, "attacker_name": player["name"],
            }, to=code)
            def _unfreeze(target=opp_sid):
                if code in _rooms and target in _rooms[code]["players"]:
                    _rooms[code]["players"][target]["frozen"] = False
                    socketio.emit("duel_unfreeze", {"sid": target}, to=code)
            threading.Timer(3, _unfreeze).start()

        elif pu == "scramble":
            socketio.emit("duel_powerup_effect", {
                "type": "scramble", "target_sid": opp_sid, "attacker_name": player["name"],
            }, to=code)

        elif pu == "time_steal":
            socketio.emit("duel_powerup_effect", {
                "type": "time_steal", "target_sid": opp_sid, "gainer_sid": sid,
                "seconds": 5, "attacker_name": player["name"],
            }, to=code)

        elif pu == "x2":
            player["x2"] = True
            emit("duel_powerup_effect", {"type": "x2", "target_sid": sid})

        elif pu == "shield":
            player["shield"] = True
            emit("duel_powerup_effect", {"type": "shield", "target_sid": sid})

        elif pu == "reveal":
            emit("duel_powerup_effect", {"type": "reveal", "word": room["word"]})

        socketio.emit("duel_score_update", _score_update_payload(room), to=code)

    # ── Disconnect ───────────────────────────────────────────────

    @socketio.on("disconnect")
    def on_disconnect():
        sid = request.sid
        for code, room in list(_rooms.items()):
            if sid in room["players"]:
                opp = _opp_sid(room, sid)
                if opp:
                    socketio.emit("duel_opponent_left", {
                        "name": room["players"][sid]["name"]
                    }, to=opp)
                del _rooms[code]
                break
