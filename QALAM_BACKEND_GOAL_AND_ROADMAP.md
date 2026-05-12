# Qalam Backend Goal And Roadmap

Last updated: 2026-05-10

This document defines the backend goal, architecture, roadmap, database decision, LinkedIn publishing strategy, AI content generation engine, and production requirements for Qalam.

Primary product architecture reference:

- `/home/krawin/code/qalam/QALAM_PRODUCT_ARCHITECTURE_PLAN.md`

Current frontend reference:

- `/home/krawin/code/qalam/frontend`

## 1. Backend Goal

The backend goal is to build a production-grade FastAPI service for Qalam that can safely power a serious LinkedIn content automation SaaS.

The backend must own every sensitive and business-critical workflow:

- User authentication and session verification.
- Workspace and client tenancy.
- Role-based authorization.
- User profile, niche, voice, and content preferences.
- AI content generation, regeneration, scoring, and usage tracking.
- Post drafts, review queue, approvals, scheduling, and publishing state.
- LinkedIn OAuth, token storage, target selection, and publishing.
- Billing plans, quota enforcement, and usage ledgers.
- Background workers for generation, scheduling, publishing, retries, and notifications.
- Audit logs, observability, and operational controls.

The frontend should never hold provider secrets, LinkedIn tokens, billing truth, quota truth, or generation logic. It should call the backend through typed API contracts.

## 2. Core Backend Product Model

Qalam is not a simple prompt wrapper. The backend should model Qalam as a content operations platform.

Core workflow:

1. A user signs up and creates a workspace.
2. The workspace collects profile, niche, audience, goals, voice, writing samples, posting preferences, and LinkedIn targets.
3. The backend stores those preferences as durable structured data.
4. The AI engine uses the workspace profile and niche strategy to generate posts.
5. Generated posts are saved as versioned drafts.
6. The user can approve, reject, edit, regenerate, or schedule posts.
7. Scheduled posts become background publishing jobs.
8. Workers publish to LinkedIn if the account is connected, authorized, healthy, and within plan limits.
9. Every generation, edit, schedule, publish attempt, failure, quota usage, and billing event is recorded.

The backend must be multi-tenant from day one. Even if most early customers are solo users, the system should use workspaces so it can later support agencies, teams, and 1000+ client workspaces without rewriting the data model.

## 3. Recommended Backend Stack

Use this stack for the first real backend implementation:

- Framework: FastAPI
- Language: Python 3.12+
- Validation: Pydantic v2
- ORM: SQLAlchemy 2.0
- Migrations: Alembic
- Database: PostgreSQL
- Early managed platform: Supabase Postgres
- Auth start: Supabase Auth, verified by FastAPI
- Cache and broker: Redis
- Workers: Celery with Redis broker
- Scheduler: Celery Beat or a dedicated scheduler process
- Storage: Supabase Storage initially, behind a storage service abstraction
- Billing: Stripe Checkout, Customer Portal, and webhooks
- Observability: structured JSON logs, Sentry, OpenTelemetry-ready request IDs
- Testing: pytest, pytest-asyncio, httpx test client, factory fixtures

Reasoning:

FastAPI is a strong fit for Qalam because it gives clean API contracts, high-quality OpenAPI output, Python-native AI orchestration, strong validation with Pydantic, and easy separation between HTTP routes and backend services.

PostgreSQL is the correct system of record because Qalam needs relational integrity across users, workspaces, posts, schedules, subscriptions, OAuth connections, usage, audit logs, and publishing attempts.

Redis-backed workers are required because AI generation, media handling, scheduling, LinkedIn publishing, retries, and webhook processing should not run inside frontend requests or long blocking API calls.

## 3.1 Environment And Configuration Strategy

Qalam should use `.env` files and runtime environment variables professionally from the first backend commit. The goal is to keep secrets out of source code, support multiple deployment environments, and make AI provider switching possible without rewriting business logic.

Required files:

- `backend/.env.example`: committed template with safe placeholder values.
- `backend/.env`: local developer secrets, never committed.
- Production environment variables: configured in the hosting platform or secret manager, not stored in the repo.

The backend should load configuration through `app/core/config.py` using Pydantic settings. Route handlers and services should read from a typed settings object, not call `os.getenv()` directly throughout the codebase.

Environment groups:

```text
APP_ENV=local
APP_NAME=Qalam API
APP_DEBUG=true
APP_API_PREFIX=/api/v1
APP_FRONTEND_URL=http://localhost:3000
APP_CORS_ORIGINS=http://localhost:3000

DATABASE_URL=postgresql+asyncpg://...
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

SUPABASE_URL=
SUPABASE_JWKS_URL=
SUPABASE_PUBLISHABLE_KEY=
SUPABASE_SECRET_KEY=
SUPABASE_JWT_SECRET=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_STORAGE_BUCKET=qalam-media

JWT_AUDIENCE=authenticated
JWT_ISSUER=
COOKIE_DOMAIN=

ENCRYPTION_KEY=
TOKEN_ENCRYPTION_KEY_ID=local

AI_DEFAULT_PROVIDER=openai
AI_DEFAULT_MODEL=
AI_FALLBACK_PROVIDER=
AI_REQUEST_TIMEOUT_SECONDS=60
AI_MAX_RETRIES=2
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_AI_API_KEY=
GROQ_API_KEY=
MISTRAL_API_KEY=

LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINKEDIN_REDIRECT_URI=http://localhost:8000/api/v1/linkedin/oauth/callback
LINKEDIN_API_VERSION=202604

STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_STARTER=
STRIPE_PRICE_PRO=
STRIPE_PRICE_AGENCY=

SENTRY_DSN=
LOG_LEVEL=INFO
RATE_LIMIT_BACKEND=redis
```

AI provider configuration:

- `.env` should decide which provider is active by default.
- Provider keys must only exist in backend env variables or a production secret manager.
- The database should store AI run metadata: provider, model, prompt version, tokens, cost, latency, and result.
- The provider abstraction should allow OpenAI, Anthropic, Google, Groq, Mistral, or a mock provider without changing API routes.
- Local and test environments should support `AI_DEFAULT_PROVIDER=mock` for deterministic tests.

Resource allocation configuration:

Plan limits should not be hardcoded in route handlers. The professional approach is:

- Store active plans and quota limits in the database.
- Define default plan limits in `.env` for each environment.
- Run a backend seed/sync command that reads those `.env` defaults and writes them into the database.
- Use the database as the runtime source of truth for each workspace subscription and quota.
- Keep Stripe price IDs in `.env`, because those are environment-specific.

Example bootstrap defaults:

```text
FREE_MONTHLY_AI_GENERATIONS=20
FREE_MONTHLY_SCHEDULED_POSTS=5
FREE_MAX_WORKSPACES=1
FREE_MAX_MEMBERS=1
FREE_MAX_LINKEDIN_CONNECTIONS=0
FREE_MEDIA_STORAGE_MB=50

STARTER_MONTHLY_AI_GENERATIONS=300
STARTER_MONTHLY_SCHEDULED_POSTS=100
STARTER_MAX_WORKSPACES=1
STARTER_MAX_MEMBERS=2
STARTER_MAX_LINKEDIN_CONNECTIONS=1
STARTER_MEDIA_STORAGE_MB=500

PRO_MONTHLY_AI_GENERATIONS=1000
PRO_MONTHLY_SCHEDULED_POSTS=500
PRO_MAX_WORKSPACES=3
PRO_MAX_MEMBERS=5
PRO_MAX_LINKEDIN_CONNECTIONS=3
PRO_MEDIA_STORAGE_MB=5000

AGENCY_MONTHLY_AI_GENERATIONS=5000
AGENCY_MONTHLY_SCHEDULED_POSTS=2500
AGENCY_MAX_WORKSPACES=50
AGENCY_MAX_MEMBERS=25
AGENCY_MAX_LINKEDIN_CONNECTIONS=50
AGENCY_MEDIA_STORAGE_MB=50000
```

Important rule:

These env quota values are seed/sync defaults, not the live quota authority during normal requests. The intended flow is:

1. Update plan defaults in `.env`.
2. Run a backend command such as `python -m app.scripts.sync_plan_limits`.
3. The command reads `.env` and updates the database `plans` rows.
4. Runtime quota checks read from `plans`, `subscriptions`, and `usage_ledger`.

That means `.env` and the database should start with the same limits, but the database is what the app trusts when a user generates, schedules, or publishes content. `.env` does not directly "contact" the database by itself; backend code reads `.env` and writes the values to the database through an explicit seed/sync command.

This is the safest long-term design because Qalam can later change plan limits, grandfather customers, add custom enterprise contracts, run promotions, or expose an admin plan editor without redeploying the backend every time.

Feature flags that can live in `.env`:

- `ENABLE_LINKEDIN_PUBLISHING`
- `ENABLE_LINKEDIN_COMPANY_PAGES`
- `ENABLE_MEDIA_UPLOADS`
- `ENABLE_STRIPE_BILLING`
- `ENABLE_AI_GENERATION`
- `ENABLE_BACKGROUND_GENERATION`
- `ENABLE_RATE_LIMITING`

Secrets that must never be committed:

- AI provider API keys.
- Supabase service role key.
- LinkedIn client secret.
- Stripe secret key.
- Stripe webhook secret.
- Token encryption keys.
- Database passwords.
- Redis passwords.
- Sentry DSN if private.

Environment validation:

- Backend startup should fail fast if required variables are missing for the selected environment.
- Local development can allow mock providers.
- Production must require real database, Redis, encryption key, auth verification config, and any enabled provider secrets.
- `.env.example` should be updated every time a new config value is introduced.

## 4. Database Decision

Decision: use PostgreSQL as the canonical database and start with Supabase Postgres for managed hosting, auth, and storage.

This means:

- The data model is designed for PostgreSQL first.
- Supabase is used as the early managed Postgres provider.
- Supabase Auth is used initially to avoid building password auth from scratch.
- Supabase Storage is used initially for user-uploaded media.
- SQLAlchemy and Alembic remain the backend source of truth for app tables and migrations.
- Core business logic should not depend on Supabase-only client-side database access.
- If the product outgrows Supabase operationally, the database can move to another managed PostgreSQL provider with less pain.

Why Supabase is a good early fit:

- It provides managed Postgres, auth, storage, backups on paid plans, and a quick path to production.
- It supports Row Level Security, which is useful as defense in depth.
- It has paid compute tiers and connection pooling options, so 1000+ client workspaces is realistic if the schema, indexes, query patterns, and workers are built correctly.

Important scale judgment:

1000+ clients is not a large number for PostgreSQL. The real scaling risks for Qalam are:

- AI generation cost and concurrency.
- LinkedIn API approval, permissions, token expiry, and rate limits.
- Publishing job reliability.
- Multi-tenant authorization mistakes.
- Poor indexes on posts, schedules, publish attempts, usage ledgers, and workspace-scoped queries.
- Large media files if video publishing is added.

Therefore the right approach is not "Supabase vs PostgreSQL" as separate choices. The right approach is PostgreSQL, with Supabase as the first managed PostgreSQL platform.

## 5. Backend Repository Structure

Recommended backend structure:

```text
backend/
  app/
    main.py
    api/
      deps.py
      errors.py
      v1/
        router.py
        auth.py
        users.py
        workspaces.py
        onboarding.py
        preferences.py
        posts.py
        schedules.py
        generation.py
        linkedin.py
        billing.py
        usage.py
        notifications.py
    core/
      config.py
      logging.py
      security.py
      permissions.py
      rate_limits.py
      idempotency.py
      encryption.py
    db/
      base.py
      session.py
      models/
      migrations/
    schemas/
      auth.py
      workspace.py
      preferences.py
      post.py
      generation.py
      linkedin.py
      billing.py
      usage.py
    services/
      auth/
      workspaces/
      preferences/
      posts/
      ai/
      linkedin/
      billing/
      usage/
      storage/
      notifications/
    workers/
      celery_app.py
      generation_jobs.py
      publishing_jobs.py
      billing_jobs.py
      maintenance_jobs.py
    tests/
      unit/
      integration/
      api/
```

Rules:

- Route handlers should stay thin.
- Business logic belongs in services.
- Database models belong in `db/models`.
- Request and response contracts belong in `schemas`.
- Background work belongs in `workers`.
- Provider-specific logic belongs behind service interfaces.

## 6. Authentication And Authorization

Initial auth decision:

- Use Supabase Auth for signup, login, email verification, password reset, and optional social login.
- FastAPI verifies Supabase JWTs on protected API requests.
- Qalam keeps internal app tables for users, workspaces, members, roles, plans, and usage.

Why:

- It avoids building password storage and account recovery from scratch.
- It is free or low-cost to start.
- It gives a clean migration path because the backend still owns authorization and business data.

Backend auth responsibilities:

- Verify JWT issuer, audience, signature, expiry, and subject.
- Map external auth user ID to internal `users.id`.
- Enforce workspace membership on every workspace-scoped query.
- Enforce role permissions for sensitive actions.
- Enforce plan and quota limits before generation, scheduling, and publishing.
- Never trust a workspace ID from the frontend without checking membership.

Initial roles:

- `owner`: full workspace control, billing, LinkedIn connections, publishing.
- `admin`: manage content, preferences, members, and publishing.
- `editor`: create, edit, approve, and schedule content if allowed.
- `viewer`: read-only access.

Auth endpoints:

- `GET /api/v1/me`
- `GET /api/v1/me/workspaces`
- `POST /api/v1/workspaces`
- `PATCH /api/v1/workspaces/{workspace_id}`
- `POST /api/v1/workspaces/{workspace_id}/members`
- `PATCH /api/v1/workspaces/{workspace_id}/members/{member_id}`

## 7. Tenancy Model

Every important business row should be scoped to a workspace.

Core tenancy entities:

- `users`
- `workspaces`
- `workspace_members`
- `workspace_invitations`
- `roles`
- `permissions`
- `audit_logs`

Workspace-scoped tables:

- `content_preferences`
- `voice_profiles`
- `writing_samples`
- `posts`
- `post_versions`
- `post_media`
- `scheduled_posts`
- `publish_attempts`
- `ai_generation_runs`
- `linkedin_connections`
- `linkedin_targets`
- `usage_ledger`
- `notifications`

Required query rule:

Every workspace-scoped service method must accept `workspace_id` and authenticated user context, then authorize access before reading or mutating data.

## 8. Initial Database Model

Initial tables:

- `users`
- `workspaces`
- `workspace_members`
- `workspace_invitations`
- `plans`
- `subscriptions`
- `usage_ledger`
- `usage_counters`
- `content_preferences`
- `voice_profiles`
- `writing_samples`
- `niche_profiles`
- `prompt_templates`
- `posts`
- `post_versions`
- `post_media`
- `scheduled_posts`
- `ai_generation_runs`
- `quality_checks`
- `linkedin_connections`
- `linkedin_targets`
- `oauth_states`
- `publish_attempts`
- `billing_customers`
- `billing_webhook_events`
- `notifications`
- `audit_logs`
- `outbox_events`

Important enums:

- `workspace_role`: `owner`, `admin`, `editor`, `viewer`
- `subscription_status`: `trialing`, `active`, `past_due`, `canceled`, `incomplete`
- `post_status`: `draft`, `generated`, `needs_review`, `approved`, `scheduled`, `publishing`, `published`, `rejected`, `failed`, `cancelled`
- `post_source`: `ai`, `custom`, `imported`
- `linkedin_target_type`: `member`, `organization`
- `linkedin_connection_status`: `connected`, `expired`, `revoked`, `error`, `disconnected`
- `publish_attempt_status`: `queued`, `running`, `succeeded`, `retrying`, `failed`, `cancelled`
- `generation_status`: `queued`, `running`, `succeeded`, `failed`, `cancelled`

Critical indexes:

- `workspace_members(user_id, workspace_id)`
- `posts(workspace_id, status, created_at)`
- `posts(workspace_id, scheduled_for)`
- `scheduled_posts(workspace_id, status, scheduled_for)`
- `publish_attempts(workspace_id, post_id, created_at)`
- `ai_generation_runs(workspace_id, created_at)`
- `usage_ledger(workspace_id, metric, period_start, period_end)`
- `linkedin_connections(workspace_id, status)`
- `audit_logs(workspace_id, created_at)`

## 9. AI Content Generation Engine

The AI engine is the most important backend subsystem. It should be built as a pipeline, not as one prompt in a route handler.

AI engine goal:

Generate high-quality LinkedIn content that reflects the user's niche, audience, voice, goals, preferred structure, and previous feedback while avoiding fake claims, repetitive output, and risky automation patterns.

### AI Input Data

The engine should use these saved inputs:

- Workspace profile.
- User profession and niche.
- Target audience.
- Products, services, offers, or expertise.
- Content goals.
- Preferred post language.
- Tone and writing style.
- CTA preference.
- Emoji and hashtag policy.
- Topics to avoid.
- Claims that are approved to mention.
- Writing samples.
- Previous approved posts.
- Previous rejected posts and rejection reasons.
- User edits and regeneration feedback.
- Posting cadence and content mix.

### Supported Niches

Niches should be stored as database seed data, not hardcoded only in prompts.

Initial niche profiles:

- HR and recruiting
- Software engineering and web development
- SaaS founders
- Business consultants
- Marketing strategists
- Content creators
- Entrepreneurs
- Career coaches
- Agency owners
- E-commerce operators
- Real estate professionals
- Finance advisors
- Healthcare professionals
- Product managers
- Sales professionals

Each niche profile should define:

- Audience types.
- Common content pillars.
- Good hook patterns.
- Useful post structures.
- Vocabulary guidance.
- Risky claims to avoid.
- CTA examples.
- Hashtag guidance.
- Banned or discouraged patterns.

### AI Pipeline

Generation pipeline:

1. Validate workspace access and plan quota.
2. Load profile, preferences, voice profile, niche profile, and recent posts.
3. Build a structured generation context.
4. Select a prompt template version.
5. Generate topic ideas if no specific prompt is provided.
6. Generate post draft.
7. Generate hook and CTA alternatives when useful.
8. Generate hashtags and optional first comment.
9. Run quality checks.
10. Run policy and safety checks.
11. Score the result.
12. Save `ai_generation_run`.
13. Save `post` and first `post_version`.
14. Increment usage ledger.
15. Return a typed response to the frontend.

Quality checks:

- No unsupported statistics.
- No fake client results.
- No fake personal experiences.
- No guaranteed business outcomes.
- No spammy engagement bait.
- No excessive hashtags.
- No repetitive format across recent posts.
- Fits LinkedIn length constraints.
- Matches the selected tone and audience.
- Includes a clear point or insight.
- Uses user-provided claims only when claims are needed.

Regeneration should accept a reason:

- `make_shorter`
- `make_more_professional`
- `make_more_personal`
- `add_storytelling`
- `stronger_hook`
- `less_hype`
- `change_tone`
- `custom_instruction`

### AI Provider Abstraction

Do not lock the system to one provider in route handlers.

Use an internal interface:

```text
ContentGenerationProvider
  generate_post(context) -> GeneratedPost
  generate_variants(context) -> GeneratedVariants
  evaluate_post(context, post) -> QualityEvaluation
```

Store for every AI run:

- Provider.
- Model.
- Prompt template name and version.
- Input JSON.
- Output JSON.
- Token usage.
- Estimated cost.
- Latency.
- Quality score.
- Failure reason if failed.

Provider keys must only exist in backend environment variables or secret storage.

## 10. Posts, Review, Scheduling, And Publishing

Post lifecycle:

```text
draft -> generated -> needs_review -> approved -> scheduled -> publishing -> published
```

Alternative states:

```text
rejected
failed
cancelled
```

Required post capabilities:

- Create custom draft.
- Generate AI draft.
- Edit draft.
- Save versions.
- Approve draft.
- Reject draft with reason.
- Regenerate draft.
- Schedule approved post.
- Publish approved post now.
- Cancel scheduled post.
- Attach media metadata.
- Track LinkedIn target and final LinkedIn post URN.

Publishing must always be job-based.

Scheduling flow:

1. User schedules an approved post.
2. API validates workspace, role, quota, target, and LinkedIn connection.
3. API creates or updates `scheduled_posts`.
4. Worker scans due scheduled posts.
5. Worker creates a `publish_attempt` with an idempotency key.
6. Worker publishes through LinkedIn service.
7. Worker marks post as `published` or `failed`.
8. Worker records full provider response metadata.
9. Worker notifies the user when action is needed.

Reliability requirements:

- Idempotency key per publish attempt.
- Retry with exponential backoff for transient failures.
- No duplicate LinkedIn posting.
- Dead-letter handling for repeated failures.
- Timezone-aware scheduling.
- Publish lock to prevent two workers from publishing the same post.
- Status audit trail.

## 11. LinkedIn Integration

LinkedIn integration must be treated as a controlled, permission-sensitive integration.

Current official LinkedIn behavior to design around:

- LinkedIn uses OAuth 2.0 for member authorization.
- Organic text, image, video, document, and multi-image posts are supported by the Posts API, but permissions and access level matter.
- Programmatic refresh tokens are available to approved Marketing Developer Platform partners.
- Access tokens are commonly short-lived enough that the backend must handle expiry and reconnect flows.
- LinkedIn can revoke tokens or restrict access, so Qalam must have graceful fallback states.

Initial scopes to plan for:

- Member profile identity scope required by the selected LinkedIn product tier.
- `w_member_social` for posting to personal profiles where approved.
- `w_organization_social` for organization posting where approved.

Backend LinkedIn endpoints:

- `GET /api/v1/workspaces/{workspace_id}/linkedin/status`
- `POST /api/v1/workspaces/{workspace_id}/linkedin/connect`
- `GET /api/v1/linkedin/oauth/callback`
- `GET /api/v1/workspaces/{workspace_id}/linkedin/targets`
- `POST /api/v1/workspaces/{workspace_id}/linkedin/disconnect`
- `POST /api/v1/workspaces/{workspace_id}/posts/{post_id}/publish-now`

Required LinkedIn tables:

- `oauth_states`
- `linkedin_connections`
- `linkedin_targets`
- `publish_attempts`

Token security:

- Store access and refresh tokens encrypted at rest.
- Use envelope encryption or a managed secret/key service when available.
- Never return LinkedIn tokens to the frontend.
- Store token expiry timestamps.
- Store scopes granted.
- Store member URN and connected target URNs.
- Support explicit disconnect and token deletion.

Publishing fallback:

Qalam should still be useful if LinkedIn API access is delayed or limited. The backend should support manual export, copy workflows, and reminders while API approval is pending.

## 12. Billing, Plans, And Resource Allocation

Use Stripe for paid plans and keep local billing state in Postgres.

Billing modules:

- Plan catalog.
- Stripe customer mapping.
- Subscription state.
- Webhook processing.
- Usage ledger.
- Quota enforcement.
- Billing portal link.

Initial plan model:

Free:

- 1 workspace.
- 1 user.
- Limited monthly AI generations.
- Limited saved drafts.
- Manual copy/export.
- No or very limited auto-publishing.

Starter:

- More monthly AI generations.
- Calendar scheduling.
- Personal LinkedIn connection if API access is approved.
- Basic media storage.

Pro:

- Higher generation quota.
- Company page support if approved.
- More scheduled posts.
- More saved voice/profile data.
- More media storage.

Agency:

- Multiple client workspaces.
- Team members.
- Higher quotas.
- Approval workflows.
- Client-specific settings.

Usage metrics to track:

- `ai_generation`
- `ai_regeneration`
- `scheduled_post`
- `published_post`
- `connected_linkedin_account`
- `workspace_count`
- `member_count`
- `media_storage_mb`

Quota rule:

Every action that consumes a paid resource must write to a usage ledger. Counters can be derived or cached, but the ledger should be the source of truth.

## 13. API Contract Roadmap

Initial REST API:

```text
/api/v1/me
/api/v1/workspaces
/api/v1/workspaces/{workspace_id}/members
/api/v1/workspaces/{workspace_id}/onboarding
/api/v1/workspaces/{workspace_id}/preferences
/api/v1/workspaces/{workspace_id}/voice-profile
/api/v1/workspaces/{workspace_id}/posts
/api/v1/workspaces/{workspace_id}/posts/{post_id}
/api/v1/workspaces/{workspace_id}/posts/{post_id}/versions
/api/v1/workspaces/{workspace_id}/posts/{post_id}/approve
/api/v1/workspaces/{workspace_id}/posts/{post_id}/reject
/api/v1/workspaces/{workspace_id}/posts/{post_id}/schedule
/api/v1/workspaces/{workspace_id}/generation/generate-post
/api/v1/workspaces/{workspace_id}/generation/regenerate-post
/api/v1/workspaces/{workspace_id}/linkedin/status
/api/v1/workspaces/{workspace_id}/linkedin/connect
/api/v1/workspaces/{workspace_id}/linkedin/targets
/api/v1/workspaces/{workspace_id}/usage
/api/v1/workspaces/{workspace_id}/billing/checkout
/api/v1/workspaces/{workspace_id}/billing/portal
/api/v1/webhooks/stripe
```

API rules:

- Version under `/api/v1`.
- Return typed JSON responses.
- Use consistent error objects.
- Support pagination on lists from the first implementation.
- Use request IDs in logs and responses.
- Use idempotency keys for publish actions and billing webhooks.
- Do not expose internal provider response bodies directly to the frontend.

## 14. Security Requirements

Security requirements from day one:

- Verify auth tokens on every protected endpoint.
- Enforce workspace authorization on every workspace-scoped operation.
- Encrypt LinkedIn tokens at rest.
- Never expose AI provider keys, Stripe secrets, or LinkedIn secrets to the frontend.
- Use CORS allowlists per environment.
- Rate limit auth, generation, schedule, and publish endpoints.
- Validate uploaded files by type and size.
- Use signed upload/download URLs for media when needed.
- Add audit logs for LinkedIn connections, publishing, billing, role changes, and destructive actions.
- Use secure environment variable handling.
- Avoid storing unnecessary personal data.
- Support account deletion and workspace data export later.

## 15. Observability And Operations

Backend observability should include:

- Structured JSON logs.
- Request ID on every API request.
- Workspace ID and user ID in safe logs.
- Sentry error tracking.
- Worker job logs.
- Publish attempt logs.
- AI generation latency and cost metrics.
- LinkedIn failure categorization.
- Stripe webhook processing logs.
- Health endpoint.
- Readiness endpoint.

Required endpoints:

- `GET /health`
- `GET /ready`

Operational alerts:

- Failed publishing spike.
- Worker queue backlog.
- AI provider failures.
- Stripe webhook failures.
- LinkedIn token refresh failures.
- Database connection pool exhaustion.
- High AI cost per workspace.

## 16. Local Development

Backend local development should support:

- Docker Compose for Postgres and Redis, or Supabase local if chosen.
- `.env.example` for all required config groups.
- `.env` for local-only secrets and provider keys.
- Alembic migrations.
- Seed data for plans, niches, prompt templates, and demo workspace.
- Plan quota seed values that can be loaded from env defaults but enforced from the database.
- Pytest test suite.
- Mock LinkedIn provider for development.
- Mock AI provider for deterministic tests.

Recommended first commands once backend is scaffolded:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
pytest
uvicorn app.main:app --reload
```

## 17. Testing Strategy

Minimum backend tests:

- Unit tests for quota checks.
- Unit tests for workspace permission checks.
- Unit tests for post state transitions.
- Unit tests for AI prompt context builder.
- Unit tests for LinkedIn token encryption/decryption wrapper.
- API tests for auth failures.
- API tests for workspace isolation.
- API tests for post create/edit/schedule.
- API tests for generation endpoint with mocked provider.
- Worker tests for due scheduled post publishing.
- Worker tests for retry and idempotency.
- Stripe webhook tests with fixture payloads.

Do not call real LinkedIn, Stripe, or AI providers in normal test runs.

## 18. Roadmap

### Phase 0: Backend Foundation

- Create FastAPI project structure.
- Add typed Pydantic settings, `.env.example`, logging, error handling, CORS, and health endpoints.
- Add SQLAlchemy, Alembic, and database session layer.
- Add Redis and Celery foundation.
- Add pytest foundation.
- Add environment validation for local, test, and production modes.

### Phase 1: Auth, Users, And Workspaces

- Integrate Supabase Auth JWT verification.
- Add internal `users`, `workspaces`, and `workspace_members`.
- Add `/me` and workspace APIs.
- Add role checks.
- Add audit logs.

### Phase 2: Preferences, Voice, And Niches

- Add onboarding/preferences models.
- Add voice profile models.
- Add writing samples.
- Add seed data for 10+ niche profiles.
- Add preference APIs for the existing frontend settings/dashboard flows.

### Phase 3: Posts And Review Workflow

- Add posts, post versions, post media metadata, and schedule models.
- Add post CRUD APIs.
- Add approve, reject, edit, regenerate, schedule, and cancel flows.
- Add pagination and filtering.

### Phase 4: AI Engine

- Add provider abstraction.
- Add prompt templates and versioning.
- Add prompt context builder.
- Add generation endpoint.
- Add regeneration endpoint.
- Add quality checks.
- Add usage ledger for AI.
- Add deterministic mock provider for development.

### Phase 5: Scheduler And Workers

- Add Celery worker process.
- Add due scheduled post scanner.
- Add publishing job queue.
- Add retry, backoff, dead-letter behavior, and idempotency.
- Add notification records for failures.

### Phase 6: LinkedIn OAuth And Publishing

- Add OAuth state handling.
- Add connect and callback endpoints.
- Store encrypted tokens.
- Add connection status and disconnect.
- Add target discovery where API permissions allow.
- Add text-only publishing through LinkedIn Posts API.
- Add publish attempt records and failure mapping.

### Phase 7: Billing And Quotas

- Add plans and subscriptions.
- Add Stripe Checkout and Customer Portal.
- Add Stripe webhook handler.
- Add quota enforcement for generation, scheduling, publishing, storage, and workspace count.
- Add frontend-ready usage endpoints.

### Phase 8: Production Hardening

- Add deployment Dockerfile.
- Add production environment config.
- Add backup strategy.
- Add observability and alerts.
- Add stricter rate limiting.
- Add security review checklist.
- Add admin maintenance commands.

## 19. Backend Acceptance Criteria

The backend is ready for real frontend integration when:

- `GET /health` and `GET /ready` work.
- Authenticated frontend requests can be verified.
- Workspaces and roles are enforced.
- Preferences and voice profile can be saved and loaded.
- Posts can be created, edited, approved, rejected, and scheduled.
- AI generation works through a backend service, not browser-side provider calls.
- AI runs and usage are stored.
- Scheduled jobs can be processed by a worker.
- LinkedIn connection state is modeled even before final API approval.
- LinkedIn tokens are encrypted when implemented.
- Quotas are enforced through a usage ledger.
- API errors are consistent and frontend-friendly.
- Tests cover auth, tenancy, posts, AI mock generation, and scheduling.

## 20. External References Checked

- Supabase Row Level Security: https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase pricing and compute: https://supabase.com/pricing
- LinkedIn OAuth overview: https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication
- LinkedIn OAuth refresh tokens: https://learn.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens
- LinkedIn Posts API: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api

## 21. Immediate Next Step

The next practical step is to scaffold the backend foundation in `/home/krawin/code/qalam/backend`:

1. Create FastAPI app structure.
2. Add config and health endpoints.
3. Add SQLAlchemy and Alembic.
4. Add initial workspace/auth/user models.
5. Add local environment and test setup.

After this foundation exists, Qalam can move from frontend prototype to real SaaS backend integration without mixing business logic into the frontend.
