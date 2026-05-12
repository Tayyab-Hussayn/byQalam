# Qalam Backend Pending Tasks

Last updated: 2026-05-10

This file tracks the remaining backend work after the initial FastAPI foundation,
Supabase database setup, auth/tenancy, preferences, posts workflow, first AI
generation layer, and LinkedIn integration foundation were built.

Master index:

- [QALAM_PENDING_TASKS.md](./QALAM_PENDING_TASKS.md)

Completed foundation:

- FastAPI app shell.
- Typed `.env` settings.
- Health and readiness endpoints.
- SQLAlchemy session/base.
- Alembic setup and initial migration.
- Initial user, workspace, plan, subscription, and usage models.
- Plan limit seed/sync service.
- Celery app foundation.
- Basic tests and lint setup.
- Supabase Postgres connection and Alembic migrations through `20260510_0005`.
- Supabase JWKS-first JWT verification with legacy JWT-secret fallback.
- Preferences, voice profiles, writing samples, and niche seeds.
- Posts, versions, media metadata, scheduled posts, and post workflow APIs.
- AI prompt template model/seed, generation run model, mock provider, and
  generation/regeneration APIs.
- LinkedIn OAuth state model, encrypted connection model, publish attempt model,
  connect/callback/status/disconnect endpoints, and text publish service.
- Celery scheduled publishing task and due-post claiming service.
- Database-backed quota resolution/enforcement and usage summary endpoint.
- Workspace invite model plus member/invite management APIs.
- Stripe checkout/portal/webhook scaffolding and billing summary endpoint.
- Real LLM provider adapters for OpenAI, Anthropic, Google, Groq, and Mistral.
- Request ID middleware and response header propagation.
- Audit log model and append-only event recording for core mutations.
- Notification model and failure notification helper for generation and publish failures.
- Dead-letter job model and Celery failure capture for worker retries.
- Structured API error contracts and normalized validation/HTTP errors.
- Redis-backed API rate limiting middleware.
- Optional Sentry integration hook.
- Media upload endpoint plus media-storage quota enforcement primitive.
- Docker image and compose-based local deployment files.
- Database backup script and operational runbook.
- Production CORS validation for deployment origins.
- Security review notes and production auth/encryption checks.
- GitHub Actions backend CI workflow for migrations, lint, and tests.

## 1. Database Setup

- Supabase Postgres selected and connected. Done.
- `backend/.env` created from `backend/.env.example`. Done.
- `DATABASE_URL` configured. Done.
- Alembic migrated through `20260510_0005`. Done.
- Plan limits synced from environment defaults into database. Done.
- Prompt templates synced into database. Done.

## 2. Auth And Tenancy

- Add Supabase JWT verification. Done.
- Add authenticated request dependency. Done.
- Add internal user sync from Supabase auth user ID. Done.
- Add `/api/v1/me`. Done.
- Add workspace creation API. Done.
- Add workspace listing API. Done.
- Add workspace member APIs. Done.
- Add role checks for `owner`, `admin`, `editor`, and `viewer`. Done for existing
  workspace-scoped APIs.
- Ensure every workspace query enforces membership. Done for current endpoints.
- Add workspace invite acceptance and role management. Done.

## 3. Preferences And Onboarding

- Add content preference models. Done.
- Add voice profile models. Done.
- Add writing sample models. Done.
- Add niche profile seed data for 10+ niches. Done.
- Add onboarding save/load APIs. Partially done through preferences, voice profile, and writing sample APIs.
- Add preferences update APIs. Done.

## 4. Posts Workflow

- Add post models. Done.
- Add post version models. Done.
- Add post media metadata models. Done.
- Add scheduled post models. Done.
- Add create/edit/delete draft APIs. Done.
- Add approve, reject, regenerate, schedule, cancel, and publish-now state transitions. Approve, reject, schedule, cancel, regenerate, and LinkedIn publish-now service foundation done.
- Add pagination and filtering for post lists. Done.

## 5. AI Content Engine

- Add AI provider interface. Done.
- Add mock AI provider for local development and tests. Done.
- Add real provider adapter support for OpenAI, Anthropic, Google, Groq, and Mistral. Done as HTTP-based adapters with config-driven API keys.
- Add prompt template models and versioning. Done.
- Add niche-aware prompt context builder. Done.
- Add generation endpoint. Done.
- Add regeneration endpoint. Done.
- Add quality checks. Basic mock quality score done; production validation pending.
- Store AI run metadata, token usage, estimated cost, latency, and output. Done.
- Enforce generation quotas through usage ledger. Done.

## 6. Workers And Scheduler

- Redis/Celery worker and beat commands are in place.
- Add scheduled post scanner. Done.
- Generation job support is in place through a Celery task.
- Publishing job queue is in place through the scheduled publishing task.
- Add retry and backoff rules. Basic Celery retry/backoff done.
- Add dead-letter handling. Done.
- Add worker-safe idempotency locks. Basic claim-by-status transition done.

## 7. LinkedIn Integration

- Add LinkedIn OAuth state model and service. Done.
- Add connect endpoint. Done.
- Add OAuth callback endpoint. Done.
- Encrypt and store access/refresh tokens. Done.
- Add LinkedIn connection status endpoint. Done.
- Add disconnect endpoint. Done.
- Add target discovery where API permissions allow.
- Add text-only publishing through LinkedIn Posts API. Done for publish-now
  service path; scheduled worker publishing still pending.
- Store publish attempts, LinkedIn post URNs, failures, and retry metadata. Done.
- Keep manual export fallback available while API approval is pending.

## 8. Billing And Quotas

- Add Stripe customer mapping. Done.
- Add Stripe Checkout endpoint. Done.
- Add Stripe Customer Portal endpoint. Done.
- Add Stripe webhook endpoint. Done.
- Store subscription status locally. Done.
- Enforce plan limits for generations, scheduled posts, published posts, workspaces, members, LinkedIn connections, and media storage. Done.
- Add usage endpoints for frontend billing/plan UI. Done.
- Add billing summary endpoint. Done.

## 9. Frontend Integration

- Set `NEXT_PUBLIC_API_BASE_URL`.
- Replace dashboard mock generation with backend generation endpoint.
- Replace hardcoded usage/plan state with backend usage APIs.
- Replace future settings mock state with preferences APIs.
- Add auth token/session integration once backend auth is ready.
- Add frontend error handling for backend API errors.

## 10. Production Hardening

- Add structured API error contracts. Done.
- Add request IDs. Done.
- Add rate limiting. Done.
- Add audit logs. Done.
- Add Sentry integration. Done.
- Add deployment Dockerfile. Done.
- Add backup strategy. Done.
- Add production CORS config. Done.
- Add security review for token encryption, secrets, auth, tenant isolation, and LinkedIn publishing. Done.
- Add CI checks for tests, lint, and migrations. Done.

## Immediate Next Task

Build LinkedIn target discovery where API permissions allow.
