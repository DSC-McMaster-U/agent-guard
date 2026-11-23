# Backend Setup

## Prerequisites

Python 3.14.x (matching CI)

## Getting Started

Navigate to the `backend/` directory.

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install dependencies (runtime and test tools):

```bash
python -m pip install -r requirements-dev.txt
```

## Running the App

```bash
python -m uvicorn app.main:app --reload
```

## Testing

Run the automated tests from `backend/` (no running server, Docker, or database needed):

```bash
python -m pytest
```

CI runs on pull requests to `main` and pushes to `main` (see `.github/workflows/backend-checks.yml`). It runs `python -m compileall -q app` and `python -m pytest` from `backend/`, then `docker compose --env-file .env.example config --quiet` from the repository root.

Manual check: with the app running (see above), visit `http://127.0.0.1:8000/health` in a browser. Expected response:

```json
{"status": "ok"}
```

## Simulated Email Tool

`app/tools/email.py` is an internal simulated adapter for `email.send`. It never sends email, opens a network connection, or writes files.

```python
from app.decision import combine_decision
from app.schemas import EmailSendArguments
from app.tools.email import dispatch_simulated_email

arguments = EmailSendArguments(recipient="alex@example.com", subject="Hi", body="Hello")
final = combine_decision(policy_result, findings)
result = dispatch_simulated_email(arguments, final["decision"])
# allow -> {"tool": "email.send", "delivery_status": "simulated", "recipient": ..., "subject": ..., "body": ...}
# block, approval_required, or anything else -> {"tool": "email.send", "delivery_status": "not_executed", "reason": ...}
```

## Tool call history

`POST /api/v1/tool-calls` evaluates the policy and saves the summary before it returns. It returns `409` for a duplicate `request_id` and a generic `503` if the database is unavailable. Invalid email arguments still return `422` and nothing is saved. `GET /api/v1/tool-calls` returns the newest 20 summaries as a JSON array, or `[]` when nothing is stored. `GET /health` does not use the database.

Set `DATABASE_URL` to a PostgreSQL URL before you start the backend, and apply migration 001 first (see [Database migrations](migrations/README.md)).

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tool-calls \
  -H "Content-Type: application/json" \
  -d '{"request_id": "req_1", "agent_id": "assistant_2", "user_id": "demo-user", "session_id": "demo-session", "original_goal": "Send a fictional report", "tool": "email.send", "arguments": {"recipient": "teammate@example.com", "subject": "Hi", "body": "Hello"}}'

curl http://127.0.0.1:8000/api/v1/tool-calls
```
