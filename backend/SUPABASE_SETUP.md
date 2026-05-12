# Supabase Setup For Qalam Backend

This backend uses Supabase as managed PostgreSQL. Supabase CLI is optional for local Supabase development, but it is not required to connect Qalam to a real hosted Supabase database.

## Recommended Connection Method

Use Supabase's **Session pooler** connection string for this FastAPI backend.

Reason:

- Qalam's API is a persistent backend service.
- Session pooler supports IPv4 and IPv6.
- It works well with SQLAlchemy's application-side connection pool.

For long-lived production servers with IPv6 support, direct connection can also work. For serverless/edge-style deployments, transaction pooler can be used, but prepared statement behavior needs extra care.

Official Supabase reference:

- https://supabase.com/docs/reference/postgres/connection-strings

## What To Copy From Supabase

In Supabase dashboard:

1. Open your project.
2. Click **Connect**.
3. Choose **Session pooler**.
4. Copy the connection string.
5. Replace `[YOUR-PASSWORD]` with the database password.

Supabase may give a URL like:

```text
postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
```

For this backend, set `DATABASE_URL` as:

```text
DATABASE_URL=postgresql+asyncpg://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
```

The important change is:

```text
postgresql:// -> postgresql+asyncpg://
```

## Required Backend Env Values

Create `backend/.env`:

```bash
cd backend
cp .env.example .env
```

Then update:

```text
DATABASE_URL=postgresql+asyncpg://...
SUPABASE_URL=https://PROJECT_REF.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
SUPABASE_SECRET_KEY=sb_secret_...
```

For database-only setup, `DATABASE_URL` is the only required value. For modern Supabase Auth verification, set `SUPABASE_URL` so the backend can use the JWKS endpoint. For backend admin operations later, use `SUPABASE_SECRET_KEY`.

Legacy compatibility:

```text
SUPABASE_JWT_SECRET=...
SUPABASE_SERVICE_ROLE_KEY=...
```

These are only for older Supabase projects or migration fallback. New hosted Supabase projects should use publishable and secret API keys.

Make sure `[YOUR-PASSWORD]` is replaced with the real database password. Leaving the placeholder in the URL will fail the connection check.

## Validate Connection

After setting `DATABASE_URL`:

```bash
cd backend
python -m app.scripts.check_database
```

Expected result:

```text
Database connection OK
```

## Run Migrations

```bash
cd backend
alembic upgrade head
```

## Sync Plan Limits

This reads plan defaults from `.env` and writes them to the database:

```bash
python -m app.scripts.sync_plan_limits
```

## Verify API Readiness

Run the API:

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://localhost:8000/api/v1/health
http://localhost:8000/api/v1/ready
```

`/health` checks that the API process is alive.

`/ready` checks that the API can query the database.
