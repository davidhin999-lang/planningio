# PlaneaAI — Architecture Design

**Date:** 2026-03-27
**Status:** Approved
**Scope:** Full SaaS MVP — generation, auth, billing, usage metering, all three subscription tiers

---

## Product Summary

PlaneaAI generates complete, SEP-compliant planeaciones didácticas for Mexican teachers (preescolar → preparatoria). Teachers input subject, grade level, topic, and learning objective; the AI returns a structured, ready-to-submit planeación in the exact SEP-required format.

**Business model:** Freemium SaaS
- Free: 5 planeaciones/month
- Pro ($149 MXN/month): unlimited, all grades/subjects
- Escuela ($799 MXN/month): up to 20 teacher seats under one school admin

**Out of scope for MVP:** Word (.docx) and PDF export (v1.1)

---

## 1. System Architecture

### Approach: Modular Monolith

One Flask backend with clear internal modules, single PostgreSQL instance with pgvector for RAG, Firebase Auth for identity, Stripe for billing.

### Deployment (Railway)

Three Railway services in one project on a private network:
- `frontend` — React + Vite static build
- `backend` — Python Flask app
- `postgres` — PostgreSQL 15 with pgvector extension (not publicly exposed)

### High-Level Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAILWAY                                  │
│                                                                  │
│  ┌──────────────┐     ┌──────────────────────────────────────┐  │
│  │   Frontend   │     │           Flask Backend              │  │
│  │  React+Vite  │────▶│                                      │  │
│  │  Tailwind    │     │  /auth      /plans     /billing      │  │
│  │  (static)    │     │  /generate  /history   /admin        │  │
│  └──────────────┘     │                                      │  │
│                        │  ┌────────────┐  ┌───────────────┐  │  │
│                        │  │  Firebase  │  │ Stripe Client │  │  │
│                        │  │ ID Token   │  │  + Webhooks   │  │  │
│                        │  │ Verifier   │  └───────────────┘  │  │
│                        │  └────────────┘                     │  │
│                        │  ┌──────────────────────────────┐   │  │
│                        │  │      Generation Pipeline      │   │  │
│                        │  │  1. Retrieve from pgvector    │   │  │
│                        │  │  2. Build prompt              │   │  │
│                        │  │  3. Call Gemini 2.0 Flash     │   │  │
│                        │  │  4. Parse + store result      │   │  │
│                        │  └──────────────────────────────┘   │  │
│                        └──────────────────────────────────────┘  │
│                                       │                          │
│                        ┌──────────────▼──────────────┐          │
│                        │   PostgreSQL + pgvector      │          │
│                        │                              │          │
│                        │  users / subscriptions       │          │
│                        │  planeaciones / usage_log    │          │
│                        │  curriculum_chunks (vectors) │          │
│                        └──────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
  Firebase Auth                    Stripe API
  (identity only)            (subscriptions + OXXO)
```

### External Services

| Service | Purpose | Notes |
|---|---|---|
| Firebase Auth | User identity, token issuance | Service account JSON in backend env |
| Stripe | Subscriptions, Checkout, Customer Portal | OXXO Pay enabled |
| Google Gemini 2.0 Flash | Planeación generation | Via `google-generativeai` SDK |
| Google text-embedding-004 | Curriculum chunk embeddings + query embedding | 768 dimensions, free tier |

---

## 2. Data Model

```sql
-- Primary user record; id = Firebase UID
users
  id            TEXT PRIMARY KEY
  email         TEXT NOT NULL UNIQUE
  display_name  TEXT
  created_at    TIMESTAMPTZ DEFAULT now()

-- One row per user; source of truth is Stripe, mirrored here via webhooks
subscriptions
  id                  SERIAL PRIMARY KEY
  user_id             TEXT REFERENCES users(id)
  stripe_customer_id  TEXT UNIQUE
  stripe_sub_id       TEXT UNIQUE
  plan                TEXT NOT NULL   -- 'free' | 'pro' | 'escuela'
  status              TEXT NOT NULL   -- 'active' | 'past_due' | 'canceled'
  current_period_end  TIMESTAMPTZ
  school_id           INT REFERENCES schools(id)  -- null unless 'escuela'

-- Escuela tier: one row per school
schools
  id          SERIAL PRIMARY KEY
  name        TEXT NOT NULL
  admin_id    TEXT REFERENCES users(id)
  created_at  TIMESTAMPTZ DEFAULT now()

-- Every generated planeación; content is structured Gemini JSON output
planeaciones
  id            SERIAL PRIMARY KEY
  user_id       TEXT REFERENCES users(id)
  title         TEXT                   -- e.g. "Matemáticas 3° - Fracciones"
  subject       TEXT NOT NULL
  grade_level   TEXT NOT NULL          -- e.g. 'primaria_3', 'secundaria_1'
  topic         TEXT NOT NULL
  objective     TEXT NOT NULL
  content       JSONB NOT NULL
  created_at    TIMESTAMPTZ DEFAULT now()
  is_deleted    BOOLEAN DEFAULT false  -- soft delete

-- Append-only log for usage metering
usage_log
  id          SERIAL PRIMARY KEY
  user_id     TEXT REFERENCES users(id)
  action      TEXT NOT NULL            -- 'generate'
  created_at  TIMESTAMPTZ DEFAULT now()

-- SEP curriculum chunks with vector embeddings for RAG
curriculum_chunks
  id          SERIAL PRIMARY KEY
  grade_level TEXT NOT NULL
  subject     TEXT NOT NULL
  source      TEXT NOT NULL            -- 'NEM_2022' | 'Plan2011' | 'Plan2017'
  chunk_text  TEXT NOT NULL
  embedding   VECTOR(768)
  metadata    JSONB                    -- {aprendizaje, bloque, campo_formativo, ...}
```

**Notes:**
- `users.id` = Firebase UID directly — no duplication; first login auto-creates the row via `POST /auth/sync`.
- `POST /auth/sync` also upserts a `subscriptions` row with `plan='free', status='active'` for new users — ensures the usage gate never sees a NULL subscription.
- `planeaciones.content` JSONB schema: `{ proposito, inicio, desarrollo, cierre, materiales, evaluacion, competencias }` — flexible without migrations as prompt output evolves.
- Free-tier usage check: `COUNT(*) WHERE user_id = ? AND action = 'generate' AND created_at > date_trunc('month', now())`.
- Escuela seat cap enforced at invite time: `COUNT(*) WHERE school_id = ? <= 20`.

**grade_level enum:**
```
preescolar_1 | preescolar_2 | preescolar_3
primaria_1 | primaria_2 | primaria_3 | primaria_4 | primaria_5 | primaria_6
secundaria_1 | secundaria_2 | secundaria_3
preparatoria_1 | preparatoria_2 | preparatoria_3
```

---

## 3. RAG Pipeline

### Ingestion (offline, run once + on curriculum updates)

Script: `scripts/ingest_curriculum.py`

1. Parse SEP curriculum source files (PDFs or structured text)
2. Chunk by natural unit — one aprendizaje esperado per chunk (~300–500 tokens), tagged with `grade_level`, `subject`, `source`, `metadata`
3. Embed each chunk via `text-embedding-004` (batch 100 at a time)
4. Upsert into `curriculum_chunks` — `ON CONFLICT (grade_level, subject, chunk_text) DO UPDATE SET embedding = excluded.embedding`

### Retrieval (per generation request)

1. **Embed query:** `text-embedding-004("{subject} {grade_level} {topic} {objective}")`
2. **Vector search with pre-filter:**
   ```sql
   SELECT chunk_text, metadata
   FROM curriculum_chunks
   WHERE grade_level = :grade AND subject = :subject
   ORDER BY embedding <=> :query_vector
   LIMIT 5
   ```
3. **Build prompt:** system instructions (SEP format + tone) + top-5 retrieved chunks + user inputs
4. **Call Gemini 2.0 Flash** with structured JSON response schema
5. **Parse + store** result in `planeaciones.content`

**Performance target:** under 8 seconds end-to-end (embedding ~150ms + pgvector retrieval ~50ms + Gemini ~5–7s). No streaming for MVP — JSON must be complete before rendering.

---

## 4. API Endpoints

All endpoints except `POST /billing/webhook` require `Authorization: Bearer <firebase_id_token>`.

```
POST   /auth/sync                  # Upsert user row on first Firebase login
GET    /auth/me                    # Current user + subscription status

POST   /generate                   # Generate a planeación (core endpoint)
GET    /planeaciones               # List user's saved planeaciones
GET    /planeaciones/:id           # Get single planeación
DELETE /planeaciones/:id           # Soft delete

POST   /billing/checkout           # Create Stripe Checkout session → { checkout_url }
POST   /billing/portal             # Create Stripe Customer Portal session → { portal_url }
POST   /billing/webhook            # Stripe webhook (verified by signature, no auth)

GET    /admin/users                # Escuela admin: list seats
POST   /admin/invite               # Escuela admin: invite teacher by email
```

### Generate Request/Response

**Request:**
```json
{
  "subject": "Matemáticas",
  "grade_level": "primaria_3",
  "topic": "Fracciones",
  "objective": "El alumno identificará fracciones equivalentes usando materiales concretos"
}
```

**Response:**
```json
{
  "id": 42,
  "title": "Matemáticas 3° - Fracciones",
  "content": {
    "proposito": "...",
    "inicio": { "duracion": "10 min", "actividades": ["..."] },
    "desarrollo": { "duracion": "30 min", "actividades": ["..."] },
    "cierre": { "duracion": "10 min", "actividades": ["..."] },
    "materiales": ["..."],
    "evaluacion": "...",
    "competencias": ["..."],
    "aprendizajes_esperados": ["..."]
  }
}
```

**Error — free tier limit reached:**
```json
{ "error": "limit_reached", "used": 5, "limit": 5 }
```
HTTP 403.

---

## 5. Auth Flow

```
React app                    Firebase              Flask Backend
    │                            │                      │
    ├─ signInWithEmailAndPassword ──▶                    │
    │                            │◀─ ID token (1hr TTL) │
    │                            │                      │
    ├─────────── POST /auth/sync (Bearer token) ────────▶│
    │                            │          verify token │
    │                            │◀─────────────────────┤
    │                            │      upsert users row │
    │◀────────────────────── { user, subscription } ─────┤
```

- Firebase ID tokens are short-lived (1hr); Firebase SDK auto-refreshes them.
- Flask uses `firebase_admin.auth.verify_id_token()` — stateless, no sessions.
- `/auth/sync` is called after every login and after Stripe redirects back to the app.

---

## 6. Billing Flow

```
User clicks "Actualizar a Pro"
        │
        ├─ POST /billing/checkout { plan: 'pro' }
        │     Creates Stripe Checkout session (price_id, customer_id,
        │     success_url=/dashboard?upgraded=1, cancel_url=/billing)
        │     Returns { checkout_url }
        │
        ├─ Frontend redirects to Stripe-hosted checkout
        │     Card or OXXO payment
        │
        ├─ Stripe calls POST /billing/webhook
        │     Events handled:
        │     • checkout.session.completed     → INSERT/UPDATE subscriptions (active)
        │     • invoice.payment_succeeded      → extend current_period_end
        │     • customer.subscription.updated  → sync plan + status
        │     • customer.subscription.deleted  → set plan='free', status='canceled'
        │
        └─ User lands on /dashboard?upgraded=1
              Frontend calls /auth/me → reads updated subscription
```

- Stripe Customer Portal handles all self-serve changes and cancellations.
- Webhook endpoint verifies Stripe signature before processing (`stripe.WebhookSignature.verify_header`).
- Stripe is source of truth for billing; `subscriptions` table mirrors it.

---

## 7. Subscription & Usage Gate (per request)

```
POST /generate
  1. Verify Firebase ID token → user_id
  2. SELECT plan, status FROM subscriptions WHERE user_id = ?
  3. If plan = 'free':
       count = SELECT COUNT(*) FROM usage_log
               WHERE user_id = ? AND action = 'generate'
               AND created_at > date_trunc('month', now())
       if count >= 5 → 403 limit_reached
  4. If plan = 'escuela':
       Verify subscriptions.school_id IS NOT NULL
       Verify subscriptions.status = 'active'
  5. Run RAG + generation pipeline
  6. INSERT usage_log + INSERT planeaciones
  7. Return planeación JSON
```

---

## 8. Frontend Structure

```
src/
├── main.jsx
├── App.jsx                    # Routes + auth guard
├── lib/
│   ├── firebase.js            # Firebase app init + auth instance
│   ├── api.js                 # Axios instance, auto-attaches Bearer token
│   └── stripe.js              # redirectToCheckout helper
├── context/
│   └── AuthContext.jsx        # { currentUser, subscription, loading }
├── pages/
│   ├── Login.jsx              # Email/password + Google OAuth
│   ├── Dashboard.jsx          # Saved planeaciones list + "Nueva" button
│   ├── Generate.jsx           # Form → loading → result
│   ├── PlanView.jsx           # Single planeación view
│   ├── Billing.jsx            # Plan comparison + upgrade CTA + manage link
│   └── AdminSchool.jsx        # Escuela admin: seat management
└── components/
    ├── GenerateForm.jsx        # 4-field input form
    ├── PlanCard.jsx            # Dashboard list item
    ├── PlanRenderer.jsx        # Renders planeación JSONB into formatted sections
    ├── UsageBadge.jsx          # "3 / 5 planeaciones este mes" (free users)
    ├── UpgradeModal.jsx        # Auto-opens on 403 limit_reached
    └── NavBar.jsx
```

### Routes
```
/              → redirect to /dashboard (authed) or /login
/login
/dashboard
/generate
/plan/:id
/billing
/admin/school  → only if plan === 'escuela' && user is school admin
```

---

## 9. Backend Module Structure

```
backend/
├── app.py                     # Flask app factory + blueprint registration
├── config.py                  # Env var loading (DATABASE_URL, STRIPE_KEY, etc.)
├── db.py                      # SQLAlchemy engine + session
├── auth/
│   ├── middleware.py          # require_auth decorator (Firebase token verification)
│   └── routes.py              # /auth/sync, /auth/me
├── generation/
│   ├── routes.py              # POST /generate
│   ├── pipeline.py            # Orchestrates embed → retrieve → prompt → Gemini → parse
│   ├── embedder.py            # text-embedding-004 calls
│   ├── retriever.py           # pgvector queries
│   └── prompt_builder.py      # System prompt + context assembly
├── planeaciones/
│   └── routes.py              # GET/DELETE /planeaciones
├── billing/
│   ├── routes.py              # /billing/checkout, /billing/portal, /billing/webhook
│   └── usage.py               # Free-tier usage check + gate logic
├── admin/
│   └── routes.py              # /admin/users, /admin/invite
├── models/
│   └── models.py              # SQLAlchemy ORM models
└── scripts/
    └── ingest_curriculum.py   # One-time RAG ingestion script
```

---

## 10. Environment Variables

```
# Database
DATABASE_URL=postgresql://...

# Firebase
FIREBASE_SERVICE_ACCOUNT_JSON='{...}'   # Service account JSON as string

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_ESCUELA=price_...

# Google AI
GOOGLE_API_KEY=...

# App
FRONTEND_URL=https://planeaai.up.railway.app
FLASK_ENV=production
```

---

## 11. Out of Scope (v1.1+)

- Word (.docx) and PDF export
- Magic link / passwordless login
- Email notifications (plan renewal reminders)
- Teacher-facing analytics (most-used subjects, grades)
- Bulk planeación generation
