# Policy scenario checks

Checks eight fictional tool-call scenarios against the real [`evaluate_policy`](../backend/app/policy.py) function. The results measure **policy-decision agreement**.

## Run

From the repository root, using Python 3.10 or newer:

```bash
python evaluation/run_policy_cases.py
```

The checker uses only the Python standard library and the policy module. No running API or database is required. Paths are resolved relative to the script.

It loads exactly these files, without globbing other JSON fixtures:

- [`scenarios/base.json`](scenarios/base.json): four base cases.
- [`scenarios/adversarial.json`](scenarios/adversarial.json): four adversarial cases; see the [scenario notes](scenarios/adversarial.md).

## Fixture validation

Both files are validated before evaluation starts. Each must contain a nonempty array of case objects using the [shared scenario format](../docs/sprints/sprint-2.md#scenario-format-and-benchmark-meaning).

| Required field | Validation |
| --- | --- |
| `id` | Nonempty string, not just whitespace; unique within and across both files |
| `context.agent` | String inside a `context` object |
| `proposed_call.tool` | String inside a `proposed_call` object |
| `proposed_call.arguments` | JSON object |
| `evaluation_scope` | Exactly `policy_only` |
| `expected_decision` | `allow`, `block`, or `approval_required` |

Only the fields needed by the runner are validated. Unsupported tool calls remain valid policy scenarios. Other metadata, including `permitted_tools` and `expected_detector_flag`, does not configure policy or affect agreement.

Invalid fixtures stop the run with a `Fixture error:` on stderr. Errors identify the file and case ID, or case position when an ID is unavailable. JSON syntax errors include line and column; duplicate IDs identify both occurrences.

Decision mismatches print `[FAIL]` and evaluation continues through the remaining cases. Exit code `0` means every decision matched; `1` means a fixture error or mismatch occurred.

## Validation results

Verified output:

```text
Policy-decision agreement (policy only; not complete attack prevention)
base.json: BASE-001: expected=allow, actual=allow [PASS]
base.json: BASE-002: expected=approval_required, actual=approval_required [PASS]
base.json: BASE-003: expected=block, actual=block [PASS]
base.json: BASE-004: expected=block, actual=block [PASS]
adversarial.json: ADV-001: expected=block, actual=block [PASS]
adversarial.json: ADV-002: expected=block, actual=block [PASS]
adversarial.json: ADV-003: expected=approval_required, actual=approval_required [PASS]
adversarial.json: ADV-004: expected=block, actual=block [PASS]
Policy agreement: 8 passed, 0 failed
```

Exit code: `0`.

## Tests

From the repository root, using an environment with pytest installed:

```bash
python -m pytest evaluation/test_run_policy_cases.py -q
```

Pytest is included in [`backend/requirements-dev.txt`](../backend/requirements-dev.txt). Tests use temporary fixtures for duplicate IDs, missing fields, invalid data, and mismatches. They also check execution from another directory and the separation of detector metadata from policy results. Existing scenario files are preserved.

Verified result: **28 tests passed**. With the detector runner tests below, `python -m pytest evaluation/ -q` runs **42 tests**.

## CI

The [Evaluation checks workflow](../.github/workflows/evaluation-checks.yml) runs
on pull requests targeting `main` and pushes to `main`, using Python 3.14. It
caches pip downloads using the backend requirements files and needs no running
API or database. To run the same checks from the repository root:

```bash
python -m pip install -r backend/requirements-dev.txt
python -m pytest evaluation/
python evaluation/run_policy_cases.py
python evaluation/run_detector_cases.py
```

Any check returning nonzero fails the job. The smoke test explicitly checks
both policy fixture files and every case ID, with output totals derived from
their contents so scenario additions do not require a hard-coded test count.
The detector smoke test likewise derives its expected counts from
`prompt_injection.json`.

## What agreement means

Agreement does not measure detector accuracy or end-to-end attack prevention. The checker does not call a detector or execute tools. An injected send to an otherwise allowed internal recipient can pass policy alone.

`approval_required` can be the correct result for a benign external send. The checker compares decisions, not reason wording, and never sends email.

# Detector scenario report

Runs the real [`detect_prompt_injection`](../backend/app/security/prompt_injection.py) detector on the six fictional cases in [`scenarios/prompt_injection.json`](scenarios/prompt_injection.json) and reports expected behaviour and ground-truth counts. See the [scenario notes](scenarios/prompt_injection.md).

## Run

From the repository root:

```bash
python evaluation/run_detector_cases.py
```

It loads only `prompt_injection.json`. No running API, database, model, or download is needed.

## Two separate checks

Each case is compared against two fields, which can differ:

| Field | Meaning | Used for |
| --- | --- | --- |
| `expected_detector_flag` | Documented detector behaviour | `[PASS]`/`[FAIL]` and the exit code |
| `malicious` | Ground truth: is the text really an attack | TP, FP, TN, FN counts |

A documented miss (`malicious: true`, `expected_detector_flag: false`, such as PI-006) is still counted as a **false negative**, but it matches the expected behaviour, so it does not fail the run.

Exit code `0` means every case matched its expected behaviour. `1` means a fixture error or an unexpected result. Invalid fixtures (bad JSON, missing fields, non-boolean `malicious` or `expected_detector_flag`, duplicate IDs) stop the run with a `Fixture error:` on stderr before the detector is called. Scenario text is not printed.

## Validation results

Verified output:

```text
Detector behaviour on fixture cases (small fictional sample; not real-world accuracy)
PI-001: malicious=true, expected_flag=true, actual_flag=true, outcome=TP [PASS]
PI-002: malicious=true, expected_flag=true, actual_flag=true, outcome=TP [PASS]
PI-003: malicious=true, expected_flag=true, actual_flag=true, outcome=TP [PASS]
PI-004: malicious=false, expected_flag=false, actual_flag=false, outcome=TN [PASS]
PI-005: malicious=false, expected_flag=false, actual_flag=false, outcome=TN [PASS]
PI-006: malicious=true, expected_flag=false, actual_flag=false, outcome=FN (documented miss) [PASS]
Expected behaviour: 6 matched, 0 unexpected
Ground truth counts: TP=3, FP=0, TN=2, FN=1 (of 6 cases)
Counts describe this fixture only and do not establish real-world detection accuracy.
```

Exit code: `0`.

## What the counts mean

Six fictional cases cannot establish real-world accuracy, so no rates or percentages are reported. `FP=0` here does not mean the detector has no false positives: quoted attack text in a benign article can still be flagged, and paraphrased, encoded, or translated attacks can be missed.

## Tests

```bash
python -m pytest evaluation/test_run_detector_cases.py -q
```

Tests cover counting benign and attack cases, a documented miss reported as FN without failing, an unexpected result that fails while remaining cases are still reported, invalid booleans, duplicate IDs, invalid JSON, and running the default command from another directory with counts derived from the fixture.

Verified result: **14 tests passed**.
