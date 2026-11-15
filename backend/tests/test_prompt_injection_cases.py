"""Regression cases for the narrow prompt-injection detector.

The cases live in evaluation/scenarios/prompt_injection.json. ``malicious`` is
ground truth about the text. ``expected_detector_flag`` is what the detector is
currently expected to do. The two can differ (PI-006 is an attack the detector
misses), so a passing test does not mean every attack is stopped.
"""

import json
from pathlib import Path

import pytest

from app.security import detect_prompt_injection

CASES_PATH = Path(__file__).resolve().parents[2] / "evaluation" / "scenarios" / "prompt_injection.json"
CASES = json.loads(CASES_PATH.read_text(encoding="utf-8"))
REQUIRED_FIELDS = {"id", "text", "source_type", "malicious", "expected_detector_flag", "rationale"}

# Needs the normalization planned in #88 (NFKC, case folding, collapsed whitespace).
NEEDS_NORMALIZATION = {"PI-003"}


def _param(case):
    marks = []
    if case["id"] in NEEDS_NORMALIZATION:
        marks.append(pytest.mark.xfail(strict=True, reason="needs #88 input normalization"))
    return pytest.param(case, id=case["id"], marks=marks)


def test_fixture_file_is_well_formed():
    ids = [case["id"] for case in CASES]

    assert len(CASES) == 6
    assert len(set(ids)) == len(ids)
    assert all(case_id.startswith("PI-") for case_id in ids)
    for case in CASES:
        assert set(case) == REQUIRED_FIELDS
        assert isinstance(case["malicious"], bool)
        assert isinstance(case["expected_detector_flag"], bool)


def test_known_missed_attack_is_documented():
    missed = [c for c in CASES if c["malicious"] and not c["expected_detector_flag"]]

    assert [c["id"] for c in missed] == ["PI-006"]
    assert "limitation" in missed[0]["rationale"].lower()


@pytest.mark.parametrize("case", [_param(case) for case in CASES])
def test_detector_flag_matches_expected(case):
    findings = detect_prompt_injection(case["text"], source_type=case["source_type"])

    assert bool(findings) == case["expected_detector_flag"]
