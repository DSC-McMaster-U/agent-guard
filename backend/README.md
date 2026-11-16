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

## Policy decision endpoint

`POST /api/v1/tool-calls` evaluates a proposed tool call against the demo policy and returns a decision summary. This route **evaluates policy only**: it does not store the request and it does not send an email.

With the app running (see above), try:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tool-calls \
  -H "Content-Type: application/json" \
  -d '{"request_id": "req-1", "agent_id": "assistant_2", "user_id": "user-1", "session_id": "session-1", "original_goal": "Send the weekly report", "tool": "email.send", "arguments": {"recipient": "alex@example.com", "subject": "Weekly report", "body": "Report attached."}}'
```

The response is HTTP 200 with `decision` set to `allow`, `block`, or `approval_required`. Invalid request or email data returns HTTP 422.