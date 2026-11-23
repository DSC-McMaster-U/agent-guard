"""Save and list tool-call decision summaries in PostgreSQL.

These functions do not commit or roll back. The caller owns the transaction
(use ``with connection:`` around a save).
"""

from psycopg import Connection, errors
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.schemas import ToolCallSummary


class DuplicateRequestError(Exception):
    """Raised when a summary with the same ``request_id`` is already stored."""


def save_summary(connection: Connection, summary: ToolCallSummary) -> None:
    """Store one decision summary.

    Args:
        connection: Open psycopg connection.
        summary: The summary to store.

    Raises:
        DuplicateRequestError: If ``summary.request_id`` is already stored.
            The existing record is never overwritten.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tool_calls (
                    request_id, agent_id, tool, arguments,
                    decision, reason, timestamp, approval_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    summary.request_id,
                    summary.agent_id,
                    summary.tool,
                    Jsonb(summary.arguments),
                    summary.decision,
                    summary.reason,
                    summary.timestamp,
                    summary.approval_status,
                ),
            )
    except errors.UniqueViolation as error:
        raise DuplicateRequestError(summary.request_id) from error


def list_summaries(connection: Connection, limit: int = 20) -> list[ToolCallSummary]:
    """Return stored summaries, newest first.

    Args:
        connection: Open psycopg connection.
        limit: Maximum number of summaries to return.

    Returns:
        Summaries sorted by ``timestamp`` descending, then ``request_id`` ascending.
    """
    with connection.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT
                request_id, agent_id, tool, arguments,
                decision, reason, timestamp, approval_status
            FROM tool_calls
            ORDER BY timestamp DESC, request_id ASC
            LIMIT %s
            """,
            (limit,),
        )
        return [ToolCallSummary.model_validate(row) for row in cursor.fetchall()]
