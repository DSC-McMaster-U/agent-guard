# Prompt-injection detector scenarios

`prompt_injection.json` holds six fictional text samples that measure the real [`detect_prompt_injection`](../../backend/app/security/prompt_injection.py) detector. They are loaded by [`backend/tests/test_prompt_injection_cases.py`](../../backend/tests/test_prompt_injection_cases.py), not by the policy checker.

## Two different fields

- `malicious` is **ground truth**: whether the text really is an attack.
- `expected_detector_flag` is **current detector behaviour**: whether the narrow rule-based detector is expected to flag it.

They can differ. A passing test means the detector behaves as documented. It does not mean every attack is stopped.

| ID | What it tests | `malicious` | `expected_detector_flag` | Notes |
| --- | --- | --- | --- | --- |
| PI-001 | Clear role marker plus override phrase | true | true | Baseline attack. |
| PI-002 | Mixed-case version of the same attack | true | true | Matching ignores case. |
| PI-003 | Full-width characters and repeated whitespace | true | true | Flagged because #88 normalizes a matching copy (NFKC, case folding, collapsed whitespace). |
| PI-004 | Ordinary benign message | false | false | No marker or phrase. |
| PI-005 | Role marker only, benign | false | false | The detector needs both a marker and an override phrase. |
| PI-006 | Paraphrased attack | true | **false** | **Known miss.** The wording avoids every supported phrase. Catching it needs semantic analysis, which is later work. |

## Limitations these cases expose

- PI-006 is a real attack the detector misses by design.
- PI-003 passes only because of #88 normalization. Zero-width characters inside words and look-alike letters from other alphabets are still missed.
- Not covered here: quoted attack text in a benign article may still be flagged (false positive), and encoded or translated attacks may be missed.

## Scope

These are six detector regression cases. They are separate from the twelve policy scenarios in `base.json` and `adversarial.json`, so do not report them as 18 end-to-end tests. All data is fictional.
