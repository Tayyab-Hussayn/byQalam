# Qalam Product And Architecture Plan

Last updated: 2026-05-08

Qalam is a full-stack SaaS product for LinkedIn content planning, AI-assisted generation, approval, scheduling, and publishing to LinkedIn personal profiles and company pages. The product must be designed as a serious production SaaS from day one: multi-tenant, secure, observable, rate-limited, and able to support 1000+ client workspaces without rewriting the core architecture.

## 1. Product Mental Model

Qalam is not just a "generate post" tool. It should behave like a professional content operations platform.

Core workflow:

1. A visitor lands on the public marketing site.
2. The visitor signs up and creates a workspace.
3. The user configures niche, voice, target audience, post goals, language, posting frequency, and LinkedIn account/page connections.
4. Qalam generates a content pipeline from the user's profile and preferences.
5. Generated posts enter a review queue.
6. The user can approve, reject, edit, regenerate, or schedule posts.
7. A scheduler publishes approved posts at the correct time.
8. Qalam tracks publishing status, failures, LinkedIn post IDs, and later analytics.

The main product promise should be:

> Consistent, high-quality LinkedIn content for professionals and teams, with human approval and reliable publishing controls.

## 2. Recommended Stack

### Frontend

Use Next.js with TypeScript.

Recommended choices:

- Framework: Next.js App Router
- Language: TypeScript
- Styling: Tailwind CSS
- UI primitives: shadcn/ui or Radix UI
- Forms: React Hook Form + Zod
- Data fetching: TanStack Query if the Python backend owns the API, or server actions only for frontend-owned flows
- Charts later: Recharts or Tremor
- Auth client: Supabase Auth client

Reasoning:

Next.js is strong for SaaS dashboards, public pages, SEO, auth flows, protected routes, and polished frontend delivery. TypeScript reduces mistakes as the app grows.

### Backend

Use FastAPI with Python.

Recommended choices:

- Framework: FastAPI
- API style: REST first, with OpenAPI contracts
- Validation: Pydantic v2
- ORM: SQLAlchemy 2.0
- Migrations: Alembic
- Background jobs: Celery or Dramatiq
- Broker/cache: Redis
- Scheduler: Celery Beat, APScheduler, or a dedicated scheduler service
- Object storage: Supabase Storage initially, S3-compatible storage later
- Observability: Sentry, OpenTelemetry-compatible logs, structured JSON logging

Reasoning:

FastAPI is a good fit because Qalam needs a clean API backend, Python AI orchestration, async integration calls, typed request/response models, and background publishing workers. Django is also reliable, but FastAPI is a better match for a modern API-first SaaS with AI services and a separate Next.js frontend.

### Database And Platform

Use PostgreSQL. Start with Supabase if budget is limited.

Recommended path:

- Development and early production: Supabase Postgres + Supabase Auth + Supabase Storage
- Scale path: keep schema portable so the database can move to managed Postgres on AWS RDS, Neon, Crunchy, or another provider if needed

Reasoning:

PostgreSQL is the correct system of record for users, workspaces, posts, schedules, billing state, audit logs, OAuth tokens, and publishing jobs. Supabase gives a free start with Postgres, Auth, Storage, and social OAuth support. As of the current Supabase pricing page, the free plan includes 50,000 monthly active users, 500 MB database, 1 GB storage, and 2 active projects, but free projects can pause after inactivity. This is good for MVP and early users, not enough for serious production scale.

### Payments

Use Stripe.

Recommended:

- Stripe Checkout for first paid tier
- Stripe Customer Portal for subscription management
- Webhooks handled by FastAPI
- Store local subscription state in PostgreSQL

### AI Provider

Use an abstraction layer instead of hard-coding one model provider.

Recommended first implementation:

- Primary provider: OpenAI API or another high-quality LLM provider
- Internal interface: `ContentGenerationProvider`
- Store prompts, inputs, model name, token usage, generation cost, and output metadata
- Add evaluation and safety checks before publishing

Reasoning:

The "AI engine" is a product subsystem, not a single prompt. Qalam needs repeatable generation, user-specific voice memory, niche-aware templates, quality scoring, and regeneration feedback.

## 3. Important LinkedIn API Reality

LinkedIn publishing is the highest-risk integration and must be treated carefully.

Current official LinkedIn documentation says:

- LinkedIn uses OAuth 2.0 for user authorization.
- Posting as a member requires `w_member_social`.
- Posting as an organization requires `w_organization_social`.
- Reading member social data with `r_member_social` is restricted and available to approved users only.
- Organization posting is limited to organizations where the authenticated member has the required company page role.
- The newer Posts API is replacing older UGC Posts and Shares APIs.
- LinkedIn REST APIs require headers such as `Linkedin-Version: YYYYMM` and `X-Restli-Protocol-Version: 2.0.0`.
- Programmatic refresh tokens are available to approved Marketing Developer Platform partners; access tokens are commonly valid for 60 days and refresh tokens for up to 365 days.

Product implication:

Qalam must support a phased LinkedIn strategy.

Phase 1:

- Build content generation, approval, calendar, and manual copy/export.
- Let users copy posts or receive reminders if API approval is not ready.

Phase 2:

- Add LinkedIn OAuth.
- Store encrypted tokens.
- Publish to approved targets where permissions allow.

Phase 3:

- Add media uploads, company pages, analytics, retry recovery, and account health warnings.

Do not build the whole business assuming instant unrestricted LinkedIn API access. The architecture should support auto-publishing, but the product should still be useful while API approval is pending.

## 4. Main Application Modules

### Public Site

Purpose:

- Convert visitors into signups.
- Explain Qalam clearly.
- Show pricing, use cases, and trust signals.

Pages:

- Landing page
- Pricing
- Use cases by niche
- Login
- Signup
- Privacy policy
- Terms

### Auth And Account

Features:

- Email/password signup
- Magic link optional
- Google OAuth optional
- Password reset
- Email verification
- Workspace creation after signup
- User profile
- Role-based access later

Recommended initially:

- Supabase Auth for free/low-cost auth
- Backend verifies Supabase JWTs
- Keep an internal `users` table mirrored from auth user IDs

### Workspace And Tenancy

Qalam should be multi-tenant from the start.

Entities:

- User
- Workspace
- Workspace member
- Role
- Subscription
- Usage quota

Even if most users are solo initially, workspaces prevent painful rewrites when agencies and teams arrive.

### Onboarding

Onboarding should gather the data needed for high-quality AI output.

Data to collect:

- Profession/niche
- Target audience
- Content goals
- Products/services
- Writing tone
- Preferred language
- Content examples
- Topics to avoid
- Posting frequency
- CTA preferences
- LinkedIn profile URL
- Company page target if applicable

### Content Preferences

Users need durable preference settings.

Examples:

- Niche: HR, web developer, SaaS founder, consultant, creator, recruiter, coach, agency owner, e-commerce operator, real estate professional, finance advisor, healthcare professional
- Tone: professional, direct, educational, storytelling, contrarian, friendly, founder-led
- Post style: short insight, list, story, tactical guide, opinion, case study, hook-heavy
- CTA style: soft CTA, direct CTA, no CTA
- Hashtag rules
- Emoji policy
- Language
- Banned words/topics
- Preferred post length

### AI Content Engine

The AI engine should be built as a pipeline.

Pipeline:

1. Load user profile and preferences.
2. Choose content strategy for the niche.
3. Generate topic ideas.
4. Generate post draft.
5. Run quality checks.
6. Run policy and safety checks.
7. Score the draft.
8. Save the draft and metadata.
9. Allow user feedback.
10. Use feedback for future regeneration.

Core capabilities:

- Niche-specific generation
- Voice profile
- Content calendar generation
- Batch generation
- Regeneration with reason
- Hook variants
- CTA variants
- Hashtag suggestions
- "Make more professional"
- "Make shorter"
- "Make more personal"
- "Add storytelling"
- "Remove hype"

Quality checks:

- No fake claims
- No unsupported statistics unless user provided them
- No spammy engagement bait
- No repetitive structure across posts
- No accidental promises of guaranteed business results
- Length within LinkedIn limits
- Tone matches profile

Storage:

- Save generation prompt version
- Save source inputs
- Save output
- Save model/provider used
- Save token/cost estimate
- Save user rating or edit distance later

### Content Review Dashboard

Primary dashboard sections:

- Generated queue
- Approved posts
- Scheduled calendar
- Published posts
- Failed posts
- Draft custom post
- Content preferences
- LinkedIn connections
- Usage and billing

Post states:

- `draft`
- `generated`
- `needs_review`
- `approved`
- `scheduled`
- `publishing`
- `published`
- `rejected`
- `failed`
- `cancelled`

User actions:

- Approve
- Reject
- Edit
- Regenerate
- Schedule
- Publish now
- Duplicate
- Add media
- Convert to custom post

### Scheduler And Publisher

Publishing should be job-based, not request-based.

Flow:

1. User schedules approved post.
2. Backend creates a scheduled publish job.
3. Worker picks due jobs.
4. Worker checks subscription/quota/account status.
5. Worker refreshes LinkedIn token if allowed.
6. Worker uploads media if present.
7. Worker creates LinkedIn post.
8. Worker records LinkedIn post URN and response.
9. Worker updates status to published or failed.
10. Worker notifies user if failure requires action.

Reliability requirements:

- Idempotency key per publish attempt
- Retry with backoff for transient failures
- No duplicate posting
- Dead-letter queue for repeated failures
- Audit log for every publish attempt
- Timezone-aware scheduling
- Account disconnect detection

### Media Uploads

Phase 1:

- Text-only publishing
- User-uploaded image/video stored for future support

Phase 2:

- Image publishing
- Video publishing
- File validation
- File size limits by plan
- Virus/malware scanning later

Storage:

- Supabase Storage initially
- S3-compatible storage later

### Billing And Plans

Suggested MVP plans:

Free:

- 1 workspace
- 1 user
- Limited AI generations per month
- Manual copy/export
- No auto-publishing or very limited auto-publishing if API approval allows

Starter:

- More generations
- Calendar scheduling
- LinkedIn personal profile connection
- Basic support

Pro:

- Higher generation quota
- Company page support
- Media uploads
- More scheduled posts
- Advanced preferences

Agency/Team:

- Multiple workspaces/clients
- Team members
- Approval workflows
- Client-specific settings
- Higher rate limits

Quota examples:

- AI generations per month
- Scheduled posts per month
- Connected LinkedIn accounts
- Workspaces/client profiles
- Media storage
- Team seats

## 5. Suggested Database Model

Initial tables:

- `users`
- `workspaces`
- `workspace_members`
- `subscriptions`
- `plans`
- `usage_counters`
- `content_preferences`
- `niches`
- `linkedin_connections`
- `linkedin_pages`
- `posts`
- `post_versions`
- `post_media`
- `scheduled_posts`
- `publish_attempts`
- `ai_generation_runs`
- `prompt_templates`
- `audit_logs`
- `notifications`

Critical fields:

`linkedin_connections`:

- `id`
- `workspace_id`
- `user_id`
- `linkedin_member_urn`
- `encrypted_access_token`
- `encrypted_refresh_token`
- `access_token_expires_at`
- `refresh_token_expires_at`
- `scopes`
- `status`
- `created_at`
- `updated_at`

`posts`:

- `id`
- `workspace_id`
- `author_user_id`
- `status`
- `source`
- `niche`
- `title_internal`
- `body`
- `scheduled_for`
- `timezone`
- `linkedin_target_type`
- `linkedin_target_urn`
- `linkedin_post_urn`
- `created_at`
- `updated_at`

`ai_generation_runs`:

- `id`
- `workspace_id`
- `post_id`
- `provider`
- `model`
- `prompt_template_version`
- `input_json`
- `output_json`
- `quality_score`
- `tokens_input`
- `tokens_output`
- `estimated_cost`
- `created_at`

## 6. Backend Architecture

Recommended backend structure:

```text
backend/
  app/
    api/
      v1/
        auth.py
        workspaces.py
        preferences.py
        posts.py
        schedules.py
        linkedin.py
        billing.py
    core/
      config.py
      security.py
      logging.py
      rate_limits.py
    db/
      session.py
      models/
      migrations/
    services/
      ai/
      linkedin/
      billing/
      scheduling/
      storage/
      notifications/
    workers/
      celery_app.py
      publish_jobs.py
      generation_jobs.py
    tests/
```

API principles:

- Version APIs under `/api/v1`
- Use typed request/response schemas
- Keep business logic in services, not route handlers
- Keep publishing in workers, not HTTP requests
- Use idempotency keys for publishing and billing webhooks
- Use structured error responses

## 7. Frontend Architecture

Recommended frontend structure:

```text
frontend/
  app/
    (public)/
      page.tsx
      pricing/
      login/
      signup/
    (app)/
      dashboard/
      posts/
      calendar/
      settings/
      billing/
      linkedin/
  components/
    ui/
    dashboard/
    posts/
    calendar/
    settings/
  lib/
    api/
    auth/
    validation/
    constants/
  styles/
```

Main product screens:

- Public landing page
- Auth pages
- Onboarding wizard
- Dashboard overview
- Generated content review
- Post editor
- Calendar scheduler
- Custom post composer
- Content preferences
- LinkedIn connection settings
- Billing and usage

UX direction:

- Professional SaaS dashboard, not a marketing-heavy layout inside the app
- Dense but clear information layout
- Fast approval/regeneration workflow
- Clear post state labels
- Calendar and queue views
- No confusing automation without human confirmation
- Clear warnings before connecting LinkedIn and auto-publishing

## 8. Should We Start With Frontend?

Yes, but not only with visual pages.

Best first sequence:

1. Convert the two existing HTML frontends into a Next.js TypeScript app.
2. Define the core routes and dashboard layout.
3. Build mocked data screens for:
   - generated posts
   - approve/reject/regenerate
   - schedule post
   - custom post
   - settings/preferences
   - LinkedIn connection state
4. Define API contracts while building the UI.
5. Implement backend models and endpoints against those contracts.
6. Replace mocked frontend data with real API calls.

This gives a working product shell quickly while still shaping the backend correctly.

## 9. Production Requirements

Security:

- Encrypt LinkedIn OAuth tokens at rest
- Never expose provider tokens to frontend
- Verify JWTs on backend
- Workspace-level authorization on every query
- Rate limit auth, AI generation, and publishing endpoints
- Keep audit logs for publishing and billing
- Use environment-specific secrets
- Add CSRF protection where needed

Reliability:

- Background workers for generation and publishing
- Retries with backoff
- Dead-letter handling
- Idempotent publishing
- Health checks
- Database migrations
- Automated tests
- Error monitoring

Scalability:

- Postgres indexes on workspace, status, scheduled time, and created time
- Redis-backed queues
- Separate API and worker services
- Connection pooling
- Pagination everywhere
- Avoid long-running API requests
- Track AI cost per workspace

Compliance:

- Privacy policy and terms
- Clear LinkedIn connection consent
- User can disconnect LinkedIn
- User can delete data
- Respect LinkedIn API terms and rate limits
- Avoid spam automation patterns

## 10. MVP Scope

MVP should include:

- Public landing page from provided HTML
- Signup/login
- Workspace creation
- Onboarding preferences
- Dashboard shell
- Generate text posts
- Review queue
- Edit, approve, reject, regenerate
- Schedule posts internally
- Manual copy/export
- Usage counters
- Basic billing plan model
- LinkedIn connection placeholder or OAuth if approval is ready

MVP should not initially include:

- Full analytics
- Multi-seat agency workflow
- Complex media publishing
- AI training/fine-tuning
- Browser extension
- Mobile app
- Deep CRM integrations

## 11. Phase Roadmap

### Phase 0: Project Foundation

- Set up Next.js frontend
- Set up FastAPI backend
- Set up PostgreSQL/Supabase
- Add environment config
- Add linting, formatting, and test foundation
- Add Docker Compose for local Postgres/Redis if not using Supabase locally

### Phase 1: Frontend Product Shell

- Import/convert public HTML page
- Import/convert dashboard HTML page
- Create app layout, navigation, and protected routes
- Build dashboard screens with mock data
- Build settings/preferences forms
- Build post editor and scheduler UI

### Phase 2: Core Backend

- Auth verification
- Workspace model
- Content preferences model
- Posts model
- Schedule model
- API endpoints
- Basic usage limits

### Phase 3: AI Engine

- Prompt templates
- Niche configuration
- Generation service
- Regeneration service
- Quality scoring
- AI run storage
- Quota enforcement

### Phase 4: Scheduling

- Redis worker setup
- Scheduled post queue
- Retry logic
- Failure notifications
- Publish attempt logs

### Phase 5: LinkedIn Integration

- LinkedIn OAuth
- Token encryption
- Profile/page target discovery where allowed
- Text post publishing
- Company page publishing
- Connection health checks

### Phase 6: Billing And Production Hardening

- Stripe checkout
- Stripe webhooks
- Plan enforcement
- Observability
- Error tracking
- Deployment pipeline
- Backups
- Security review

## 12. Key Decisions To Make Soon

1. Confirm whether Supabase will be used for Auth, Postgres, and Storage.
2. Decide whether the backend will be deployed separately from the frontend from day one.
3. Choose the initial AI provider.
4. Confirm whether the first release can ship with manual export while LinkedIn API approval is pending.
5. Provide the two HTML frontend files so they can be converted into the Next.js app.

## 13. External References Checked

- LinkedIn Posts API documentation: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api
- LinkedIn API access and permissions: https://learn.microsoft.com/linkedin/shared/authentication/getting-access
- LinkedIn OAuth refresh tokens: https://learn.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens
- Supabase pricing and free plan limits: https://supabase.com/pricing
- Supabase billing overview: https://supabase.com/docs/guides/platform/billing-on-supabase

