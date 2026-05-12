# Qalam Frontend Goal And Roadmap

Last updated: 2026-05-09

This document defines the frontend development goal for Qalam and the roadmap for converting the existing HTML frontend into a professional Next.js SaaS application.

Primary source design:

- `/home/krawin/code/qalam/Qalam Project.html`
- `/home/krawin/code/qalam/qalam_world_class_mvp.html`

Primary product architecture reference:

- `/home/krawin/code/qalam/QALAM_PRODUCT_ARCHITECTURE_PLAN.md`

## 1. Frontend Goal

The frontend goal is to build a production-grade Next.js application for Qalam that exactly recreates the existing HTML-based Qalam frontend and then grows it into the full SaaS interface described in the product architecture plan.

The first frontend milestone is not to redesign Qalam. The first milestone is to faithfully reproduce the existing design, layout, brand, typography, colors, content sections, animations, and responsive behavior from `Qalam Project.html` inside a clean Next.js TypeScript codebase.

After the public page is converted, the frontend will expand into the logged-in SaaS dashboard where users can:

- Generate LinkedIn posts using AI.
- Review generated content.
- Approve, reject, edit, or regenerate posts.
- Schedule approved posts.
- Create custom posts.
- Manage content preferences.
- Connect LinkedIn accounts and company pages.
- Track plan usage and subscription state.
- Manage profile, workspace, and billing settings.

The frontend must feel like a serious international SaaS product, but it should preserve Qalam's existing brand direction: refined, editorial, professional, founder-led, and clearly focused on LinkedIn content generation.

## 2. Source HTML Understanding

`Qalam Project.html` currently represents the public visitor experience for Qalam.

The existing page includes:

- Fixed navigation.
- Qalam wordmark.
- Hero section.
- Building-in-public badge.
- Strong headline and subheadline.
- Hero CTA buttons.
- Trust/status chips.
- Product mockup preview.
- Trust strip.
- Building-in-public section.
- Problem versus solution toggle.
- Product features section.
- Pricing section.
- Founder story.
- Final CTA.
- Footer.
- Inline CSS.
- Inline JavaScript for interactive behavior.

The current HTML is a strong marketing page. It should become the public route of the Next.js app.

Target route:

- `/`

The source page currently includes references such as waitlist, founder story, pricing, LinkedIn links, and building-in-public content. These should be preserved during the first conversion unless we intentionally update copy later.

## 2.1 Dashboard HTML Integration Rule

`qalam_world_class_mvp.html` is the source of truth for the authenticated Qalam dashboard experience.

This dashboard must be converted exactly as it exists in the HTML file before any product restructuring happens. The conversion must not invent new dashboard routes, rename features, remove panels, add new features, or split the dashboard into `/posts`, `/calendar`, `/settings`, `/linkedin`, or `/billing` unless the HTML itself is later changed to contain that structure.

The source dashboard is a single-page app shell with internal views controlled by navigation state:

- Landing view
- Dashboard view
- AI Writer view
- Voice Fingerprint view
- Analytics view
- Onboarding modal
- Notification toast
- Sidebar navigation
- Top bar
- Pro plan card
- Quick actions
- Recent posts
- Posting streak
- Voice health
- Prompt writer
- Generated post output
- Hashtag and first-comment sections
- Voice fingerprint configuration
- Analytics cards, chart, content mix, and heatmap

The Next.js implementation should preserve these views and interactions as a single dashboard experience. A single entry route may host this dashboard, but the internal dashboard structure must remain faithful to `qalam_world_class_mvp.html`.

Dashboard conversion acceptance criteria:

- Visual design matches `qalam_world_class_mvp.html`.
- Sidebar labels and ordering are preserved.
- Top bar titles/subtitles update according to the selected internal view.
- Initial active view remains AI Writer, matching the HTML source.
- Onboarding modal step flow is preserved.
- Notification toast behavior is preserved.
- Tone selection is preserved.
- Prompt shortcut buttons are preserved.
- Generate button behavior is preserved as a frontend demo interaction until the real backend AI API is integrated.
- Voice Fingerprint view preserves all cards, form controls, metrics, tags, and actions.
- Analytics view preserves the metrics, bar chart, donut chart, heatmap, and legend.
- No dashboard feature from the source HTML is removed during conversion.
- No extra dashboard feature is added during the initial conversion.

## 3. Frontend Stack

Recommended stack:

- Framework: Next.js App Router
- Language: TypeScript
- Styling: Tailwind CSS
- UI system: shadcn/ui and Radix UI where useful
- Icons: lucide-react
- Forms: React Hook Form
- Validation: Zod
- Data fetching: TanStack Query for backend API calls
- Auth client: Supabase Auth client
- State: local React state first, lightweight stores only where needed
- Date/time UI: date-fns or dayjs
- Calendar UI: custom calendar first, advanced calendar library later if needed

Frontend principles:

- Keep the first conversion visually faithful to the HTML.
- Split the page into reusable components.
- Avoid locking the app into one giant page file.
- Use typed mock data for dashboard screens before backend APIs exist.
- Build protected routes with real future auth boundaries in mind.
- Keep backend integration points explicit and replaceable.
- Use responsive layouts from the beginning.
- Keep visual polish high while maintaining clean code.

## 4. Required Next.js Structure

Recommended structure:

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
      linkedin/
      billing/
    layout.tsx
    globals.css
  components/
    marketing/
    dashboard/
    posts/
    calendar/
    settings/
    linkedin/
    billing/
    layout/
    ui/
  lib/
    api/
    auth/
    mock-data/
    types/
    validation/
    constants/
  hooks/
  public/
```

The exact structure can be adjusted once the Next.js project is initialized, but the principle should remain: public marketing components, logged-in app components, shared UI, typed data, and API helpers should be separated.

## 5. Public Marketing Page Goal

The public page must be an exact Next.js replica of `Qalam Project.html`.

Conversion requirements:

- Preserve Qalam's visual identity.
- Preserve the section order.
- Preserve typography, spacing, color system, buttons, cards, and mock product preview.
- Preserve responsive behavior.
- Preserve animations and interactive states.
- Replace inline JavaScript with React state and effects.
- Replace inline CSS with Tailwind and/or scoped component CSS where appropriate.
- Replace raw SVG/icon patterns with lucide-react where it does not change the visual identity.
- Use semantic sections and accessible landmarks.
- Use Next.js metadata for title and description.

Public page sections to implement:

1. Navigation
2. Hero
3. Product mockup preview
4. Trust strip
5. Building-in-public section
6. Problem/solution toggle
7. Product features
8. Pricing
9. Founder story
10. Final CTA
11. Footer

Acceptance criteria:

- The page should look visually equivalent to the HTML source on desktop.
- The page should remain polished on tablet and mobile.
- Navigation anchors should work.
- Interactive toggle should work.
- Hero typewriter/mock behavior should work if present in the source.
- No text should overflow cards or buttons.
- The page should pass basic accessibility checks for headings, links, contrast, and focus states.

## 6. SaaS Dashboard Goal

After the public page is converted, the logged-in application should be built as a practical SaaS dashboard.

Primary app route:

- `/dashboard`

Core dashboard goals:

- Give the user a clear view of their content pipeline.
- Make generated posts easy to review quickly.
- Make approval, rejection, editing, regeneration, and scheduling fast.
- Make LinkedIn connection state obvious.
- Make usage limits and plan state visible without being distracting.
- Make content preferences easy to configure and update.

Dashboard navigation:

- Dashboard
- Posts
- Calendar
- Generate
- Settings
- LinkedIn
- Billing

Suggested dashboard widgets:

- Posts generated this month
- Approved posts
- Scheduled posts
- Published posts
- Failed posts
- AI generation quota
- LinkedIn connection status
- Upcoming scheduled posts
- Recent generated drafts

## 7. Logged-In Screens

### Dashboard Overview

Purpose:

- Show the user's current content operation at a glance.

Includes:

- KPI cards.
- Content status summary.
- Upcoming scheduled posts.
- Recent drafts.
- Quick actions.
- LinkedIn connection warning if disconnected.

### Generated Posts

Purpose:

- Let the user review AI-generated content.

Features:

- Post list.
- Status filters.
- Search.
- Post preview.
- Approve button.
- Reject button.
- Edit button.
- Regenerate button.
- Schedule button.
- Copy button for manual LinkedIn posting.

### Post Editor

Purpose:

- Let users refine generated or custom content before scheduling.

Features:

- Text editor.
- Character/length guidance.
- Tone controls.
- CTA controls.
- Hashtag controls.
- Media upload placeholder.
- Save draft.
- Approve.
- Schedule.

### Calendar

Purpose:

- Give the user a clear publishing calendar.

Features:

- Month/week view.
- Scheduled post cards.
- Empty slot prompts.
- Schedule editing.
- Timezone indicator.
- Status colors.

### Generate

Purpose:

- Trigger AI content generation.

Features:

- Generate single post.
- Generate batch.
- Select niche/topic.
- Select style.
- Select goal.
- Use saved preferences.
- Show generation progress state.

### Settings And Preferences

Purpose:

- Store the user's content identity.

Settings:

- Niche.
- Target audience.
- Voice/tone.
- Writing samples.
- Topics to write about.
- Topics to avoid.
- Preferred language.
- Post length.
- CTA style.
- Hashtag preference.
- Posting frequency.
- Timezone.

### LinkedIn Connection

Purpose:

- Manage LinkedIn publishing connection.

States:

- Not connected.
- Connected to personal profile.
- Connected to company pages.
- Token expiring.
- Permission missing.
- Disconnected/error.

Important:

LinkedIn auto-publishing depends on LinkedIn API approval and OAuth scopes. The frontend should support direct publishing states, but it must also support manual copy/export while API approval is pending.

### Billing

Purpose:

- Show plan, usage, and upgrade path.

Includes:

- Current plan.
- Usage counters.
- Plan limits.
- Upgrade CTA.
- Billing portal link later.

## 8. Frontend Data Model

The frontend should use typed data models from the beginning, even before backend integration.

Important types:

- `User`
- `Workspace`
- `Plan`
- `UsageSummary`
- `ContentPreference`
- `Post`
- `PostStatus`
- `PostVersion`
- `ScheduledPost`
- `LinkedInConnection`
- `LinkedInTarget`
- `GenerationRun`

Post statuses:

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

## 9. API Contracts To Design During Frontend Work

The frontend should be built with mocked API contracts that match the planned FastAPI backend.

Initial endpoints:

- `GET /api/v1/me`
- `GET /api/v1/workspaces/current`
- `GET /api/v1/preferences`
- `PUT /api/v1/preferences`
- `GET /api/v1/posts`
- `GET /api/v1/posts/:id`
- `POST /api/v1/posts/generate`
- `POST /api/v1/posts/:id/approve`
- `POST /api/v1/posts/:id/reject`
- `POST /api/v1/posts/:id/regenerate`
- `POST /api/v1/posts/:id/schedule`
- `POST /api/v1/posts/:id/cancel-schedule`
- `GET /api/v1/linkedin/status`
- `POST /api/v1/linkedin/connect`
- `POST /api/v1/linkedin/disconnect`
- `GET /api/v1/billing/usage`

During frontend development, these can be represented as local mock functions in `lib/mock-data` or `lib/api`.

## 10. Frontend Roadmap

### Phase 1: Next.js Foundation

Goal:

Create the frontend application foundation.

Tasks:

- Initialize Next.js in `frontend/`.
- Add TypeScript.
- Add Tailwind CSS.
- Add base app layout.
- Add global font setup.
- Add design tokens for Qalam colors.
- Add linting and formatting.
- Add reusable button, badge, card, input, textarea, tabs, modal, and dropdown patterns.

Deliverable:

- A running Next.js frontend with Qalam's base design system prepared.

### Phase 2: Exact Public Page Conversion

Goal:

Convert `Qalam Project.html` into the Next.js public landing page.

Tasks:

- Extract the HTML into React components.
- Move styles into Tailwind/global CSS/component CSS.
- Convert interactive JavaScript into React state.
- Preserve the visual structure exactly.
- Add responsive behavior.
- Add metadata.
- Test desktop and mobile viewports.

Deliverable:

- `/` renders the Qalam public page as an exact replica of the source HTML.

### Phase 3: Exact Dashboard HTML Conversion

Goal:

Convert `qalam_world_class_mvp.html` into the Next.js app as one faithful dashboard experience.

Tasks:

- Preserve the single-page dashboard shell from the HTML.
- Rebuild HTML event handlers as React state and event callbacks.
- Preserve the internal views: Landing, Dashboard, AI Writer, Voice Fingerprint, and Analytics.
- Preserve onboarding modal behavior.
- Preserve notification toast behavior.
- Preserve generated post demo behavior without exposing provider API keys in the browser.
- Preserve charts, streak dots, heatmap, selected tags, tone pills, and quick action prompts.
- Scope dashboard styling so it does not damage the public landing page.
- Verify lint and production build.

Deliverable:

- The dashboard HTML is replicated in Next.js as a single cohesive dashboard page.

### Phase 4: App Shell Hardening

Goal:

Harden the converted dashboard shell for production without changing its source-defined features.

Tasks:

- Add route group for logged-in app screens.
- Build sidebar/topbar layout.
- Add user/workspace switcher placeholder.
- Add plan/usage display placeholder.
- Add responsive mobile navigation.
- Add loading, empty, and error states.

Deliverable:

- `/dashboard` renders a professional SaaS dashboard shell.

### Phase 5: Mock Dashboard Screens

Goal:

Use typed mock data behind the exact dashboard UI where the HTML currently uses hardcoded values.

Tasks:

- Build Dashboard Overview.
- Build Generated Posts queue.
- Build Post Editor.
- Build Calendar view.
- Build Generate screen.
- Build Settings/Preferences screen.
- Build LinkedIn connection screen.
- Build Billing/Usage screen.

Deliverable:

- Users can click through the complete SaaS frontend flow without a real backend.

### Phase 6: Auth UI

Goal:

Prepare user registration and login screens.

Tasks:

- Build signup page.
- Build login page.
- Build forgot password page.
- Build onboarding entry route.
- Add Supabase Auth client structure.
- Add protected route logic placeholder.

Deliverable:

- Auth UI is ready for Supabase integration.

### Phase 7: Onboarding

Goal:

Collect the information needed for high-quality AI generation.

Tasks:

- Build niche selection.
- Build target audience form.
- Build tone and voice form.
- Build writing sample input.
- Build topic preferences.
- Build posting frequency and timezone.
- Build completion summary.

Deliverable:

- New users can configure their content profile before entering the dashboard.

### Phase 8: Backend API Integration

Goal:

Replace mocked data with real FastAPI backend calls.

Tasks:

- Add API client.
- Add auth token forwarding.
- Integrate preferences endpoints.
- Integrate posts endpoints.
- Integrate generation endpoint.
- Integrate schedule endpoint.
- Integrate LinkedIn status endpoint.
- Integrate usage/billing endpoint.

Deliverable:

- The frontend works against the real backend.

### Phase 9: Production Polish

Goal:

Make the frontend production-ready.

Tasks:

- Accessibility pass.
- Loading skeletons.
- Error boundaries.
- Empty states.
- Mobile QA.
- SEO for public pages.
- Metadata for all public routes.
- Form validation messages.
- Toast notifications.
- Performance optimization.
- Image and font optimization.
- Basic analytics events.

Deliverable:

- Frontend is polished enough for real users and early paid customers.

## 11. Design System Direction

Qalam's frontend should preserve the current brand tokens from the HTML:

- Gold: `#C9871F`
- Light gold: `#E8A835`
- Pale gold: `#FDE5A0`
- Teal: `#0D4A45`
- Light teal: `#156860`
- Teal background: `#EAF4F3`
- Ink: `#0F172A`
- Secondary ink: `#334155`
- Muted ink: `#64748B`
- Border: `#E2E8F0`
- Off white: `#F8F9FB`

Typography:

- Primary: Plus Jakarta Sans
- Editorial accent: Cormorant Garamond

Visual direction:

- Professional SaaS.
- Calm, premium, editorial.
- Clear interface hierarchy.
- No unnecessary decoration inside the logged-in app.
- Dashboard should be practical and efficient, not a marketing page.

## 12. Quality Bar

Every frontend screen should satisfy:

- Responsive on desktop, tablet, and mobile.
- No text overflow.
- Clear focus states.
- Accessible labels for forms and controls.
- Real loading, empty, and error states.
- Predictable navigation.
- Consistent spacing and typography.
- No hardcoded backend assumptions.
- No fake connected LinkedIn state without clear labeling.

## 13. Immediate Next Action

The next engineering step is to initialize the Next.js frontend in `frontend/` and begin Phase 1.

Recommended first command sequence:

```bash
cd /home/krawin/code/qalam/frontend
npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir false --import-alias "@/*"
```

After the app is initialized, the first implementation task should be:

1. Add Qalam theme tokens and fonts.
2. Convert `Qalam Project.html` into the `/` route.
3. Verify the page visually against the HTML source.
