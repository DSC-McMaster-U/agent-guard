"""Pure pending-to-approved/denied transition for approval-required tool calls.

Not the complete approval service: no send, DB write, HTTP, or concurrency
protection. January integration order: authenticated reviewer -> atomic pending
check + stored event -> authorized execution handoff.
"""

from datetime import datetime, timezone
from typing import Literal, NamedTuple

from app.schemas import ToolCallSummary

ReviewAction = Literal["approve", "deny"]

_STATUS_BY_ACTION = {"approve": "approved", "deny": "denied"}


class ApprovalTransitionError(ValueError):
    """Raised when a review cannot be applied to the supplied summary."""


class ReviewResult(NamedTuple):
    """New reviewed summary plus its review event."""

    summary: ToolCallSummary
    event: dict[str, str]


def apply_review(
    summary: ToolCallSummary,
    action: ReviewAction,
    reviewer_id: str,
    reviewed_at: datetime,
) -> ReviewResult:
    """Apply an approve or deny review to a pending approval-required summary.

    Args:
        summary: Current summary; not modified.
        action: ``approve`` or ``deny``.
        reviewer_id: Reviewer ID from a trusted server caller.
        reviewed_at: Timezone-aware review time.

    Returns:
        New summary with ``approved``/``denied`` status, and the review event.

    Raises:
        ApprovalTransitionError: Malformed input, or summary is not a pending
            ``approval_required`` call.
    """
    if not isinstance(action, str) or action not in _STATUS_BY_ACTION:
        raise ApprovalTransitionError(
            f"action must be one of {sorted(_STATUS_BY_ACTION)}, got {action!r}"
        )
    if not isinstance(reviewer_id, str) or not reviewer_id.strip():
        raise ApprovalTransitionError("reviewer_id must be a nonempty string")
    if not isinstance(reviewed_at, datetime) or reviewed_at.utcoffset() is None:
        raise ApprovalTransitionError("reviewed_at must be a timezone-aware datetime")
    if summary.decision != "approval_required":
        raise ApprovalTransitionError(
            f"only approval_required calls can be reviewed, got decision {summary.decision!r}"
        )
    if summary.approval_status != "pending":
        raise ApprovalTransitionError(
            f"only pending approvals can be reviewed, got status {summary.approval_status!r}"
        )

    reviewed = summary.model_copy(
        update={"approval_status": _STATUS_BY_ACTION[action]}, deep=True
    )
    event = {
        "request_id": summary.request_id,
        "reviewer_id": reviewer_id,
        "action": action,
        "reviewed_at": reviewed_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return ReviewResult(summary=reviewed, event=event)
