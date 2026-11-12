"""Check both policy fixture files for agreement with the demo policy.

This checks policy decisions only, not complete attack prevention.
"""

import json
from collections.abc import Iterable
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.policy import evaluate_policy


CASE_PATHS = (
    REPO_ROOT / "evaluation" / "scenarios" / "base.json",
    REPO_ROOT / "evaluation" / "scenarios" / "adversarial.json",
)


class FixtureError(ValueError):
    """A policy fixture cannot be loaded or has an invalid case."""


def load_cases(case_paths: Iterable[Path]) -> list[tuple[Path, dict[str, Any]]]:
    """Validate every input before returning cases with their source paths."""
    cases = []
    seen_ids = {}
    for path in case_paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise FixtureError(
                f"{path}: invalid JSON at line {error.lineno}, "
                f"column {error.colno}: {error.msg}"
            ) from error
        except (OSError, UnicodeError) as error:
            raise FixtureError(f"{path}: cannot read fixture: {error}") from error

        if not isinstance(data, list) or not data:
            raise FixtureError(f"{path}: expected a nonempty array of cases")

        for index, case in enumerate(data, start=1):
            location = f"{path}: case #{index}"
            if not isinstance(case, dict):
                raise FixtureError(f"{location}: case must be an object")
            case_id = case.get("id")
            if not isinstance(case_id, str) or not case_id.strip():
                raise FixtureError(f"{location}: id must be a nonempty string")
            location = f"{path}: case {case_id!r} (#{index})"
            if case_id in seen_ids:
                raise FixtureError(
                    f"{location}: duplicate id; first defined at {seen_ids[case_id]}"
                )

            context = case.get("context")
            if not isinstance(context, dict):
                raise FixtureError(f"{location}: context must be an object")
            if not isinstance(context.get("agent"), str):
                raise FixtureError(f"{location}: context.agent must be a string")
            call = case.get("proposed_call")
            if not isinstance(call, dict):
                raise FixtureError(f"{location}: proposed_call must be an object")
            if not isinstance(call.get("tool"), str):
                raise FixtureError(f"{location}: proposed_call.tool must be a string")
            if not isinstance(call.get("arguments"), dict):
                raise FixtureError(f"{location}: proposed_call.arguments must be an object")
            if case.get("evaluation_scope") != "policy_only":
                raise FixtureError(f"{location}: evaluation_scope must be 'policy_only'")
            if case.get("expected_decision") not in ("allow", "block", "approval_required"):
                raise FixtureError(
                    f"{location}: expected_decision must be allow, block, or approval_required"
                )

            seen_ids[case_id] = location
            cases.append((path, case))
    return cases


def main(case_paths: Iterable[Path] = CASE_PATHS) -> int:
    try:
        cases = load_cases(case_paths)
    except FixtureError as error:
        print(f"Fixture error: {error}", file=sys.stderr)
        return 1

    passed = 0
    print("Policy-decision agreement (policy only; not complete attack prevention)")
    for path, case in cases:
        proposed_call = case["proposed_call"]
        # Fixture metadata, including permitted_tools, cannot grant access.
        result = evaluate_policy(
            case["context"]["agent"],
            proposed_call["tool"],
            proposed_call["arguments"],
        )
        expected = case["expected_decision"]
        actual = result["decision"]
        matches = actual == expected
        passed += matches
        status = "PASS" if matches else "FAIL"
        print(f"{path.name}: {case['id']}: expected={expected}, actual={actual} [{status}]")

    failed = len(cases) - passed
    print(f"Policy agreement: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
