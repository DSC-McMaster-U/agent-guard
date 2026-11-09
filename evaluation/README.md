# Base policy scenario checks

The Sprint 2 checker runs the four corrected examples from [#32](https://github.com/DSC-McMaster-U/agent-guard/issues/32#issuecomment-6611135333) against the real `evaluate_policy` function in `backend/app/policy.py`.

## Run

From the repository root, using Python 3.10 or newer:

```bash
python evaluation/run_policy_cases.py
```

No third-party dependencies, running API, database, or benchmark service are needed. The script resolves paths relative to its own file and imports the policy from `backend/`.

It loads only `scenarios/base.json`, containing two benign and two adversarial fictional cases. Each case passes `context.agent`, `proposed_call.tool`, and `proposed_call.arguments` to the policy. Context such as `permitted_tools` is fixture metadata and does not configure server permissions.

The scenario wrapper follows the [Sprint 2 handoff](../docs/sprints/sprint-2.md): IDs use the `BASE-` prefix, the user task is stored as `context.user_request`, and `evaluation_scope` is `policy_only`.

## Validation results

The command was run against the real policy with these results:

```text
Policy-decision agreement (policy only; not complete attack prevention)
BASE-001: expected=allow, actual=allow [PASS]
BASE-002: expected=approval_required, actual=approval_required [PASS]
BASE-003: expected=block, actual=block [PASS]
BASE-004: expected=block, actual=block [PASS]
Policy agreement: 4 passed, 0 failed
```

Exit code: `0`.

To check the failure path, `BASE-001`'s expected decision was temporarily changed from `allow` to `block` and the same command was run:

```text
BASE-001: expected=block, actual=allow [FAIL]
Policy agreement: 3 passed, 1 failed
```

Exit code: `1`. The fixture was restored byte-for-byte, and another run returned four passes and exit code `0`. The checker also passed when launched by its full path from outside the repository root.

## What agreement means

These results measure policy-decision agreement, not complete attack prevention or detector accuracy. The adversarial cases are blocked because they request an unsupported tool or a denied destination; the checker does not detect injection or inspect sensitive content. An injected send to an otherwise allowed internal recipient can pass this policy alone.

`approval_required` is the expected result for a legitimate external send; a benign label does not imply `allow`. The checker compares decisions, not reason wording, and does not execute tools or send email.

Sana's separate [adversarial.json](scenarios/adversarial.json) and its [explanation](scenarios/adversarial.md) belong to #65 and are not loaded by this checker. Multi-file loading, detailed fixture validation, JSON reports, extra cases, and detector metrics are deferred to Sprint 3.
