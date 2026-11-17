
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
| `npm run typecheck` | Run TypeScript type checking |
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

## Continuous integration

The `Frontend checks` workflow runs on pull requests to `main` and pushes to
`main`. It uses Node.js 24, caches npm downloads using `package-lock.json`, and
runs these commands from `frontend/`:

```bash
npm ci
npm run typecheck
npm run build
```

Run the same commands before opening a PR. A failed install, type check, or build
fails the CI job. This validates the local dashboard; it does not deploy it.
