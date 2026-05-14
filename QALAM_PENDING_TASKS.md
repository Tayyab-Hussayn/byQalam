# Qalam Pending Tasks

Last updated: 2026-05-14

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
- Auto-redirect logged-in users from `/`, `/login`, `/register` to dashboard
- Proper null handling for Supabase client across all components

### Login/Register UI Split ✓ (2026-05-14)
- Separate `/login` and `/register` routes with distinct UIs
- Google OAuth button on both pages (pending provider enablement)
- Visual divider with "or" between OAuth and email/password
- Login: "Forgot password?" link, bottom "Sign up" link
- Register: Password hint "Use 8 or more characters", bottom "Log in" link

### Forgot Password Flow ✓ (2026-05-14)
- `/forgot-password` - Request password reset email
- `/reset-password` - Set new password after clicking email link
- Supabase `resetPasswordForEmail()` with redirect URL
- Middleware updated to allow access to auth pages when not authenticated

### Logout Button ✓ (2026-05-14)
- Sign out button added in Settings tab
- Clears Supabase session + httpOnly cookie
- Redirects to `/login`

### Repository Setup ✓
- Single `main` branch (removed old `backend` and `frontend` branches)
- All code in `/frontend` and `/backend` directories
- GitHub repo: https://github.com/Tayyab-Hussayn/byQalam

## Frontend Remaining Tasks

- Connect backend API for full dashboard data
- Complete LinkedIn integration UI
- Complete billing UI
- Add email verification handling

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