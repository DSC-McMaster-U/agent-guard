# AgentGuard Frontend

React and TypeScript dashboard for AgentGuard, built with Vite.

## Setup

Requires Node.js 20.19+ or 22.12+.

```bash
cd frontend
npm install
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

- `src/App.tsx` holds the page shell: the AgentGuard heading and the Activity and Approvals sections.
- Future Activity and Approvals views should replace those placeholder sections as their own components.
