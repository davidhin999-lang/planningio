# Setup Completo: Dos Ramas en Un Solo Repo

## Estado Actual

✅ **Cambios realizados:**
- Removidos todos los efectos de sonido de `online_duel.js`
- Removidos script tags de sonidos de `index.html`
- Actualizado `.gitignore` para excluir archivos de sonido
- Documentación creada

## Próximos Pasos (Ejecutar en Terminal)

### PASO 1: Commit versión limpia en main
```bash
cd c:\Users\HP\Documents\lasalle-spelling-bee
git add .
git commit -m "Clean: Remove sound effects from Battle Arena

- Removed all ArenaSounds and ArenaParticles function calls
- Removed sound effect script tags from index.html
- Updated .gitignore to exclude sound files
- Kept Battle Arena UI and multiplayer features intact
- This is the stable version for Render/Vercel deployment"
git push origin main
```

### PASO 2: Crear rama project-apollo desde main
```bash
git checkout -b project-apollo
git push origin project-apollo
```

### PASO 3: Verificar que ambas ramas existen
```bash
git branch -a
```

### PASO 4: Proteger rama main en GitHub (MANUAL)
1. Ve a: https://github.com/davidhin999-lang/lasalle-spelling-bee/settings/branches
2. Haz click en "Add rule"
3. Branch name pattern: `main`
4. Habilita:
   - "Require pull request reviews before merging"
   - "Require status checks to pass before merging"
   - "Require branches to be up to date before merging"
5. Guarda los cambios

### PASO 5: Restaurar sonidos en rama project-apollo
```bash
git checkout project-apollo
```

Luego edita estos archivos:

**En `templates/index.html` (línea ~715):**
Descomentar o agregar:
```html
<script src="/static/arena_sounds.js"></script>
<script src="/static/arena_ui_sounds.js"></script>
<script src="/static/arena_ambience.js"></script>
```

**En `static/online_duel.js`:**
Descomentar las llamadas a `ArenaSounds` en:
- `odType()` - agregar sonido de tipeo
- `odBackspace()` - agregar sonido de borrado
- `odBeginRound()` - agregar sonido de inicio
- `odShowCountdown()` - agregar sonidos de cuenta regresiva
- `odUsePowerup()` - agregar sonidos de power-ups
- `odShowMyComplete()` - agregar sonido de victoria
- `odShowMatchOver()` - agregar sonidos de victoria/derrota

Luego:
```bash
git add .
git commit -m "PROJECT APOLLO: Add sound effects and visual enhancements

- Re-added arena_sounds.js (Web Audio API sound system)
- Re-added arena_ui_sounds.js (UI interaction sounds)
- Re-added arena_ambience.js (background particle effects)
- Re-enabled all sound effect calls in online_duel.js
- Re-enabled particle animations and visual effects
- This is the experimental version for local testing only"
git push origin project-apollo
```

## Estructura Final

```
lasalle-spelling-bee (un solo repo)
├── main (rama estable)
│   ├── Sin sonidos
│   ├── Sin efectos visuales
│   ├── Battle Arena UI funcional
│   ├── Multiplayer duel system
│   └── Protegida en GitHub (no cambios directos)
│
└── project-apollo (rama experimental)
    ├── Todos los cambios de main
    ├── + Sonidos (arena_sounds.js, etc.)
    ├── + Efectos visuales
    ├── + Animaciones de partículas
    └── Solo testing local (nunca se mergea a main)
```

## Flujo de Trabajo

**Para trabajar en experimentos:**
```bash
git checkout project-apollo
# ... hacer cambios ...
git add .
git commit -m "..."
git push origin project-apollo
```

**Para volver a la versión estable:**
```bash
git checkout main
# ... código limpio, sin sonidos ...
```

**Para mergear cambios a main:**
```bash
# Crear Pull Request en GitHub
# Revisar cambios
# Mergear manualmente (con protección)
```

## Testing

**lasalle-spelling-bee (main - Clean):**
- [ ] Run: `python app.py`
- [ ] Menu carga sin errores
- [ ] Battle Arena button funciona
- [ ] Multiplayer duel funciona end-to-end
- [ ] Sin errores de sonido (intencional)
- [ ] Power-ups y scoring funcionan

**project-apollo (experimental - Full Features):**
- [ ] Run: `python app.py` (puerto diferente)
- [ ] Todas las features de main funcionan
- [ ] Sonidos se reproducen correctamente
- [ ] Animaciones de partículas funcionan
- [ ] Sin errores en consola

---

**Status:** Listo para ejecutar comandos en terminal
**Creado:** March 12, 2026 at 10:12 PM UTC-06:00
