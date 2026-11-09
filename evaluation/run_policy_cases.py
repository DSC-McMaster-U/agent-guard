"""Check the four base scenarios for agreement with the demo policy.

This checks policy decisions only, not complete attack prevention.
"""

import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.policy import evaluate_policy


def main() -> int:
    cases_path = REPO_ROOT / "evaluation" / "scenarios" / "base.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    passed = 0

    print("Policy-decision agreement (policy only; not complete attack prevention)")
    for case in cases:
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
        print(f"{case['id']}: expected={expected}, actual={actual} [{status}]")

    failed = len(cases) - passed
    print(f"Policy agreement: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
