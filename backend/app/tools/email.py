"""Simulated ``email.send`` adapter for the demo.

Internal only, not an authorization check: the caller must pass a final decision
the server produced (``combine_decision``), never a value taken from the request.
No HTTP route invokes this module yet.
"""

from typing import Any

from pydantic import ValidationError

from app.schemas import EmailSendArguments

TOOL_NAME = "email.send"

BLOCKED_REASON = "Action was blocked, so the email was not sent."
APPROVAL_REQUIRED_REASON = "Action is waiting for approval, so the email was not sent."
UNKNOWN_DECISION_REASON = "Decision is not recognized, so the email was not sent."
INVALID_ARGUMENTS_REASON = "Email arguments are not validated, so the email was not sent."

_NOT_ALLOWED_REASONS = {
    "block": BLOCKED_REASON,
    "approval_required": APPROVAL_REQUIRED_REASON,
}


def simulate_email_send(arguments: EmailSendArguments) -> dict[str, str]:
    """Return a simulated delivery record without any network or filesystem access.

    Args:
        arguments: Email arguments already validated by ``EmailSendArguments``.

    Returns:
        A new dictionary describing the simulated send.
    """
    return {
        "tool": TOOL_NAME,
        "delivery_status": "simulated",
        "recipient": arguments.recipient,
        "subject": arguments.subject,
        "body": arguments.body,
    }


def dispatch_simulated_email(arguments: Any, final_decision: Any) -> dict[str, str]:
    """Run the simulated send only when the server's final decision is ``allow``.

    Args:
        arguments: An ``EmailSendArguments`` instance.
        final_decision: The ``decision`` string from ``combine_decision``.

    Returns:
        The simulated delivery record, or a ``not_executed`` result with a reason.
    """
    # type() rather than isinstance: a str subclass could override __eq__ to match "allow".
    if type(final_decision) is not str:
        return _not_executed(UNKNOWN_DECISION_REASON)
    if final_decision != "allow":
        return _not_executed(_NOT_ALLOWED_REASONS.get(final_decision, UNKNOWN_DECISION_REASON))

    validated = _revalidate(arguments)
    if validated is None:
        return _not_executed(INVALID_ARGUMENTS_REASON)
    return simulate_email_send(validated)


def _revalidate(arguments: Any) -> EmailSendArguments | None:
    """Return validated arguments; ``model_construct`` instances skip validation, so re-check."""
    if not isinstance(arguments, EmailSendArguments):
        return None
    try:
        return EmailSendArguments.model_validate(arguments.model_dump())
    except ValidationError:
        return None


def _not_executed(reason: str) -> dict[str, str]:
    return {"tool": TOOL_NAME, "delivery_status": "not_executed", "reason": reason}
