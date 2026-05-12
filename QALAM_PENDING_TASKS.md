# Qalam Pending Tasks

Last updated: 2026-05-10

This is the master list of remaining work for Qalam. It consolidates the
frontend and backend trackers so the current build state is easy to read in one
place.

Detailed trackers:

- [QALAM_FRONTEND_PENDING_TASKS.md](./QALAM_FRONTEND_PENDING_TASKS.md)
- [QALAM_BACKEND_PENDING_TASKS.md](./QALAM_BACKEND_PENDING_TASKS.md)

## Frontend Remaining Tasks

- LinkedIn + billing surface is implemented in the dashboard.
- More aggressive server-state management if needed
- Frontend error reporting is in place through the local reporter and API route.
- CI checks for lint, build, and type safety are in place.
- Minor cleanup of any remaining non-critical mock dashboard sections

## Backend Remaining Tasks

- LinkedIn target discovery where API permissions allow

## Current Priority

The route-level hardening, error reporting, and CI work is done. The remaining
frontend work is optional cleanup and state-management refinement, followed by
the backend hardening and quota/workflow edge cases.
