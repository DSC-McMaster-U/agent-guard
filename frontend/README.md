
# AgentGuard Frontend

React and TypeScript dashboard for AgentGuard, built with Vite.

## Setup

Use Node.js 24 to match CI. Vite also supports Node.js 20.19+ or 22.12+.

```bash
cd frontend
npm ci
npm start
```

Then open http://localhost:5173.

## Commands

| Command | What it does |
| --- | --- |
| `npm start` | Start the dev server (same as `npm run dev`) |
| `npm run lint` | Check JavaScript, TypeScript, and React Hooks rules |
| `npm run typecheck` | Run TypeScript type checking |
| `npm test` | Run the Vitest suite once (no watch mode) |
| `npm run build` | Type-check and build for production into `dist/` |
| `npm run preview` | Serve the production build locally |

## Structure

- `src/App.tsx` connects ActivityList and ApprovalDetails using copied local mock state.
- Selecting a request shows its details; Approve/Deny updates a pending request once. Refresh resets local state.
- The dashboard currently uses fictional fixtures, with no API connection or persisted approvals.

## Shared Dashboard Types and Mock Data

Shared types are located in `src/types/toolCall.ts`.

Exports:
- `ToolCallDecision`
- `ApprovalStatus`
- `ToolCallSummary`

Mock requests are exported as `mockToolCalls` from `src/mocks/toolCalls.ts`.

The three mock requests demonstrate:
- An allowed internal email
- A blocked email to example.net
- An external email requiring approval

These shared types and mocks are intended for the ActivityList and ApprovalDetails components.

All mock requests are simulated. No actual emails are sent.

## API client

`src/api/toolCalls.ts` wraps the backend's `/api/v1/tool-calls` routes so
components don't call `fetch` directly. The dashboard doesn't use it yet.

Exports:
- `evaluateToolCall(request, signal?)` sends `POST /api/v1/tool-calls` and returns a `ToolCallSummary`
- `getRecentToolCalls(signal?)` sends `GET /api/v1/tool-calls` and returns `ToolCallSummary[]`
- `ToolCallRequest` and `TriggerSource`, matching `backend/app/schemas.py`
- `ToolCallApiError`, with `kind` set to `network`, `validation` (422), `conflict` (409),
  `unavailable` (502/503/504), `http` (other non-2xx), or `malformed` (2xx with an invalid body)
- `isToolCallSummary`, the guard used to check every response

Responses are checked before they are returned. A failed request or invalid body is
thrown as an error and never treated as an allowed result. Aborting via `signal`
rethrows the browser's `AbortError` unchanged, so callers can ignore it.

`GET /api/v1/tool-calls` comes from backend issue #103. Until that is merged the
backend responds with 405, which the client reports as an `http` error.

## Running with the local backend

API URLs are relative (`/api/...`). In development, `vite.config.ts` proxies
`/api` to `http://127.0.0.1:8000`, so the browser never makes a cross-origin
request and the backend needs no CORS changes.

Run two terminals:

```bash
# Terminal 1: backend (see ../backend/README.md for setup)
cd backend
python -m uvicorn app.main:app --reload

# Terminal 2: frontend
cd frontend
npm start
```

Requests to http://localhost:5173/api/... now reach the backend. If the backend
isn't running, the proxy returns 502 and the client reports `unavailable`.

The proxy only applies to `npm start`/`npm run dev`. `npm run preview` and any
production hosting do not proxy `/api`. They need their own API routing, such as
a reverse proxy that serves the frontend and backend from the same origin.

## Continuous integration

The `Frontend checks` workflow runs on pull requests to `main` and pushes to
`main`. It uses Node.js 24, caches npm downloads using `package-lock.json`, and
runs these commands from `frontend/`:

```bash
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```

Run the same commands before opening a PR. A failed install, lint check, type check, test, or build
fails the CI job. This validates the local dashboard; it does not deploy it.

## Testing

Run `npm test` from `frontend/`. It runs Vitest once and exits, so it works the
same locally and in CI.

- Tests live next to the code they cover as `*.test.ts` or `*.test.tsx`
  (for example `src/components/ActivityList.test.tsx`).
- API client tests run in Vitest's default Node environment.
- Component tests start with a `// @vitest-environment jsdom` comment and use
  React Testing Library. Query by role or label, as a user would, and call
  `cleanup` after each test.
- Use small fictional fixtures inside the test file. Tests need no backend,
  database, or browser, and do not use snapshots.

## Linting

Run `npm run lint` from `frontend/`. The flat `eslint.config.js` uses recommended
JavaScript, TypeScript, and React Hooks rules. It checks source and configuration
files, ignores `dist/` and `node_modules/`, and uses browser globals for the app
and Node globals for tooling. Warnings also fail the check.

Read each reported file, line, and rule name, then fix the cause and rerun lint.
For an unused variable, remove it or use it; for a Hooks error, call the Hook at
the component's top level. Avoid disabling rules to get a passing check.
