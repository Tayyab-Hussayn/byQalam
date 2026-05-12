# Qalam Codex Context

This file is the Codex context file for the Qalam repository. Treat it as the repo-level operating guide.

## Product

Qalam is a full-stack SaaS product for LinkedIn content generation, review, scheduling, and publishing. The long-term architecture is:

- Frontend: Next.js App Router, TypeScript, Tailwind CSS
- Backend: FastAPI, Python, PostgreSQL/Supabase, Redis-backed workers
- Auth: temporary frontend demo cookie now; production should use Supabase/FastAPI-backed secure sessions
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

- `/` public marketing page
- `/login` temporary demo login
- `/dashboard` guarded dashboard route
- `/api/auth/demo-login` temporary demo session endpoint

Dashboard is a React conversion of `qalam_world_class_mvp.html`. Keep its UI stable while improving code structure.

Important dashboard files:

- `src/app/dashboard/DashboardClient.tsx` owns orchestration state.
- `src/app/dashboard/components/` contains extracted dashboard UI pieces.
- `src/app/dashboard/dashboardConfig.ts` contains dashboard labels/config.
- `src/app/dashboard/dashboardStyles.ts` contains the original dashboard CSS adapted for Next.js fonts.
- `src/features/dashboard/data/dashboardMock.ts` contains typed mock dashboard data.

API/backend preparation:

- `src/lib/api/client.ts` is the typed API wrapper.
- `src/services/posts.ts` contains the first post-generation service contract.
- `src/types/` contains shared domain/API types.
- `.env.example` defines `NEXT_PUBLIC_API_BASE_URL`.

Task tracking:

- `QALAM_PENDING_TASKS.md` is the master source of truth for remaining frontend
  and backend work.
- `QALAM_FRONTEND_PENDING_TASKS.md` and `QALAM_BACKEND_PENDING_TASKS.md` contain
  the detailed per-area lists.

## Engineering Rules

- Prefer preserving existing UI before improving internals.
- Do not expose AI provider API keys in frontend code.
- Do not call Anthropic/OpenAI/etc. directly from browser components; route generation through backend services.
- Keep dashboard routes protected. Current guard is `src/proxy.ts` with temporary `qalam_session`.
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

The build may need elevated permissions in the Codex sandbox because Turbopack can use local build worker ports.

## Known Temporary Decisions

- `/login` is a demo login, not production auth.
- `qalam_session` is a temporary httpOnly demo cookie.
- Dashboard generation is a mock response until FastAPI AI generation exists.
- Dashboard data is typed mock data and should later be replaced through service calls.
