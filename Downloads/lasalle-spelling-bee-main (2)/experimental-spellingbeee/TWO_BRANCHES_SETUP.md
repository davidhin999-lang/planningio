# Setup: Dos Ramas en Un Solo Repo

## Cambios Completados

✅ Removidos todos los efectos de sonido de `online_duel.js`
✅ Removidos script tags de sonidos de `index.html`
✅ Actualizado `.gitignore` para excluir archivos de sonido
✅ Documentación creada

## Comandos a Ejecutar (Copiar y Pegar en Terminal)

### Comando 1: Commit versión limpia en main
```
cd c:\Users\HP\Documents\lasalle-spelling-bee
git add .
git commit -m "Clean: Remove sound effects from Battle Arena - Removed all ArenaSounds and ArenaParticles function calls - Removed sound effect script tags from index.html - Updated .gitignore to exclude sound files - Kept Battle Arena UI and multiplayer features intact - This is the stable version for Render/Vercel deployment"
git push origin main
```

### Comando 2: Crear rama project-apollo
```
git checkout -b project-apollo
git push origin project-apollo
```

### Comando 3: Verificar ramas
```
git branch -a
```

## Estructura Final

```
lasalle-spelling-bee (un solo repo)
├── main (rama estable)
│   ├── Sin sonidos
│   ├── Sin efectos visuales
│   ├── Battle Arena UI funcional
│   └── Protegida en GitHub
│
└── project-apollo (rama experimental)
    ├── Todos los cambios de main
    ├── + Sonidos
    ├── + Efectos visuales
    └── Solo testing local
```

## Próximos Pasos

1. Ejecutar los comandos arriba
2. Restaurar sonidos en rama project-apollo
3. Testear ambas ramas localmente
4. Proteger rama main en GitHub (opcional)
