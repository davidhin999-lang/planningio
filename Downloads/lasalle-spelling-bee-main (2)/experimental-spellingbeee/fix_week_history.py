#!/usr/bin/env python3
"""
Fix missing week history by:
1. Checking current and previous week keys
2. Manually archiving previous week's scores if they exist
3. Clearing old ranked_best scores from player profiles
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import (
    get_week_key, USE_FIRESTORE, gcol, _fs_call, _fs_write,
    archive_week_scores, VALID_GROUPS
)

def get_previous_week_key():
    """Get the previous week's ISO week key."""
    now = datetime.now(timezone.utc) - timedelta(hours=6)  # UTC-6
    prev_week = now - timedelta(days=7)
    return prev_week.strftime("%G-W%V")

def check_and_fix_week_history():
    """Check current/previous weeks and archive if needed."""
    current_week = get_week_key()
    previous_week = get_previous_week_key()
    
    print(f"Current week: {current_week}")
    print(f"Previous week: {previous_week}")
    print()
    
    for group in VALID_GROUPS:
        print(f"\n=== Group: {group} ===")
        
        # Check if previous week data exists in score_history
        def _check_history():
            try:
                doc = gcol(group, "score_history").document(previous_week).get()
                return doc.exists
            except Exception as e:
                print(f"Error checking history: {e}")
                return False
        
        history_exists = _fs_call(_check_history, default=False, timeout=5)
        print(f"Previous week ({previous_week}) in history: {history_exists}")
        
        if not history_exists:
            print(f"Archiving previous week ({previous_week}) scores...")
            success = archive_week_scores(previous_week, group)
            print(f"Archive result: {success}")
        
        # Check for old ranked_best scores in player profiles
        def _check_old_scores():
            old_scores = []
            try:
                docs = gcol(group, "player_profiles").stream()
                for d in docs:
                    p = d.to_dict()
                    old_rk = f"ranked_best_{previous_week}"
                    if old_rk in p and p[old_rk] > 0:
                        old_scores.append({
                            "name": p.get("name", d.id),
                            "score": p[old_rk],
                            "week": previous_week
                        })
            except Exception as e:
                print(f"Error checking old scores: {e}")
            return old_scores
        
        old_scores = _fs_call(_check_old_scores, default=[], timeout=8)
        if old_scores:
            print(f"Found {len(old_scores)} players with old week scores:")
            for score in old_scores[:5]:  # Show first 5
                print(f"  - {score['name']}: {score['score']} pts ({score['week']})")
        
        # Check current week leaderboard
        def _check_current_lb():
            count = 0
            try:
                for diff in ["easy", "medium", "hard"]:
                    docs = gcol(group, "leaderboard").document(diff).collection("scores").stream()
                    count += len(list(docs))
            except Exception as e:
                print(f"Error checking leaderboard: {e}")
            return count
        
        lb_count = _fs_call(_check_current_lb, default=0, timeout=8)
        print(f"Current leaderboard entries: {lb_count}")

if __name__ == "__main__":
    check_and_fix_week_history()
