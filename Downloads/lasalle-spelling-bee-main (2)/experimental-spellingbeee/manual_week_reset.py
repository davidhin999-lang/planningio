#!/usr/bin/env python3
"""
Manually reset the week:
1. Archive previous week's scores to history
2. Clear current leaderboard entries
3. Reset ranked attempts
4. Reset ranked_best_{previous_week} in player profiles
"""

import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app import (
    get_week_key, USE_FIRESTORE, gcol, _fs_call, _fs_write,
    archive_week_scores, VALID_GROUPS
)

def get_previous_week_key():
    """Get the previous week's ISO week key."""
    now = datetime.now(timezone.utc) - timedelta(hours=6)
    prev_week = now - timedelta(days=7)
    return prev_week.strftime("%G-W%V")

def manual_week_reset():
    """Manually perform week reset for all groups."""
    current_week = get_week_key()
    previous_week = get_previous_week_key()
    
    print(f"Current week: {current_week}")
    print(f"Previous week: {previous_week}")
    print()
    
    for group in VALID_GROUPS:
        print(f"\n{'='*60}")
        print(f"Processing group: {group}")
        print(f"{'='*60}")
        
        # Step 1: Archive previous week
        print(f"\n[1/4] Archiving previous week ({previous_week})...")
        try:
            success = archive_week_scores(previous_week, group)
            print(f"✓ Archive: {success}")
        except Exception as e:
            print(f"✗ Archive failed: {e}")
        
        # Step 2: Clear leaderboard entries
        print(f"\n[2/4] Clearing leaderboard entries...")
        if USE_FIRESTORE:
            def _clear_leaderboard():
                cleared = 0
                try:
                    for diff in ["easy", "medium", "hard"]:
                        docs = gcol(group, "leaderboard").document(diff).collection("scores").stream()
                        for d in docs:
                            d.reference.delete()
                            cleared += 1
                except Exception as e:
                    print(f"Error clearing leaderboard: {e}")
                return cleared
            
            cleared = _fs_call(_clear_leaderboard, default=0, timeout=10)
            print(f"✓ Cleared {cleared} leaderboard entries")
        
        # Step 3: Reset ranked attempts for previous week
        print(f"\n[3/4] Resetting ranked attempts for {previous_week}...")
        if USE_FIRESTORE:
            def _reset_attempts():
                reset = 0
                try:
                    docs = gcol(group, "ranked_attempts").where("week", "==", previous_week).stream()
                    for d in docs:
                        d.reference.set({"attempts": 0, "name": d.to_dict().get("name", ""), "week": previous_week}, merge=True)
                        reset += 1
                except Exception as e:
                    print(f"Error resetting attempts: {e}")
                return reset
            
            reset = _fs_call(_reset_attempts, default=0, timeout=10)
            print(f"✓ Reset {reset} ranked attempt records")
        
        # Step 4: Clear old ranked_best scores from player profiles
        print(f"\n[4/4] Clearing old ranked_best_{previous_week} from player profiles...")
        if USE_FIRESTORE:
            def _clear_old_scores():
                cleared = 0
                try:
                    rk = f"ranked_best_{previous_week}"
                    docs = gcol(group, "player_profiles").stream()
                    for d in docs:
                        p = d.to_dict()
                        if rk in p and p[rk] > 0:
                            d.reference.update({rk: 0})
                            cleared += 1
                except Exception as e:
                    print(f"Error clearing old scores: {e}")
                return cleared
            
            cleared = _fs_call(_clear_old_scores, default=0, timeout=10)
            print(f"✓ Cleared old scores from {cleared} player profiles")
        
        # Step 5: Reset team weekly scores
        print(f"\n[5/5] Resetting team weekly scores...")
        if USE_FIRESTORE:
            def _reset_team_scores():
                reset = 0
                try:
                    docs = gcol(group, "teams").stream()
                    for d in docs:
                        d.reference.set({"weekly_score": 0, "games_played": 0}, merge=True)
                        reset += 1
                except Exception as e:
                    print(f"Error resetting team scores: {e}")
                return reset
            
            reset = _fs_call(_reset_team_scores, default=0, timeout=10)
            print(f"✓ Reset weekly scores for {reset} teams")
        
        print(f"\n✓ Group {group} reset complete!")

if __name__ == "__main__":
    manual_week_reset()
    print("\n" + "="*60)
    print("Week reset complete! Scores from previous week are now archived.")
    print("Current week should now show only new scores.")
    print("="*60)
