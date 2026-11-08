# Backend Setup

## Prerequisites

Python 3.14.2

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

Manual check: with the app running (see above), visit `http://127.0.0.1:8000/health` in a browser. Expected response:

```json
{"status": "ok"}
```