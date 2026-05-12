# Qalam Frontend

Next.js frontend for Qalam, a LinkedIn content automation SaaS.

## Routes

- `/` - public marketing page converted from `Qalam Project.html`
- `/login` - temporary demo login while production auth is being integrated
- `/dashboard` - authenticated dashboard converted from `qalam_world_class_mvp.html`

## Development

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

To access `/dashboard`, use the demo login at `/login`. The current guard uses a temporary `qalam_session` httpOnly cookie. This should be replaced by Supabase/FastAPI-backed session handling before production.

## Backend Integration

Set the FastAPI base URL:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

The frontend API wrapper lives in `src/lib/api/client.ts`, and service functions should be added under `src/services`.
