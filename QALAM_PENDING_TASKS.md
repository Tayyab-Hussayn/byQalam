# Qalam Pending Tasks

Last updated: 2026-05-12

This is the master list of remaining work for Qalam. It consolidates the
frontend and backend trackers so the current build state is easy to read in one
place.

Detailed trackers:

- [QALAM_FRONTEND_PENDING_TASKS.md](./QALAM_FRONTEND_PENDING_TASKS.md)
- [QALAM_BACKEND_PENDING_TASKS.md](./QALAM_BACKEND_PENDING_TASKS.md)

## Completed This Session (Auth Flow)

### Authentication System ✓
- Unified repository structure (frontend + backend in single repo)
- Supabase JWT authentication integrated
- Session sync endpoint stores JWT in httpOnly cookie
- Auth middleware redirects authenticated users to dashboard
- Auto-redirect logged-in users from `/` and `/login` to dashboard
- Proper null handling for Supabase client across all components

### Repository Setup ✓
- Single `main` branch (removed old `backend` and `frontend` branches)
- All code in `/frontend` and `/backend` directories
- GitHub repo: https://github.com/Tayyab-Hussayn/byQalam

## Frontend Remaining Tasks

- Connect backend API for full dashboard data
- Complete LinkedIn integration UI
- Complete billing UI
- Add email verification handling

### Completed This Session
- Forgot password flow implemented (/forgot-password, /reset-password)

## Backend Remaining Tasks

- Deploy backend to production (Render)
- Configure Supabase JWT verification in production
- Connect frontend to production backend API
- LinkedIn target discovery where API permissions allow

## Current Priority

1. Deploy backend to production (Render)
2. Connect frontend to production backend
3. Complete user onboarding flow
4. Test full auth flow end-to-end

## Architecture Notes

- Frontend: Next.js 16, TypeScript, Tailwind CSS
- Auth: Supabase Auth with JWT stored in httpOnly cookie
- Middleware: Next.js middleware for auth-aware routing
- Dashboard: Protected by middleware, redirects to `/login` if no session