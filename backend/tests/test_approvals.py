from datetime import datetime, timedelta, timezone

import pytest

from app.approvals import ApprovalTransitionError, ReviewResult, apply_review
from app.schemas import ToolCallSummary

REVIEWED_AT = datetime(2026, 11, 24, 10, 0, tzinfo=timezone(timedelta(hours=-5)))


def make_summary(decision="approval_required", approval_status="pending"):
    return ToolCallSummary(
        request_id="req_1",
        agent_id="assistant_2",
        tool="email.send",
        arguments={
            "recipient": "lead@example.com",
            "subject": "Report",
            "body": "Hi, see attached.",
            "meta": {"tags": ["q4"]},
        },
        decision=decision,
        reason="External recipient requires approval.",
        timestamp=datetime(2026, 11, 24, 14, 0, tzinfo=timezone.utc),
        approval_status=approval_status,
    )


@pytest.mark.parametrize(
    ("action", "expected_status"),
    [("approve", "approved"), ("deny", "denied")],
)
def test_pending_approval_transitions(action, expected_status):
    original = make_summary()

    result = apply_review(original, action, "reviewer_7", REVIEWED_AT)

    assert isinstance(result, ReviewResult)
    assert result.summary.approval_status == expected_status
    assert result.summary.model_dump(exclude={"approval_status"}) == original.model_dump(
        exclude={"approval_status"}
    )
    assert result.event == {
        "request_id": "req_1",
        "reviewer_id": "reviewer_7",
        "action": action,
        "reviewed_at": "2026-11-24T15:00:00Z",
    }


def test_result_unpacks_as_summary_and_event():
    summary, event = apply_review(make_summary(), "approve", "reviewer_7", REVIEWED_AT)

    assert summary.approval_status == "approved"
    assert event["action"] == "approve"


@pytest.mark.parametrize(
    ("decision", "approval_status"),
    [
        ("block", "not_required"),
        ("allow", "not_required"),
        ("approval_required", "approved"),
        ("approval_required", "denied"),
        ("approval_required", "not_required"),
    ],
)
@pytest.mark.parametrize("action", ["approve", "deny"])
def test_non_pending_input_is_rejected(decision, approval_status, action):
    summary = make_summary(decision=decision, approval_status=approval_status)

    with pytest.raises(ApprovalTransitionError):
        apply_review(summary, action, "reviewer_7", REVIEWED_AT)


@pytest.mark.parametrize("first", ["approve", "deny"])
@pytest.mark.parametrize("second", ["approve", "deny"])
def test_repeated_review_is_rejected(first, second):
    reviewed, _ = apply_review(make_summary(), first, "reviewer_7", REVIEWED_AT)

    with pytest.raises(ApprovalTransitionError, match="pending"):
        apply_review(reviewed, second, "reviewer_8", REVIEWED_AT)


@pytest.mark.parametrize(
    ("action", "reviewer_id", "reviewed_at", "match"),
    [
        (None, "reviewer_7", REVIEWED_AT, "action"),
        ("", "reviewer_7", REVIEWED_AT, "action"),
        ("APPROVE", "reviewer_7", REVIEWED_AT, "action"),
        ("approved", "reviewer_7", REVIEWED_AT, "action"),
        ("escalate", "reviewer_7", REVIEWED_AT, "action"),
        (["approve"], "reviewer_7", REVIEWED_AT, "action"),
        ("approve", None, REVIEWED_AT, "reviewer_id"),
        ("approve", "", REVIEWED_AT, "reviewer_id"),
        ("approve", "   ", REVIEWED_AT, "reviewer_id"),
        ("approve", 7, REVIEWED_AT, "reviewer_id"),
        ("approve", "reviewer_7", None, "reviewed_at"),
        ("approve", "reviewer_7", "2026-11-24T15:00:00Z", "reviewed_at"),
        ("approve", "reviewer_7", datetime(2026, 11, 24, 15, 0), "reviewed_at"),
    ],
)
def test_malformed_review_input_is_rejected(action, reviewer_id, reviewed_at, match):
    with pytest.raises(ApprovalTransitionError, match=match):
        apply_review(make_summary(), action, reviewer_id, reviewed_at)


@pytest.mark.parametrize("action", ["approve", "deny"])
def test_input_summary_is_not_mutated(action):
    original = make_summary()
    snapshot = original.model_dump()

    result = apply_review(original, action, "reviewer_7", REVIEWED_AT)

    assert original.model_dump() == snapshot
    assert result.summary is not original


def test_new_summary_does_not_share_nested_arguments():
    original = make_summary()

    result = apply_review(original, "approve", "reviewer_7", REVIEWED_AT)
    result.summary.arguments["meta"]["tags"].append("tampered")
    result.summary.arguments["recipient"] = "attacker@example.net"

    assert original.arguments["meta"]["tags"] == ["q4"]
    assert original.arguments["recipient"] == "lead@example.com"


def test_event_omits_message_content_and_evidence():
    _, event = apply_review(make_summary(), "deny", "reviewer_7", REVIEWED_AT)

    assert set(event) == {"request_id", "reviewer_id", "action", "reviewed_at"}
