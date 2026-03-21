import os
# Fix Firestore gRPC hanging on Vercel serverless — disable gRPC before any imports
if os.environ.get("VERCEL"):
    os.environ["GRPC_DNS_RESOLVER"] = "native"
    os.environ["GRPC_POLL_STRATEGY"] = "poll"
    os.environ["GOOGLE_CLOUD_DISABLE_GRPC"] = "true"

from flask import Flask, render_template, jsonify, request, send_file, session, redirect, url_for
from flask_socketio import SocketIO
from urllib.parse import unquote
import hashlib
from datetime import datetime, timezone
import edge_tts
import asyncio
import io
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
import json
import requests as http_requests
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore
# Google Cloud TTS removed — too heavy for Vercel serverless (50MB+ with gRPC).
# Using ElevenLabs API (lightweight HTTP) + Edge TTS as fallback chain.
GOOGLE_TTS_AVAILABLE = False

# Force Firestore to use REST instead of gRPC on Vercel
if os.environ.get("VERCEL"):
    try:
        from google.cloud.firestore_v1 import _helpers
        _helpers.USE_GRPC = False
        print("[DB] Disabled gRPC for Firestore (Vercel)")
    except (ImportError, AttributeError) as e:
        print(f"[DB] Could not disable gRPC: {e}")
from words import (EASY_WORDS, MEDIUM_WORDS, HARD_WORDS, PHRASE_WORDS, WORD_IMAGES, WORD_SENTENCES,
                    get_words_for_week, get_week_count, get_ranked_words, get_bomb_words, get_bomb_words_by_difficulty,
                    VALID_GROUPS, GROUP_CONFIG, get_group_label, format_spelling_text)
import time
import uuid
import threading

load_dotenv()

# ==================== IN-MEMORY CACHE (reduces Firestore reads by ~90%) ====================
_cache = {}
_cache_lock = threading.Lock()

def cache_get(key):
    """Return cached value or None if expired/missing."""
    with _cache_lock:
        entry = _cache.get(key)
        if entry and time.time() < entry["expires"]:
            return entry["data"]
        if entry:
            del _cache[key]
    return None

def cache_set(key, data, ttl=30):
    """Cache data for `ttl` seconds."""
    with _cache_lock:
        _cache[key] = {"data": data, "expires": time.time() + ttl}

def cache_invalidate(*prefixes):
    """Remove cache entries whose keys start with any of the given prefixes."""
    with _cache_lock:
        to_del = [k for k in _cache if any(k.startswith(p) for p in prefixes)]
        for k in to_del:
            del _cache[k]

CACHE_TTL_LEADERBOARD = 600
CACHE_TTL_TEAMS = 600
CACHE_TTL_PROFILES = 300
CACHE_TTL_TEAM_LB = 60    # Short TTL so game-over screen shows fresh scores
CACHE_TTL_MEMBERS = 60    # Short TTL so team member scores update quickly
CACHE_TTL_WEEK_SCORES = 600

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, "static"), template_folder=os.path.join(BASE_DIR, "templates"))

# Security: Use environment variables if available, fallback to safe defaults
_SECRET_KEY = os.getenv("SECRET_KEY", "spelling-bee-secret-2024-fallback")
app.secret_key = _SECRET_KEY

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading", allow_upgrades=False)

# Admin password: use env var if available, fallback to default
_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "spellingbee2024")
ADMIN_PASSWORD = _ADMIN_PASSWORD
TEAMS_FILE = os.path.join(BASE_DIR, "teams.json")
TEAM_SCORES_FILE = os.path.join(BASE_DIR, "team_scores.json")

# Firebase setup — each group has its own Firebase project with a dedicated key file.
# Key files: firebase-key-group1.json, firebase-key-group2.json, etc.
# Also supports env vars: FIREBASE_CREDENTIALS_GROUP1, FIREBASE_CREDENTIALS_GROUP2, etc.
USE_FIRESTORE = False
db = None
_group_db = {}  # group_name -> firestore.client()

def _init_firebase_app(cred_source, app_name=None):
    """Initialize a Firebase app and return its Firestore client.
    cred_source can be a JSON string, a dict, or a file path."""
    import json as _json
    if isinstance(cred_source, str):
        if os.path.exists(cred_source):
            cred = credentials.Certificate(cred_source)
        else:
            cred_dict = _json.loads(cred_source)
            cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate(cred_source)
    if app_name:
        fb_app = firebase_admin.initialize_app(cred, name=app_name)
    else:
        fb_app = firebase_admin.initialize_app(cred)
    return firestore.client(fb_app)

try:
    _first_app_initialized = False
    for grp in VALID_GROUPS:
        # Try env var first, then key file
        env_key = f"FIREBASE_CREDENTIALS_{grp.upper()}"
        grp_creds = os.getenv(env_key, "")
        key_file = os.path.join(os.path.dirname(__file__), f"firebase-key-{grp}.json")

        source = None
        source_label = None
        if grp_creds:
            source = grp_creds
            source_label = f"env var {env_key}"
        elif os.path.exists(key_file):
            source = key_file
            source_label = f"key file {key_file}"

        if source:
            try:
                if not _first_app_initialized:
                    # First Firebase app is the default app
                    client = _init_firebase_app(source)
                    _first_app_initialized = True
                    db = client
                else:
                    client = _init_firebase_app(source, app_name=f"fb_{grp}")
                _group_db[grp] = client
                USE_FIRESTORE = True
                print(f"[DB] Firebase for '{grp}' initialized ({source_label})")
            except Exception as e:
                print(f"[DB] Firebase init error for '{grp}': {e}")
        else:
            print(f"[DB] No Firebase credentials for '{grp}' — skipped")
except Exception as e:
    print(f"[DB] Firebase init error: {e}")

# Tournament now has its own Firebase project — no mapping needed

LEADERBOARD_FILE = os.path.join(os.path.dirname(__file__), "leaderboard.json")


def _get_db(group):
    """Return the Firestore client for the given group.
    Groups with their own Firebase project get a dedicated client.
    Others fall back to the default client."""
    return _group_db.get(group, db)


def get_group():
    """Extract group from request args or JSON body. Falls back to 'group1'.
    IMPORTANT: uses force=True so the cached parse matches route handlers."""
    g = request.args.get("group", "")
    if not g:
        try:
            data = request.get_json(silent=True, force=True) or {}
            g = data.get("group", "")
        except Exception:
            pass
    g = (g or "").strip().lower()
    if g not in VALID_GROUPS:
        g = "group1"
    return g


def get_admin_group():
    """Get group for admin endpoints - respects URL lock if present."""
    # Check if admin is locked to a specific group via URL parameter
    locked_group = request.args.get("locked_group", "").strip().lower()
    if locked_group and locked_group in VALID_GROUPS:
        return locked_group
    # Fall back to regular group detection
    return get_group()


# Groups that share another group's Firebase project need prefixed collections
# to isolate their data. Groups with their own Firebase project use unprefixed names.
# Tournament shares group1's Firebase and uses prefixed collections (e.g., tournament_teams, tournament_leaderboard)
_SHARED_DB_GROUPS = {"tournament"}

def gcol(group, collection_name):
    """Return a Firestore collection reference for the given group.
    Groups sharing a Firebase project get prefixed collection names for isolation.
    Groups with their own Firebase project use root collections directly."""
    group_db = _get_db(group)
    if group in _SHARED_DB_GROUPS:
        return group_db.collection(f"{group}_{collection_name}")
    return group_db.collection(collection_name)



def _fs_call(func, default=None, timeout=5):
    """Run a Firestore operation with a timeout. Returns default on timeout/error.
    Prevents the app from hanging when Firestore is quota-exhausted or unavailable."""
    result = [default]
    error = [None]
    def target():
        try:
            result[0] = func()
        except Exception as e:
            error[0] = e
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        print(f"[Firestore] Timeout after {timeout}s")
        return default
    if error[0]:
        print(f"[Firestore] Error: {error[0]}")
        return default
    return result[0]


def _fs_write(func, timeout=5):
    """Run a Firestore write with timeout. Silently fails on timeout/error."""
    def target():
        try:
            func()
        except Exception as e:
            print(f"[Firestore] Write error: {e}")
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        print(f"[Firestore] Write timeout after {timeout}s")


# TTS config — ElevenLabs primary, Edge TTS fallback
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Bella
ELEVENLABS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

# Use consistent voice for all TTS to avoid gender changes
VOICE_NORMAL = "en-US-JennyNeural"  # Clear female voice
VOICE_SLOW = "en-US-JennyNeural"   # Same voice for consistency
VOICE_SPELL = "en-US-JennyNeural"  # Same voice for spelling
print("[TTS] Using ElevenLabs primary, Edge TTS fallback")
print("[TTS] Voice consistency: en-US-JennyNeural for all modes")

# Check if ElevenLabs is available
ELEVENLABS_AVAILABLE = bool(ELEVENLABS_API_KEY)
print(f"[TTS] ElevenLabs available: {ELEVENLABS_AVAILABLE}")



image_cache = {}
WIKI_HEADERS = {"User-Agent": "SpellingBeeApp/1.0 (educational; contact@example.com)"}




# Load pre-fetched Pixabay image URLs
PIXABAY_IMAGES = {}
_pixabay_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "word_images.json")
if os.path.exists(_pixabay_path):
    with open(_pixabay_path, "r", encoding="utf-8") as _f:
        PIXABAY_IMAGES = json.load(_f)
    print(f"[Images] Loaded {len(PIXABAY_IMAGES)} pre-fetched image entries")


# Pre-cached audio directory (committed to repo, works on Vercel read-only filesystem)
PRECACHED_AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")

# Dynamic audio cache directory — use /tmp on Vercel (read-only filesystem)
import tempfile
if os.environ.get("VERCEL"):
    AUDIO_CACHE_DIR = os.path.join(tempfile.gettempdir(), "audio_cache")
else:
    AUDIO_CACHE_DIR = os.path.join(os.path.dirname(__file__), "audio_cache")
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)


def get_precached_audio(word, suffix=""):
    safe_name = word.replace(" ", "_").lower()
    path = os.path.join(PRECACHED_AUDIO_DIR, f"{safe_name}{suffix}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 100:
        print(f"[Precache] Hit: {path}")
        return path
    return None


def edge_cache_key(text, voice, rate):
    raw = f"edge_{voice}_{text}_{rate}"
    return hashlib.md5(raw.encode()).hexdigest() + ".mp3"


def cache_and_return_edge(text, voice, rate):
    """Generate Edge TTS audio. Returns BytesIO object or None on failure."""
    try:
        print(f"[Edge TTS] Generating: {text[:30]}")
        audio = run_async(generate_speech_edge(text, voice, rate=rate))
        if audio:
            # Try to cache to disk if possible (Vercel /tmp is writable)
            try:
                path = os.path.join(AUDIO_CACHE_DIR, edge_cache_key(text, voice, rate))
                with open(path, "wb") as f:
                    audio.seek(0)
                    f.write(audio.read())
                audio.seek(0)
                print(f"[Edge TTS] Success (cached): {text[:30]}")
            except Exception as e:
                # If caching fails, still return the audio in memory
                audio.seek(0)
                print(f"[Edge TTS] Success (memory): {text[:30]} (cache failed: {e})")
            return audio
    except Exception as e:
        print(f"[Edge TTS] Generation failed: {e}")
    return None


def cache_and_return_elevenlabs(text, voice_id=None, stability=0.75, similarity_boost=0.75):
    """Generate ElevenLabs TTS audio. Returns BytesIO object or None on failure."""
    if not ELEVENLABS_AVAILABLE:
        return None
    
    print(f"[ElevenLabs] Generating: {text[:30]}")
    try:
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        response = http_requests.post(ELEVENLABS_URL, json=data, headers=headers)
        response.raise_for_status()
        
        audio = io.BytesIO(response.content)
        
        # Try to cache to disk if possible (Vercel /tmp is writable)
        try:
            cache_key = f"elevenlabs_{hash(text)}_{voice_id}_{stability}_{similarity_boost}"
            path = os.path.join(AUDIO_CACHE_DIR, cache_key + ".mp3")
            with open(path, "wb") as f:
                f.write(response.content)
            print(f"[ElevenLabs] Success (cached): {text[:30]}")
        except Exception as e:
            print(f"[ElevenLabs] Success (memory): {text[:30]} (cache failed: {e})")
        
        return audio
    except Exception as e:
        print(f"[ElevenLabs] Generation failed: {e}")
        return None


def run_async(coro):
    """Run async coroutine safely in any environment including Vercel serverless."""
    import concurrent.futures
    def _run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(_run)
                return future.result(timeout=15)
        else:
            return _run()
    except Exception:
        return _run()


async def generate_speech_edge(text, voice, rate="+0%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    audio = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio.write(chunk["data"])
    audio.seek(0)
    return audio


def cache_and_return_gtts(text):
    """Generate TTS using gTTS (Google Translate TTS). Synchronous HTTP, no API key needed.
    Returns BytesIO object or None on failure."""
    if not GTTS_AVAILABLE:
        return None
    try:
        print(f"[gTTS] Generating: {text[:30]}")
        tts = gTTS(text=text, lang='en', slow=False)
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        if audio.getbuffer().nbytes > 100:
            print(f"[gTTS] Success: {text[:30]} ({audio.getbuffer().nbytes} bytes)")
            return audio
        print(f"[gTTS] Empty audio for: {text[:30]}")
        return None
    except Exception as e:
        print(f"[gTTS] Generation failed: {e}")
        return None





# ==================== TEAMS HELPERS ====================

def get_week_key():
    """Return ISO year-week string e.g. '2026-W08'.
    Uses UTC-6 (Central Mexico) so the week boundary matches local time."""
    from datetime import timedelta
    now = datetime.now(timezone.utc) - timedelta(hours=6)
    return now.strftime("%G-W%V")


# ---- Teams CRUD (Firestore-first, JSON fallback) ----

def load_teams(group="group1"):
    ck = f"teams:{group}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    if USE_FIRESTORE:
        def _load_teams():
            docs = gcol(group, "teams").order_by("created_at").stream()
            return [dict(d.to_dict(), id=d.id) for d in docs]
        result = _fs_call(_load_teams)
        if result is not None:
            cache_set(ck, result, CACHE_TTL_TEAMS)
            return result
    if os.path.exists(TEAMS_FILE):
        try:
            with open(TEAMS_FILE, "r", encoding="utf-8") as f:
                result = json.load(f)
                cache_set(ck, result, CACHE_TTL_TEAMS)
                return result
        except Exception:
            pass
    return []


def save_team_fs(team, group="group1"):
    """Upsert a team dict into Firestore."""
    cache_invalidate("teams:", "team_lb:")
    if USE_FIRESTORE:
        def _save():
            tid = team["id"]
            data = {k: v for k, v in team.items() if k != "id"}
            if "created_at" not in data:
                data["created_at"] = firestore.SERVER_TIMESTAMP
            gcol(group, "teams").document(tid).set(data)
        _fs_write(_save)
        return True
    # JSON fallback
    teams = load_teams(group)
    found = False
    for i, t in enumerate(teams):
        if t["id"] == team["id"]:
            teams[i] = team
            found = True
            break
    if not found:
        teams.append(team)
    with open(TEAMS_FILE, "w", encoding="utf-8") as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    return True


def delete_team_fs(team_id, group="group1"):
    cache_invalidate("teams:", "team_lb:")
    if USE_FIRESTORE:
        def _del():
            gcol(group, "teams").document(team_id).delete()
            week = get_week_key()
            gcol(group, "team_scores").document(week).collection("scores").document(team_id).delete()
        _fs_write(_del)
        return True
    # JSON fallback
    teams = load_teams(group)
    teams = [t for t in teams if t["id"] != team_id]
    with open(TEAMS_FILE, "w", encoding="utf-8") as f:
        json.dump(teams, f, ensure_ascii=False, indent=2)
    return True


# ---- Team scores (Firestore-first, JSON fallback) ----

def add_team_score(team_id, team_name, score_delta, group="group1"):
    """Atomically increment team's weekly score."""
    cache_invalidate("week_scores:", "team_lb:", "all_scores:")
    week = get_week_key()
    if USE_FIRESTORE:
        def _add():
            ref = gcol(group, "team_scores").document(week).collection("scores").document(team_id)
            ref.set({
                "team_name": team_name,
                "weekly_score": firestore.Increment(score_delta),
                "games_played": firestore.Increment(1),
            }, merge=True)
        _fs_write(_add)
        return
    # JSON fallback
    if os.path.exists(TEAM_SCORES_FILE):
        try:
            with open(TEAM_SCORES_FILE, "r", encoding="utf-8") as f:
                scores = json.load(f)
        except Exception:
            scores = {}
    else:
        scores = {}
    if week not in scores:
        scores[week] = {}
    if team_id not in scores[week]:
        scores[week][team_id] = {"team_name": team_name, "weekly_score": 0, "games_played": 0}
    scores[week][team_id]["weekly_score"] += score_delta
    scores[week][team_id]["games_played"] += 1
    scores[week][team_id]["team_name"] = team_name
    with open(TEAM_SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)


def load_week_scores(week, group="group1"):
    ck = f"week_scores:{group}:{week}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    if USE_FIRESTORE:
        def _load_week_scores_data():
            docs = gcol(group, "team_scores").document(week).collection("scores").stream()
            return {d.id: d.to_dict() for d in docs}
        result = _fs_call(_load_week_scores_data)
        if result is not None:
            cache_set(ck, result, CACHE_TTL_WEEK_SCORES)
            return result
    if os.path.exists(TEAM_SCORES_FILE):
        try:
            with open(TEAM_SCORES_FILE, "r", encoding="utf-8") as f:
                result = json.load(f).get(week, {})
                cache_set(ck, result, CACHE_TTL_WEEK_SCORES)
                return result
        except Exception:
            pass
    return {}


def reset_week_scores(week, group="group1"):
    """Clear all scores for a given week (both Firestore and JSON fallback)."""
    cache_invalidate("week_scores:", "team_lb:", "all_scores:", "leaderboard:", f"profile:{group}:")
    
    if USE_FIRESTORE:
        def _reset():
            # Clear team_scores subcollection
            docs = gcol(group, "team_scores").document(week).collection("scores").stream()
            for d in docs:
                d.reference.delete()
            # Clear leaderboard entries
            for diff in ["easy", "medium", "hard"]:
                docs = gcol(group, "leaderboard").document(diff).collection("scores").stream()
                for d in docs:
                    d.reference.delete()
        _fs_write(_reset, timeout=15)
    
    # Also clear JSON fallback
    if os.path.exists(TEAM_SCORES_FILE):
        try:
            with open(TEAM_SCORES_FILE, "r", encoding="utf-8") as f:
                scores = json.load(f)
            scores[week] = {}
            with open(TEAM_SCORES_FILE, "w", encoding="utf-8") as f:
                json.dump(scores, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    # Clear leaderboard JSON file
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


def get_all_week_scores(group="group1"):
    """Return {week: {team_id: {...}}} for all weeks."""
    ck = f"all_scores:{group}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    if USE_FIRESTORE:
        def _load_all_week_scores():
            r = {}
            weeks_docs = gcol(group, "team_scores").stream()
            for wd in weeks_docs:
                week = wd.id
                score_docs = gcol(group, "team_scores").document(week).collection("scores").stream()
                r[week] = {d.id: d.to_dict() for d in score_docs}
            return r
        result = _fs_call(_load_all_week_scores, timeout=8)
        if result is not None:
            cache_set(ck, result, CACHE_TTL_WEEK_SCORES)
            return result
    if os.path.exists(TEAM_SCORES_FILE):
        try:
            with open(TEAM_SCORES_FILE, "r", encoding="utf-8") as f:
                result = json.load(f)
                cache_set(ck, result, CACHE_TTL_WEEK_SCORES)
                return result
        except Exception:
            pass
    return {}


def archive_week_scores(week, group="group1"):
    """Archive current week's scores to score_history collection before reset."""
    if not USE_FIRESTORE:
        return False
    
    def _archive_week_scores_data():
        try:
            # Copy team scores to history
            team_scores = load_week_scores(week, group)
            if team_scores:
                ref = gcol(group, "score_history").document(week)
                ref.set({
                    "team_scores": team_scores,
                    "archived_at": firestore.SERVER_TIMESTAMP,
                    "week": week,
                }, merge=True)
            
            # Copy leaderboard entries to history
            for difficulty in ["easy", "medium", "hard"]:
                docs = gcol(group, "leaderboard").document(difficulty).collection("scores").stream()
                leaderboard_data = {d.id: d.to_dict() for d in docs}
                if leaderboard_data:
                    ref = gcol(group, "score_history").document(week)
                    ref.set({
                        f"leaderboard_{difficulty}": leaderboard_data,
                    }, merge=True)
            
            # Copy team leaderboard to history
            team_lb_docs = gcol(group, "team_leaderboard").stream()
            team_lb_data = {d.id: d.to_dict() for d in team_lb_docs}
            if team_lb_data:
                ref = gcol(group, "score_history").document(week)
                ref.set({"team_leaderboard": team_lb_data}, merge=True)

            # BUG 9 FIX: Save player-level ranked best scores for this week
            rk = f"ranked_best_{week}"
            player_ranked = {}
            prof_docs = gcol(group, "player_profiles").stream()
            for d in prof_docs:
                p = d.to_dict()
                best = p.get(rk, 0)
                if best > 0:
                    player_ranked[d.id] = {
                        "name": p.get("name", d.id),
                        "ranked_best": best,
                        "team_id": p.get("team_id", ""),
                        "team_name": p.get("team_name", ""),
                    }
            if player_ranked:
                ref = gcol(group, "score_history").document(week)
                ref.set({"player_ranked_scores": player_ranked}, merge=True)

            return True
        except Exception as e:
            print(f"[Archive] Error archiving week {week}: {e}")
            return False
    
    return _fs_call(_archive_week_scores_data, default=False, timeout=10)


def get_week_history(group="group1"):
    """Load all archived weeks from score_history."""
    ck = f"week_history:{group}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    
    if not USE_FIRESTORE:
        return {}
    
    def _load_week_history_data():
        history = {}
        docs = gcol(group, "score_history").stream()
        for d in docs:
            data = d.to_dict()
            history[d.id] = {
                "week": d.id,
                "archived_at": data.get("archived_at"),
                "team_scores": data.get("team_scores", {}),
                "leaderboard_easy": data.get("leaderboard_easy", {}),
                "leaderboard_medium": data.get("leaderboard_medium", {}),
                "leaderboard_hard": data.get("leaderboard_hard", {}),
                "team_leaderboard": data.get("team_leaderboard", {}),
                "player_ranked_scores": data.get("player_ranked_scores", {}),
            }
        return history
    
    result = _fs_call(_load_week_history_data, default={}, timeout=10)
    if result:
        cache_set(ck, result, CACHE_TTL_WEEK_SCORES)
    return result or {}


def save_weekly_snapshot(group="group1"):
    """Save current week's scores to history before reset. Called manually or automatically."""
    week = get_week_key()
    cache_invalidate("week_history:")
    return archive_week_scores(week, group)


# ---- Player membership ----

def get_player_team(player_name, group="group1"):
    ck = f"player_team:{group}:{player_name}"
    cached = cache_get(ck)
    if cached is not None:
        return cached if cached != "__none__" else None
    if USE_FIRESTORE:
        def _get_player_team_data():
            doc = gcol(group, "player_teams").document(player_name).get()
            return doc.to_dict() if doc.exists else None
        result = _fs_call(_get_player_team_data)
        cache_set(ck, result if result is not None else "__none__", CACHE_TTL_PROFILES)
        return result
    return None


def set_player_team(player_name, team_id, team_name, team_color, group="group1"):
    cache_invalidate(f"player_team:{group}:{player_name}", f"profile:{group}:{player_name}", "team_lb:", "members:")
    if USE_FIRESTORE:
        def _set_player_team_data():
            gcol(group, "player_teams").document(player_name).set({
                "team_id": team_id,
                "team_name": team_name,
                "team_color": team_color,
                "updated_at": firestore.SERVER_TIMESTAMP,
            })
            gcol(group, "player_profiles").document(player_name).set({
                "team_id": team_id,
                "team_name": team_name,
                "team_color": team_color,
            }, merge=True)
        _fs_write(_set_player_team_data)
        return True
    return False


# ---- Player profiles ----

BADGE_DEFS = [
    {"id": "first_blood",      "name": "First Blood",      "emoji": "\U0001f31f", "desc": "Complete your first ranked game"},
    {"id": "iron_brain",       "name": "Iron Brain",       "emoji": "\U0001f9e0", "desc": "10 correct words in a row"},
    {"id": "speed_runner",     "name": "Speed Runner",     "emoji": "\u26a1",     "desc": "Answer 5 words with time to spare"},
    {"id": "bomb_master",      "name": "Bomb Master",      "emoji": "\U0001f4a3", "desc": "Nail 3 bomb words correctly"},
    {"id": "on_fire",          "name": "On Fire",          "emoji": "\U0001f525", "desc": "Reach \u00d73 streak multiplier"},
    {"id": "precision_king",   "name": "Precision",        "emoji": "\U0001f3af", "desc": "95%+ accuracy in a ranked game"},
    {"id": "centurion",        "name": "Centurion",        "emoji": "\U0001f3c6", "desc": "Score 100+ points in ranked"},
    {"id": "comeback_kid",     "name": "Comeback Kid",     "emoji": "\U0001f4aa", "desc": "Win ranked after losing a life"},
    {"id": "perfect_speller",  "name": "Perfect Speller",  "emoji": "\u2728",     "desc": "5 perfect words in one game"},
    {"id": "team_player",      "name": "Team Player",      "emoji": "\U0001f91d", "desc": "Contribute to your team\u2019s weekly score"},
    {"id": "veteran",          "name": "Veteran",          "emoji": "\U0001f396\ufe0f", "desc": "Use all 3 ranked attempts in a week"},
    {"id": "champion",         "name": "Champion",         "emoji": "\U0001f451", "desc": "Reach #1 on the weekly leaderboard"},
    {"id": "word_warrior",     "name": "Word Warrior",     "emoji": "\u2694\ufe0f", "desc": "Spell 20+ words in a single ranked game"},
    {"id": "half_century",     "name": "Half Century",     "emoji": "\U0001f4af", "desc": "Score 50+ points in ranked"},
    {"id": "double_century",   "name": "Double Century",   "emoji": "\U0001f48e", "desc": "Score 200+ points in ranked"},
    {"id": "survivor",         "name": "Survivor",         "emoji": "\U0001f6e1\ufe0f", "desc": "Finish ranked with all 3 lives"},
    {"id": "night_owl",        "name": "Night Owl",        "emoji": "\U0001f989", "desc": "Play a ranked game after 9 PM"},
    {"id": "early_bird",       "name": "Early Bird",       "emoji": "\U0001f426", "desc": "Play a ranked game before 8 AM"},
    {"id": "streak_master",    "name": "Streak Master",    "emoji": "\U0001f4a5", "desc": "15 correct words in a row"},
    {"id": "bomb_defuser",     "name": "Bomb Defuser",     "emoji": "\U0001f9e8", "desc": "Nail 5 bomb words in one game"},
    {"id": "spelling_legend",  "name": "Spelling Legend",  "emoji": "\U0001f47c", "desc": "Score 300+ points in ranked"},
    {"id": "dedicated",        "name": "Dedicated",        "emoji": "\U0001f4c5", "desc": "Play ranked 3 weeks in a row"},
]


def get_profile(name, group="group1"):
    ck = f"profile:{group}:{name}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    if USE_FIRESTORE:
        def _get_profile_doc_data():
            doc = gcol(group, "player_profiles").document(name).get()
            return doc.to_dict() if doc.exists else {}
        result = _fs_call(_get_profile_doc_data, default={})
        cache_set(ck, result, CACHE_TTL_PROFILES)
        return result
    return {}


def update_profile(name, game_data, group="group1"):
    """Merge a completed game's stats into the player's profile."""
    cache_invalidate(f"profile:{group}:{name}", "leaderboard:", "team_lb:", "members:")
    if not USE_FIRESTORE:
        return
    def _update_profile_data():
        ref = gcol(group, "player_profiles").document(name)
        score = int(game_data.get("score", 0))
        accuracy = float(game_data.get("accuracy", 0))
        streak = int(game_data.get("streak", 0))
        bombs = int(game_data.get("bombs_correct", 0))
        time_bonuses = int(game_data.get("time_bonuses", 0))
        is_ranked = bool(game_data.get("is_ranked", False))
        difficulty = str(game_data.get("difficulty", "easy"))
        team_id = str(game_data.get("team_id", ""))
        team_name = str(game_data.get("team_name", ""))

        doc = ref.get()
        existing = doc.to_dict() if doc.exists else {}

        updates = {
            "name": name,
            "total_games": firestore.Increment(1),
            "total_score": firestore.Increment(score),
            "best_streak": max(existing.get("best_streak", 0), streak),
            "bombs_correct_total": firestore.Increment(bombs),
            "updated_at": firestore.SERVER_TIMESTAMP,
        }

        # Best score per difficulty
        best_key = f"best_{difficulty}"
        if score > existing.get(best_key, 0):
            updates[best_key] = score

        # Cumulative accuracy tracking (general accuracy = total_correct / total_attempted)
        if accuracy > 0:
            words_in_game = max(1, int(game_data.get("words_completed", 0)))
            correct_in_game = int(round(accuracy * words_in_game))
            updates["total_correct_words"] = firestore.Increment(correct_in_game)
            updates["total_attempted_words"] = firestore.Increment(words_in_game)
        # Keep best_accuracy for badge checks
        if accuracy > existing.get("best_accuracy", 0):
            updates["best_accuracy"] = accuracy

        # Ranked games
        if is_ranked:
            updates["ranked_games"] = firestore.Increment(1)
            week = get_week_key()
            rk = f"ranked_best_{week}"
            old_best = existing.get(rk, 0)
            if score > old_best:
                updates[rk] = score
                # Update pre-computed team scores — pass delta (new - old) not full score
                if team_id:
                    try:
                        delta = score - old_best
                        update_team_scores_computed(name, team_id, score, delta, group)
                    except Exception as e:
                        print(f"[TeamComputed] error: {e}")

        # Team
        if team_id:
            updates["team_id"] = team_id
            updates["team_name"] = team_name

        # Badge unlocks
        earned = list(existing.get("badges", []))
        # first_blood: complete first ranked game
        if is_ranked and "first_blood" not in earned:
            earned.append("first_blood")
        if streak >= 10 and "iron_brain" not in earned:
            earned.append("iron_brain")
        
        # Badge checking moved to profile view to reduce Firebase reads
        if bombs >= 3 and "bomb_master" not in earned:
            earned.append("bomb_master")
        if accuracy >= 0.95 and is_ranked and "precision_king" not in earned:
            earned.append("precision_king")
        if game_data.get("reached_x3") and "on_fire" not in earned:
            earned.append("on_fire")
        if time_bonuses >= 3 and "speed_runner" not in earned:
            earned.append("speed_runner")
        if is_ranked and score >= 100 and "centurion" not in earned:
            earned.append("centurion")
        if team_id and score > 0 and "team_player" not in earned:
            earned.append("team_player")
        # veteran: used all 3 ranked attempts this week
        if is_ranked:
            week = get_week_key()
            used_now = get_ranked_attempts(name, week, group)
            if used_now >= 3 and "veteran" not in earned:
                earned.append("veteran")
        # word_warrior: 20+ words in a single ranked game
        words_in_game = int(game_data.get("words_completed", 0))
        if is_ranked and words_in_game >= 20 and "word_warrior" not in earned:
            earned.append("word_warrior")
        # half_century: 50+ points in ranked
        if is_ranked and score >= 50 and "half_century" not in earned:
            earned.append("half_century")
        # double_century: 200+ points in ranked
        if is_ranked and score >= 200 and "double_century" not in earned:
            earned.append("double_century")
        # spelling_legend: 300+ points in ranked
        if is_ranked and score >= 300 and "spelling_legend" not in earned:
            earned.append("spelling_legend")
        # survivor: finish ranked with all 3 lives (no lives lost)
        # We check accuracy as proxy — 100% accuracy means no wrong answers
        if is_ranked and accuracy >= 1.0 and "survivor" not in earned:
            earned.append("survivor")
        # streak_master: 15+ streak
        if streak >= 15 and "streak_master" not in earned:
            earned.append("streak_master")
        # bomb_defuser: 5+ bomb words correct
        if bombs >= 5 and "bomb_defuser" not in earned:
            earned.append("bomb_defuser")
        # night_owl / early_bird: based on server time
        now_hour = datetime.now(timezone.utc).hour
        if is_ranked and now_hour >= 21 and "night_owl" not in earned:
            earned.append("night_owl")
        if is_ranked and now_hour < 8 and "early_bird" not in earned:
            earned.append("early_bird")
        updates["badges"] = earned

        ref.set(updates, merge=True)
    _fs_write(_update_profile_data, timeout=8)


# ---- Ranked attempts ----

def get_ranked_attempts(name, week, group="group1"):
    """Return number of ranked attempts used this week."""
    ck = f"ranked:{group}:{name}:{week}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    if USE_FIRESTORE:
        def _get_ranked_attempts_data():
            doc = gcol(group, "ranked_attempts").document(f"{name}_{week}").get()
            return doc.to_dict().get("attempts", 0) if doc.exists else 0
        result = _fs_call(_get_ranked_attempts_data, default=0)
        cache_set(ck, result, CACHE_TTL_PROFILES)
        return result
    return 0


def increment_ranked_attempt(name, week, group="group1"):
    cache_invalidate(f"ranked:{group}:{name}:{week}")
    if USE_FIRESTORE:
        def _inc_ranked_attempt():
            ref = gcol(group, "ranked_attempts").document(f"{name}_{week}")
            ref.set({"attempts": firestore.Increment(1), "name": name, "week": week}, merge=True)
        _fs_write(_inc_ranked_attempt)


# ---- Team scoring ----

def update_team_scores_computed(player_name, team_id, score, delta, group="group1"):
    """Update the pre-computed team scores document when a ranked score changes.
    Stores each player's best score under their team — avoids scanning all profiles.
    `score` is the new best score, `delta` is (new_best - old_best)."""
    if not USE_FIRESTORE or not team_id:
        return
    week = get_week_key()
    cache_invalidate("team_lb:")
    def _update_team_scores_data():
        ref = gcol(group, "team_scores_computed").document(week)
        # Store only the best score for each player
        ref.set({
            f"{team_id}.{player_name}": score,
            f"_members.{team_id}.{player_name}": True,
        }, merge=True)
    _fs_write(_update_team_scores_data)
    
    # Increment team total by DELTA only (not full score) to avoid double-counting
    update_team_profile_score(team_id, delta, group)


def update_team_profile_score(team_id, delta, group="group1"):
    """Increment team profile's weekly score by the delta (new_best - old_best)."""
    if not USE_FIRESTORE or not team_id or delta <= 0:
        return
    cache_invalidate("team_lb:")
    def _update_team_profile_data():
        ref = gcol(group, "teams").document(team_id)
        # Increment weekly score by delta only — prevents double-counting
        ref.set({
            "weekly_score": firestore.Increment(delta),
            "games_played": firestore.Increment(1),
        }, merge=True)
    _fs_write(_update_team_profile_data)


def get_team_leaderboard(group="group1"):
    """Return sorted list of teams with weekly scores computed as sum of each
    member's best ranked score this week. This is the authoritative calculation
    and avoids drift from the delta-incremented weekly_score field (BUG 5 fix)."""
    week = get_week_key()
    ck = f"team_lb:{group}:{week}"
    cached = cache_get(ck)
    if cached is not None:
        if isinstance(cached, dict) and "teams" in cached:
            return cached
        if isinstance(cached, list):
            return {"teams": cached, "winner": None, "week": week}

    teams = load_teams(group)
    result = []

    if USE_FIRESTORE:
        def _compute_scores():
            rk = f"ranked_best_{week}"
            # Sum each player's best ranked score per team
            team_scores = {}   # team_id -> total score
            team_games = {}    # team_id -> player count with score > 0
            prof_docs = gcol(group, "player_profiles").stream()
            for d in prof_docs:
                p = d.to_dict()
                tid = p.get("team_id", "")
                if not tid:
                    continue
                best = p.get(rk, 0)
                team_scores[tid] = team_scores.get(tid, 0) + best
                if best > 0:
                    team_games[tid] = team_games.get(tid, 0) + 1
            return team_scores, team_games

        scores_result = _fs_call(_compute_scores, default=({}, {}), timeout=8) or ({}, {})
        team_scores, team_games = scores_result if isinstance(scores_result, tuple) else ({}, {})

        for team in teams:
            tid = team["id"]
            result.append({
                "id": tid,
                "name": team["name"],
                "color": team.get("color", "#f59e0b"),
                "emoji": team.get("emoji", "\U0001f3c5"),
                "weekly_score": team_scores.get(tid, 0),
                "games_played": team_games.get(tid, 0),
                "player_count": team_games.get(tid, 0),
            })
    else:
        for team in teams:
            result.append({
                "id": team["id"],
                "name": team["name"],
                "color": team.get("color", "#f59e0b"),
                "emoji": team.get("emoji", "\U0001f3c5"),
                "weekly_score": 0,
                "games_played": 0,
                "player_count": 0,
            })

    result.sort(key=lambda x: x["weekly_score"], reverse=True)

    winner = None
    if result and result[0]["weekly_score"] > 0:
        winner = {
            "name": result[0]["name"],
            "emoji": result[0]["emoji"],
            "score": result[0]["weekly_score"],
            "color": result[0]["color"]
        }

    lb_result = {"teams": result, "winner": winner, "week": week}
    cache_set(ck, lb_result, CACHE_TTL_TEAM_LB)
    return lb_result


def save_weekly_snapshot_history(group="group1"):
    """Save current week's final results to history. Call this on Sunday night."""
    week = get_week_key()
    lb_data = get_team_leaderboard(group)
    teams = lb_data.get("teams", [])
    
    if not USE_FIRESTORE or not teams:
        return False
        
    def _save_snapshot_data():
        ref = gcol(group, "weekly_history").document(week)
        snapshot = {
            "week": week,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "teams": teams[:10],  # Save top 10 teams
            "total_teams": len(teams)
        }
        ref.set(snapshot, merge=True)
        return True
    
    return _fs_write(_save_snapshot_data)


def load_weekly_history(group="group1", limit_weeks=20):
    """Load weekly history records."""
    if not USE_FIRESTORE:
        return []
    
    def _load_weekly_history_data():
        history = {}
        docs = gcol(group, "weekly_history").order_by("week", direction="DESCENDING").limit(limit_weeks).stream()
        for d in docs:
            data = d.to_dict()
            week = data.get("week", d.id)
            history[week] = data.get("teams", [])
        return history
    
    return _fs_call(_load_weekly_history_data, default={}, timeout=8) or {}


def load_leaderboard(group="group1", is_ranked=False):
    """Load leaderboard entries. Separate collections for ranked vs regular modes."""
    ck = f"leaderboard:{group}:{'ranked' if is_ranked else 'regular'}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    if USE_FIRESTORE:
        def _load_leaderboard_data():
            board = {}
            try:
                # Load all teams once for emoji lookup
                teams_data = {}
                team_docs = gcol(group, "teams").stream()
                for t in team_docs:
                    team = t.to_dict()
                    teams_data[team["id"]] = team
            except Exception as e:
                print(f"[Leaderboard] Error loading teams: {e}")
                teams_data = {}
            
            # Use different collection for ranked vs regular
            collection_name = "leaderboard_ranked" if is_ranked else "leaderboard"
            
            # Only read leaderboard scores (3 collection reads, no profile scan)
            for diff in ("easy", "medium", "hard"):
                try:
                    docs = gcol(group, collection_name).document(diff).collection("scores").stream()
                    best_by_name = {}
                    for d in docs:
                        data = d.to_dict()
                        name = data.get("name", "")
                        score = data.get("score", 0)
                        if name not in best_by_name or score > best_by_name[name]["score"]:
                            team_emoji = data.get("team_emoji", "")
                            # If no emoji in leaderboard entry, get it from teams data
                            if not team_emoji and data.get("team_id"):
                                team = teams_data.get(data.get("team_id"))
                                if team:
                                    team_emoji = team.get("emoji", "")
                            
                            best_by_name[name] = {
                                "name": name,
                                "score": score,
                                "streak": data.get("streak", 0),
                                "avatar": data.get("avatar", ""),
                                "team_name": data.get("team_name", ""),
                                "team_emoji": team_emoji,
                            }
                    entries = sorted(best_by_name.values(), key=lambda x: x["score"], reverse=True)
                    board[diff] = entries[:15]
                except Exception as e:
                    print(f"[Leaderboard] Error loading {diff} scores: {e}")
                    board[diff] = []
            return board
        result = _fs_call(_load_leaderboard_data, default={"easy": [], "medium": [], "hard": []}, timeout=8)
        cache_set(ck, result, CACHE_TTL_LEADERBOARD)
        return result
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                result = json.load(f)
                cache_set(ck, result, CACHE_TTL_LEADERBOARD)
                return result
        except Exception:
            return {"easy": [], "medium": [], "hard": []}
    return {"easy": [], "medium": [], "hard": []}


def save_leaderboard_entry(name, score, streak, difficulty, group="group1", avatar="", team_name="", team_emoji="", team_id="", is_ranked=False):
    """Save leaderboard entry — only one entry per user per difficulty (highest score wins).
    Includes avatar/team data so load_leaderboard doesn't need profile scans.
    Separate collections for ranked vs regular modes."""
    cache_invalidate("leaderboard:")
    if USE_FIRESTORE:
        def _save_leaderboard_entry_data():
            # Use different collection for ranked vs regular
            collection_name = "leaderboard_ranked" if is_ranked else "leaderboard"
            ref = gcol(group, collection_name).document(difficulty).collection("scores").document(name)
            existing = ref.get()
            if existing.exists:
                old_score = existing.to_dict().get("score", 0)
                if score <= old_score:
                    return False
            ref.set({
                "name": name,
                "score": score,
                "streak": streak,
                "avatar": avatar,
                "team_name": team_name,
                "team_emoji": team_emoji,
                "team_id": team_id,
                "week": get_week_key(),
                "timestamp": firestore.SERVER_TIMESTAMP,
                "is_ranked": is_ranked,
            })
            return True
        result = _fs_call(_save_leaderboard_entry_data, default=False)
        return result
    return False


def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/static/<path:filename>")
def serve_static(filename):
    from flask import make_response
    resp = make_response(send_file(os.path.join(BASE_DIR, "static", filename)))
    # Cache static assets for 1 week (604800 seconds) for better performance
    # Vercel will serve from CDN with these headers
    resp.headers["Cache-Control"] = "public, max-age=604800, immutable"
    return resp


@app.route("/words")
def get_words():
    group = get_group()
    difficulty = request.args.get("difficulty", "easy").lower().strip()
    week = int(request.args.get("week", 0))
    
    # Strict validation: only allow valid difficulties
    if difficulty not in ("easy", "medium", "hard"):
        difficulty = "easy"
    
    # Get words for the specific week and group
    words = get_words_for_week(difficulty, week, group)
    
    # Remove duplicates while preserving order
    seen = set()
    words = [w for w in words if not (w in seen or seen.add(w))]
    
    return jsonify({"words": words})


@app.route("/weeks")
def get_weeks():
    group = get_group()
    return jsonify({
        "easy": get_week_count("easy", group),
        "medium": get_week_count("medium", group),
        "hard": get_week_count("hard", group),
    })


@app.route("/api/health")
def api_health():
    """Health check endpoint for debugging production issues."""
    info = {
        "ok": True,
        "use_firestore": USE_FIRESTORE,
        "vercel": bool(os.environ.get("VERCEL")),
        "python": __import__("sys").version.split()[0],
    }
    # Diagnose gRPC/Firestore state
    try:
        from google.cloud.firestore_v1 import _helpers
        info["use_grpc"] = getattr(_helpers, "USE_GRPC", "attr_missing")
    except ImportError:
        info["use_grpc"] = "import_failed"
    try:
        import grpc
        info["grpc_version"] = grpc.__version__
    except ImportError:
        info["grpc_version"] = "not_installed"
    try:
        import google.cloud.firestore_v1
        info["firestore_pkg"] = google.cloud.firestore_v1.__version__
    except Exception:
        info["firestore_pkg"] = "unknown"
    # Multi-Firebase project status
    info["firebase_groups"] = {}
    for grp in VALID_GROUPS:
        if grp in _group_db:
            info["firebase_groups"][grp] = "own_project"
        else:
            info["firebase_groups"][grp] = "not_configured"
    # Quick Firestore test with timeout
    if USE_FIRESTORE and request.args.get("test_db"):
        import threading
        result = {"status": "timeout"}
        def _test_db_health():
            try:
                doc = db.collection("_health").document("ping").get()
                result["status"] = "ok" if doc.exists else "empty_ok"
            except Exception as e:
                result["status"] = f"error: {e}"
        t = threading.Thread(target=_test_db_health)
        t.start()
        t.join(timeout=5)
        info["db_test"] = result["status"]
    return jsonify(info)


@app.route("/api/dbtest")
def api_dbtest():
    """Direct HTTP test to Firestore REST API — bypasses SDK entirely."""
    import threading
    info = {"sdk_test": "skipped", "http_test": "skipped", "token_test": "skipped"}

    if not USE_FIRESTORE:
        info["error"] = "Firestore not enabled"
        return jsonify(info)

    # Test 1: Can we get an access token?
    try:
        app_cred = firebase_admin.get_app().credential
        token = app_cred.get_access_token()
        info["token_test"] = f"ok (expires={token.expiry})"
        access_token = token.access_token

        # Test 2: Direct HTTP request to Firestore REST API
        try:
            project_id = firebase_admin.get_app().project_id
            url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/_health/ping"
            headers = {"Authorization": f"Bearer {access_token}"}
            resp = http_requests.get(url, headers=headers, timeout=5)
            info["http_test"] = f"status={resp.status_code}"
            info["http_body"] = resp.text[:500]
            if resp.status_code == 404:
                info["http_test"] = "ok (document not found, but API reachable)"
            elif resp.status_code == 200:
                info["http_test"] = "ok (document exists)"
        except Exception as e:
            info["http_test"] = f"error: {e}"
    except Exception as e:
        info["token_test"] = f"error: {e}"

    # Test 3: SDK test with timeout
    result = {"status": "timeout"}
    def _test_db_sdk():
        try:
            doc = db.collection("_health").document("ping").get()
            result["status"] = "ok" if doc.exists else "empty_ok"
        except Exception as e:
            result["status"] = f"error: {e}"
    t = threading.Thread(target=_test_db_sdk)
    t.start()
    t.join(timeout=5)
    info["sdk_test"] = result["status"]

    return jsonify(info)


@app.route("/api/group-info")
def api_group_info():
    """Return current group label and valid groups list."""
    group = get_group()
    return jsonify({
        "group": group,
        "label": get_group_label(group),
        "groups": {g: get_group_label(g) for g in VALID_GROUPS},
    })


@app.route("/image/<path:word>")
def get_image(word):
    w = word.lower()
    # 1) Check locally stored image (downloaded from Pixabay)
    pixabay = PIXABAY_IMAGES.get(w, {})
    local_file = pixabay.get("local")
    if local_file:
        return jsonify({"url": "/static/img/words/" + local_file})
    # 2) Emoji from Pixabay JSON fallback
    if pixabay.get("emoji"):
        return jsonify({"emoji": pixabay["emoji"]})
    # 3) Emoji from WORD_IMAGES dict (verified mapping)
    emoji = WORD_IMAGES.get(w)
    if emoji:
        return jsonify({"emoji": emoji})
    # 4) Generic fallback emoji (no Wikipedia fallback - use verified sources only)
    return jsonify({"emoji": "\ud83d\udcdd"})


def get_or_generate_audio(text, cache_key=None, edge_voice=None, edge_rate="-30%"):
    """On-demand audio generation with progressive caching.
    Fallback chain: Cache → ElevenLabs → Edge TTS → None
    """
    if not text or len(text.strip()) == 0:
        return None

    # 1) Check existing caches (ElevenLabs + Edge already have their own)
    #    Just delegate to the existing functions which handle caching.

    # 2) Try ElevenLabs first (lightweight HTTP, high quality)
    if ELEVENLABS_AVAILABLE:
        try:
            result = cache_and_return_elevenlabs(text, voice_id=ELEVENLABS_VOICE_ID)
            if result:
                print(f"[TTS] ElevenLabs success: {text[:30]}")
                return result
        except Exception as e:
            print(f"[TTS] ElevenLabs failed: {e}")

    # 3) Fall back to Edge TTS (WebSocket-based, no API key needed)
    try:
        voice = edge_voice or VOICE_NORMAL
        result = cache_and_return_edge(text, voice, edge_rate)
        if result:
            print(f"[TTS] Edge TTS success: {text[:30]}")
            return result
    except Exception as e:
        print(f"[TTS] Edge TTS failed: {e}")

    # 4) Fall back to gTTS (synchronous HTTP, works everywhere including Vercel)
    try:
        result = cache_and_return_gtts(text)
        if result:
            print(f"[TTS] gTTS success: {text[:30]}")
            return result
    except Exception as e:
        print(f"[TTS] gTTS failed: {e}")

    print(f"[TTS] All TTS methods failed for: {text[:30]}")
    return None


def generate_tts_with_fallback(text, edge_voice=None, edge_rate="-30%", elevenlabs_speed=0.75):
    """Generate TTS with fallback chain: ElevenLabs → Edge TTS.
    Returns file path or BytesIO object, or None on complete failure."""
    if not text or len(text.strip()) == 0:
        return None
    return get_or_generate_audio(text, edge_voice=edge_voice, edge_rate=edge_rate)


def serve_tts(result):
    """Return a Flask response from a TTS result (file path or BytesIO)."""
    if result is None:
        # Critical TTS failure - return a proper error response
        return jsonify({"error": "TTS generation failed - both ElevenLabs and Edge TTS unavailable"}), 503
    if isinstance(result, io.BytesIO):
        result.seek(0)
        return send_file(result, mimetype="audio/mpeg")
    return send_file(result, mimetype="audio/mpeg")


@app.route("/tts-debug")
def tts_debug():
    """Diagnostic endpoint for TTS troubleshooting."""
    info = {
        "elevenlabs_available": ELEVENLABS_AVAILABLE,
        "elevenlabs_key_set": bool(ELEVENLABS_API_KEY),
        "elevenlabs_key_prefix": ELEVENLABS_API_KEY[:8] + "..." if ELEVENLABS_API_KEY else None,
        "gtts_available": GTTS_AVAILABLE,
        "edge_tts_module": bool(edge_tts),
        "audio_cache_dir": AUDIO_CACHE_DIR,
        "vercel": bool(os.environ.get("VERCEL")),
    }
    # Quick test: try gTTS
    try:
        test = cache_and_return_gtts("test")
        info["gtts_test"] = "OK" if test else "EMPTY"
    except Exception as e:
        info["gtts_test"] = f"FAIL: {e}"
    # Quick test: try ElevenLabs
    if ELEVENLABS_AVAILABLE:
        try:
            test = cache_and_return_elevenlabs("test")
            info["elevenlabs_test"] = "OK" if test else "EMPTY"
        except Exception as e:
            info["elevenlabs_test"] = f"FAIL: {e}"
    # Quick test: try Edge TTS
    try:
        test = cache_and_return_edge("test", VOICE_NORMAL, "-30%")
        info["edge_tts_test"] = "OK" if test else "EMPTY"
    except Exception as e:
        info["edge_tts_test"] = f"FAIL: {e}"
    return jsonify(info)


@app.route("/speak/<path:word>")
def speak(word):
    try:
        word = unquote(word).strip()
        precached = get_precached_audio(word)
        if precached:
            return send_file(precached, mimetype="audio/mpeg")
        result = generate_tts_with_fallback(word, edge_rate="-30%")
        return serve_tts(result)
    except Exception as e:
        print(f"[speak] TTS Error for word '{word}': {e}")
        return jsonify({"error": "TTS generation failed"}), 500


@app.route("/speak_slow/<path:word>")
def speak_slow(word):
    try:
        word = unquote(word).strip()
        precached = get_precached_audio(word, suffix="_slow")
        if precached:
            return send_file(precached, mimetype="audio/mpeg")
        result = generate_tts_with_fallback(word, edge_voice=VOICE_SLOW, edge_rate="-55%")
        return serve_tts(result)
    except Exception as e:
        print(f"[speak_slow] TTS Error for word '{word}': {e}")
        return jsonify({"error": "TTS generation failed"}), 500


@app.route("/spell/<path:word>")
def spell(word):
    try:
        word = unquote(word).strip()
        precached = get_precached_audio(word, suffix="_spell")
        if precached:
            return send_file(precached, mimetype="audio/mpeg")
        text = format_spelling_text(word)
        result = generate_tts_with_fallback(text, edge_rate="-30%")
        return serve_tts(result)
    except Exception as e:
        print(f"[spell] Unhandled error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/spell_slow/<path:word>")
def spell_slow(word):
    try:
        word = unquote(word).strip()
        precached = get_precached_audio(word, suffix="_spell")
        if precached:
            return send_file(precached, mimetype="audio/mpeg")
        text = format_spelling_text(word)
        result = generate_tts_with_fallback(text, edge_voice=VOICE_SLOW, edge_rate="-55%")
        return serve_tts(result)
    except Exception as e:
        print(f"[spell_slow] Unhandled error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/prewarm-audio", methods=["POST"])
def prewarm_audio():
    """Pre-generate audio for current week in background (non-blocking).
    Called when game starts to warm up cache for smooth playback."""
    data = request.get_json(force=True) or {}
    group = data.get("group", "group1").strip().lower()
    if group not in VALID_GROUPS:
        group = "group1"
    
    difficulty = data.get("difficulty", "easy").lower()
    if difficulty not in ("easy", "medium", "hard"):
        difficulty = "easy"
    
    week = int(data.get("week", 1))
    
    # Get words for this week
    words = get_words_for_week(difficulty, week, group)
    
    # Pre-warm in background thread (non-blocking)
    def _prewarm():
        count = 0
        for word in words[:10]:  # Limit to first 10 words to avoid long delays
            try:
                get_or_generate_audio(word)
                count += 1
            except Exception as e:
                print(f"[Prewarm] Error for '{word}': {e}")
        print(f"[Prewarm] Completed: {count}/{min(10, len(words))} words cached")
    
    thread = threading.Thread(target=_prewarm, daemon=True)
    thread.start()
    
    return jsonify({"ok": True, "message": "Audio pre-warming started in background"})


@app.route("/sentence/<path:word>")
def sentence(word):
    try:
        w = unquote(word).lower().strip()
        precached = get_precached_audio(w, suffix="_sentence")
        if precached:
            return send_file(precached, mimetype="audio/mpeg")
        
        # Use contextual sentence if available, otherwise create helpful fallback
        if w in WORD_SENTENCES:
            text = WORD_SENTENCES[w]
        else:
            # Create helpful contextual sentences by word type/length
            if len(w) <= 4:
                text = f"Can you spell the word {w}?"
            elif len(w) <= 7:
                text = f"The word {w} is commonly used in everyday language."
            else:
                text = f"Learning to spell the word {w} requires practice and patience."
        
        # Play sentence slowly for better comprehension
        result = generate_tts_with_fallback(text, elevenlabs_speed=0.6, edge_rate="-30%")
        return serve_tts(result)
    except Exception as e:
        print(f"[sentence] Unhandled error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/words_all")
def get_words_all():
    group = get_group()
    from words import get_words_with_weeks
    return jsonify(get_words_with_weeks(group))


@app.route("/words_ranked")
def get_words_ranked():
    group = get_group()
    ranked = get_ranked_words(group)
    return jsonify(ranked)


@app.route("/words_bombs")
def get_words_bombs():
    group = get_group()
    bombs = get_bomb_words(group)
    return jsonify(bombs)


@app.route("/words_bombs_tournament")
def get_words_bombs_tournament():
    """Tournament-specific bomb words endpoint that respects difficulty"""
    group = get_group()
    difficulty = request.args.get("difficulty", "hard").lower().strip()
    
    # Use the new function that handles difficulty-specific bomb words
    bombs = get_bomb_words_by_difficulty(group, difficulty)
    return jsonify(bombs)


# Simple in-memory rate limiter for leaderboard submissions
_lb_rate = {}  # ip -> last_submit_time
LB_RATE_LIMIT_SECONDS = 5


@app.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    group = get_group()
    is_ranked = request.args.get("is_ranked", "false").lower() == "true"
    return jsonify(load_leaderboard(group, is_ranked=is_ranked))


@app.route("/leaderboard", methods=["POST"])
def post_leaderboard():
    data = request.get_json(force=True)
    group = data.get("group", "group1").strip().lower()
    if group not in VALID_GROUPS:
        group = "group1"
    import re
    name = re.sub(r'[^\w\s]', '', str(data.get("name", "")).strip()).strip()[:20]
    score = int(data.get("score", 0))
    difficulty = str(data.get("difficulty", "easy"))
    streak = int(data.get("streak", 0))
    team_id = str(data.get("team_id", "")).strip()
    team_name = str(data.get("team_name", "")).strip()[:30]
    team_emoji = str(data.get("team_emoji", "")).strip()[:4]
    is_competition = bool(data.get("is_competition", False))
    is_ranked = bool(data.get("is_ranked", False))
    accuracy = float(data.get("accuracy", 0))
    words_completed = int(data.get("words_completed", 0))
    bombs_correct = int(data.get("bombs_correct", 0))
    time_bonuses = int(data.get("time_bonuses", 0))
    reached_x3 = bool(data.get("reached_x3", False))

    if difficulty not in ("easy", "medium", "hard"):
        difficulty = "medium"

    if not name or score < 0:
        return jsonify({"ok": False}), 400

    # Early ranked attempt consumption: frontend sends _consume_only after 3 correct
    # words to prevent tab-close abuse. Only increment attempt, don't update profile.
    consume_only = bool(data.get("_consume_only", False))
    if is_ranked and consume_only:
        week = get_week_key()
        used = get_ranked_attempts(name, week, group)
        if used < 3:
            increment_ranked_attempt(name, week, group)
        return jsonify({"ok": True})

    # Rate limit only for non-ranked submissions (ranked must always go through)
    if not is_ranked:
        ip = request.remote_addr or "unknown"
        now = time.time()
        if ip in _lb_rate and (now - _lb_rate[ip]) < LB_RATE_LIMIT_SECONDS:
            return jsonify({"ok": False, "error": "Too fast, please wait."}), 429
        _lb_rate[ip] = now

    # Team scoring for ranked games is handled by update_team_scores_computed()
    # inside update_profile() — stores only the player's best score per week.
    # No need for add_team_score() here (it was cumulative/redundant).

    # Ranked attempt tracking — skip if attempt was already consumed early
    skip_attempt = bool(data.get("_skip_attempt", False))
    week = get_week_key()
    if is_ranked and not skip_attempt:
        used = get_ranked_attempts(name, week, group)
        if used >= 3:
            return jsonify({"ok": False, "error": "No ranked attempts left this week"}), 403
        # Only increment if this is a meaningful game (3+ words completed)
        words_completed = int(data.get("words_completed", 0))
        if words_completed >= 3:
            increment_ranked_attempt(name, week, group)

    # Update player profile
    try:
        update_profile(name, {
            "score": score, "accuracy": accuracy, "streak": streak,
            "words_completed": words_completed,
            "bombs_correct": bombs_correct, "time_bonuses": time_bonuses,
            "is_ranked": is_ranked, "difficulty": difficulty,
            "team_id": team_id, "team_name": team_name,
            "reached_x3": reached_x3,
        }, group)
    except Exception as e:
        print(f"[Profile] update error in leaderboard POST: {e}")

    # Save to leaderboard for both ranked and non-ranked games
    if USE_FIRESTORE:
        # Get avatar and team emoji from profile/team data
        prof = get_profile(name, group) or {}
        p_avatar = prof.get("avatar", "")
        p_team_name = prof.get("team_name", team_name)
        p_team_emoji = team_emoji  # Use team_emoji from request
        # Pass is_ranked flag to save to correct collection
        save_leaderboard_entry(name, score, streak, difficulty, group,
                               avatar=p_avatar, team_name=p_team_name, team_emoji=p_team_emoji, team_id=team_id,
                               is_ranked=is_ranked)
        board = load_leaderboard(group, is_ranked=is_ranked)
        return jsonify({"ok": True, "board": board.get(difficulty, [])})
    # Fallback to JSON file — one entry per user per difficulty (highest score)
    board = load_leaderboard(group, is_ranked=is_ranked)
    entries = board.setdefault(difficulty, [])
    existing = next((e for e in entries if e.get("name") == name), None)
    if existing:
        if score > existing.get("score", 0):
            existing["score"] = score
            existing["streak"] = streak
    else:
        entries.append({"name": name, "score": score, "streak": streak})
    board[difficulty].sort(key=lambda x: x["score"], reverse=True)
    board[difficulty] = board[difficulty][:15]
    save_leaderboard(board)
    return jsonify({"ok": True, "board": board.get(difficulty, [])})


# ==================== TEAM API ROUTES ====================

def _get_team_member_counts(group="group1"):
    """Get member counts per team, cached."""
    ck = f"members:counts:{group}"
    cached = cache_get(ck)
    if cached is not None:
        return cached
    team_member_counts = {}
    if USE_FIRESTORE:
        def _count_team_members():
            counts = {}
            docs = gcol(group, "player_teams").stream()
            for d in docs:
                pt = d.to_dict()
                tid = pt.get("team_id", "")
                if tid:
                    counts[tid] = counts.get(tid, 0) + 1
            return counts
        team_member_counts = _fs_call(_count_team_members, default={}) or {}
    cache_set(ck, team_member_counts, CACHE_TTL_MEMBERS)
    return team_member_counts


@app.route("/api/teams", methods=["GET"])
def api_get_teams():
    group = get_group()
    teams = load_teams(group)
    team_member_counts = _get_team_member_counts(group)
    for t in teams:
        t["member_count"] = team_member_counts.get(t["id"], 0)
    return jsonify({"teams": teams})


@app.route("/api/team-leaderboard", methods=["GET"])
def api_team_leaderboard():
    group = get_group()
    lb_data = get_team_leaderboard(group)
    teams = lb_data.get("teams", [])
    week = get_week_key()
    return jsonify({"teams": teams, "week_label": week})


# ==================== ADMIN ROUTES ====================

def check_admin_auth():
    """Stateless auth: password via X-Admin-Password header only.
    Works on Vercel serverless where sessions don't persist.
    NOTE: Do NOT read request.get_json() here — it consumes the body stream."""
    pw = request.headers.get("X-Admin-Password", "")
    return pw == ADMIN_PASSWORD


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_admin_auth():
            return jsonify({"ok": False, "error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/admin/api/upload-avatar", methods=["POST"])
@admin_required
def admin_upload_avatar():
    """Upload team avatar image."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    # Validate image
    if not file.content_type.startswith("image/"):
        return jsonify({"error": "File must be an image"}), 400
    
    # Generate unique filename
    import uuid
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["jpg", "jpeg", "png", "gif", "webp"]:
        return jsonify({"error": "Invalid image format"}), 400
    
    filename = f"avatar_{uuid.uuid4().hex[:8]}.{ext}"
    
    # Save to static/avatars
    avatars_dir = os.path.join(BASE_DIR, "static", "avatars")
    os.makedirs(avatars_dir, exist_ok=True)
    filepath = os.path.join(avatars_dir, filename)
    file.save(filepath)
    
    return jsonify({"url": f"/static/avatars/{filename}"})


@app.route("/admin", methods=["GET"])
def admin_panel():
    # Extract group from URL parameter for teacher-specific admin access
    group = request.args.get("group", "").strip().lower()
    if group and group in VALID_GROUPS:
        # Teacher-specific admin URL - lock to this group
        return render_template("admin.html", locked_group=group, group_label=get_group_label(group))
    else:
        # No group specified - can switch between groups (for super admin)
        return render_template("admin.html", locked_group=None, group_label=None)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Verify password and return ok — client stores it in localStorage."""
    if request.method == "POST":
        data = request.get_json(force=True, silent=True) or {}
        pw = data.get("password", "") or request.form.get("password", "")
        if pw == ADMIN_PASSWORD:
            return jsonify({"ok": True})
        return jsonify({"ok": False, "error": "Wrong password."}), 401
    return render_template("admin_login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    return jsonify({"ok": True})


@app.route("/admin/api/teams", methods=["GET"])
@admin_required
def admin_api_get_teams():
    group = get_admin_group()
    week = get_week_key()
    # Use get_team_leaderboard for accurate scores
    lb_data = get_team_leaderboard(group)
    lb_teams = lb_data.get("teams", [])
    winner = lb_data.get("winner")
    raw_teams = load_teams(group)
    lb_map = {t["id"]: t for t in lb_teams}
    result = []
    for t in raw_teams:
        lb = lb_map.get(t["id"], {})
        t["weekly_score"] = lb.get("weekly_score", 0)
        t["games_played"] = lb.get("games_played", 0)
        t["member_count"] = lb.get("player_count", 0)
        t["avatar_url"] = t.get("avatar_url", "")  # Ensure avatar_url exists
        result.append(t)
    return jsonify({"teams": result, "week": week, "winner": winner})


@app.route("/admin/api/teams", methods=["POST"])
@admin_required
def admin_api_create_team():
    data = request.get_json(force=True)
    group = get_admin_group()  # Use locked group instead of data.group
    name = str(data.get("name", "")).strip()[:30]
    color = str(data.get("color", "#f59e0b"))[:20]
    emoji = str(data.get("emoji", "\U0001f3c5"))[:4]
    avatar_url = str(data.get("avatar_url", "")).strip()[:200]
    if not name:
        return jsonify({"ok": False, "error": "Name required"}), 400
    teams = load_teams(group)
    if any(t["name"].lower() == name.lower() for t in teams):
        return jsonify({"ok": False, "error": "Team name already exists"}), 400
    team = {"id": str(uuid.uuid4()), "name": name, "color": color, "emoji": emoji, "avatar_url": avatar_url, "member_count": 0}
    save_team_fs(team, group)
    return jsonify({"ok": True, "team": team})


@app.route("/admin/api/teams/<team_id>", methods=["PUT"])
@admin_required
def admin_api_update_team(team_id):
    data = request.get_json(force=True)
    group = get_admin_group()  # Use locked group
    teams = load_teams(group)
    for t in teams:
        if t["id"] == team_id:
            if "name" in data: t["name"] = str(data["name"]).strip()[:30]
            if "color" in data: t["color"] = str(data["color"])[:20]
            if "emoji" in data: t["emoji"] = str(data["emoji"])[:4]
            if "avatar_url" in data: t["avatar_url"] = str(data["avatar_url"]).strip()[:200]
            save_team_fs(t, group)
            return jsonify({"ok": True, "team": t})
    return jsonify({"ok": False, "error": "Not found"}), 404


@app.route("/admin/api/teams/<team_id>", methods=["DELETE"])
@admin_required
def admin_api_delete_team(team_id):
    group = get_admin_group()
    delete_team_fs(team_id, group)
    return jsonify({"ok": True})


@app.route("/admin/api/reset-week", methods=["POST"])
@admin_required
def admin_api_reset_week():
    """Full week reset: archive first, then wipe all scores/attempts/team totals."""
    group = get_admin_group()
    week = get_week_key()
    cache_invalidate("profile:", "leaderboard:", "team_lb:", "ranked:", "classmates:", "members:", "week_history:", "week_scores:", "all_scores:")

    # Archive before reset
    archive_week_scores(week, group)

    if USE_FIRESTORE:
        def _full_reset():
            # 1. Wipe individual leaderboard entries
            for diff in ["easy", "medium", "hard"]:
                docs = gcol(group, "leaderboard").document(diff).collection("scores").stream()
                for d in docs:
                    d.reference.delete()
            # 2. Wipe team_scores subcollection
            docs = gcol(group, "team_scores").document(week).collection("scores").stream()
            for d in docs:
                d.reference.delete()
            # 3. Reset weekly_score + games_played on each team profile
            docs = gcol(group, "teams").stream()
            for d in docs:
                d.reference.set({"weekly_score": 0, "games_played": 0}, merge=True)
            # 4. Reset ranked attempts for this week
            docs = gcol(group, "ranked_attempts").where("week", "==", week).stream()
            for d in docs:
                d.reference.set({"attempts": 0, "name": d.to_dict().get("name", ""), "week": week}, merge=True)
            # 5. Reset ranked_best_{week} in all player profiles
            rk = f"ranked_best_{week}"
            docs = gcol(group, "player_profiles").stream()
            for d in docs:
                if d.to_dict().get(rk, 0) > 0:
                    d.reference.update({rk: 0})
            # 6. Clear computed scores document
            try:
                gcol(group, "team_scores_computed").document(week).delete()
            except Exception:
                pass
        _fs_call(_full_reset, timeout=15)

    return jsonify({"ok": True, "week": week})


@app.route("/admin/api/all-scores", methods=["GET"])
@admin_required
def admin_api_all_scores():
    group = get_admin_group()
    # Use score_history system which contains all archived data
    history = get_week_history(group)
    
    # Transform the data to match what the frontend expects
    formatted_history = {}
    for week, data in history.items():
        # Extract team scores from score_history
        team_scores = data.get("team_scores", {})
        teams = []
        
        # Convert team_scores to the format expected by frontend
        for team_id, team_data in team_scores.items():
            teams.append({
                "team_id": team_id,
                "team_name": team_data.get("team_name", ""),
                "weekly_score": team_data.get("weekly_score", 0),
                "games_played": team_data.get("games_played", 0),
                "emoji": team_data.get("emoji", "🏅"),
                "color": team_data.get("color", "#f59e0b")
            })
        
        # Sort by score
        teams.sort(key=lambda x: x["weekly_score"], reverse=True)
        formatted_history[week] = teams
    
    return jsonify({"history": formatted_history})


# ---- Badge API (uses BADGE_DEFS from line 610) ----

@app.route("/api/badges", methods=["GET"])
def api_get_badges():
    """Return all available badge definitions."""
    return jsonify({"badges": {b["id"]: b for b in BADGE_DEFS}})

@app.route("/api/player-badges/<player_name>", methods=["GET"])
def api_get_player_badges(player_name):
    """Get a player's earned badges."""
    group = get_group()
    profile = get_profile(player_name, group)
    if not profile:
        return jsonify({"badges": []})
    
    badge_map = {b["id"]: b for b in BADGE_DEFS}
    earned_ids = profile.get("badges", [])
    earned = []
    for badge_id in earned_ids:
        if badge_id in badge_map:
            badge = badge_map[badge_id].copy()
            badge["icon"] = badge.get("emoji", "")
            earned.append(badge)
    
    return jsonify({"badges": earned})

# ---- Admin Player Management API ----

@app.route("/admin/api/players", methods=["GET"])
@admin_required
def admin_api_list_players():
    """List all player profiles with their team, stats, and ranked info."""
    group = get_admin_group()
    players = []
    week = get_week_key()
    if USE_FIRESTORE:
        def _list():
            result = []
            docs = gcol(group, "player_profiles").stream()
            for d in docs:
                p = d.to_dict()
                attempts_used = get_ranked_attempts(d.id, week, group)
                result.append({
                    "name": p.get("name", d.id),
                    "has_pin": bool(p.get("pin")),
                    "avatar": p.get("avatar", ""),
                    "team_id": p.get("team_id", ""),
                    "team_name": p.get("team_name", ""),
                    "team_color": p.get("team_color", ""),
                    "total_games": p.get("total_games", 0),
                    "best_streak": p.get("best_streak", 0),
                    "ranked_attempts_used": attempts_used,
                    "ranked_attempts_left": max(0, 3 - attempts_used),
                    "ranked_best": p.get(f"ranked_best_{week}", 0),
                })
            return result
        players = _fs_call(_list, default=[], timeout=10) or []
    players.sort(key=lambda x: x["name"].lower())
    return jsonify({"players": players, "week": week})


@app.route("/admin/api/players/<player_name>", methods=["DELETE"])
@admin_required
def admin_api_delete_player(player_name):
    """Delete a player profile entirely."""
    group = get_admin_group()
    player_name = unquote(player_name)
    cache_invalidate("profile:", "player_team:", "leaderboard:", "team_lb:", "members:", "ranked:")
    if USE_FIRESTORE:
        def _del_admin_player():
            gcol(group, "player_profiles").document(player_name).delete()
            try:
                gcol(group, "player_teams").document(player_name).delete()
            except Exception:
                pass
            for diff in ("easy", "medium", "hard"):
                docs = gcol(group, "leaderboard").document(diff).collection("scores").where("name", "==", player_name).stream()
                for d in docs:
                    d.reference.delete()
        try:
            _fs_write(_del_admin_player, timeout=8)
        except Exception as e:
            print(f"[Admin] delete player error: {e}")
            return jsonify({"ok": False, "error": str(e)}), 500
    return jsonify({"ok": True})


@app.route("/admin/api/players/<player_name>/team", methods=["PUT"])
@admin_required
def admin_api_assign_team(player_name):
    """Assign a player to a team."""
    player_name = unquote(player_name)
    data = request.get_json(force=True)
    group = get_admin_group()  # Use locked group
    team_id = str(data.get("team_id", "")).strip()
    team_name = str(data.get("team_name", "")).strip()
    team_color = str(data.get("team_color", "#f59e0b")).strip()
    if not team_id:
        cache_invalidate("profile:", "player_team:", "team_lb:", "members:")
        if USE_FIRESTORE:
            _fs_write(lambda: (
                gcol(group, "player_profiles").document(player_name).set(
                    {"team_id": "", "team_name": "", "team_color": ""}, merge=True),
                gcol(group, "player_teams").document(player_name).delete()
            ))
        return jsonify({"ok": True})
    set_player_team(player_name, team_id, team_name, team_color, group)
    return jsonify({"ok": True})


@app.route("/admin/api/players/<player_name>/rename", methods=["PUT"])
@admin_required
def admin_api_rename_player(player_name):
    """Rename a player — copies profile, team, leaderboard entries to new name."""
    player_name = unquote(player_name)
    data = request.get_json(force=True)
    group = get_admin_group()  # Use locked group
    new_name = str(data.get("new_name", "")).strip()
    if not new_name:
        return jsonify({"ok": False, "error": "New name is required"}), 400
    if new_name == player_name:
        return jsonify({"ok": True})
    cache_invalidate("profile:", "player_team:", "leaderboard:", "team_lb:", "members:", "ranked:")
    if USE_FIRESTORE:
        def _rename():
            gc = lambda c: gcol(group, c)
            existing = gc("player_profiles").document(new_name).get()
            if existing.exists:
                return f"Name '{new_name}' is already taken"
            old_doc = gc("player_profiles").document(player_name).get()
            if old_doc.exists:
                profile = old_doc.to_dict()
                profile["name"] = new_name
                gc("player_profiles").document(new_name).set(profile)
                gc("player_profiles").document(player_name).delete()
            old_team = gc("player_teams").document(player_name).get()
            if old_team.exists:
                team_data = old_team.to_dict()
                team_data["name"] = new_name
                gc("player_teams").document(new_name).set(team_data)
                gc("player_teams").document(player_name).delete()
            for diff in ("easy", "medium", "hard"):
                docs = gc("leaderboard").document(diff).collection("scores").where("name", "==", player_name).stream()
                for d in docs:
                    d.reference.update({"name": new_name})
            attempts_docs = gc("ranked_attempts").where("name", "==", player_name).stream()
            for d in attempts_docs:
                old_data = d.to_dict()
                old_data["name"] = new_name
                w = old_data.get("week", "")
                gc("ranked_attempts").document(f"{new_name}_{w}").set(old_data)
                d.reference.delete()
            return None  # success
        err = _fs_call(_rename, default="Firestore timeout", timeout=10)
        if err:
            return jsonify({"ok": False, "error": err}), 409 if "taken" in str(err) else 500
    return jsonify({"ok": True, "old_name": player_name, "new_name": new_name})


@app.route("/admin/api/players/<player_name>/reset-pin", methods=["POST"])
@admin_required
def admin_api_reset_pin(player_name):
    """Reset a player's PIN so they can set a new one on next login."""
    group = get_admin_group()  # Use locked group
    player_name = unquote(player_name)
    cache_invalidate(f"profile:{group}:{player_name}")
    if USE_FIRESTORE:
        _fs_write(lambda: gcol(group, "player_profiles").document(player_name).update({"pin": firestore.DELETE_FIELD}))
    return jsonify({"ok": True})


@app.route("/admin/api/players/<player_name>/reset-attempts", methods=["POST"])
@admin_required
def admin_api_reset_attempts(player_name):
    """Reset a player's ranked attempts for the current week."""
    group = get_admin_group()  # Use locked group
    player_name = unquote(player_name)
    week = get_week_key()
    cache_invalidate(f"ranked:{group}:{player_name}")
    if USE_FIRESTORE:
        _fs_write(lambda: gcol(group, "ranked_attempts").document(f"{player_name}_{week}").set(
            {"attempts": 0, "name": player_name, "week": week}))
    return jsonify({"ok": True, "week": week})


@app.route("/admin/api/players/pre-register", methods=["POST"])
@admin_required
def admin_api_pre_register():
    """Pre-register a username assigned to a team. No PIN — user creates it on first login."""
    data = request.get_json(force=True)
    group = get_admin_group()  # Use locked group
    names_raw = str(data.get("names", "")).strip()
    team_id = str(data.get("team_id", "")).strip()
    team_name = str(data.get("team_name", "")).strip()
    team_color = str(data.get("team_color", "#f59e0b")).strip()
    if not names_raw or not team_id:
        return jsonify({"ok": False, "error": "Names and team required"}), 400
    import re
    names = [re.sub(r'[^\w\s]', '', n.strip()).strip()[:20] for n in names_raw.split(",") if n.strip()]
    names = [n for n in names if n]
    if not names:
        return jsonify({"ok": False, "error": "No valid names"}), 400
    created = 0
    skipped = 0
    for name in names:
        existing = get_profile(name, group)
        if existing.get("pin"):
            set_player_team(name, team_id, team_name, team_color, group)
            skipped += 1
        else:
            if USE_FIRESTORE:
                _fs_write(lambda n=name: gcol(group, "player_profiles").document(n).set({
                    "name": n,
                    "team_id": team_id,
                    "team_name": team_name,
                    "team_color": team_color,
                    "pre_registered": True,
                }, merge=True))
                created += 1
            else:
                set_player_team(name, team_id, team_name, team_color, group)
                created += 1
    return jsonify({"ok": True, "created": created, "updated": skipped})


@app.route("/admin/api/players/bulk-assign-team", methods=["POST"])
@admin_required
def admin_api_bulk_assign_team():
    """Assign multiple players to a team at once."""
    data = request.get_json(force=True)
    group = get_admin_group()  # Use locked group
    player_names = data.get("players", [])
    team_id = str(data.get("team_id", "")).strip()
    team_name = str(data.get("team_name", "")).strip()
    team_color = str(data.get("team_color", "#f59e0b")).strip()
    if not team_id or not player_names:
        return jsonify({"ok": False, "error": "Missing players or team"}), 400
    for name in player_names:
        set_player_team(str(name).strip(), team_id, team_name, team_color, group)
    return jsonify({"ok": True, "count": len(player_names)})


@app.route("/admin/api/players/<player_name>/history", methods=["GET"])
@admin_required
def admin_api_player_history(player_name):
    """Get detailed history for a specific player."""
    player_name = unquote(player_name)
    group = get_admin_group()
    
    if USE_FIRESTORE:
        def _get_player_history():
            profile = gcol(group, "player_profiles").document(player_name).get()
            profile_data = profile.to_dict() if profile.exists else {}
            
            # Get leaderboard scores
            scores = {"easy": [], "medium": [], "hard": []}
            for diff in ["easy", "medium", "hard"]:
                docs = gcol(group, "leaderboard").document(diff).collection("scores").where("name", "==", player_name).order_by("timestamp", direction="DESCENDING").limit(20).stream()
                for d in docs:
                    score_data = d.to_dict()
                    score_data["difficulty"] = diff
                    scores[diff].append(score_data)
            
            # Get ranked attempts
            attempts = []
            docs = gcol(group, "ranked_attempts").where("name", "==", player_name).stream()
            for d in docs:
                attempt_data = d.to_dict()
                attempts.append(attempt_data)
            
            return {
                "profile": profile_data,
                "scores": scores,
                "attempts": attempts
            }
        
        history = _fs_call(_get_player_history, default={"profile": {}, "scores": {}, "attempts": []}, timeout=8)
        return jsonify(history)
    else:
        # Fallback for non-Firestore
        return jsonify({"profile": {}, "scores": {}, "attempts": []})


@app.route("/admin/api/reset-group-scores/<group_name>", methods=["POST"])
@admin_required
def admin_api_reset_group_scores(group_name):
    """Reset all scores for a specific group. Archives scores first."""
    group_name = unquote(group_name)
    if group_name not in VALID_GROUPS:
        return jsonify({"ok": False, "error": "Invalid group"}), 400
    
    week = get_week_key()
    cache_invalidate("profile:", "leaderboard:", "team_lb:", "ranked:", "classmates:", "members:", "week_history:")
    
    # Archive scores before reset
    archive_week_scores(week, group_name)
    
    if USE_FIRESTORE:
        def _reset_group_scores():
            # Reset ALL leaderboard scores (delete all entries — old ones may lack week field)
            for diff in ["easy", "medium", "hard"]:
                docs = gcol(group_name, "leaderboard").document(diff).collection("scores").stream()
                for d in docs:
                    d.reference.delete()
            
            # Reset team leaderboard scores in this group
            try:
                docs = gcol(group_name, "team_leaderboard").stream()
                for d in docs:
                    d.reference.delete()
            except Exception:
                pass
                
            # Reset ranked attempts for the week in this group
            docs = gcol(group_name, "ranked_attempts").where("week", "==", week).stream()
            for d in docs:
                d.reference.set({"attempts": 0, "name": d.to_dict().get("name", ""), "week": week}, merge=True)
            
            # Reset weekly scores in team profiles for this group
            docs = gcol(group_name, "teams").stream()
            for d in docs:
                d.reference.set({
                    "weekly_score": 0,
                    "games_played": 0
                }, merge=True)
            
            # Also clear the computed scores document for this week
            try:
                gcol(group_name, "team_scores_computed").document(week).delete()
            except Exception:
                pass
            
            # Reset ranked_best_{week} in all player profiles
            docs = gcol(group_name, "player_profiles").stream()
            rk = f"ranked_best_{week}"
            for d in docs:
                profile = d.to_dict()
                if profile.get(rk, 0) > 0:
                    d.reference.update({rk: 0})
            
            return None
        
        err = _fs_call(_reset_group_scores, timeout=15)
        if err:
            return jsonify({"ok": False, "error": "Failed to reset group scores"}), 500
    
    return jsonify({"ok": True, "group": group_name, "week": week, "message": f"All scores for {group_name} week {week} have been reset"})


@app.route("/admin/api/reset-week-scores", methods=["POST"])
@admin_required
def admin_api_reset_week_scores():
    """Reset all scores for the current week. Archives scores first."""
    group = get_admin_group()
    week = get_week_key()
    cache_invalidate("profile:", "leaderboard:", "team_lb:", "ranked:", "classmates:", "members:", "week_history:")
    
    # Archive scores before reset
    archive_week_scores(week, group)
    
    if USE_FIRESTORE:
        def _reset_scores():
            # Reset ALL leaderboard scores (delete all entries — old ones may lack week field)
            for diff in ["easy", "medium", "hard"]:
                docs = gcol(group, "leaderboard").document(diff).collection("scores").stream()
                for d in docs:
                    d.reference.delete()
            
            # Reset team leaderboard scores
            try:
                docs = gcol(group, "team_leaderboard").stream()
                for d in docs:
                    d.reference.delete()
            except Exception:
                pass
                
            # Reset ranked attempts for the week
            docs = gcol(group, "ranked_attempts").where("week", "==", week).stream()
            for d in docs:
                d.reference.set({"attempts": 0, "name": d.to_dict().get("name", ""), "week": week}, merge=True)
            
            # Reset weekly scores in team profiles
            docs = gcol(group, "teams").stream()
            for d in docs:
                d.reference.set({
                    "weekly_score": 0,
                    "games_played": 0
                }, merge=True)
            
            # Also clear the computed scores document for this week
            try:
                gcol(group, "team_scores_computed").document(week).delete()
            except Exception:
                pass
            
            # Reset ranked_best_{week} in all player profiles
            docs = gcol(group, "player_profiles").stream()
            rk = f"ranked_best_{week}"
            for d in docs:
                profile = d.to_dict()
                if profile.get(rk, 0) > 0:
                    d.reference.update({rk: 0})
            
            return None
        
        err = _fs_call(_reset_scores, timeout=15)
        if err:
            return jsonify({"ok": False, "error": "Failed to reset scores"}), 500
    
    return jsonify({"ok": True, "week": week, "message": f"All scores for week {week} have been reset"})


@app.route("/admin/api/players/bulk-reset-attempts", methods=["POST"])
@admin_required
def admin_api_bulk_reset_attempts():
    """Reset ranked attempts for all players."""
    group = get_admin_group()  # Use locked group
    cache_invalidate("ranked:")
    week = get_week_key()
    if USE_FIRESTORE:
        def _reset():
            docs = gcol(group, "ranked_attempts").where("week", "==", week).stream()
            for d in docs:
                d.reference.set({"attempts": 0}, merge=True)
        _fs_write(_reset, timeout=10)
    return jsonify({"ok": True, "week": week})


@app.route("/admin/api/save-week-snapshot", methods=["POST"])
@admin_required
def admin_api_save_week_snapshot():
    """Manually save current week's results to history."""
    group = get_admin_group()
    week = get_week_key()
    success = archive_week_scores(week, group)
    if success:
        return jsonify({"ok": True, "week": week, "message": "Week snapshot saved to history"})
    else:
        return jsonify({"error": "Failed to save snapshot"}), 500


@app.route("/admin/api/week-history", methods=["GET"])
@admin_required
def admin_api_week_history():
    """Get all archived week snapshots."""
    group = get_admin_group()
    history = get_week_history(group)
    weeks = sorted(history.items(), key=lambda x: x[0], reverse=True)
    
    result_weeks = []
    for w in weeks:
        archived_at = w[1].get("archived_at")
        # Convert Firestore timestamp to Unix timestamp
        archived_timestamp = None
        if archived_at:
            try:
                if hasattr(archived_at, 'timestamp'):
                    archived_timestamp = int(archived_at.timestamp())
                elif isinstance(archived_at, (int, float)):
                    archived_timestamp = int(archived_at)
            except Exception:
                pass
        
        result_weeks.append({
            "week": w[0],
            "archived_at": archived_timestamp,
            "team_count": len(w[1].get("team_leaderboard", {})),
            "easy_entries": len(w[1].get("leaderboard_easy", {})),
            "medium_entries": len(w[1].get("leaderboard_medium", {})),
            "hard_entries": len(w[1].get("leaderboard_hard", {})),
        })
    
    return jsonify({
        "ok": True,
        "weeks": result_weeks
    })


@app.route("/admin/api/ranked-scores-history", methods=["GET"])
@admin_required
def admin_api_ranked_scores_history():
    """Get all historic ranked scores for the admin's group."""
    group = get_admin_group()
    
    if not USE_FIRESTORE:
        return jsonify({"error": "Not available without Firebase"}), 503
    
    def _load_all_ranked_scores():
        """Load all player profiles and extract ranked scores for all weeks."""
        all_scores = {}  # week -> {individuals: [], teams: {}}
        
        # Get all player profiles
        prof_docs = gcol(group, "player_profiles").stream()
        for d in prof_docs:
            p = d.to_dict()
            name = p.get("name", d.id)
            team_id = p.get("team_id", "")
            team_name = p.get("team_name", "")
            
            # Find all ranked_best fields for all weeks
            for key, value in p.items():
                if key.startswith("ranked_best_") and isinstance(value, (int, float)) and value > 0:
                    week = key.replace("ranked_best_", "")
                    if week not in all_scores:
                        all_scores[week] = {"individuals": [], "teams": {}}
                    
                    # Add individual score
                    all_scores[week]["individuals"].append({
                        "name": name,
                        "score": int(value),
                        "team_id": team_id,
                        "team_name": team_name
                    })
                    
                    # Add to team total if player is on a team
                    if team_id and team_name:
                        if team_id not in all_scores[week]["teams"]:
                            all_scores[week]["teams"][team_id] = {
                                "team_name": team_name,
                                "team_id": team_id,
                                "total_score": 0,
                                "player_count": 0,
                                "players": []
                            }
                        all_scores[week]["teams"][team_id]["total_score"] += int(value)
                        all_scores[week]["teams"][team_id]["player_count"] += 1
                        all_scores[week]["teams"][team_id]["players"].append({
                            "name": name,
                            "score": int(value)
                        })
        
        # Sort each week
        for week in all_scores:
            # Sort individuals by score descending
            all_scores[week]["individuals"].sort(key=lambda x: (-x["score"], x["name"].lower()))
            
            # Convert teams dict to list and sort by total score descending
            team_list = list(all_scores[week]["teams"].values())
            team_list.sort(key=lambda x: (-x["total_score"], x["team_name"].lower()))
            # Sort players within each team
            for team in team_list:
                team["players"].sort(key=lambda x: (-x["score"], x["name"].lower()))
            all_scores[week]["teams"] = team_list
        
        return all_scores
    
    result = _fs_call(_load_all_ranked_scores, default={}, timeout=15)
    return jsonify({
        "ok": True,
        "weeks": result,
        "group": group
    })


@app.route("/admin/api/auto-backup-check", methods=["POST"])
@admin_required
def admin_api_auto_backup_check():
    """Check if weekly backup/reset should run and execute if needed.
    Called by admin frontend on page load and periodically.
    Runs Sunday 11:50PM–11:59PM UTC-6: archive snapshot for all groups.
    Runs Monday 00:00–00:10 UTC-6: full reset for all groups (new week)."""
    from datetime import timedelta
    now = datetime.now(timezone.utc) - timedelta(hours=6)  # UTC-6
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    hour = now.hour
    minute = now.minute

    # BUG 4 FIX: correct operator precedence with explicit parentheses
    is_sunday_backup_time = (weekday == 6) and (hour == 23) and (minute >= 50)
    is_monday_reset_time  = (weekday == 0) and (hour == 0)  and (minute <= 10)

    if is_sunday_backup_time:
        # Archive snapshot for all groups before reset
        results = {}
        for g in VALID_GROUPS:
            results[g] = save_weekly_snapshot(g)
        return jsonify({"ok": True, "action": "snapshot", "week": get_week_key(), "groups": results})

    if is_monday_reset_time:
        # Full reset for all groups: archive + wipe scores/attempts
        week = get_week_key()
        for g in VALID_GROUPS:
            # Archive first
            save_weekly_snapshot(g)
            cache_invalidate("profile:", "leaderboard:", "team_lb:", "ranked:", "classmates:", "members:", "week_history:", "week_scores:", "all_scores:")
            if USE_FIRESTORE:
                def _auto_reset(grp=g, wk=week):
                    for diff in ["easy", "medium", "hard"]:
                        docs = gcol(grp, "leaderboard").document(diff).collection("scores").stream()
                        for d in docs:
                            d.reference.delete()
                    docs = gcol(grp, "team_scores").document(wk).collection("scores").stream()
                    for d in docs:
                        d.reference.delete()
                    team_docs = gcol(grp, "teams").stream()
                    for d in team_docs:
                        d.reference.set({"weekly_score": 0, "games_played": 0}, merge=True)
                    att_docs = gcol(grp, "ranked_attempts").where("week", "==", wk).stream()
                    for d in att_docs:
                        d.reference.set({"attempts": 0, "name": d.to_dict().get("name", ""), "week": wk}, merge=True)
                    rk = f"ranked_best_{wk}"
                    prof_docs = gcol(grp, "player_profiles").stream()
                    for d in prof_docs:
                        if d.to_dict().get(rk, 0) > 0:
                            d.reference.update({rk: 0})
                    try:
                        gcol(grp, "team_scores_computed").document(wk).delete()
                    except Exception:
                        pass
                _fs_call(_auto_reset, timeout=20)
        return jsonify({"ok": True, "action": "reset", "week": week})

    return jsonify({"ok": False, "message": "Not backup/reset time", "weekday": weekday, "hour": hour, "minute": minute})


# ---- Auth API (server-side PIN) ----

@app.route("/api/auth", methods=["POST"])
def api_auth():
    """Server-side PIN auth: check if user exists, verify PIN, or register new PIN."""
    import re
    try:
        data = request.get_json(force=True, silent=True) or {}
    except Exception as e:
        print(f"[Auth] get_json error: {e}")
        data = {}
    print(f"[Auth] data keys: {list(data.keys())} action={data.get('action')} name={data.get('name','')[:10]}")
    group = str(data.get("group", "group1")).strip().lower()
    if group not in VALID_GROUPS: group = "group1"
    name = re.sub(r'[^\w\s]', '', str(data.get("name", "")).strip()).strip()[:20]
    pin = str(data.get("pin", "")).strip()[:6]
    action = str(data.get("action", "check")).strip()

    if not name:
        return jsonify({"ok": False, "error": "Name required"}), 400

    if action == "check":
        profile = get_profile(name, group)
        has_pin = bool(profile.get("pin"))
        resp = {"ok": True, "exists": has_pin, "name": name}
        if not has_pin and profile.get("team_name"):
            resp["pre_registered"] = True
            resp["team_name"] = profile.get("team_name", "")
            resp["team_color"] = profile.get("team_color", "")
        return jsonify(resp)

    if not pin or len(pin) < 4:
        return jsonify({"ok": False, "error": "PIN must be 4+ digits"}), 400

    if action == "register":
        profile = get_profile(name, group)
        if profile.get("pin"):
            return jsonify({"ok": False, "error": "User already exists. Enter your PIN."}), 409
        cache_invalidate(f"profile:{group}:{name}")
        if USE_FIRESTORE:
            _fs_write(lambda: gcol(group, "player_profiles").document(name).set({"name": name, "pin": pin}, merge=True))
        week = get_week_key()
        team = get_player_team(name, group)
        return jsonify({
            "ok": True, "name": name, "is_new": True,
            "team_id": team.get("team_id", "") if team else "",
            "team_name": team.get("team_name", "") if team else "",
            "team_color": team.get("team_color", "#f59e0b") if team else "",
            "ranked_attempts_left": 3,
        })

    if action == "login":
        profile = get_profile(name, group)
        stored_pin = profile.get("pin", "")
        if not stored_pin:
            return jsonify({"ok": False, "error": "No account found. Register first."}), 404
        if stored_pin != pin:
            return jsonify({"ok": False, "error": "Wrong PIN"}), 401
        week = get_week_key()
        team = get_player_team(name, group)
        attempts_used = get_ranked_attempts(name, week, group)
        return jsonify({
            "ok": True, "name": name, "is_new": False,
            "team_id": team.get("team_id", "") if team else "",
            "team_name": team.get("team_name", "") if team else "",
            "team_color": team.get("team_color", "#f59e0b") if team else "",
            "ranked_attempts_left": max(0, 3 - attempts_used),
            "avatar": profile.get("avatar", ""),
        })

    return jsonify({"ok": False, "error": "Invalid action"}), 400


# ---- Player profile API ----

@app.route("/api/profile", methods=["POST"])
def api_save_profile():
    """Save avatar or other profile fields."""
    data = request.get_json(force=True)
    group = data.get("group", "group1").strip().lower()
    if group not in VALID_GROUPS: group = "group1"
    name = str(data.get("name", "")).strip()[:20]
    if not name:
        return jsonify({"ok": False}), 400
    updates = {}
    if "avatar" in data:
        updates["avatar"] = str(data["avatar"])[:4]
    if updates and USE_FIRESTORE:
        cache_invalidate(f"profile:{group}:{name}", "leaderboard:")
        _fs_write(lambda: gcol(group, "player_profiles").document(name).set(updates, merge=True))
    return jsonify({"ok": True})


@app.route("/api/profile", methods=["GET"])
def api_get_profile():
    group = get_group()
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"profile": {}, "badges": BADGE_DEFS})
    profile = get_profile(name, group)
    week = get_week_key()
    team = get_player_team(name, group)
    if team:
        profile["team_id"] = team.get("team_id", "")
        profile["team_name"] = team.get("team_name", "")
        profile["team_color"] = team.get("team_color", "#f59e0b")
    attempts_used = get_ranked_attempts(name, week, group)
    profile["ranked_attempts_used"] = attempts_used
    profile["ranked_attempts_left"] = max(0, 3 - attempts_used)
    return jsonify({"profile": profile, "badges": BADGE_DEFS, "week": week})


@app.route("/api/ranked-check", methods=["GET"])
def api_ranked_check():
    group = get_group()
    name = request.args.get("name", "").strip()
    week = get_week_key()
    if not name:
        return jsonify({"ok": False, "attempts_left": 0})
    used = get_ranked_attempts(name, week, group)
    left = max(0, 3 - used)
    return jsonify({"ok": left > 0, "attempts_left": left, "attempts_used": used, "week": week})


# ---- Player team membership ----

@app.route("/api/player-team", methods=["GET"])
def api_get_player_team():
    group = get_group()
    name = request.args.get("name", "").strip()
    if not name:
        return jsonify({"team": None})
    team = get_player_team(name, group)
    return jsonify({"team": team})


@app.route("/api/player-team", methods=["POST"])
def api_set_player_team():
    data = request.get_json(force=True)
    group = data.get("group", "group1").strip().lower()
    if group not in VALID_GROUPS: group = "group1"
    name = str(data.get("name", "")).strip()[:20]
    team_id = str(data.get("team_id", "")).strip()
    team_name = str(data.get("team_name", "")).strip()[:30]
    team_color = str(data.get("team_color", "#f59e0b")).strip()[:20]
    if not name or not team_id:
        return jsonify({"ok": False}), 400
    set_player_team(name, team_id, team_name, team_color, group)
    return jsonify({"ok": True})


@app.route("/api/classmates", methods=["GET"])
def api_get_classmates():
    """Get all student profiles for comparison - shows name, avatar, team, badges, and stats."""
    group = get_group()
    week = get_week_key()
    ck = f"classmates:{group}:{week}"
    cached = cache_get(ck)
    if cached is not None:
        return jsonify({"classmates": cached, "week": week})
    
    classmates = []
    if USE_FIRESTORE:
        def _load_classmates():
            result = []
            docs = gcol(group, "player_profiles").stream()
            for d in docs:
                p = d.to_dict()
                # Get ranked best score for current week
                ranked_best = p.get(f"ranked_best_{week}", 0)
                # Get badges
                badge_ids = p.get("badges", [])
                badge_map = {b["id"]: b for b in BADGE_DEFS}
                badges = []
                for badge_id in badge_ids:
                    if badge_id in badge_map:
                        badge = badge_map[badge_id].copy()
                        badges.append(badge)
                
                result.append({
                    "name": p.get("name", d.id),
                    "avatar": p.get("avatar", ""),
                    "team_name": p.get("team_name", ""),
                    "team_color": p.get("team_color", "#f59e0b"),
                    "team_id": p.get("team_id", ""),
                    "total_games": p.get("total_games", 0),
                    "best_streak": p.get("best_streak", 0),
                    "ranked_best": ranked_best,
                    "badges": badges,
                    "badge_count": len(badges),
                })
            # Sort by ranked score descending, then by name
            result.sort(key=lambda x: (-x["ranked_best"], x["name"].lower()))
            return result
        classmates = _fs_call(_load_classmates, default=[], timeout=10) or []
    
    cache_set(ck, classmates, CACHE_TTL_MEMBERS)
    return jsonify({"classmates": classmates, "week": week})


@app.route("/api/team-members", methods=["GET"])
def api_team_members():
    """Return all players in a given team with their ranked best score this week."""
    group = get_group()
    team_id = request.args.get("team_id", "").strip()
    week = get_week_key()
    ck = f"members:team:{group}:{team_id}:{week}"
    cached = cache_get(ck)
    if cached is not None:
        return jsonify({"members": cached, "week": week})
    members = []
    if USE_FIRESTORE and team_id:
        def _load_team_members():
            m = []
            docs = gcol(group, "player_profiles").where("team_id", "==", team_id).stream()
            for d in docs:
                p = d.to_dict()
                m.append({
                    "name": p.get("name", d.id),
                    "best_score": p.get(f"ranked_best_{week}", 0),
                    "total_games": p.get("total_games", 0),
                    "best_streak": p.get("best_streak", 0),
                })
            m.sort(key=lambda x: x["best_score"], reverse=True)
            return m
        members = _fs_call(_load_team_members, default=[], timeout=8) or []
    cache_set(ck, members, CACHE_TTL_MEMBERS)
    return jsonify({"members": members, "week": week})


@app.route("/api/ranked-scores-all-weeks", methods=["GET"])
def api_ranked_scores_all_weeks():
    """Get all ranked scores for all weeks across all players."""
    group = get_group()
    
    if not USE_FIRESTORE:
        return jsonify({"error": "Not available without Firebase"}), 503
    
    def _load_all_ranked_scores():
        """Load all player profiles and extract ranked scores for all weeks."""
        all_scores = {}  # week -> list of {name, score, team_id, team_name}
        
        # Get all player profiles
        prof_docs = gcol(group, "player_profiles").stream()
        for d in prof_docs:
            p = d.to_dict()
            name = p.get("name", d.id)
            team_id = p.get("team_id", "")
            team_name = p.get("team_name", "")
            
            # Find all ranked_best fields for all weeks
            for key, value in p.items():
                if key.startswith("ranked_best_") and isinstance(value, (int, float)) and value > 0:
                    week = key.replace("ranked_best_", "")
                    if week not in all_scores:
                        all_scores[week] = []
                    all_scores[week].append({
                        "name": name,
                        "score": int(value),
                        "team_id": team_id,
                        "team_name": team_name
                    })
        
        # Sort each week by score descending
        for week in all_scores:
            all_scores[week].sort(key=lambda x: (-x["score"], x["name"].lower()))
        
        return all_scores
    
    result = _fs_call(_load_all_ranked_scores, default={}, timeout=15)
    return jsonify({"weeks": result})


# Register online duel events
from duel_server import register_duel_events
def _get_duel_words(difficulty, week):
    if week and int(week) > 0:
        return get_words_for_week(difficulty, int(week), "group1")
    from words import EASY_WORDS, MEDIUM_WORDS, HARD_WORDS
    return {"easy": EASY_WORDS, "medium": MEDIUM_WORDS, "hard": HARD_WORDS}.get(difficulty, EASY_WORDS)
register_duel_events(socketio, _get_duel_words)

if __name__ == "__main__":
    socketio.run(app, debug=True)


