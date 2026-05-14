# Qalam Codex Context

This file is the Codex context file for the Qalam repository. Treat it as the repo-level operating guide.

## Product

Qalam is a full-stack SaaS product for LinkedIn content generation, review, scheduling, and publishing. The long-term architecture is:

- Frontend: Next.js App Router, TypeScript, Tailwind CSS
- Backend: FastAPI, Python, PostgreSQL/Supabase, Redis-backed workers
- Auth: Supabase Auth with JWT stored in httpOnly cookie, validated by FastAPI
- AI: backend-owned content generation service, never direct provider keys in browser

Primary planning docs:

- `QALAM_PRODUCT_ARCHITECTURE_PLAN.md`
- `QALAM_FRONTEND_GOAL_AND_ROADMAP.md`
- `QALAM_PENDING_TASKS.md`

## Source Design Files

Do not casually redesign these.

- `Qalam Project.html` is the source of truth for the public marketing page.
- `qalam_world_class_mvp.html` is the source of truth for the dashboard UI.

When converting or refactoring UI, preserve visual design, copy, layout, internal views, and interactions unless the user explicitly asks for changes.

## Current Frontend State

Frontend lives in `frontend/`.

Important routes:

- `/` - public marketing page (redirects logged-in users to dashboard)
- `/login` - Supabase authentication (redirects logged-in users to dashboard)
- `/dashboard` - protected dashboard route (redirects to login if not authenticated)
- `/api/auth/session-sync` - syncs Supabase JWT to httpOnly cookie
- `/api/auth/session-clear` - clears session on logout

Authentication flow:
1. User logs in via Supabase Auth (email/password)
2. Supabase returns JWT access token
3. AuthProvider syncs token to httpOnly `qalam_session` cookie
4. Middleware checks cookie and redirects appropriately

Important auth files:

- `src/middleware.ts` - auth-aware routing (redirects, protected routes)
- `src/providers/auth-provider.tsx` - syncs session on auth state changes
- `src/lib/auth/supabase.ts` - Supabase client (returns null if env vars missing)
- `src/lib/api/client.ts` - typed API wrapper with JWT forwarding
- `src/app/login/LoginClient.tsx` - login/signup form

## Repository Structure

```
/home/krawin/code/qalam/
├── frontend/          # Next.js frontend
│   ├── src/
│   │   ├── middleware.ts       # Auth-aware routing
│   │   ├── app/                 # Next.js app router pages
│   │   ├── lib/                 # API client, auth, utilities
│   │   ├── providers/           # React providers
│   │   └── services/            # Service layer
│   └── package.json
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/        # API routes
│   │   ├── core/       # Auth, config, security
│   │   ├── db/         # SQLAlchemy models
│   │   ├── services/   # Business logic
│   │   └── workers/    # Celery tasks
│   └── pyproject.toml
└── QALAM_*.md         # Planning documents
```

## Engineering Rules

- Prefer preserving existing UI before improving internals.
- Do not expose AI provider API keys in frontend code.
- Do not call Anthropic/OpenAI/etc. directly from browser components; route generation through backend services.
- Keep dashboard routes protected via `src/middleware.ts`.
- When adding backend integration, use `src/lib/api/client.ts` and service modules instead of raw `fetch` in components.
- Keep TypeScript strict and avoid `any`.
- Use `next/font` for fonts; do not reintroduce CSS `@import` font loading.
- Keep `DashboardClient.tsx` as an orchestration shell; add or move UI into focused components.
- If refactoring dashboard UI, verify `npm run lint` and `npm run build`.

## Validation Commands

Run from `frontend/`:

```bash
npm run lint
npm run build
```

## Environment Variables

Frontend requires:

- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` - Supabase anon key
- `NEXT_PUBLIC_API_BASE_URL` - Backend API URL (optional for local dev)

Backend requires (see `backend/.env.example`):

- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_JWKS_URL` or `SUPABASE_JWT_SECRET` - for JWT validation
- `JWT_AUDIENCE` - typically "authenticated"

## GitHub Repository

https://github.com/Tayyab-Hussayn/byQalam

- Main branch: `main`
- Single unified repo containing both frontend and backend

## Known Temporary Decisions

- Auth is now production Supabase Auth with JWT forwarding to FastAPI
- Backend still needs deployment for full API integration
- Dashboard data is typed mock data until backend is connected
- Some features (LinkedIn publishing, billing) require backend deployment