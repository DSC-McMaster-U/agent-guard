# Start here

Use your assigned issue for scope and the [project board](https://github.com/orgs/DSC-McMaster-U/projects/22)
for status. The [Sprint 3 checkpoint](sprints/sprint-3-checkpoint.md) explains
which pieces currently work and which integrations are still missing.

## Before editing

If you already have a checkout, keep it; do not clone a second copy unnecessarily.
For a first checkout:

```bash
git clone https://github.com/DSC-McMaster-U/agent-guard.git
cd agent-guard
```

From a clean working tree, update main and create your issue branch:

```bash
git switch main
git pull --ff-only
git switch -c feature/ISSUE_NUMBER-short-description
```

Replace the example branch name with your issue's number and description. If
`git status` shows existing changes, commit or safely save them before switching;
do not discard them to follow these commands. See [CONTRIBUTING.md](../CONTRIBUTING.md)
for the complete PR workflow. Move your issue to In Progress when you start.

## Set up only what your task needs

| Work | Setup | Before requesting review |
| --- | --- | --- |
| Backend | [Python setup](../backend/README.md); use Python 3.14.x | From `backend/`: `python -m pytest` |
| Frontend | [React setup](../frontend/README.md); Node.js 24 matches CI | From `frontend/`: `npm ci`, `npm run lint`, `npm run typecheck`, `npm run build` |
| Security/evaluation | Backend Python environment, [evaluation commands](../evaluation/README.md) | From root: `python -m pytest evaluation/test_run_policy_cases.py -q` and `python evaluation/run_policy_cases.py`; backend tests for detector changes |
| Database/infrastructure | [Local PostgreSQL](../README.md#local-postgresql) | Follow your issue's Compose validation/startup checks; preserve the named volume |
| Documentation | Read the relevant source and follow the documented commands | Check links and `git diff --check`; include actual command results when documenting behavior |

Pure policy, detector, and backend unit tests currently need no running Docker,
DB, or web server. Frontend development needs Node but no backend until an API
integration task requires it. Use the committed npm lockfile; change dependencies
only when your issue calls for it.

## Common setup problems

- **`python` is not found:** on macOS/Linux, try `python3`; on Windows, use the
  installed Python launcher (`py -3.14`). Use that interpreter to create the
  environment. After activation, check `python --version`.
- **`ensurepip` or `venv` is unavailable:** install your platform's matching Python
  venv support (often `python3.14-venv` on Ubuntu/Debian), or ask for setup help.
  Do not install project packages into the system Python to get around it.
- **`No module named app` during backend tests:** activate the correct environment,
  install `requirements-dev.txt`, and run pytest from `backend/`.
- **Vite reports an unsupported Node version:** use Node 24 and rerun `npm ci`.
- **The dashboard still shows placeholders:** the local dashboard landed in PR #117.
  Check your branch/commit and pull the latest main before creating your next branch.
- **The decision route returns 404:** use `POST /api/v1/tool-calls` (implemented in
  PR #121), check your branch/commit, and restart the backend after updating.
- **The board returns 404:** check you are signed into your team GitHub account,
  then ask the Lead to coordinate project access with an organization owner.

When asking for help, share the command, working directory, version, and relevant
error text. Remove secrets from logs. Ask after about 20 minutes blocked.

## Leave a useful handoff

Post a short issue update before the Tuesday meeting or whenever a teammate is
waiting on you:

```text
PR: <link, or not opened yet>
Working: <what you verified and the command/result>
Remaining/blocker: <specific gap, or none>
Handoff: <file/export/example the teammate needs and agreed time>
```

Agree shared field names or function props early; a draft PR can expose an
interface before the complete implementation is ready. Coordinate shared files
such as App.tsx, requirements, package-lock, and workflows with their owners.
If a prerequisite is unfinished, work on independent tests/contracts or ask the
Lead to adjust scope. Carryover is part of the same three-hour week.

Open a focused PR, link the issue, and request @rinnegannn's review. Only use
`Closes #NUMBER` when the PR completes the issue's acceptance criteria; otherwise
use `Related to #NUMBER` and explain what remains.
