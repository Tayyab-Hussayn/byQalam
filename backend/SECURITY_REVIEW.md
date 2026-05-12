# Qalam Security Review

## Current Baseline

- Auth tokens are verified server-side with Supabase JWKS or the legacy JWT
  secret fallback.
- Workspace access is checked on workspace-scoped endpoints.
- LinkedIn tokens are encrypted before persistence.
- API errors no longer surface raw exception text by default.
- Rate limiting, request IDs, audit logs, and failure notifications are in
  place.

## Enforced Production Checks

- Production CORS origins must be explicit and must not include localhost.
- Production encryption keys must be valid Fernet keys.
- Production auth verification must have either JWKS or the legacy JWT secret
  configured.

## Remaining Manual Review

- Validate deployment secrets in the runtime environment.
- Review LinkedIn app permissions before enabling publishing in production.
- Confirm backup restore procedures on a staging copy before launch.
- Review any new API routes for workspace membership checks.
