"""Report how the prompt-injection detector behaves on its fixture cases.

Each case is checked against two separate things:

- ``expected_detector_flag``: the documented detector behaviour. A mismatch
  is unexpected and fails the run.
- ``malicious``: ground truth. It sorts each case into TP, FP, TN, or FN.
  A documented miss (an attack the detector is expected not to flag) still
  counts as a false negative, but it does not fail the run.

The fixture is a handful of fictional cases, so the counts describe this
fixture only. They do not establish real-world detection accuracy.
"""

import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.security import detect_prompt_injection


CASE_PATH = REPO_ROOT / "evaluation" / "scenarios" / "prompt_injection.json"
BOOLEAN_FIELDS = ("malicious", "expected_detector_flag")


class FixtureError(ValueError):
    """The detector fixture cannot be loaded or has an invalid case."""


def load_cases(path: Path) -> list[dict[str, Any]]:
    """Validate every case before any detector call."""
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

    seen_ids = {}
    for index, case in enumerate(data, start=1):
        location = f"{path}: case #{index}"
        if not isinstance(case, dict):
            raise FixtureError(f"{location}: case must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            raise FixtureError(f"{location}: id must be a nonempty string")
        location = f"{path}: case {case_id!r} (#{index})"
        if case_id in seen_ids:
            raise FixtureError(f"{location}: duplicate id; first defined at case #{seen_ids[case_id]}")
        if not isinstance(case.get("text"), str):
            raise FixtureError(f"{location}: text must be a string")
        source_type = case.get("source_type")
        if not isinstance(source_type, str) or not source_type.strip():
            raise FixtureError(f"{location}: source_type must be a nonempty string")
        for field in BOOLEAN_FIELDS:
            if not isinstance(case.get(field), bool):
                raise FixtureError(f"{location}: {field} must be true or false")
        seen_ids[case_id] = index
    return data


def classify(malicious: bool, flagged: bool) -> str:
    """Return TP, FP, TN, or FN from ground truth and the actual flag."""
    if malicious:
        return "TP" if flagged else "FN"
    return "FP" if flagged else "TN"


def main(case_path: Path = CASE_PATH) -> int:
    try:
        cases = load_cases(case_path)
    except FixtureError as error:
        print(f"Fixture error: {error}", file=sys.stderr)
        return 1

    counts = {"TP": 0, "FP": 0, "TN": 0, "FN": 0}
    unexpected = 0
    print("Detector behaviour on fixture cases (small fictional sample; not real-world accuracy)")
    for case in cases:
        flagged = bool(detect_prompt_injection(case["text"], source_type=case["source_type"]))
        outcome = classify(case["malicious"], flagged)
        counts[outcome] += 1
        expected = case["expected_detector_flag"]
        status = "PASS" if flagged == expected else "FAIL"
        unexpected += status == "FAIL"
        note = " (documented miss)" if outcome == "FN" and not expected else ""
        print(
            f"{case['id']}: malicious={str(case['malicious']).lower()}, "
            f"expected_flag={str(expected).lower()}, actual_flag={str(flagged).lower()}, "
            f"outcome={outcome}{note} [{status}]"
        )

    matched = len(cases) - unexpected
    print(f"Expected behaviour: {matched} matched, {unexpected} unexpected")
    print(
        f"Ground truth counts: TP={counts['TP']}, FP={counts['FP']}, "
        f"TN={counts['TN']}, FN={counts['FN']} (of {len(cases)} cases)"
    )
    print("Counts describe this fixture only and do not establish real-world detection accuracy.")
    return 1 if unexpected else 0


if __name__ == "__main__":
    raise SystemExit(main())
