# Cleanup Manifest - Development Artifacts to Remove

This file documents all development/debugging scripts that should be removed from production.

## Python Utility Scripts (60+ files)
These are one-off scripts used during development and debugging. They should be removed before deployment:

### Audio/TTS Related
- analyze_audio_quality.py
- cache_all_audio.py
- cache_easy_mode_audio.py
- check_audio.py
- check_audio_quality.py
- check_missing_tts.py
- check_robotic_audio.py
- check_tournament_audio.py
- check_tournament_audio_status.py
- debug_tournament_audio.py
- disable_robotic_tts.py
- emergency_audio_all_194.py
- emergency_audio_copy.py
- emergency_edge_tts_fix.py
- generate_all_missing_audio.py
- generate_audio.py
- generate_group3_audio.py
- generate_missing_sentences.py
- generate_student_sentence.py
- local_edge_tts.py
- precache_tournament_tts.py
- regenerate_all_audio.py
- regenerate_all_precached.py
- regenerate_sentence_audio.py
- scan_tts_implementations.py
- simple_precache_tts.py
- test_voices.py
- urgent_audio_fix.py

### Word/Tournament Related
- add_final_tournament_words.py
- analyze_tournament_words.py
- analyze_word_repetition.py
- categorize_tournament_words.py
- check_all_194_words.py
- check_all_groups.py
- check_tournament_ranked.py
- check_tournament_words.py
- clean_tournament_words.py
- compare_words.py
- count_missing_images.py
- count_words.py
- debug_get_group_words.py
- debug_group3.py
- debug_words_endpoint.py
- dedupe_tournament.py
- diagnose_word_mismatch.py
- find_extra_words.py
- fix_creation_feelings.py
- fix_duplicates.py
- fix_group3_words.py
- finalize_tournament.py
- generate_correct_words.py
- identify_issues.py
- simulate_mismatch.py
- update_tournament.py
- verify_categorized_tournament.py
- verify_tournament_fix.py

### Data/Database Related
- clear_leaderboards.py
- fix_data_issues.py
- fix_ranked_week.py
- fix_week_history.py
- manual_week_reset.py
- reset_leaderboards.py
- show_week2.py

### Testing/Debugging
- bug_finder.py
- debug_tournament_audio.py
- emergency_diagnosis.py
- emergency_fix.py
- simple_test.py
- test_bombs_endpoint.py
- test_correct_endpoints.py
- test_fixed_bombs.py
- test_game_flow.py
- test_images.py
- test_local_logic.py
- test_new_endpoint.py
- test_spell.mp3
- wait_and_test.py

### Image/Misc
- download_images.py
- fetch_images.py
- fix_css.py

## Documentation Files (20+ files)
These are development notes and should be archived or removed:

- ATTEMPTS_ANALYSIS.md
- BUG_FIX_SUMMARY.md
- BUG_REPORT.md
- COMMIT_PROJECT_APOLLO.txt
- DATA_ISSUES_REPORT.md
- EASY_MODE_AUDIO_PRELOAD.md
- HISTORY_DISPLAY_FIX.md
- RANKED_MODE_FIXES.md
- REPO_ORGANIZATION.md
- SCORE_SAVING_AUDIT.md
- SENTENCE_AUDIO_ISSUE.md
- SETUP_COMPLETE.md
- SPEECH_RECOGNITION_FIXES.md
- SYSTEM_FAILURE_POLICY.md
- TTS_CONFIG.md
- TTS_IMPLEMENTATION_STATUS.md
- TTS_IMPROVEMENTS.md
- TWO_BRANCHES_SETUP.md
- bomb_improvements.md

## Setup/Config Files (to review)
- FINAL_SETUP.sh
- run_setup.bat
- setup_branches.ps1

## Large Archive (to remove)
- lasalle-spelling-bee-current.zip (44.5 MB)

## Files to Keep
- .env.example
- .gitignore
- Procfile
- app.py
- words.py
- duel_server.py
- requirements.txt
- runtime.txt
- vercel.json
- railway.json
- custom_words.json
- word_images.json
- leaderboard.json
- teams.json
- api/
- audio/
- static/
- templates/

## Cleanup Instructions
1. Create a backup of the root directory
2. Remove all files listed above
3. Keep only the essential application files
4. Test deployment on Vercel
