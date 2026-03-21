# Repository Organization: Main vs Project Apollo

## Current Status

### lasalle-spelling-bee (Main Repo - Clean)
- **Branch:** main
- **Status:** Cleaned - sound effects removed
- **Features:**
  - ✅ Battle Arena UI (experimental multiplayer)
  - ✅ Online 1v1 duel system
  - ✅ Power-ups and scoring
  - ❌ Sound effects (removed)
  - ❌ Particle animations (removed)
  - ❌ Visual enhancements (removed)

### project-apollo (Experimental Repo)
- **Status:** To be created
- **Features:**
  - ✅ Battle Arena UI
  - ✅ Online 1v1 duel system
  - ✅ Power-ups and scoring
  - ✅ Sound effects (Web Audio API)
  - ✅ Particle animations
  - ✅ Visual enhancements
  - ✅ Word images

## Changes Made

### Removed from lasalle-spelling-bee:
1. Sound effect function calls from online_duel.js
2. Particle effect function calls from online_duel.js
3. Sound effect files (arena_sounds.js, arena_ui_sounds.js, arena_ambience.js) - added to .gitignore

### Kept in lasalle-spelling-bee:
1. Battle Arena UI and styling
2. Online multiplayer duel system
3. Power-ups and game mechanics
4. Word images integration

## Next Steps

1. Commit cleaned lasalle-spelling-bee
2. Create project-apollo repo as separate experimental branch
3. Reset main repo to original (remove Battle Arena if needed)
4. Test both repos for bugs
5. Document any issues found

## Testing Checklist

### lasalle-spelling-bee (Clean Version)
- [ ] Menu loads without errors
- [ ] Battle Arena button appears
- [ ] Lobby screens load correctly
- [ ] Game screen renders properly
- [ ] No console errors
- [ ] No sound errors (sounds removed)
- [ ] Power-ups work correctly
- [ ] Scoring system works
- [ ] Word images load (if endpoint available)

### project-apollo (Full Features)
- [ ] All features from clean version
- [ ] Sound effects play correctly
- [ ] Particle animations work
- [ ] Visual enhancements display
- [ ] No console errors
- [ ] No performance issues

## Deployment

- **Main Repo (lasalle-spelling-bee):** Deployed to Vercel via vercel-stable branch
- **Project Apollo:** Deployed to Render/Railway for experimental testing
