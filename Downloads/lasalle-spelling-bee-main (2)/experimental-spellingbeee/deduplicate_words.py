#!/usr/bin/env python3
"""
Word deduplication and validation script.
Removes duplicates within groups and adds missing words to reach targets.
"""

# Target word counts per group
TARGETS = {
    "group1": 240,
    "group2": 200,
    "group3": 240,
    "group4": 300,
    "tournament": 200,
}

# Additional words to add to groups that fall short
ADDITIONAL_WORDS = {
    "group4": [
        # Additional words to reach 300 target
        "abbreviation", "abolition", "absorption", "abstraction", "acceleration",
        "acceptance", "accessibility", "accommodation", "accomplishment", "accordance",
        "accumulation", "accusation", "achievement", "acquisition", "activation",
        "adaptation", "addiction", "adjustment", "administration", "admiration",
        "admission", "adolescence", "advancement", "adversity", "advertisement",
        "advocacy", "affection", "affiliation", "affordability", "aggravation",
        "aggregation", "agitation", "agriculture", "alignment", "allegation",
        "allegiance", "allocation", "allowance", "allusion", "alteration",
        "alternation", "ambition", "ambivalence", "amendment", "amusement",
        "analogous", "analysis", "analytical", "ancestor", "ancillary",
        "anecdote", "anesthesia", "animation", "annihilation", "anniversary",
        "annotation", "announcement", "annoyance", "annuity", "anomaly",
        "anonymity", "antagonism", "antecedent", "antennae", "anthology",
        "anticipation", "antidote", "antiquity", "antiseptic", "antithesis",
        "anxiety", "anxiousness", "apathy", "aperture", "aphasia",
        "aphorism", "apocalypse", "apogee", "apologetic", "apology",
        "apoplexy", "apostasy", "apostle", "apostrophe", "appall",
        "apparatus", "apparel", "apparent", "apparition", "appeal",
        "appearance", "appeasement", "appellant", "appendage", "appendix",
        "appetite", "applaud", "applause", "apple", "appliance",
        "applicant", "application", "applique", "appoint", "appointment",
        "apportionment", "appraisal", "appreciate", "appreciation", "apprentice",
        "apprenticeship", "apprised", "apprising", "approach", "approbation",
        "appropriation", "approval", "approve", "approximate", "approximation",
        "apricot", "april", "apron", "apropos", "aptitude",
        "aquamarine", "aquarium", "aquatic", "aqueduct", "aqueous",
        "arabesque", "arable", "arachnid", "arbiter", "arbitrary",
        "arbitration", "arboreal", "arboretum", "arbor", "arbutus",
    ],
    "tournament": [
        # Additional words to reach 200 target
        "abbreviation", "abolition", "absorption", "abstraction", "acceleration",
        "acceptance", "accessibility", "accommodation", "accomplishment", "accordance",
        "accumulation", "accusation", "achievement", "acquisition", "activation",
        "adaptation", "addiction", "adjustment", "administration", "admiration",
        "admission", "adolescence", "advancement", "adversity", "advertisement",
        "advocacy", "affection", "affiliation", "affordability", "aggravation",
        "aggregation", "agitation", "agriculture", "alignment", "allegation",
        "allegiance", "allocation", "allowance", "allusion", "alteration",
        "alternation", "ambition", "ambivalence", "amendment", "amusement",
        "analogous", "analysis", "analytical", "ancestor", "ancillary",
        "anecdote", "anesthesia", "animation", "annihilation", "anniversary",
        "annotation", "announcement", "annoyance", "annuity", "anomaly",
        "anonymity", "antagonism", "antecedent", "antennae", "anthology",
        "anticipation", "antidote", "antiquity", "antiseptic", "antithesis",
        "anxiety", "anxiousness", "apathy", "aperture", "aphasia",
        "aphorism", "apocalypse", "apogee", "apologetic", "apology",
    ],
}

def deduplicate_list(words):
    """Remove duplicates while preserving order."""
    seen = set()
    unique = []
    for w in words:
        w_lower = w.lower()
        if w_lower not in seen:
            seen.add(w_lower)
            unique.append(w)
    return unique

def remove_cross_difficulty_duplicates(easy, medium, hard):
    """Remove words that appear in multiple difficulties."""
    easy_set = set(w.lower() for w in easy)
    medium_set = set(w.lower() for w in medium)
    hard_set = set(w.lower() for w in hard)
    
    # Medium should not contain easy words
    medium_filtered = [w for w in medium if w.lower() not in easy_set]
    
    # Hard should not contain easy or medium words
    hard_filtered = [w for w in hard if w.lower() not in easy_set and w.lower() not in medium_set]
    
    return easy, medium_filtered, hard_filtered

def analyze_group(group_name, easy, medium, hard):
    """Analyze and report on a group's word lists."""
    print(f"\n{'='*60}")
    print(f"GROUP: {group_name}")
    print(f"{'='*60}")
    
    # Check for internal duplicates
    easy_dupes = [w for w in easy if easy.count(w) > 1]
    medium_dupes = [w for w in medium if medium.count(w) > 1]
    hard_dupes = [w for w in hard if hard.count(w) > 1]
    
    if easy_dupes:
        print(f"⚠️  Easy has internal duplicates: {set(easy_dupes)}")
    if medium_dupes:
        print(f"⚠️  Medium has internal duplicates: {set(medium_dupes)}")
    if hard_dupes:
        print(f"⚠️  Hard has internal duplicates: {set(hard_dupes)}")
    
    # Check for cross-difficulty duplicates
    easy_set = set(w.lower() for w in easy)
    medium_set = set(w.lower() for w in medium)
    hard_set = set(w.lower() for w in hard)
    
    easy_medium = easy_set & medium_set
    medium_hard = medium_set & hard_set
    easy_hard = easy_set & hard_set
    
    if easy_medium:
        print(f"⚠️  Easy/Medium overlap: {easy_medium}")
    if medium_hard:
        print(f"⚠️  Medium/Hard overlap: {medium_hard}")
    if easy_hard:
        print(f"⚠️  Easy/Hard overlap: {easy_hard}")
    
    # Count words
    total = len(easy) + len(medium) + len(hard)
    target = TARGETS.get(group_name, 0)
    
    print(f"\nWord counts:")
    print(f"  Easy:   {len(easy):3d} words")
    print(f"  Medium: {len(medium):3d} words")
    print(f"  Hard:   {len(hard):3d} words")
    print(f"  Total:  {total:3d} words (target: {target})")
    
    if total < target * 0.9:
        deficit = target - total
        print(f"  ❌ DEFICIT: Need ~{deficit} more words")
    elif total < target:
        print(f"  ⚠️  Below target by {target - total} words")
    else:
        print(f"  ✅ Meets or exceeds target")
    
    return {
        "easy": easy,
        "medium": medium,
        "hard": hard,
        "total": total,
        "target": target,
    }

def print_deduplication_code(group_name, easy, medium, hard):
    """Print Python code to update the group in words.py."""
    print(f"\n# CODE FOR {group_name.upper()}:")
    print(f'"{group_name}": {{')
    print(f'    "label": "{group_name.title()}",')
    print(f'    "ranked_week": 1,')
    print(f'    "words": {{')
    print(f'        "easy": [')
    
    # Print easy words
    for i, word in enumerate(easy):
        if i % 5 == 0:
            print(f'            ', end='')
        print(f'"{word}", ', end='')
        if (i + 1) % 5 == 0:
            print()
    if len(easy) % 5 != 0:
        print()
    
    print(f'        ],')
    print(f'        "medium": [')
    
    # Print medium words
    for i, word in enumerate(medium):
        if i % 5 == 0:
            print(f'            ', end='')
        print(f'"{word}", ', end='')
        if (i + 1) % 5 == 0:
            print()
    if len(medium) % 5 != 0:
        print()
    
    print(f'        ],')
    print(f'        "hard": [')
    
    # Print hard words
    for i, word in enumerate(hard):
        if i % 5 == 0:
            print(f'            ', end='')
        print(f'"{word}", ', end='')
        if (i + 1) % 5 == 0:
            print()
    if len(hard) % 5 != 0:
        print()
    
    print(f'        ],')
    print(f'    }},')
    print(f'}},')

if __name__ == "__main__":
    print("WORD DEDUPLICATION ANALYSIS")
    print("=" * 60)
    
    # This script is meant to be run to analyze the current state
    # The actual deduplication will be done by editing words.py directly
    print("\nThis script provides analysis and code generation for deduplication.")
    print("Run with specific group analysis or use to generate updated code.")
