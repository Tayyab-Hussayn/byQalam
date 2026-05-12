 Complete Auth Flow Analysis

  Current Architecture (per docs)

  User → Supabase Auth → Supabase JWT → FastAPI validates JWT → Backend creates user → Dashboard

  The Real Problem

  Looking at the code, the backend expects Authorization: Bearer <Supabase_JWT> header on protected
  routes. But the frontend isn't sending this.

  Detailed Breakdown

  1. Backend JWT Verification (working)

  backend/app/core/auth.py correctly validates Supabase JWTs via:
  - JWKS (preferred) - verifies ES256/RS256 tokens
  - Legacy HS256 secret fallback

  2. The Missing Pieces

  a) /api/auth/session-sync endpoint doesn't exist
  LoginClient.tsx:9 calls this endpoint but it's not created in the frontend.

  b) Supabase token is not forwarded to backend
  After login, LoginClient.tsx gets the Supabase access token but:
  - Never stores it for API calls
  - Never sends it as Bearer token to the backend

  c) No middleware to protect /dashboard
  There's no middleware.ts to:
  - Check Supabase auth state
  - Redirect unauthenticated users to login

  d) API client doesn't use Supabase token
  api/client.ts:32 adds Authorization: Bearer <token> but lib/auth/session.ts stores a separate in-memory
   token that's never set from Supabase auth.

  3. What The Docs Say Should Happen (per QALAM_BACKEND_GOAL_AND_ROADMAP.md:356-370)

  ▎ - FastAPI verifies Supabase JWTs on protected API requests
  ▎ - Backend auth responsibilities: Verify JWT issuer, audience, signature, expiry, and subject

  This is correct — backend IS set up to verify Supabase JWTs. But frontend isn't sending them.

  Summary of Issues

  ┌───────────────────────────────┬──────────────────────┬────────────┐
  │             Issue             │       Location       │   Status   │
  ├───────────────────────────────┼──────────────────────┼────────────┤
  │ No session-sync endpoint      │ Frontend /api/auth/* │ Missing    │
  ├───────────────────────────────┼──────────────────────┼────────────┤
  │ Supabase token not forwarded  │ LoginClient.tsx      │ Broken     │
  ├───────────────────────────────┼──────────────────────┼────────────┤
  │ No auth middleware            │ middleware.ts        │ Missing    │
  ├───────────────────────────────┼──────────────────────┼────────────┤
  │ Dashboard route not protected │ /dashboard           │ Exposed    │
  ├───────────────────────────────┼──────────────────────┼────────────┤
  │ Backend JWT verification      │ auth.py, deps.py     │ ✅ Working │
  └───────────────────────────────┴──────────────────────┴────────────┘

  What's Needed to Fix

  1. Session Sync API endpoint — sync Supabase session to backend
  2. Middleware — protect /dashboard, redirect to /login
  3. Token forwarding — send Supabase JWT as Bearer header on all API calls
  4. Backend session handling — create internal session or validate directly

  Should I build the missing auth pieces now? This will make registration/login work with Supabase and
  connect properly to the FastAPI backend.
