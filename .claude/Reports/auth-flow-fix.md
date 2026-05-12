Auth Flow Fix - Final Design

  Architecture:
  User → Supabase Auth → Supabase JWT → Frontend stores in memory
         ↓
  Middleware checks token → allows/redirects to /login
         ↓
  API calls: Authorization: Bearer <Supabase_JWT>
         ↓
  Backend validates JWT, syncs user, returns data

  Components to build:

  1. Enhanced session-sync route

  - Accepts Supabase access token from client
  - Stores in httpOnly cookie (for SSR) + React context (for client)
  - Sets it so it can be read by Next.js server components

  2. Auth middleware (middleware.ts)

  - Intercepts /dashboard/* requests
  - Checks for qalam_session cookie OR Supabase token in headers
  - Redirects unauthenticated users to /login?next=<return_url>

  3. Updated LoginClient.tsx

  - On successful Supabase auth, calls session-sync with the access token
  - Sets token in React context for client-side API calls

  4. Updated API client (lib/api/client.ts)

  - Reads token from cookie (for server) or context (for client)
  - Sends Authorization: Bearer <token> on all requests
  - Handles 401 errors → redirect to login

  5. Backend /api/v1/me bootstrap

  - Validates JWT, creates/updates user in database
  - Returns user + workspaces

  ---
  Should I proceed with implementation? This will give you a working auth flow: register, login,
  protected dashboard.
