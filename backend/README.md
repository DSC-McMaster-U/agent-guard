# Backend Setup

## Prerequisites

Python 3.14.2

## Getting Started

Navigate to the `backend/` directory.

## Installation

```bash
pip install -r requirements.txt
```

## Running the App

```bash
python -m uvicorn app.main:app --reload
```

## Testing

Visit `http://127.0.0.1:8000/health` in a browser (with the app running) to confirm the `/health` endpoint. Expected response:

```json
{"status": "ok"}
```