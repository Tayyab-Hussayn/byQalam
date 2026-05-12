# Auth Flow Fix Implementation Plan

**Goal:** Enable Supabase auth registration/login with JWT forwarded to FastAPI backend for protected dashboard access.

**Architecture:** Store Supabase JWT in httpOnly cookie + React context. Middleware protects `/dashboard`. API calls send Bearer token. Backend validates JWT and syncs users.

**Tech Stack:** Next.js 15, Supabase JS, FastAPI, JWT

---

## File Structure

```
frontend-wt/frontend/
├── src/
│   ├── middleware.ts                    # NEW: protect dashboard routes
│   ├── lib/auth/
│   │   ├── session.ts                   # MODIFY: token management
│   │   ├── supabase.ts                  # EXISTS: keep as-is
│   │   └── providers.tsx                # NEW: auth context provider
│   ├── lib/api/
│   │   └── client.ts                    # MODIFY: read token from cookie/context
│   └── app/
│       ├── layout.tsx                   # MODIFY: wrap with auth provider
│       ├── api/auth/session-sync/
│       │   └── route.ts                 # MODIFY: forward JWT to backend
│       └── login/LoginClient.tsx        # MODIFY: call session-sync
```

---

## Task 1: Create Auth Context Provider

**Files:**
- Create: `frontend-wt/frontend/src/lib/auth/providers.tsx`
- Test: `frontend-wt/frontend/src/lib/auth/__tests__/providers.test.tsx`

- [ ] **Step 1: Create auth context provider**

```tsx
// frontend-wt/frontend/src/lib/auth/providers.tsx
"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { supabase } from "./supabase";

interface AuthUser {
  id: string;
  email: string;
  accessToken: string;
}

interface AuthContextValue {
  user: AuthUser | null;
  isLoading: boolean;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
    setUser(null);
    await fetch("/api/auth/session-clear", { method: "POST" });
  }, []);

  useEffect(() => {
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      if (session?.access_token) {
        const {
          data: { user: supabaseUser },
        } = await supabase.auth.getUser();
        if (supabaseUser) {
          setUser({
            id: supabaseUser.id,
            email: supabaseUser.email ?? "",
            accessToken: session.access_token,
          });
        }
      } else {
        setUser(null);
      }
      setIsLoading(false);
    });

    // Initial session check
    supabase.auth.getSession().then(({ data }) => {
      if (data.session?.access_token) {
        const supabaseUser = data.session.user;
        setUser({
          id: supabaseUser.id,
          email: supabaseUser.email ?? "",
          accessToken: data.session.access_token,
        });
      }
      setIsLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
```

- [ ] **Step 2: Create test file**

```tsx
// frontend-wt/frontend/src/lib/auth/__tests__/providers.test.tsx
import { render, screen, waitFor } from "@testing-library/react";
import { AuthProvider, useAuth } from "../providers";
import { act } from "react";

function TestConsumer() {
  const { user, isLoading } = useAuth();
  return (
    <div>
      <span data-testid="loading">{String(isLoading)}</span>
      <span data-testid="user">{user?.email ?? "none"}</span>
    </div>
  );
}

describe("AuthProvider", () => {
  it("provides initial loading state", async () => {
    render(
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    );
    // isLoading should be true initially
    await waitFor(() => {
      expect(screen.getByTestId("loading")).toHaveTextContent("false");
    });
  });
});
```

- [ ] **Step 3: Commit**

```bash
cd /home/krawin/code/qalam
git add frontend-wt/frontend/src/lib/auth/providers.tsx
git add frontend-wt/frontend/src/lib/auth/__tests__/providers.test.tsx
git commit -m "feat(auth): add auth context provider for Supabase session"
```

---

## Task 2: Update Root Layout with AuthProvider

**Files:**
- Modify: `frontend-wt/frontend/src/app/layout.tsx`

- [ ] **Step 1: Read current layout**

Run: `cat frontend-wt/frontend/src/app/layout.tsx`

- [ ] **Step 2: Add AuthProvider wrapper**

```tsx
// frontend-wt/frontend/src/app/layout.tsx
import type { Metadata } from "next";
import { Plus_Jakarta_Sans, Cormorant_Garamond } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth/providers";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["400", "600"],
  variable: "--font-serif",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Qalam - AI-Powered LinkedIn Content Engine",
  description:
    "Generate authentic, on-brand LinkedIn content that sounds like you — not like a robot.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${plusJakarta.variable} ${cormorant.variable}`}>
      <body className="antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
```

- [ ] **Step 3: Commit**

```bash
cd /home/krawin/code/qalam
git add frontend-wt/frontend/src/app/layout.tsx
git commit -m "feat(auth): wrap app with AuthProvider"
```

---

## Task 3: Update API Client to Use Auth Token

**Files:**
- Modify: `frontend-wt/frontend/src/lib/api/client.ts`

- [ ] **Step 1: Read current client**

Run: `cat frontend-wt/frontend/src/lib/api/client.ts`

- [ ] **Step 2: Update to read from cookie for server-side, use useAuth for client-side**

```ts
// frontend-wt/frontend/src/lib/api/client.ts
import { cookies } from "next/headers";
import { ApiError } from "./error";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;
const SESSION_COOKIE = "qalam_session";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public body?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function getServerToken(): Promise<string | null> {
  const cookieStore = await cookies();
  return cookieStore.get(SESSION_COOKIE)?.value ?? null;
}

// Client-side: Import from useAuth via a singleton
let clientAccessToken: string | null = null;

export function setClientAccessToken(token: string | null) {
  clientAccessToken = token;
}

export function getClientAccessToken() {
  return clientAccessToken;
}

export async function apiRequest<T>(
  path: string,
  init: RequestInit = {},
  signal?: AbortSignal,
): Promise<T> {
  if (!API_BASE_URL) {
    throw new Error("NEXT_PUBLIC_API_BASE_URL is not configured");
  }

  // Try to get token - client-side first, then server-side
  let accessToken = clientAccessToken;
  if (!accessToken) {
    accessToken = await getServerToken();
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    signal,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
      ...init.headers,
    },
  });

  const contentType = response.headers.get("content-type") ?? "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message =
      typeof body === "object" && body && "message" in body
        ? String(body.message)
        : typeof body === "string" && body
          ? body
          : `Request failed with status ${response.status}`;

    throw new ApiError(response.status, message, body);
  }

  return body as T;
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend-wt/frontend/src/lib/api/client.ts
git commit -m "feat(auth): api client reads token from cookie/context"
```

---

## Task 4: Update Session Sync Route

**Files:**
- Modify: `frontend-wt/frontend/src/app/api/auth/session-sync/route.ts`

- [ ] **Step 1: Read current route**

Run: `cat frontend-wt/frontend/src/app/api/auth/session-sync/route.ts`

- [ ] **Step 2: Update to store JWT in httpOnly cookie**

```ts
// frontend-wt/frontend/src/app/api/auth/session-sync/route.ts
import { NextRequest, NextResponse } from "next/server";

const SESSION_COOKIE = "qalam_session";

export async function POST(request: NextRequest) {
  try {
    const { accessToken } = await request.json();

    if (!accessToken || typeof accessToken !== "string") {
      return NextResponse.json(
        { error: "Access token is required" },
        { status: 400 }
      );
    }

    const response = NextResponse.json({ ok: true });
    response.cookies.set(SESSION_COOKIE, accessToken, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24 * 7, // 7 days - match Supabase token expiry
    });

    // Also sync the client-side token
    response.cookies.set("qalam_token", accessToken, {
      httpOnly: false, // readable by client JS
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      maxAge: 60 * 60 * 24 * 7,
    });

    return response;
  } catch {
    return NextResponse.json(
      { error: "Failed to sync session" },
      { status: 500 }
    );
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend-wt/frontend/src/app/api/auth/session-sync/route.ts
git commit -m "feat(auth): session-sync stores JWT in httpOnly cookie"
```

---

## Task 5: Update LoginClient to Sync JWT

**Files:**
- Modify: `frontend-wt/frontend/src/app/login/LoginClient.tsx`

- [ ] **Step 1: Read current LoginClient**

Run: `cat frontend-wt/frontend/src/app/login/LoginClient.tsx`

- [ ] **Step 2: Update handleSignIn and handleSignUp to sync JWT**

```tsx
// frontend-wt/frontend/src/app/login/LoginClient.tsx
"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/auth/supabase";
import { setClientAccessToken } from "@/lib/api/client";

async function syncSessionCookie(accessToken: string) {
  const response = await fetch("/api/auth/session-sync", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ accessToken }),
  });
  return response.ok;
}

export default function LoginClient({ nextPath }: { nextPath: string }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState<"signin" | "signup" | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const canSubmit = useMemo(() => Boolean(email.trim() && password.trim()), [email, password]);

  async function handleSignIn() {
    if (!canSubmit || loading) return;
    setLoading("signin");
    setMessage(null);
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    if (error) {
      setMessage(error.message);
      setLoading(null);
      return;
    }
    if (data.session?.access_token) {
      // Store client-side token
      setClientAccessToken(data.session.access_token);
      // Sync with backend
      await syncSessionCookie(data.session.access_token);
      router.push(nextPath);
      router.refresh();
      return;
    }
    setMessage("Signed in, but no session token was returned.");
    setLoading(null);
  }

  async function handleSignUp() {
    if (!canSubmit || loading) return;
    setLoading("signup");
    setMessage(null);
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    });
    if (error) {
      setMessage(error.message);
      setLoading(null);
      return;
    }
    if (data.session?.access_token) {
      // Store client-side token
      setClientAccessToken(data.session.access_token);
      // Sync with backend
      await syncSessionCookie(data.session.access_token);
      router.push(nextPath);
      router.refresh();
      return;
    }
    setMessage("Check your email to confirm the account before continuing.");
    setLoading(null);
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-[#060D0A] px-6 py-12 text-[#F0EDE6]">
      <section className="w-full max-w-md rounded-2xl border border-[rgba(201,146,42,0.25)] bg-[#0A1510] p-8 shadow-2xl">
        <Link href="/" className="mb-8 inline-block text-sm font-semibold text-[#C9922A]">
          Qalam.
        </Link>
        <h1 className="font-serif text-3xl text-[#F0EDE6]">Log in to Qalam</h1>
        <p className="mt-3 text-sm leading-6 text-[#B8B4AA]">
          Use your Supabase account to access the dashboard and connect the backend session.
        </p>
        <div className="mt-8 space-y-5">
          <label className="block">
            <span className="text-xs uppercase tracking-[0.14em] text-[#7A7670]">Email</span>
            <input
              className="mt-2 w-full rounded-lg border border-[rgba(201,146,42,0.15)] bg-[#0F1E17] px-4 py-3 text-sm outline-none transition focus:border-[#C9922A]"
              name="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label className="block">
            <span className="text-xs uppercase tracking-[0.14em] text-[#7A7670]">Password</span>
            <input
              className="mt-2 w-full rounded-lg border border-[rgba(201,146,42,0.15)] bg-[#0F1E17] px-4 py-3 text-sm outline-none transition focus:border-[#C9922A]"
              name="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
          {message ? <p className="text-sm leading-6 text-[#E8B84B]">{message}</p> : null}
          <div className="grid gap-3">
            <button
              className="w-full rounded-lg bg-[#C9922A] px-4 py-3 text-sm font-semibold text-[#060D0A] transition hover:bg-[#E8B84B] disabled:cursor-not-allowed disabled:opacity-70"
              type="button"
              disabled={!canSubmit || loading !== null}
              onClick={handleSignIn}
            >
              {loading === "signin" ? "Signing in..." : "Continue to dashboard"}
            </button>
            <button
              className="w-full rounded-lg border border-[rgba(201,146,42,0.25)] bg-transparent px-4 py-3 text-sm font-semibold text-[#F0EDE6] transition hover:border-[#C9922A] disabled:cursor-not-allowed disabled:opacity-70"
              type="button"
              disabled={!canSubmit || loading !== null}
              onClick={handleSignUp}
            >
              {loading === "signup" ? "Creating account..." : "Create account"}
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend-wt/frontend/src/app/login/LoginClient.tsx
git commit -m "feat(auth): login syncs Supabase JWT to backend"
```

---

## Task 6: Create Auth Middleware

**Files:**
- Create: `frontend-wt/frontend/src/middleware.ts`

- [ ] **Step 1: Create middleware**

```ts
// frontend-wt/frontend/src/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const SESSION_COOKIE = "qalam_session";
const PUBLIC_PATHS = ["/", "/login", "/api/auth/", "/_next/", "/favicon.ico"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths
  if (PUBLIC_PATHS.some((path) => pathname.startsWith(path))) {
    return NextResponse.next();
  }

  // Check for session cookie
  const sessionCookie = request.cookies.get(SESSION_COOKIE);
  if (sessionCookie?.value) {
    return NextResponse.next();
  }

  // Redirect to login with return URL
  const loginUrl = new URL("/login", request.url);
  loginUrl.searchParams.set("next", pathname);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/dashboard/:path*", "/api/v1/:path*"],
};
```

- [ ] **Step 2: Commit**

```bash
git add frontend-wt/frontend/src/middleware.ts
git commit -m "feat(auth): add middleware to protect dashboard routes"
```

---

## Task 7: Verify Build

- [ ] **Step 1: Run lint**

```bash
cd frontend-wt/frontend && npm run lint
```
Expected: No errors

- [ ] **Step 2: Run build**

```bash
cd frontend-wt/frontend && npm run build
```
Expected: Build successful

- [ ] **Step 3: Test the flow**

1. Start frontend: `cd frontend-wt/frontend && npm run dev`
2. Start backend: `cd backend && uvicorn app.main:app --reload`
3. Visit `/login`
4. Try creating account or signing in
5. Verify redirect to `/dashboard` works
6. Check browser devtools for `qalam_session` cookie

---

## Task 8: Write Design Document

- [ ] **Step 1: Write auth flow design doc**

```markdown
# Auth Flow Implementation - Design

## Goal
Enable Supabase auth registration/login with JWT forwarded to FastAPI backend for protected dashboard access.

## Architecture

User → Supabase Auth → JWT stored in httpOnly cookie → Middleware checks → API calls send Bearer token → Backend validates JWT and syncs user

## Components

1. **AuthProvider** (`providers.tsx`)
   - React context managing auth state
   - Listens to Supabase auth state changes
   - Exposes `user`, `isLoading`, `signOut`

2. **API Client** (`lib/api/client.ts`)
   - Reads `qalam_session` cookie for server-side requests
   - Uses client-side token for client requests
   - Sends `Authorization: Bearer <token>` header

3. **Session Sync** (`/api/auth/session-sync`)
   - Accepts Supabase access token from client
   - Stores in httpOnly `qalam_session` cookie

4. **Middleware** (`middleware.ts`)
   - Protects `/dashboard` routes
   - Checks for `qalam_session` cookie
   - Redirects to `/login` if missing

5. **LoginClient** (`/login/LoginClient.tsx`)
   - After Supabase auth, syncs JWT to backend
   - Stores token client-side for API calls

## Backend Integration

Backend expects `Authorization: Bearer <Supabase_JWT>` on protected routes.
`deps.py:get_current_user` validates JWT and syncs user via `sync_authenticated_user`.
```

- [ ] **Step 2: Save design doc**

```bash
mkdir -p docs/superpowers/specs
cat > docs/superpowers/specs/2026-05-11-auth-flow-fix.md << 'EOF'
# Auth Flow Implementation Design

> Document the auth flow fix implementation.

## Architecture
[see above]

## Components
[see above]

## Backend Contract
- GET /api/v1/me - requires Authorization: Bearer <JWT>
- Returns user + workspaces
EOF
```

- [ ] **Step 3: Commit design doc**

```bash
git add docs/superpowers/specs/2026-05-11-auth-flow-fix.md
git commit -m "docs: add auth flow implementation design"
```

---

## Self-Review Checklist

- [ ] All files have exact paths
- [ ] Each task has code to write, test to run, commit to make
- [ ] No placeholders (TBD, TODO, etc.)
- [ ] Type consistency across tasks
- [ ] Spec requirements covered: session-sync, middleware, token forwarding, login integration