"""Combine a policy decision with security findings into one final decision.

Future gateway order: validate the request, evaluate policy, run detectors,
then combine. Findings can only make a decision stricter, never looser:

| Policy            | Findings                         | Result            |
|-------------------|----------------------------------|-------------------|
| block             | any                              | block             |
| approval_required | any                              | approval_required |
| allow             | any high                         | approval_required |
| allow             | any unrecognized severity        | approval_required |
| allow             | none, or only low/medium         | allow             |

An invalid policy result is blocked. Reasons never copy finding evidence.
"""

from collections.abc import Mapping
from typing import Any, get_args

from app.policy import Decision, PolicyResult

DECISIONS = frozenset(get_args(Decision))
HIGH_SEVERITY = "high"
LOWER_SEVERITIES = frozenset({"low", "medium"})

SECURITY_REVIEW_REASON = "Security review required."
UNKNOWN_SEVERITY_REASON = "Unrecognized finding severity; security review required."
INVALID_POLICY_REASON = "Policy result is invalid, so the action is blocked."


def combine_decision(policy_result: Any, findings: Any) -> PolicyResult:
    """Return the final decision for a policy result and its security findings.

    Args:
        policy_result: Result of ``evaluate_policy`` with ``decision`` and ``reason``.
        findings: Finding dictionaries from the detectors, or None for no findings.

    Returns:
        A new dictionary with the final ``decision`` and ``reason``.
    """
    if not _is_valid_policy(policy_result):
        return {"decision": "block", "reason": INVALID_POLICY_REASON}

    decision = policy_result["decision"]
    reason = policy_result["reason"]
    if decision != "allow":
        return {"decision": decision, "reason": reason}

    severities = _severities(findings)
    if HIGH_SEVERITY in severities:
        return {"decision": "approval_required", "reason": SECURITY_REVIEW_REASON}
    if severities - LOWER_SEVERITIES:
        return {"decision": "approval_required", "reason": UNKNOWN_SEVERITY_REASON}
    return {"decision": "allow", "reason": reason}


def _is_valid_policy(policy_result: Any) -> bool:
    return (
        isinstance(policy_result, Mapping)
        and policy_result.get("decision") in DECISIONS
        and isinstance(policy_result.get("reason"), str)
    )


def _severities(findings: Any) -> set[Any]:
    """Return the set of severities; malformed input yields an unrecognized marker."""
    if findings is None:
        return set()
    # A bare dict or string is iterable but is not a list of findings.
    if not isinstance(findings, (list, tuple)):
        return {None}
    return {
        finding.get("severity") if isinstance(finding, Mapping) else None
        for finding in findings
    }
