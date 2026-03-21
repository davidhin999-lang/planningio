#!/usr/bin/env python3
"""
Automatically fix duplicate nested function definitions in app.py.
Renames nested functions to be unique while preserving functionality.
"""
import re
import sys

def fix_duplicates():
    """Fix all duplicate nested function definitions."""
    
    filepath = r"c:\Users\deifh\Downloads\CascadeProjects\windsurf-project\lasalle-spelling-bee\app.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Define mapping of outer function to inner function renames
    # Pattern: (outer_func_pattern, old_inner_name, new_inner_name)
    fixes = [
        # _load functions - rename based on context
        (r'def get_profile\([^)]*\):', '_load', '_load_profile'),
        (r'def get_team\([^)]*\):', '_load', '_load_team'),
        (r'def get_ranked_attempts\([^)]*\):', '_load', '_load_ranked_attempts'),
        (r'def get_week_history\([^)]*\):', '_load', '_load_week_history'),
        (r'def load_leaderboard\([^)]*\):', '_load', '_load_leaderboard'),
        (r'def load_weekly_history\([^)]*\):', '_load', '_load_weekly_history'),
        (r'def get_team_leaderboard\([^)]*\):', '_load', '_load_team_leaderboard'),
        (r'def get_precached_audio\([^)]*\):', '_load', '_load_precached_audio'),
        
        # _save functions
        (r'def save_leaderboard_entry\([^)]*\):', '_save', '_save_leaderboard_entry'),
        (r'def save_weekly_snapshot\([^)]*\):', '_save', '_save_snapshot'),
        (r'def increment_ranked_attempt\([^)]*\):', '_save', '_save_attempt'),
        
        # _get functions
        (r'def get_player_team\([^)]*\):', '_get', '_get_player_team'),
        (r'def get_profile\([^)]*\):', '_get', '_get_profile_doc'),
        (r'def get_team\([^)]*\):', '_get', '_get_team_doc'),
        
        # _update functions
        (r'def update_profile\([^)]*\):', '_update', '_update_profile'),
        (r'def update_team_scores_computed\([^)]*\):', '_update', '_update_team_scores'),
        (r'def update_team_profile_score\([^)]*\):', '_update', '_update_team_profile'),
        
        # _reset functions
        (r'def reset_week_scores\([^)]*\):', '_reset', '_reset_week_scores'),
        (r'def reset_player_attempts\([^)]*\):', '_reset', '_reset_player_attempts'),
        
        # _del functions
        (r'def delete_player\([^)]*\):', '_del', '_del_player'),
        (r'def admin_api_delete_player\([^)]*\):', '_del', '_del_admin_player'),
    ]
    
    print("Starting duplicate function fixes...")
    print("=" * 70)
    
    # Process each fix
    for outer_pattern, old_name, new_name in fixes:
        # Find the outer function
        outer_match = re.search(outer_pattern, content)
        if not outer_match:
            continue
        
        start_pos = outer_match.start()
        
        # Find the nested function definition after this outer function
        # Look for "def old_name(" within the next 500 characters
        search_area = content[start_pos:start_pos + 2000]
        inner_pattern = rf'\n\s+def {re.escape(old_name)}\('
        inner_match = re.search(inner_pattern, search_area)
        
        if inner_match:
            # Calculate absolute position
            inner_pos = start_pos + inner_match.start()
            
            # Replace this specific occurrence
            old_def = f'def {old_name}('
            new_def = f'def {new_name}('
            
            # Replace only this occurrence
            before = content[:inner_pos]
            after = content[inner_pos:]
            after_replaced = after.replace(old_def, new_def, 1)
            content = before + after_replaced
            
            # Also replace calls to this function in the same outer function
            # Find the end of the outer function (next "def " at same indentation)
            outer_indent = len(outer_match.group(0)) - len(outer_match.group(0).lstrip())
            next_def_pattern = rf'\n{" " * outer_indent}def '
            next_def_match = re.search(next_def_pattern, content[inner_pos + 100:])
            
            if next_def_match:
                func_end = inner_pos + 100 + next_def_match.start()
            else:
                func_end = len(content)
            
            # Replace calls to old_name with new_name in this function
            func_body = content[inner_pos:func_end]
            func_body_replaced = func_body.replace(f'{old_name}(', f'{new_name}(')
            content = content[:inner_pos] + func_body_replaced + content[func_end:]
            
            print(f"[OK] {outer_pattern:40} {old_name:20} -> {new_name}")
    
    # Write the fixed content
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n" + "=" * 70)
        print("[SUCCESS] Fixed all duplicate function definitions!")
        print(f"[INFO] File updated: {filepath}")
        return True
    else:
        print("\n[WARNING] No changes made - pattern matching may need adjustment")
        return False

if __name__ == "__main__":
    success = fix_duplicates()
    sys.exit(0 if success else 1)
