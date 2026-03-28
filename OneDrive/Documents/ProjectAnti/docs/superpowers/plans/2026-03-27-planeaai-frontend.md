# PlaneaAI Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the complete PlaneaAI React frontend — landing page, auth, dashboard, generate flow, plan viewer, billing, and school admin — as a polished, SEP-teacher-targeted SaaS UI.

**Architecture:** React + Vite SPA with Firebase Auth (ID token → Bearer), Axios API client pointed at the Flask backend, Tailwind CSS + shadcn/ui component primitives. AuthContext provides `{ currentUser, subscription, loading }` app-wide; all protected routes redirect to `/login` if unauthenticated.

**Tech Stack:** React 18, Vite 5, Tailwind CSS 3, shadcn/ui, react-router-dom 6, Firebase SDK 10, Axios, react-hot-toast, @testing-library/react, vitest

---

## Design System Reference

**Color tokens (defined in `tailwind.config.js`):**
```
primary:     #4338CA  (Indigo 700)
primary-50:  #EEF2FF
primary-100: #E0E7FF
accent:      #D97706  (Amber 600)
accent-50:   #FFFBEB
success:     #059669
error:       #DC2626
bg:          #FAFAF9  (warm white)
surface:     #FFFFFF
text:        #1C1917
muted:       #78716C
border:      #E7E5E4
```

**Typography:** Inter (Google Fonts) — base 16px, line-height 1.5, headings 600–700 weight.

**Spacing/radius:** 4px grid, rounded-lg (8px) for cards/inputs, rounded-xl (12px) for modals.

**Accessibility:** 4.5:1 contrast minimum, visible focus rings (2px indigo), all buttons ≥44×44px touch target, aria-labels on icon-only buttons.

---

## File Map

```
frontend/
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── components.json                  # shadcn/ui config
├── src/
│   ├── main.jsx
│   ├── App.jsx                      # Routes + auth guard
│   ├── lib/
│   │   ├── firebase.js              # Firebase app + auth instance
│   │   ├── api.js                   # Axios instance (auto Bearer token)
│   │   └── utils.js                 # cn() helper, formatDate
│   ├── context/
│   │   └── AuthContext.jsx          # currentUser, subscription, loading
│   ├── pages/
│   │   ├── Landing.jsx              # Public marketing page
│   │   ├── Login.jsx                # Email/password + Google OAuth
│   │   ├── Dashboard.jsx            # Plan list + usage badge
│   │   ├── Generate.jsx             # Form → loading → result
│   │   ├── PlanView.jsx             # Single plan reader
│   │   ├── Billing.jsx              # Pricing cards + manage subscription
│   │   └── AdminSchool.jsx          # Escuela admin: seat management
│   ├── components/
│   │   ├── NavBar.jsx               # Top nav with user menu + UsageBadge
│   │   ├── GenerateForm.jsx         # subject/grade/topic/objective form
│   │   ├── PlanCard.jsx             # Dashboard list item
│   │   ├── PlanRenderer.jsx         # Renders planeación JSONB into sections
│   │   ├── UsageBadge.jsx           # "3 / 5 planeaciones este mes"
│   │   └── UpgradeModal.jsx         # Auto-opens on 403 limit_reached
│   └── __tests__/
│       ├── AuthContext.test.jsx
│       ├── GenerateForm.test.jsx
│       ├── PlanRenderer.test.jsx
│       ├── UsageBadge.test.jsx
│       └── UpgradeModal.test.jsx
```

---

## Task 1: Project Scaffold

**Files:**
- Create: `frontend/` (root)
- Create: `frontend/vite.config.js`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/components.json`
- Create: `frontend/src/lib/utils.js`

- [ ] **Step 1: Scaffold Vite + React project**

```bash
cd "c:/Users/deifh/OneDrive/Documents/ProjectAnti"
npm create vite@latest frontend -- --template react
cd frontend
npm install
```

- [ ] **Step 2: Install all dependencies**

```bash
npm install react-router-dom axios firebase react-hot-toast clsx tailwind-merge
npm install -D tailwindcss postcss autoprefixer @tailwindcss/forms vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
npx tailwindcss init -p
```

- [ ] **Step 3: Install shadcn/ui**

```bash
npx shadcn@latest init
```
When prompted: TypeScript → No, style → Default, base color → Slate, CSS variables → Yes.

- [ ] **Step 4: Install shadcn/ui components used in the app**

```bash
npx shadcn@latest add button input label select textarea card badge dialog separator avatar dropdown-menu progress
```

- [ ] **Step 5: Write `tailwind.config.js`**

This runs AFTER shadcn/ui init so we extend its generated config rather than replace it.
shadcn/ui init generates a `tailwind.config.js` — open it and replace its full contents with:

```js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      // shadcn/ui CSS variable mappings (do not remove — shadcn components use these)
      colors: {
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: { DEFAULT: 'hsl(var(--card))', foreground: 'hsl(var(--card-foreground))' },
        popover: { DEFAULT: 'hsl(var(--popover))', foreground: 'hsl(var(--popover-foreground))' },
        secondary: { DEFAULT: 'hsl(var(--secondary))', foreground: 'hsl(var(--secondary-foreground))' },
        muted: { DEFAULT: 'hsl(var(--muted))', foreground: 'hsl(var(--muted-foreground))' },
        destructive: { DEFAULT: 'hsl(var(--destructive))', foreground: 'hsl(var(--destructive-foreground))' },
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        // PlaneaAI brand tokens
        primary: {
          DEFAULT: '#4338CA',
          50: '#EEF2FF',
          100: '#E0E7FF',
          600: '#4F46E5',
          700: '#4338CA',
          800: '#3730A3',
          foreground: '#FFFFFF',
        },
        accent: {
          DEFAULT: '#D97706',
          50: '#FFFBEB',
          100: '#FEF3C7',
          foreground: '#FFFFFF',
        },
        bg: '#FAFAF9',
        surface: '#FFFFFF',
        'text-primary': '#1C1917',
        border: '#E7E5E4',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
```

- [ ] **Step 6: Write `src/index.css`**

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-bg text-text-primary font-sans;
  }
  *:focus-visible {
    @apply outline-2 outline-primary outline-offset-2;
  }
}
```

- [ ] **Step 7: Write `src/lib/utils.js`**

```js
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatDate(isoString) {
  return new Date(isoString).toLocaleDateString('es-MX', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

export function gradeLabel(grade) {
  const map = {
    preescolar_1: 'Preescolar 1°', preescolar_2: 'Preescolar 2°', preescolar_3: 'Preescolar 3°',
    primaria_1: 'Primaria 1°', primaria_2: 'Primaria 2°', primaria_3: 'Primaria 3°',
    primaria_4: 'Primaria 4°', primaria_5: 'Primaria 5°', primaria_6: 'Primaria 6°',
    secundaria_1: 'Secundaria 1°', secundaria_2: 'Secundaria 2°', secundaria_3: 'Secundaria 3°',
    preparatoria_1: 'Preparatoria 1°', preparatoria_2: 'Preparatoria 2°', preparatoria_3: 'Preparatoria 3°',
  }
  return map[grade] ?? grade
}
```

- [ ] **Step 8: Configure vitest in `vite.config.js`**

```js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000',
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/__tests__/setup.js'],
  },
})
```

- [ ] **Step 9: Create test setup file**

```js
// src/__tests__/setup.js
import '@testing-library/jest-dom'
```

- [ ] **Step 10: Verify dev server starts**

```bash
npm run dev
```
Expected: Vite server running at http://localhost:5173 with no errors.

- [ ] **Step 11: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold PlaneaAI frontend with Vite + React + Tailwind + shadcn/ui"
```

---

## Task 2: Firebase Auth + API Client

**Files:**
- Create: `frontend/src/lib/firebase.js`
- Create: `frontend/src/lib/api.js`
- Create: `frontend/.env.example`

- [ ] **Step 1: Write `src/lib/firebase.js`**

```js
import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
}

const app = initializeApp(firebaseConfig)
export const auth = getAuth(app)
export default app
```

- [ ] **Step 2: Write `src/lib/api.js`**

```js
import axios from 'axios'
import { auth } from './firebase'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? '/api',
})

api.interceptors.request.use(async (config) => {
  const user = auth.currentUser
  if (user) {
    const token = await user.getIdToken()
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api
```

- [ ] **Step 3: Write `.env.example`**

```
VITE_FIREBASE_API_KEY=
VITE_FIREBASE_AUTH_DOMAIN=
VITE_FIREBASE_PROJECT_ID=
VITE_FIREBASE_STORAGE_BUCKET=
VITE_FIREBASE_MESSAGING_SENDER_ID=
VITE_FIREBASE_APP_ID=
VITE_API_URL=http://localhost:5000/api
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/lib/ frontend/.env.example
git commit -m "feat: add Firebase auth client and Axios API instance"
```

---

## Task 3: AuthContext

**Files:**
- Create: `frontend/src/context/AuthContext.jsx`
- Create: `frontend/src/__tests__/AuthContext.test.jsx`

- [ ] **Step 1: Write the failing test**

```jsx
// src/__tests__/AuthContext.test.jsx
import { render, screen, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '../context/AuthContext'

// Mock Firebase
vi.mock('../lib/firebase', () => ({ auth: {} }))
vi.mock('firebase/auth', () => ({
  onAuthStateChanged: vi.fn((auth, cb) => { cb(null); return () => {} }),
}))
vi.mock('../lib/api', () => ({
  default: { post: vi.fn().mockResolvedValue({ data: { subscription: { plan: 'free', status: 'active' } } }) },
}))

function TestComponent() {
  const { currentUser, subscription, loading } = useAuth()
  if (loading) return <div>loading</div>
  return <div>{currentUser ? 'logged-in' : 'logged-out'} {subscription?.plan}</div>
}

test('shows logged-out state when no Firebase user', async () => {
  render(<AuthProvider><TestComponent /></AuthProvider>)
  await waitFor(() => expect(screen.queryByText('loading')).not.toBeInTheDocument())
  expect(screen.getByText('logged-out')).toBeInTheDocument()
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npx vitest run src/__tests__/AuthContext.test.jsx
```
Expected: FAIL — `AuthProvider` not found.

- [ ] **Step 3: Write `src/context/AuthContext.jsx`**

```jsx
import { createContext, useContext, useEffect, useState } from 'react'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from '../lib/firebase'
import api from '../lib/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null)
  const [subscription, setSubscription] = useState({ plan: 'free', status: 'active' })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setCurrentUser(user)
      if (user) {
        try {
          const { data } = await api.post('/auth/sync')
          setSubscription(data.subscription)
        } catch {
          // keep default free subscription if sync fails
        }
      } else {
        setSubscription({ plan: 'free', status: 'active' })
      }
      setLoading(false)
    })
    return unsubscribe
  }, [])

  return (
    <AuthContext.Provider value={{ currentUser, subscription, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
npx vitest run src/__tests__/AuthContext.test.jsx
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/context/ frontend/src/__tests__/AuthContext.test.jsx
git commit -m "feat: add AuthContext with Firebase onAuthStateChanged and /auth/sync"
```

---

## Task 4: App Shell — Router + Auth Guard

**Files:**
- Modify: `frontend/src/main.jsx`
- Modify: `frontend/src/App.jsx`

- [ ] **Step 1: Write `src/main.jsx`**

```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
        <Toaster position="top-right" />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
)
```

- [ ] **Step 2: Write `src/App.jsx`**

```jsx
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Generate from './pages/Generate'
import PlanView from './pages/PlanView'
import Billing from './pages/Billing'
import AdminSchool from './pages/AdminSchool'

function RequireAuth({ children }) {
  const { currentUser, loading } = useAuth()
  if (loading) return (
    <div className="min-h-screen bg-bg flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" aria-label="Cargando" />
    </div>
  )
  return currentUser ? children : <Navigate to="/login" replace />
}

function RequireSchoolAdmin({ children }) {
  const { subscription } = useAuth()
  if (subscription.plan !== 'escuela') return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  const { currentUser, loading } = useAuth()

  if (loading) return (
    <div className="min-h-screen bg-bg flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" aria-label="Cargando" />
    </div>
  )

  return (
    <Routes>
      <Route path="/" element={currentUser ? <Navigate to="/dashboard" replace /> : <Landing />} />
      <Route path="/login" element={currentUser ? <Navigate to="/dashboard" replace /> : <Login />} />
      <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
      <Route path="/generate" element={<RequireAuth><Generate /></RequireAuth>} />
      <Route path="/plan/:id" element={<RequireAuth><PlanView /></RequireAuth>} />
      <Route path="/billing" element={<RequireAuth><Billing /></RequireAuth>} />
      <Route path="/admin/school" element={<RequireAuth><RequireSchoolAdmin><AdminSchool /></RequireSchoolAdmin></RequireAuth>} />
    </Routes>
  )
}
```

- [ ] **Step 3: Verify app compiles**

```bash
npm run dev
```
Expected: No errors, `http://localhost:5173` shows a blank page (pages not yet implemented).

- [ ] **Step 4: Commit**

```bash
git add frontend/src/main.jsx frontend/src/App.jsx
git commit -m "feat: add app shell with auth-guarded routing"
```

---

## Task 5: NavBar + UsageBadge

**Files:**
- Create: `frontend/src/components/NavBar.jsx`
- Create: `frontend/src/components/UsageBadge.jsx`
- Create: `frontend/src/__tests__/UsageBadge.test.jsx`

- [ ] **Step 1: Write failing test for UsageBadge**

```jsx
// src/__tests__/UsageBadge.test.jsx
import { render, screen } from '@testing-library/react'
import UsageBadge from '../components/UsageBadge'

test('shows usage count for free plan', () => {
  render(<UsageBadge used={3} limit={5} plan="free" />)
  expect(screen.getByText(/3 \/ 5/)).toBeInTheDocument()
})

test('hidden for pro plan', () => {
  const { container } = render(<UsageBadge used={999} limit={null} plan="pro" />)
  expect(container.firstChild).toBeNull()
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npx vitest run src/__tests__/UsageBadge.test.jsx
```
Expected: FAIL.

- [ ] **Step 3: Write `src/components/UsageBadge.jsx`**

```jsx
export default function UsageBadge({ used, limit, plan }) {
  if (plan !== 'free') return null
  const pct = (used / limit) * 100
  const color = pct >= 80 ? 'text-red-600 bg-red-50 border-red-200' : 'text-muted bg-surface border-border'

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border ${color}`}>
      <span>{used} / {limit}</span>
      <span className="hidden sm:inline">planeaciones este mes</span>
    </span>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
npx vitest run src/__tests__/UsageBadge.test.jsx
```
Expected: PASS.

- [ ] **Step 5: Write `src/components/NavBar.jsx`**

```jsx
import { Link, useNavigate } from 'react-router-dom'
import { signOut } from 'firebase/auth'
import { auth } from '../lib/firebase'
import { useAuth } from '../context/AuthContext'
import UsageBadge from './UsageBadge'
import { Button } from './ui/button'
import {
  DropdownMenu, DropdownMenuContent,
  DropdownMenuItem, DropdownMenuSeparator, DropdownMenuTrigger
} from './ui/dropdown-menu'
import { Avatar, AvatarFallback } from './ui/avatar'

export default function NavBar({ usageStats }) {
  const { currentUser, subscription } = useAuth()
  const navigate = useNavigate()

  const initials = currentUser?.displayName
    ? currentUser.displayName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : currentUser?.email?.[0]?.toUpperCase() ?? '?'

  async function handleSignOut() {
    await signOut(auth)
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-30 bg-surface border-b border-border">
      <nav className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between" aria-label="Navegación principal">
        <Link to="/dashboard" className="flex items-center gap-2 font-semibold text-text-primary">
          <span className="text-primary text-xl">✦</span>
          <span>PlaneaAI</span>
        </Link>

        <div className="flex items-center gap-3">
          {usageStats && (
            <UsageBadge
              used={usageStats.used}
              limit={usageStats.limit}
              plan={subscription.plan}
            />
          )}

          <Button asChild size="sm" className="hidden sm:inline-flex">
            <Link to="/generate">Nueva planeación</Link>
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                className="rounded-full focus-visible:outline-2 focus-visible:outline-primary"
                aria-label="Menú de usuario"
              >
                <Avatar className="h-8 w-8">
                  <AvatarFallback className="bg-primary-100 text-primary text-xs font-semibold">
                    {initials}
                  </AvatarFallback>
                </Avatar>
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <div className="px-2 py-1.5">
                <p className="text-xs text-muted truncate">{currentUser?.email}</p>
                <p className="text-xs font-medium mt-0.5 capitalize">{subscription.plan}</p>
              </div>
              <DropdownMenuSeparator />
              <DropdownMenuItem asChild>
                <Link to="/dashboard">Mis planeaciones</Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link to="/billing">Suscripción</Link>
              </DropdownMenuItem>
              {subscription.plan === 'escuela' && (
                <DropdownMenuItem asChild>
                  <Link to="/admin/school">Mi escuela</Link>
                </DropdownMenuItem>
              )}
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleSignOut} className="text-red-600 cursor-pointer">
                Cerrar sesión
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </nav>
    </header>
  )
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/NavBar.jsx frontend/src/components/UsageBadge.jsx frontend/src/__tests__/UsageBadge.test.jsx
git commit -m "feat: add NavBar and UsageBadge components"
```

---

## Task 6: Landing Page

**Files:**
- Create: `frontend/src/pages/Landing.jsx`

- [ ] **Step 1: Write `src/pages/Landing.jsx`**

```jsx
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'

const features = [
  {
    icon: '📋',
    title: 'Formato SEP exacto',
    desc: 'Genera planeaciones alineadas a la Nueva Escuela Mexicana (NEM 2022), Plan 2011 y Plan 2017.',
  },
  {
    icon: '⚡',
    title: 'Lista en segundos',
    desc: 'Solo ingresa materia, grado, tema y propósito. El resto lo hace la IA en menos de 10 segundos.',
  },
  {
    icon: '📚',
    title: 'Historial completo',
    desc: 'Todas tus planeaciones guardadas, buscables y reutilizables cuando las necesites.',
  },
  {
    icon: '🏫',
    title: 'Para toda la escuela',
    desc: 'El plan Escuela permite hasta 20 docentes bajo un mismo administrador.',
  },
]

const plans = [
  {
    name: 'Gratis',
    price: '$0',
    period: 'para siempre',
    features: ['5 planeaciones al mes', 'Todos los grados y materias', 'Historial de planeaciones'],
    cta: 'Empezar gratis',
    href: '/login',
    highlight: false,
  },
  {
    name: 'Pro',
    price: '$149',
    period: 'MXN / mes',
    features: ['Planeaciones ilimitadas', 'Todos los grados y materias', 'Historial completo', 'Soporte prioritario'],
    cta: 'Comenzar prueba',
    href: '/login',
    highlight: true,
  },
  {
    name: 'Escuela',
    price: '$799',
    period: 'MXN / mes',
    features: ['Hasta 20 docentes', 'Panel de administrador', 'Planeaciones ilimitadas', 'Factura fiscal disponible'],
    cta: 'Contactar',
    href: '/login',
    highlight: false,
  },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-bg">
      {/* Nav */}
      <header className="sticky top-0 z-30 bg-surface/90 backdrop-blur border-b border-border">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <span className="flex items-center gap-2 font-semibold text-text-primary">
            <span className="text-primary text-xl">✦</span>
            PlaneaAI
          </span>
          <div className="flex items-center gap-3">
            <Button variant="ghost" asChild size="sm">
              <Link to="/login">Iniciar sesión</Link>
            </Button>
            <Button asChild size="sm">
              <Link to="/login">Empezar gratis</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-4 pt-20 pb-16 text-center">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-primary-50 text-primary text-sm font-medium mb-6">
          ✦ Alineado a NEM 2022 · Plan 2011 · Plan 2017
        </span>
        <h1 className="text-4xl sm:text-5xl font-bold text-text-primary leading-tight mb-5">
          Tu planeación didáctica<br className="hidden sm:block" />
          <span className="text-primary"> lista en segundos</span>
        </h1>
        <p className="text-lg text-muted max-w-2xl mx-auto mb-8">
          PlaneaAI genera planeaciones didácticas completas y en el formato exacto que pide la SEP —
          solo dile la materia, grado, tema y propósito.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Button asChild size="lg" className="text-base px-8">
            <Link to="/login">Generar mi primera planeación →</Link>
          </Button>
          <Button asChild variant="outline" size="lg" className="text-base px-8">
            <a href="#precios">Ver precios</a>
          </Button>
        </div>

        {/* Demo card */}
        <div className="mt-12 bg-surface rounded-2xl border border-border shadow-sm p-6 text-left max-w-2xl mx-auto">
          <div className="flex items-center gap-2 mb-4">
            <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
            <span className="w-2.5 h-2.5 rounded-full bg-green-400" />
            <span className="ml-2 text-xs text-muted">PlaneaAI · Matemáticas 3° · Fracciones</span>
          </div>
          <div className="space-y-3 text-sm">
            {[
              { label: 'Propósito', value: 'El alumno identificará fracciones equivalentes usando materiales concretos.' },
              { label: 'Inicio (10 min)', value: 'Exploración con círculos fraccionarios: los alumnos comparan ½ y 2/4...' },
              { label: 'Desarrollo (30 min)', value: 'En parejas, los alumnos completan una tabla de fracciones equivalentes...' },
              { label: 'Cierre (10 min)', value: 'Plenaria: cada equipo comparte una fracción equivalente que descubrió...' },
            ].map(({ label, value }) => (
              <div key={label}>
                <span className="font-semibold text-text-primary">{label}: </span>
                <span className="text-muted">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-center text-text-primary mb-10">
          Todo lo que necesitas, nada que no necesitas
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map(({ icon, title, desc }) => (
            <div key={title} className="bg-surface rounded-xl border border-border p-5">
              <span className="text-2xl mb-3 block">{icon}</span>
              <h3 className="font-semibold text-text-primary mb-1">{title}</h3>
              <p className="text-sm text-muted leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="precios" className="max-w-5xl mx-auto px-4 py-16">
        <h2 className="text-2xl font-bold text-center text-text-primary mb-2">Precios</h2>
        <p className="text-center text-muted mb-10">Empieza gratis, actualiza cuando quieras.</p>
        <div className="grid sm:grid-cols-3 gap-6">
          {plans.map(({ name, price, period, features, cta, href, highlight }) => (
            <div
              key={name}
              className={`rounded-2xl border p-6 flex flex-col ${
                highlight
                  ? 'border-primary bg-primary-50 shadow-md shadow-primary/10'
                  : 'border-border bg-surface'
              }`}
            >
              {highlight && (
                <span className="self-start px-2.5 py-0.5 rounded-full bg-primary text-white text-xs font-semibold mb-3">
                  Más popular
                </span>
              )}
              <h3 className="font-semibold text-text-primary">{name}</h3>
              <div className="mt-2 mb-4">
                <span className="text-3xl font-bold text-text-primary">{price}</span>
                <span className="text-sm text-muted ml-1">{period}</span>
              </div>
              <ul className="space-y-2 flex-1 mb-6">
                {features.map(f => (
                  <li key={f} className="flex items-start gap-2 text-sm text-muted">
                    <span className="text-primary mt-0.5">✓</span>
                    {f}
                  </li>
                ))}
              </ul>
              <Button
                asChild
                variant={highlight ? 'default' : 'outline'}
                className="w-full"
              >
                <Link to={href}>{cta}</Link>
              </Button>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8 mt-8">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-muted">
          <span className="flex items-center gap-1.5 font-medium text-text-primary">
            <span className="text-primary">✦</span> PlaneaAI
          </span>
          <span>© {new Date().getFullYear()} PlaneaAI · Hecho para docentes mexicanos</span>
        </div>
      </footer>
    </div>
  )
}
```

- [ ] **Step 2: Verify landing page renders**

```bash
npm run dev
```
Visit `http://localhost:5173` — should show the full landing page with hero, features, and pricing.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Landing.jsx
git commit -m "feat: add landing page with hero, features, and pricing sections"
```

---

## Task 7: Login Page

**Files:**
- Create: `frontend/src/pages/Login.jsx`

- [ ] **Step 1: Write `src/pages/Login.jsx`**

```jsx
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  updateProfile,
} from 'firebase/auth'
import { auth } from '../lib/firebase'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import toast from 'react-hot-toast'

const provider = new GoogleAuthProvider()

const FIREBASE_ERRORS = {
  'auth/user-not-found': 'No existe una cuenta con ese correo.',
  'auth/wrong-password': 'Contraseña incorrecta.',
  'auth/email-already-in-use': 'Ese correo ya está registrado.',
  'auth/weak-password': 'La contraseña debe tener al menos 6 caracteres.',
  'auth/invalid-email': 'El formato del correo no es válido.',
  'auth/invalid-credential': 'Correo o contraseña incorrectos.',
}

export default function Login() {
  const navigate = useNavigate()
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (mode === 'register') {
        const cred = await createUserWithEmailAndPassword(auth, email, password)
        await updateProfile(cred.user, { displayName: name })
      } else {
        await signInWithEmailAndPassword(auth, email, password)
      }
      navigate('/dashboard')
    } catch (err) {
      setError(FIREBASE_ERRORS[err.code] ?? 'Ocurrió un error. Intenta de nuevo.')
    } finally {
      setLoading(false)
    }
  }

  async function handleGoogle() {
    setError('')
    setLoading(true)
    try {
      await signInWithPopup(auth, provider)
      navigate('/dashboard')
    } catch (err) {
      setError(FIREBASE_ERRORS[err.code] ?? 'No se pudo iniciar sesión con Google.')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg flex flex-col items-center justify-center px-4">
      <Link to="/" className="flex items-center gap-2 font-semibold text-text-primary mb-8">
        <span className="text-primary text-xl">✦</span>
        PlaneaAI
      </Link>

      <div className="w-full max-w-sm bg-surface rounded-2xl border border-border p-7 shadow-sm">
        <h1 className="text-xl font-bold text-text-primary mb-1">
          {mode === 'login' ? 'Bienvenido de nuevo' : 'Crea tu cuenta'}
        </h1>
        <p className="text-sm text-muted mb-6">
          {mode === 'login'
            ? 'Ingresa para acceder a tus planeaciones.'
            : 'Empieza gratis, sin tarjeta de crédito.'}
        </p>

        {/* Google */}
        <button
          type="button"
          onClick={handleGoogle}
          disabled={loading}
          className="w-full flex items-center justify-center gap-2.5 h-10 rounded-lg border border-border bg-surface text-sm font-medium text-text-primary hover:bg-bg transition-colors disabled:opacity-60 cursor-pointer mb-4"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24" aria-hidden="true">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continuar con Google
        </button>

        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-border" /></div>
          <div className="relative flex justify-center"><span className="bg-surface px-2 text-xs text-muted">o con correo</span></div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {mode === 'register' && (
            <div className="space-y-1.5">
              <Label htmlFor="name">Nombre completo</Label>
              <Input
                id="name"
                type="text"
                placeholder="Ej. María González"
                value={name}
                onChange={e => setName(e.target.value)}
                required
                autoComplete="name"
              />
            </div>
          )}
          <div className="space-y-1.5">
            <Label htmlFor="email">Correo electrónico</Label>
            <Input
              id="email"
              type="email"
              placeholder="tu@correo.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="password">Contraseña</Label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            />
          </div>

          {error && (
            <p role="alert" className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <Button type="submit" className="w-full" disabled={loading}>
            {loading
              ? <span className="flex items-center gap-2"><span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />Cargando...</span>
              : mode === 'login' ? 'Iniciar sesión' : 'Crear cuenta'
            }
          </Button>
        </form>

        <p className="text-center text-sm text-muted mt-5">
          {mode === 'login' ? '¿No tienes cuenta? ' : '¿Ya tienes cuenta? '}
          <button
            type="button"
            onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}
            className="text-primary font-medium hover:underline cursor-pointer"
          >
            {mode === 'login' ? 'Regístrate gratis' : 'Inicia sesión'}
          </button>
        </p>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify login page renders**

```bash
npm run dev
```
Visit `http://localhost:5173/login` — should show email/password form + Google button.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Login.jsx
git commit -m "feat: add login/register page with Firebase auth and Google OAuth"
```

---

## Task 8: Dashboard Page + PlanCard

**Files:**
- Create: `frontend/src/pages/Dashboard.jsx`
- Create: `frontend/src/components/PlanCard.jsx`

- [ ] **Step 1: Write `src/components/PlanCard.jsx`**

```jsx
import { Link } from 'react-router-dom'
import { formatDate, gradeLabel } from '../lib/utils'

export default function PlanCard({ plan, onDelete }) {
  return (
    <article className="bg-surface rounded-xl border border-border p-5 hover:border-primary/40 hover:shadow-sm transition-all group">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <Link
            to={`/plan/${plan.id}`}
            className="font-semibold text-text-primary hover:text-primary line-clamp-1 transition-colors"
          >
            {plan.title}
          </Link>
          <p className="text-sm text-muted mt-0.5">
            {gradeLabel(plan.grade_level)} · {plan.subject}
          </p>
          <p className="text-xs text-muted mt-1">{formatDate(plan.created_at)}</p>
        </div>
        <button
          onClick={() => onDelete(plan.id)}
          aria-label={`Eliminar ${plan.title}`}
          className="p-1.5 text-muted hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all rounded-md hover:bg-red-50 cursor-pointer"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </article>
  )
}
```

- [ ] **Step 2: Write `src/pages/Dashboard.jsx`**

```jsx
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import NavBar from '../components/NavBar'
import PlanCard from '../components/PlanCard'
import { Button } from '../components/ui/button'
import api from '../lib/api'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [plans, setPlans] = useState([])
  const [usage, setUsage] = useState({ used: 0, limit: 5 })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      try {
        const [plansRes, meRes] = await Promise.all([
          api.get('/planeaciones'),
          api.get('/auth/me'),
        ])
        setPlans(plansRes.data)
        setUsage(meRes.data.usage)
      } catch {
        toast.error('Error al cargar tus planeaciones.')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  async function handleDelete(id) {
    if (!confirm('¿Eliminar esta planeación?')) return
    try {
      await api.delete(`/planeaciones/${id}`)
      setPlans(prev => prev.filter(p => p.id !== id))
      toast.success('Planeación eliminada.')
    } catch {
      toast.error('No se pudo eliminar.')
    }
  }

  return (
    <div className="min-h-screen bg-bg">
      <NavBar usageStats={usage} />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Mis planeaciones</h1>
            <p className="text-sm text-muted mt-0.5">
              {plans.length === 0 ? 'Aún no tienes planeaciones.' : `${plans.length} planeación${plans.length !== 1 ? 'es' : ''}`}
            </p>
          </div>
          <Button asChild>
            <Link to="/generate">+ Nueva planeación</Link>
          </Button>
        </div>

        {loading ? (
          <div className="grid sm:grid-cols-2 gap-4">
            {[1,2,3,4].map(i => (
              <div key={i} className="bg-surface rounded-xl border border-border p-5 animate-pulse">
                <div className="h-4 bg-border rounded w-3/4 mb-2" />
                <div className="h-3 bg-border rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : plans.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-4xl mb-4">📋</p>
            <h2 className="font-semibold text-text-primary mb-1">Aún no tienes planeaciones</h2>
            <p className="text-sm text-muted mb-6">Genera tu primera planeación didáctica en segundos.</p>
            <Button asChild>
              <Link to="/generate">Generar ahora</Link>
            </Button>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 gap-4">
            {plans.map(plan => (
              <PlanCard key={plan.id} plan={plan} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Dashboard.jsx frontend/src/components/PlanCard.jsx
git commit -m "feat: add Dashboard with plan list, loading skeletons, and delete"
```

---

## Task 9: PlanRenderer

**Files:**
- Create: `frontend/src/components/PlanRenderer.jsx`
- Create: `frontend/src/__tests__/PlanRenderer.test.jsx`

- [ ] **Step 1: Write failing test**

```jsx
// src/__tests__/PlanRenderer.test.jsx
import { render, screen } from '@testing-library/react'
import PlanRenderer from '../components/PlanRenderer'

const mockContent = {
  proposito: 'Identificar fracciones equivalentes.',
  inicio: { duracion: '10 min', actividades: ['Exploración con círculos fraccionarios.'] },
  desarrollo: { duracion: '30 min', actividades: ['Completan tabla en parejas.'] },
  cierre: { duracion: '10 min', actividades: ['Plenaria de cierre.'] },
  materiales: ['Círculos fraccionarios', 'Cuaderno'],
  evaluacion: 'Observación directa y tabla completada.',
  competencias: ['Resolución de problemas matemáticos'],
  aprendizajes_esperados: ['Identifica fracciones equivalentes.'],
}

test('renders all planeación sections', () => {
  render(<PlanRenderer content={mockContent} />)
  expect(screen.getByText('Propósito')).toBeInTheDocument()
  expect(screen.getByText('Identificar fracciones equivalentes.')).toBeInTheDocument()
  expect(screen.getByText('Inicio')).toBeInTheDocument()
  expect(screen.getByText('10 min')).toBeInTheDocument()
  expect(screen.getByText('Exploración con círculos fraccionarios.')).toBeInTheDocument()
  expect(screen.getByText('Materiales')).toBeInTheDocument()
  expect(screen.getByText('Círculos fraccionarios')).toBeInTheDocument()
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npx vitest run src/__tests__/PlanRenderer.test.jsx
```
Expected: FAIL.

- [ ] **Step 3: Write `src/components/PlanRenderer.jsx`**

```jsx
function Section({ title, accent, children }) {
  return (
    <section className="bg-surface rounded-xl border border-border overflow-hidden">
      <div className={`px-5 py-3 border-b border-border flex items-center justify-between ${accent ? 'bg-primary-50' : 'bg-bg'}`}>
        <h2 className="font-semibold text-text-primary">{title}</h2>
        {accent && <span className="text-xs text-primary font-medium">{accent}</span>}
      </div>
      <div className="px-5 py-4">{children}</div>
    </section>
  )
}

function ActivityList({ items }) {
  return (
    <ol className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex gap-3 text-sm text-muted">
          <span className="flex-shrink-0 w-5 h-5 rounded-full bg-primary-50 text-primary text-xs flex items-center justify-center font-medium mt-0.5">
            {i + 1}
          </span>
          {item}
        </li>
      ))}
    </ol>
  )
}

export default function PlanRenderer({ content }) {
  const {
    proposito, inicio, desarrollo, cierre,
    materiales, evaluacion, competencias, aprendizajes_esperados
  } = content

  return (
    <div className="space-y-4">
      {/* Propósito */}
      <Section title="Propósito de la sesión">
        <p className="text-sm text-muted leading-relaxed">{proposito}</p>
      </Section>

      {/* Secuencia didáctica */}
      <div className="grid sm:grid-cols-3 gap-4">
        {[
          { key: 'inicio', label: 'Inicio', data: inicio },
          { key: 'desarrollo', label: 'Desarrollo', data: desarrollo },
          { key: 'cierre', label: 'Cierre', data: cierre },
        ].map(({ key, label, data }) => (
          <Section key={key} title={label} accent={data.duracion}>
            <ActivityList items={data.actividades} />
          </Section>
        ))}
      </div>

      {/* Aprendizajes esperados */}
      {aprendizajes_esperados?.length > 0 && (
        <Section title="Aprendizajes esperados">
          <ul className="space-y-1">
            {aprendizajes_esperados.map((a, i) => (
              <li key={i} className="flex gap-2 text-sm text-muted">
                <span className="text-primary">✓</span>{a}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {/* Materiales + Evaluación side by side */}
      <div className="grid sm:grid-cols-2 gap-4">
        <Section title="Materiales necesarios">
          <ul className="space-y-1">
            {materiales.map((m, i) => (
              <li key={i} className="flex gap-2 text-sm text-muted">
                <span className="text-accent">·</span>{m}
              </li>
            ))}
          </ul>
        </Section>
        <Section title="Evaluación">
          <p className="text-sm text-muted leading-relaxed">{evaluacion}</p>
        </Section>
      </div>

      {/* Competencias */}
      {competencias?.length > 0 && (
        <Section title="Competencias que se favorecen">
          <div className="flex flex-wrap gap-2">
            {competencias.map((c, i) => (
              <span key={i} className="px-2.5 py-1 rounded-full bg-primary-50 text-primary text-xs font-medium">
                {c}
              </span>
            ))}
          </div>
        </Section>
      )}
    </div>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
npx vitest run src/__tests__/PlanRenderer.test.jsx
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/PlanRenderer.jsx frontend/src/__tests__/PlanRenderer.test.jsx
git commit -m "feat: add PlanRenderer component for structured planeación display"
```

---

## Task 10: Generate Page + UpgradeModal

**Files:**
- Create: `frontend/src/pages/Generate.jsx`
- Create: `frontend/src/components/GenerateForm.jsx`
- Create: `frontend/src/components/UpgradeModal.jsx`
- Create: `frontend/src/__tests__/UpgradeModal.test.jsx`

- [ ] **Step 1: Write failing test for UpgradeModal**

```jsx
// src/__tests__/UpgradeModal.test.jsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import UpgradeModal from '../components/UpgradeModal'

test('shows modal when open=true', () => {
  render(
    <BrowserRouter>
      <UpgradeModal open={true} onClose={() => {}} />
    </BrowserRouter>
  )
  expect(screen.getByRole('dialog')).toBeInTheDocument()
  expect(screen.getByText(/límite del mes/i)).toBeInTheDocument()
})

test('calls onClose when cancel is clicked', async () => {
  const onClose = vi.fn()
  render(
    <BrowserRouter>
      <UpgradeModal open={true} onClose={onClose} />
    </BrowserRouter>
  )
  await userEvent.click(screen.getByRole('button', { name: /ahora no/i }))
  expect(onClose).toHaveBeenCalledOnce()
})
```

- [ ] **Step 2: Run test to verify it fails**

```bash
npx vitest run src/__tests__/UpgradeModal.test.jsx
```
Expected: FAIL.

- [ ] **Step 3: Write `src/components/UpgradeModal.jsx`**

```jsx
import { Link } from 'react-router-dom'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog'
import { Button } from './ui/button'

export default function UpgradeModal({ open, onClose }) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-sm" aria-labelledby="upgrade-title">
        <DialogHeader>
          <div className="text-3xl mb-2">🚀</div>
          <DialogTitle id="upgrade-title">Alcanzaste el límite del mes</DialogTitle>
          <DialogDescription>
            Has usado tus 5 planeaciones gratuitas. Actualiza a Pro para generar planeaciones ilimitadas por solo $149 MXN al mes.
          </DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-2 mt-2">
          <Button asChild className="w-full" onClick={onClose}>
            <Link to="/billing">Ver planes y actualizar</Link>
          </Button>
          <Button variant="ghost" className="w-full" onClick={onClose}>
            Ahora no
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
npx vitest run src/__tests__/UpgradeModal.test.jsx
```
Expected: PASS.

- [ ] **Step 5: Write `src/components/GenerateForm.jsx`**

```jsx
import { Button } from './ui/button'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Textarea } from './ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select'

const GRADE_LEVELS = [
  { group: 'Preescolar', items: ['preescolar_1','preescolar_2','preescolar_3'] },
  { group: 'Primaria', items: ['primaria_1','primaria_2','primaria_3','primaria_4','primaria_5','primaria_6'] },
  { group: 'Secundaria', items: ['secundaria_1','secundaria_2','secundaria_3'] },
  { group: 'Preparatoria', items: ['preparatoria_1','preparatoria_2','preparatoria_3'] },
]

const GRADE_LABELS = {
  preescolar_1: 'Preescolar 1°', preescolar_2: 'Preescolar 2°', preescolar_3: 'Preescolar 3°',
  primaria_1: 'Primaria 1°', primaria_2: 'Primaria 2°', primaria_3: 'Primaria 3°',
  primaria_4: 'Primaria 4°', primaria_5: 'Primaria 5°', primaria_6: 'Primaria 6°',
  secundaria_1: 'Secundaria 1°', secundaria_2: 'Secundaria 2°', secundaria_3: 'Secundaria 3°',
  preparatoria_1: 'Preparatoria 1°', preparatoria_2: 'Preparatoria 2°', preparatoria_3: 'Preparatoria 3°',
}

export default function GenerateForm({ onSubmit, loading }) {
  function handleSubmit(e) {
    e.preventDefault()
    const fd = new FormData(e.target)
    onSubmit({
      subject: fd.get('subject'),
      grade_level: fd.get('grade_level'),
      topic: fd.get('topic'),
      objective: fd.get('objective'),
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5" noValidate>
      <div className="grid sm:grid-cols-2 gap-5">
        <div className="space-y-1.5">
          <Label htmlFor="subject">Materia</Label>
          <Input
            id="subject"
            name="subject"
            placeholder="Ej. Matemáticas, Español, Ciencias..."
            required
            disabled={loading}
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="grade_level">Grado</Label>
          <Select name="grade_level" required disabled={loading}>
            <SelectTrigger id="grade_level">
              <SelectValue placeholder="Selecciona un grado" />
            </SelectTrigger>
            <SelectContent>
              {GRADE_LEVELS.map(({ group, items }) => (
                <div key={group}>
                  <div className="px-2 py-1 text-xs font-semibold text-muted">{group}</div>
                  {items.map(val => (
                    <SelectItem key={val} value={val}>{GRADE_LABELS[val]}</SelectItem>
                  ))}
                </div>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="topic">Tema</Label>
        <Input
          id="topic"
          name="topic"
          placeholder="Ej. Fracciones equivalentes, La célula, El cuento..."
          required
          disabled={loading}
        />
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="objective">Propósito / Aprendizaje esperado</Label>
        <Textarea
          id="objective"
          name="objective"
          placeholder="Ej. El alumno identificará fracciones equivalentes usando materiales concretos."
          rows={3}
          required
          disabled={loading}
          className="resize-none"
        />
        <p className="text-xs text-muted">Describe qué lograrán los alumnos al final de la sesión.</p>
      </div>

      <Button type="submit" className="w-full" size="lg" disabled={loading}>
        {loading
          ? <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Generando tu planeación...
            </span>
          : '✦ Generar planeación'
        }
      </Button>
    </form>
  )
}
```

- [ ] **Step 6: Write `src/pages/Generate.jsx`**

```jsx
import { useState } from 'react'
import NavBar from '../components/NavBar'
import GenerateForm from '../components/GenerateForm'
import PlanRenderer from '../components/PlanRenderer'
import UpgradeModal from '../components/UpgradeModal'
import { Button } from '../components/ui/button'
import { Link } from 'react-router-dom'
import api from '../lib/api'
import toast from 'react-hot-toast'

export default function Generate() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)  // { id, title, content }
  const [showUpgrade, setShowUpgrade] = useState(false)

  async function handleGenerate(formData) {
    setLoading(true)
    setResult(null)
    try {
      const { data } = await api.post('/generate', formData)
      setResult(data)
    } catch (err) {
      if (err.response?.data?.error === 'limit_reached') {
        setShowUpgrade(true)
      } else {
        toast.error('Error al generar la planeación. Intenta de nuevo.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg">
      <NavBar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        {!result ? (
          <>
            <div className="mb-7">
              <h1 className="text-2xl font-bold text-text-primary">Nueva planeación</h1>
              <p className="text-sm text-muted mt-1">
                Completa los 4 campos y la IA generará tu planeación didáctica completa.
              </p>
            </div>
            <div className="bg-surface rounded-2xl border border-border p-6 shadow-sm">
              <GenerateForm onSubmit={handleGenerate} loading={loading} />
            </div>
          </>
        ) : (
          <>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-text-primary">{result.title}</h1>
                <p className="text-sm text-green-600 mt-0.5 font-medium">✓ Planeación generada y guardada</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => setResult(null)}
                  size="sm"
                >
                  Nueva planeación
                </Button>
                <Button asChild size="sm">
                  <Link to="/dashboard">Ver todas</Link>
                </Button>
              </div>
            </div>
            <PlanRenderer content={result.content} />
          </>
        )}
      </main>
      <UpgradeModal open={showUpgrade} onClose={() => setShowUpgrade(false)} />
    </div>
  )
}
```

- [ ] **Step 7: Commit**

```bash
git add frontend/src/pages/Generate.jsx frontend/src/components/GenerateForm.jsx frontend/src/components/UpgradeModal.jsx frontend/src/__tests__/UpgradeModal.test.jsx
git commit -m "feat: add Generate page with form, loading state, result view, and upgrade modal"
```

---

## Task 11: PlanView Page

**Files:**
- Create: `frontend/src/pages/PlanView.jsx`

- [ ] **Step 1: Write `src/pages/PlanView.jsx`**

```jsx
import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import NavBar from '../components/NavBar'
import PlanRenderer from '../components/PlanRenderer'
import { Button } from '../components/ui/button'
import { gradeLabel } from '../lib/utils'
import api from '../lib/api'
import toast from 'react-hot-toast'

export default function PlanView() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get(`/planeaciones/${id}`)
      .then(r => setPlan(r.data))
      .catch(() => { toast.error('No se encontró la planeación.'); navigate('/dashboard') })
      .finally(() => setLoading(false))
  }, [id, navigate])

  if (loading) return (
    <div className="min-h-screen bg-bg">
      <NavBar />
      <div className="max-w-3xl mx-auto px-4 py-8 space-y-4">
        {[1,2,3].map(i => <div key={i} className="h-32 bg-surface rounded-xl border border-border animate-pulse" />)}
      </div>
    </div>
  )

  if (!plan) return null

  return (
    <div className="min-h-screen bg-bg">
      <NavBar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-center gap-2 text-sm text-muted mb-6">
          <Link to="/dashboard" className="hover:text-primary transition-colors">Mis planeaciones</Link>
          <span>/</span>
          <span className="text-text-primary truncate">{plan.title}</span>
        </div>

        <div className="flex items-start justify-between gap-4 mb-6">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">{plan.title}</h1>
            <p className="text-sm text-muted mt-1">
              {gradeLabel(plan.grade_level)} · {plan.subject} · {plan.topic}
            </p>
          </div>
          <Button asChild variant="outline" size="sm">
            <Link to="/generate">Nueva planeación</Link>
          </Button>
        </div>

        <PlanRenderer content={plan.content} />
      </main>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/PlanView.jsx
git commit -m "feat: add PlanView page with breadcrumb and plan renderer"
```

---

## Task 12: Billing Page

**Files:**
- Create: `frontend/src/pages/Billing.jsx`

- [ ] **Step 1: Write `src/pages/Billing.jsx`**

```jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import NavBar from '../components/NavBar'
import { Button } from '../components/ui/button'
import { useAuth } from '../context/AuthContext'
import api from '../lib/api'
import toast from 'react-hot-toast'

const PLANS = [
  {
    id: 'free',
    name: 'Gratis',
    price: '$0',
    period: '',
    features: [
      '5 planeaciones al mes',
      'Todos los grados y materias',
      'Historial de planeaciones',
    ],
    cta: 'Plan actual',
    highlight: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: '$149',
    period: 'MXN/mes',
    features: [
      'Planeaciones ilimitadas',
      'Todos los grados y materias',
      'Historial completo',
      'Soporte prioritario',
    ],
    cta: 'Actualizar a Pro',
    highlight: true,
  },
  {
    id: 'escuela',
    name: 'Escuela',
    price: '$799',
    period: 'MXN/mes',
    features: [
      'Hasta 20 docentes',
      'Panel de administrador',
      'Planeaciones ilimitadas para todos',
      'Factura fiscal disponible',
    ],
    cta: 'Actualizar a Escuela',
    highlight: false,
  },
]

export default function Billing() {
  const { subscription } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(null)

  async function handleUpgrade(planId) {
    setLoading(planId)
    try {
      const { data } = await api.post('/billing/checkout', { plan: planId })
      window.location.href = data.checkout_url
    } catch {
      toast.error('Error al iniciar el proceso de pago.')
      setLoading(null)
    }
  }

  async function handleManage() {
    setLoading('manage')
    try {
      const { data } = await api.post('/billing/portal')
      window.location.href = data.portal_url
    } catch {
      toast.error('Error al abrir el portal de suscripción.')
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen bg-bg">
      <NavBar />
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text-primary">Suscripción</h1>
          <p className="text-sm text-muted mt-1">
            Plan actual: <span className="font-medium text-text-primary capitalize">{subscription.plan}</span>
            {subscription.plan !== 'free' && (
              <> · <button onClick={handleManage} className="text-primary hover:underline cursor-pointer" disabled={loading === 'manage'}>
                Administrar suscripción
              </button></>
            )}
          </p>
        </div>

        <div className="grid sm:grid-cols-3 gap-5">
          {PLANS.map(plan => {
            const isCurrent = subscription.plan === plan.id
            const isUpgrade = !isCurrent && plan.id !== 'free'
            return (
              <div
                key={plan.id}
                className={`rounded-2xl border p-6 flex flex-col ${
                  plan.highlight
                    ? 'border-primary bg-primary-50 shadow-md shadow-primary/10'
                    : 'border-border bg-surface'
                } ${isCurrent ? 'ring-2 ring-primary' : ''}`}
              >
                {isCurrent && (
                  <span className="self-start px-2.5 py-0.5 rounded-full bg-primary text-white text-xs font-semibold mb-3">
                    Plan actual
                  </span>
                )}
                {!isCurrent && plan.highlight && (
                  <span className="self-start px-2.5 py-0.5 rounded-full bg-primary text-white text-xs font-semibold mb-3">
                    Más popular
                  </span>
                )}

                <h2 className="font-semibold text-text-primary">{plan.name}</h2>
                <div className="mt-2 mb-4">
                  <span className="text-3xl font-bold text-text-primary">{plan.price}</span>
                  {plan.period && <span className="text-sm text-muted ml-1">{plan.period}</span>}
                </div>

                <ul className="space-y-2 flex-1 mb-6">
                  {plan.features.map(f => (
                    <li key={f} className="flex items-start gap-2 text-sm text-muted">
                      <span className="text-primary mt-0.5">✓</span>{f}
                    </li>
                  ))}
                </ul>

                <Button
                  variant={plan.highlight && isUpgrade ? 'default' : 'outline'}
                  className="w-full"
                  disabled={isCurrent || loading === plan.id}
                  onClick={() => isUpgrade && handleUpgrade(plan.id)}
                >
                  {loading === plan.id
                    ? <span className="flex items-center gap-2">
                        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                        Redirigiendo...
                      </span>
                    : isCurrent ? 'Plan actual' : plan.cta
                  }
                </Button>
              </div>
            )
          })}
        </div>

        <p className="text-xs text-muted text-center mt-6">
          Los pagos son procesados de forma segura por Stripe. OXXO Pay disponible.
        </p>
      </main>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/Billing.jsx
git commit -m "feat: add Billing page with plan cards and Stripe checkout/portal"
```

---

## Task 13: AdminSchool Page

**Files:**
- Create: `frontend/src/pages/AdminSchool.jsx`

- [ ] **Step 1: Write `src/pages/AdminSchool.jsx`**

```jsx
import { useState, useEffect } from 'react'
import NavBar from '../components/NavBar'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui/badge'
import api from '../lib/api'
import toast from 'react-hot-toast'

export default function AdminSchool() {
  const [users, setUsers] = useState([])
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(true)
  const [inviting, setInviting] = useState(false)

  useEffect(() => {
    api.get('/admin/users')
      .then(r => setUsers(r.data))
      .catch(() => toast.error('Error al cargar los docentes.'))
      .finally(() => setLoading(false))
  }, [])

  async function handleInvite(e) {
    e.preventDefault()
    if (!email) return
    setInviting(true)
    try {
      await api.post('/admin/invite', { email })
      toast.success(`Invitación enviada a ${email}`)
      setEmail('')
      const r = await api.get('/admin/users')
      setUsers(r.data)
    } catch (err) {
      const msg = err.response?.data?.error
      if (msg === 'seat_limit_reached') {
        toast.error('Alcanzaste el límite de 20 docentes.')
      } else {
        toast.error('Error al enviar la invitación.')
      }
    } finally {
      setInviting(false)
    }
  }

  return (
    <div className="min-h-screen bg-bg">
      <NavBar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="mb-7">
          <h1 className="text-2xl font-bold text-text-primary">Mi escuela</h1>
          <p className="text-sm text-muted mt-1">
            Administra los docentes de tu plan Escuela.
            <span className="ml-2 font-medium text-text-primary">{users.length} / 20 asientos usados</span>
          </p>
        </div>

        {/* Invite form */}
        <div className="bg-surface rounded-2xl border border-border p-6 mb-6">
          <h2 className="font-semibold text-text-primary mb-4">Invitar docente</h2>
          <form onSubmit={handleInvite} className="flex gap-3">
            <div className="flex-1 space-y-1.5">
              <Label htmlFor="invite-email" className="sr-only">Correo del docente</Label>
              <Input
                id="invite-email"
                type="email"
                placeholder="correo@docente.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
                disabled={inviting || users.length >= 20}
              />
            </div>
            <Button
              type="submit"
              disabled={inviting || users.length >= 20}
            >
              {inviting ? 'Enviando...' : 'Invitar'}
            </Button>
          </form>
          {users.length >= 20 && (
            <p className="text-xs text-amber-600 mt-2">Alcanzaste el límite de 20 docentes.</p>
          )}
        </div>

        {/* Seats table */}
        <div className="bg-surface rounded-2xl border border-border overflow-hidden">
          <div className="px-5 py-3 border-b border-border">
            <h2 className="font-semibold text-text-primary">Docentes ({users.length})</h2>
          </div>
          {loading ? (
            <div className="p-5 space-y-3">
              {[1,2,3].map(i => <div key={i} className="h-8 bg-border rounded animate-pulse" />)}
            </div>
          ) : users.length === 0 ? (
            <div className="p-8 text-center text-sm text-muted">
              Aún no has invitado docentes. Usa el formulario de arriba.
            </div>
          ) : (
            <ul className="divide-y divide-border">
              {users.map(u => (
                <li key={u.id} className="px-5 py-3 flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium text-text-primary">{u.display_name || u.email}</p>
                    {u.display_name && <p className="text-xs text-muted">{u.email}</p>}
                  </div>
                  <Badge variant={u.status === 'active' ? 'default' : 'secondary'}>
                    {u.status === 'active' ? 'Activo' : 'Pendiente'}
                  </Badge>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  )
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/pages/AdminSchool.jsx
git commit -m "feat: add AdminSchool page with invite form and seat management"
```

---

## Task 14: Run All Tests

- [ ] **Step 1: Run full test suite**

```bash
cd frontend && npx vitest run
```
Expected: All tests pass. Fix any failures before proceeding.

- [ ] **Step 2: Verify dev build**

```bash
npm run build
```
Expected: Build succeeds with no errors. Warnings about bundle size are OK.

- [ ] **Step 3: Final commit**

```bash
git add .
git commit -m "test: verify all frontend tests pass and build succeeds"
```
