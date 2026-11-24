-- Migration 001: store tool-call decision summaries for the audit trail.
-- Does not drop or rewrite existing data.

BEGIN;

CREATE TABLE IF NOT EXISTS tool_calls (
    request_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    tool TEXT NOT NULL,
    arguments JSONB NOT NULL,
    decision TEXT NOT NULL
        CHECK (decision IN ('allow', 'block', 'approval_required')),
    reason TEXT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    approval_status TEXT NOT NULL
        CHECK (approval_status IN ('not_required', 'pending', 'approved', 'denied'))
);

CREATE INDEX IF NOT EXISTS tool_calls_timestamp_idx ON tool_calls (timestamp);

COMMIT;
