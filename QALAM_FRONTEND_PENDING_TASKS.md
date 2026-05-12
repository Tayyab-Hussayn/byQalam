# Qalam Frontend Pending Tasks

Last updated: 2026-05-10

This file tracks the remaining frontend work for the Qalam SaaS after the
marketing page, dashboard UI conversion, route guard, and initial backend service
layer were established.

Master index:

- [QALAM_PENDING_TASKS.md](./QALAM_PENDING_TASKS.md)

Completed frontend foundation:

- Next.js App Router frontend in `frontend-wt/frontend`.
- Marketing page converted from the source HTML design.
- Dashboard UI converted from `qalam_world_class_mvp.html`.
- Temporary login route and protected dashboard route.
- Shared API wrapper in `src/lib/api/client.ts`.
- Backend-aware dashboard generation service in `src/services/dashboard.ts`.
- Initial service wrappers for preferences, LinkedIn, and billing APIs.
- LinkedIn connection, publishing, and billing surfaces are wired into the dashboard.
- Production build currently passes.

## 1. Authentication And Session Wiring

- Supabase session bootstrap on the client is in place. Done.
- Frontend API calls now attach the active Supabase bearer token. Done.
- Auth-aware `/login` and `/dashboard` route behavior is in place through the shared cookie bridge. Done.
- Surface current user and workspace context in the UI. Partially done through `/me` bootstrap.

## 2. Dashboard Data Integration

- Dashboard usage summary and recent posts now come from backend data. Done.
- Sidebar plan card now reflects the backend billing plan. Done.
- Keep wiring the remaining dashboard sections to live data where useful. In progress.

## 3. Preferences And Voice Profile UI

- Settings surface for content preferences is in place. Done.
- Voice profile editing and writing sample persistence are in place. Done.
- Niche profile selection and preference loading are in place. Done.
- Keep refining preference UX as backend data grows. In progress.

## 4. LinkedIn Integration UI

- Done.

## 5. Billing And Plan UI

- Done.

## 6. State Management And Server Data

- Introduce a server-state library if needed for caching and invalidation.
- Separate UI state from server state more aggressively.
- Add request cancellation and stale-response handling for all API workflows.

## 7. Production Hardening

- Frontend error boundaries and loading states for API-driven routes are in place.
- Retry UX for failed backend fetches is in place.
- Frontend error reporting is in place through the local error reporter and API route.
- CI checks for lint, build, and type safety are in place.

## Immediate Next Task

The frontend hardening slice is complete. The remaining frontend work is low
priority cleanup and optional state-management refinement only.
