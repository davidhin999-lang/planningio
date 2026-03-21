#!/usr/bin/env python3
"""
Corrected diagnostic for tournament word-audio mismatches and ranked mode
"""

import os
import sys

# Add the project directory to path
sys.path.insert(0, os.path.dirname(__file__))

from words import get_group_words, get_ranked_words, get_words_for_week, GROUP_CONFIG, WORDS_PER_WEEK

def check_tournament_ranked_mode():
    print("=" * 80)
    print("TOURNAMENT RANKED MODE DIAGNOSTIC")
    print("=" * 80)
    
    # Get tournament configuration
    tournament_config = GROUP_CONFIG.get("tournament", {})
    ranked_week = tournament_config.get("ranked_week", 1)
    
    print(f"Tournament configuration:")
    print(f"  Ranked week: {ranked_week}")
    print(f"  Words per week: {WORDS_PER_WEEK}")
    
    # Get all tournament words
    easy_words = get_group_words("tournament", "easy")
    medium_words = get_group_words("tournament", "medium") 
    hard_words = get_group_words("tournament", "hard")
    
    print(f"\nTournament word counts:")
    print(f"  Easy: {len(easy_words)} words")
    print(f"  Medium: {len(medium_words)} words")
    print(f"  Hard: {len(hard_words)} words")
    print(f"  Total: {len(easy_words) + len(medium_words) + len(hard_words)} words")
    
    # Get ranked words for current week
    ranked_words = get_ranked_words("tournament")
    ranked_easy = ranked_words["easy"]
    ranked_medium = ranked_words["medium"]
    ranked_hard = ranked_words["hard"]
    
    print(f"\nRanked mode words (week {ranked_week}):")
    print(f"  Easy: {len(ranked_easy)} words")
    print(f"  Medium: {len(ranked_medium)} words")
    print(f"  Hard: {len(ranked_hard)} words")
    print(f"  Total: {len(ranked_easy) + len(ranked_medium) + len(ranked_hard)} words")
    
    # Check if ranked words are from tournament list
    print(f"\nChecking if ranked words come from tournament list:")
    
    easy_from_tournament = [w for w in ranked_easy if w in easy_words]
    medium_from_tournament = [w for w in ranked_medium if w in medium_words]
    hard_from_tournament = [w for w in ranked_hard if w in hard_words]
    
    print(f"  Easy ranked from tournament: {len(easy_from_tournament)}/{len(ranked_easy)}")
    print(f"  Medium ranked from tournament: {len(medium_from_tournament)}/{len(ranked_medium)}")
    print(f"  Hard ranked from tournament: {len(hard_from_tournament)}/{len(ranked_hard)}")
    
    # Show any non-tournament words
    if len(easy_from_tournament) != len(ranked_easy):
        non_tournament_easy = [w for w in ranked_easy if w not in easy_words]
        print(f"  Non-tournament easy words: {non_tournament_easy}")
    
    if len(medium_from_tournament) != len(ranked_medium):
        non_tournament_medium = [w for w in ranked_medium if w not in medium_words]
        print(f"  Non-tournament medium words: {non_tournament_medium}")
    
    if len(hard_from_tournament) != len(ranked_hard):
        non_tournament_hard = [w for w in ranked_hard if w not in hard_words]
        print(f"  Non-tournament hard words: {non_tournament_hard}")
    
    # Check weekly breakdown
    print(f"\nWeekly breakdown for tournament:")
    
    for difficulty, words in [("easy", easy_words), ("medium", medium_words), ("hard", hard_words)]:
        print(f"  {difficulty.capitalize()}:")
        week_count = (len(words) + WORDS_PER_WEEK - 1) // WORDS_PER_WEEK  # Ceiling division
        
        for week in range(1, min(week_count + 1, 4)):  # Show first 3 weeks max
            week_words = get_words_for_week(difficulty, week, "tournament")
            print(f"    Week {week}: {len(week_words)} words")
            if week == 1:  # Show first week words
                print(f"      Words: {', '.join(week_words[:5])}{'...' if len(week_words) > 5 else ''}")
        
        if week_count > 3:
            print(f"    ... and {week_count - 3} more weeks")
    
    # Verify ranked week is valid
    max_week = max(
        (len(easy_words) + WORDS_PER_WEEK - 1) // WORDS_PER_WEEK,
        (len(medium_words) + WORDS_PER_WEEK - 1) // WORDS_PER_WEEK,
        (len(hard_words) + WORDS_PER_WEEK - 1) // WORDS_PER_WEEK
    )
    
    print(f"\nRanked week validation:")
    print(f"  Current ranked week: {ranked_week}")
    print(f"  Max available weeks: {max_week}")
    
    if ranked_week > max_week:
        print(f"  WARNING: Ranked week exceeds available weeks!")
    else:
        print(f"  OK: Ranked week is valid")
    
    print(f"\n" + "=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    check_tournament_ranked_mode()
