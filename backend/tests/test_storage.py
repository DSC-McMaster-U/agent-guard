import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg
import pytest

from app.schemas import ToolCallSummary
from app.storage import DuplicateRequestError, list_summaries, save_summary

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
MIGRATION = Path(__file__).resolve().parents[1] / "migrations" / "001_tool_calls.sql"

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL, reason="TEST_DATABASE_URL is not set"
)


@pytest.fixture
def connection():
    with psycopg.connect(TEST_DATABASE_URL, autocommit=True) as setup:
        if not setup.info.dbname.endswith("_test"):
            pytest.fail("TEST_DATABASE_URL must name a database ending in _test.")
        setup.execute(MIGRATION.read_text())
        setup.execute("TRUNCATE tool_calls")
    with psycopg.connect(TEST_DATABASE_URL) as connection:
        yield connection


def make_summary(request_id, timestamp):
    return ToolCallSummary(
        request_id=request_id,
        agent_id="assistant_2",
        tool="email.send",
        arguments={
            "recipient": "teammate@example.com",
            "subject": "Hi",
            "body": "Hello",
        },
        decision="allow",
        reason="Recipient is inside the organization.",
        timestamp=timestamp,
        approval_status="not_required",
    )


def test_saved_summary_round_trips(connection):
    summary = make_summary("req_1", datetime(2026, 11, 3, 18, 0, tzinfo=timezone.utc))
    save_summary(connection, summary)
    assert list_summaries(connection) == [summary]


def test_summaries_are_listed_newest_first_then_by_request_id(connection):
    older = datetime(2026, 11, 3, 18, 0, tzinfo=timezone.utc)
    newer = older + timedelta(minutes=5)
    for request_id, timestamp in [("req_b", newer), ("req_old", older), ("req_a", newer)]:
        save_summary(connection, make_summary(request_id, timestamp))

    ids = [summary.request_id for summary in list_summaries(connection)]
    assert ids == ["req_a", "req_b", "req_old"]


def test_limit_caps_the_number_of_summaries(connection):
    start = datetime(2026, 11, 3, 18, 0, tzinfo=timezone.utc)
    for minute in range(3):
        save_summary(connection, make_summary(f"req_{minute}", start + timedelta(minutes=minute)))

    assert len(list_summaries(connection, limit=2)) == 2


def test_duplicate_request_id_is_rejected_without_overwriting(connection):
    timestamp = datetime(2026, 11, 3, 18, 0, tzinfo=timezone.utc)
    original = make_summary("req_1", timestamp)
    save_summary(connection, original)
    connection.commit()

    replacement = original.model_copy(update={"decision": "block", "reason": "Changed."})
    with pytest.raises(DuplicateRequestError):
        save_summary(connection, replacement)
    connection.rollback()

    assert list_summaries(connection) == [original]
