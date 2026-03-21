# Script para configurar dos ramas: main (estable) y project-apollo (experimentos)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP: Dos Ramas en Un Solo Repo" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# PASO 1: Commit versión limpia en main
Write-Host "`n[PASO 1] Committing cleaned version to main..." -ForegroundColor Yellow
cd "c:\Users\HP\Documents\lasalle-spelling-bee"

git add .
git commit -m "Clean: Remove sound effects from Battle Arena

- Removed all ArenaSounds and ArenaParticles function calls
- Removed sound effect script tags from index.html
- Updated .gitignore to exclude sound files
- Kept Battle Arena UI and multiplayer features intact
- This is the stable version for Render/Vercel deployment"

git push origin main
Write-Host "[PASO 1] Complete!" -ForegroundColor Green

# PASO 2: Crear rama project-apollo desde main
Write-Host "`n[PASO 2] Creating project-apollo branch..." -ForegroundColor Yellow
git checkout -b project-apollo
git push origin project-apollo
Write-Host "[PASO 2] Complete!" -ForegroundColor Green

# PASO 3: Verificar ramas
Write-Host "`n[PASO 3] Verifying branches..." -ForegroundColor Yellow
git branch -a
Write-Host "[PASO 3] Complete!" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nRamas creadas:" -ForegroundColor Yellow
Write-Host "  main           = Versión estable (sin sonidos)" -ForegroundColor White
Write-Host "  project-apollo = Experimentos (con sonidos y efectos)" -ForegroundColor White

Write-Host "`nProximos pasos:" -ForegroundColor Yellow
Write-Host "1. Restaurar sonidos en rama project-apollo" -ForegroundColor White
Write-Host "2. Proteger rama main en GitHub" -ForegroundColor White
Write-Host "3. Testear ambas ramas localmente" -ForegroundColor White
