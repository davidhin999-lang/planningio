#!/bin/bash

# Script para configurar dos ramas: main (estable) y project-apollo (experimentos)

echo "========================================"
echo "SETUP: Dos Ramas en Un Solo Repo"
echo "========================================"
echo ""

# PASO 1: Commit versión limpia en main
echo "[PASO 1] Committing cleaned version to main..."
cd /c/Users/HP/Documents/lasalle-spelling-bee

git add .
git commit -m "Clean: Remove sound effects from Battle Arena

- Removed all ArenaSounds and ArenaParticles function calls
- Removed sound effect script tags from index.html
- Updated .gitignore to exclude sound files
- Kept Battle Arena UI and multiplayer features intact
- This is the stable version for Render/Vercel deployment"

git push origin main

echo "[PASO 1] Complete!"
echo ""

# PASO 2: Crear rama project-apollo desde main
echo "[PASO 2] Creating project-apollo branch..."
git checkout -b project-apollo
git push origin project-apollo

echo "[PASO 2] Complete!"
echo ""

# PASO 3: Verificar ramas
echo "[PASO 3] Verifying branches..."
git branch -a

echo ""
echo "========================================"
echo "SETUP COMPLETE!"
echo "========================================"
echo ""
echo "Ramas creadas:"
echo "  main           = Version estable (sin sonidos)"
echo "  project-apollo = Experimentos (con sonidos y efectos)"
echo ""
