"""Deterministic demo policy for proposed agent tool calls."""

from types import MappingProxyType
from typing import Any, Literal, TypedDict

Decision = Literal["allow", "block", "approval_required"]


class PolicyResult(TypedDict):
    decision: Decision
    reason: str


SUPPORTED_TOOLS = frozenset({"email.send"})
AGENT_PERMISSIONS = MappingProxyType({
    "assistant_2": frozenset({"email.send"}),
    "support-assistant": frozenset({"email.send"}),
})
EMAIL_ARGUMENT_KEYS = frozenset({"recipient", "subject", "body"})
DENIED_DOMAINS = frozenset({"example.net"})
INTERNAL_DOMAINS = frozenset({"example.com"})


def evaluate_policy(agent_id: str, tool: str, arguments: Any) -> PolicyResult:
    """Evaluate a proposed tool call against the server-owned demo policy.

    Args:
        agent_id: Identifier of the calling agent.
        tool: Normalized tool name, such as ``email.send``.
        arguments: Tool arguments object.

    Returns:
        The decision and a short human-readable reason.
    """
    if tool not in SUPPORTED_TOOLS:
        return _block(f"'{tool}' is not a supported tool.")
    if tool not in AGENT_PERMISSIONS.get(agent_id, frozenset()):
        return _block(f"Agent '{agent_id}' is not permitted to use '{tool}'.")
    if not isinstance(arguments, dict):
        return _block("Tool arguments must be an object.")
    unexpected = sorted(set(arguments) - EMAIL_ARGUMENT_KEYS)
    if unexpected:
        return _block(f"Unexpected email argument(s): {', '.join(unexpected)}.")

    domain = _recipient_domain(arguments.get("recipient"))
    if domain is None:
        return _block("Recipient is missing or not a valid email address.")
    # Deny also covers subdomains so mail.example.net cannot fall through to approval.
    if any(domain == d or domain.endswith("." + d) for d in DENIED_DOMAINS):
        return _block(f"Recipient domain '{domain}' is explicitly denied.")
    if domain in INTERNAL_DOMAINS:
        return {"decision": "allow", "reason": "Recipient is inside the organization."}
    return {
        "decision": "approval_required",
        "reason": f"Recipient domain '{domain}' is external, so a person must approve.",
    }


def _block(reason: str) -> PolicyResult:
    return {"decision": "block", "reason": reason}


def _recipient_domain(recipient: Any) -> str | None:
    """Return the lowercased domain of an obviously well-formed address, else None."""
    if not isinstance(recipient, str) or any(c.isspace() for c in recipient):
        return None
    local, at, domain = recipient.partition("@")
    if not at or not local or "@" in domain:
        return None
    labels = domain.split(".")
    if len(labels) < 2 or not all(labels):
        return None
    return domain.lower()
