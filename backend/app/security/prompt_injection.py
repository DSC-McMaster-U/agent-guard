"""Narrow, rule-based prompt-injection detector.

The detector flags text only when it contains BOTH a fake role marker
(text pretending to be a system or developer instruction) and an explicit
override phrase. It returns heuristic findings for later decision logic.
It never blocks an action, grants a permission, or overrides a policy block.

Known limitations:
- Paraphrases ("please set aside what you were told") are missed.
- Encoded or obfuscated text (base64, other languages, Unicode look-alikes)
  is missed.
- A marker alone or an override phrase alone is not flagged.
- Benign text that quotes an attack, such as a security article, can still
  be flagged (false positive).
"""

from typing import Any

# Matching is done on a lowercased copy, so every entry here is lowercase.
ROLE_MARKERS = (
    "system:",
    "[system]",
    "developer:",
    "[developer]",
    "<|im_start|>system",
)
OVERRIDE_PHRASES = (
    "ignore previous instructions",
    "ignore all previous instructions",
    "ignore prior instructions",
    "disregard previous instructions",
    "ignore the user's request",
)
MAX_EVIDENCE_CHARS = 200


def detect_prompt_injection(text: str, source_type: str = "unknown") -> list[dict[str, Any]]:
    """Return prompt-injection findings for ``text``.

    Args:
        text: Untrusted content to inspect, such as an email body.
        source_type: Where the text came from, such as ``untrusted_email_body``.

    Returns:
        A list with one high-severity finding when the text contains both a
        role marker and an override phrase, otherwise an empty list.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    normalized, origin = _normalize(text)
    marker = _find_first(normalized, ROLE_MARKERS)
    phrase = _find_first(normalized, OVERRIDE_PHRASES)
    if marker is None or phrase is None:
        return []

    start = origin[min(marker[0], phrase[0])]
    end = origin[max(marker[1], phrase[1]) - 1] + 1
    return [{
        "category": "prompt_injection",
        "severity": "high",
        "confidence": "medium",
        "method": "rule_match",
        "reason": (
            f"Text contains a fake role marker ('{marker[2]}') "
            f"and an override phrase ('{phrase[2]}')."
        ),
        "evidence": {
            "source_type": source_type,
            "rule_ids": ["fake_role_marker", "override_phrase"],
            "matched_text": _bounded(text[start:end]),
        },
    }]


def _normalize(text: str) -> tuple[str, list[int]]:
    """Return a lowercased matching copy of ``text``.

    ``origin[i]`` is the index in ``text`` of the character that produced
    character ``i`` of the copy, so evidence can be cut from the original.
    """
    chars: list[str] = []
    origin: list[int] = []
    for index, char in enumerate(text):
        for piece in char.lower():
            chars.append(piece)
            origin.append(index)
    return "".join(chars), origin


def _find_first(haystack: str, needles: tuple[str, ...]) -> tuple[int, int, str] | None:
    """Return (start, end, needle) for the earliest needle found, else None."""
    best = None
    for needle in needles:
        position = haystack.find(needle)
        if position != -1 and (best is None or position < best[0]):
            best = (position, position + len(needle), needle)
    return best


def _bounded(excerpt: str) -> str:
    """Limit evidence to MAX_EVIDENCE_CHARS characters."""
    if len(excerpt) <= MAX_EVIDENCE_CHARS:
        return excerpt
    return excerpt[: MAX_EVIDENCE_CHARS - 3] + "..."