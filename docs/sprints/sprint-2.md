# Sprint 2: First Working Prototypes

**Dates:** Tuesday, November 3 to the Tuesday meeting on November 10, 2026.
**Lead:** Aryan (@rinnegannn).
**Capacity:** About three hours per person for the whole week, including the 20–30 minute meeting, setup, handoff, and review preparation.

The goal is a working policy-decision API, a usable dashboard prototype, the first prompt-injection detector, a runnable policy benchmark, and reproducible development checks. Build each assignment from its owner's Sprint 1 result. AI assistance is expected during implementation; acceptance is based on demonstrated behaviour and validation results rather than a fixed limit on task size.

The milestone dates in [PROJECT.md](../../PROJECT.md) remain the planning targets: a November progress checkpoint, optional December maintenance, the late-January local MVP, and a March release candidate by March 22 before the end-of-March showcase. The exact showcase dates are still unannounced. First policy, detector, and dashboard prototypes move into Sprint 2. Sprint 3 connects the detector and API, replaces dashboard mocks with evaluated requests, and stabilizes the combined flow; persistence and broader integration follow in Sprint 4.

## Starting point from Sprint 1

For Sprint 2 planning, assume the Sprint 1 deliverables are completed and accepted before November 3. All eleven assignments are Ready for the November 3 kickoff. Sprint 1 issue statuses continue to reflect actual reviewed submissions.

Use the results already produced: Nozhin's glossary (#26/#55), Sheraz's FastAPI scaffold (#25/#53), Billy's decision examples (#27), Naman's React shell (#28/#56), Barzin's accepted sketches (#29), Erfan's detector recommendation (#31), and MD Tanzeem's dashboard journeys (#35). Sana's corrected threat cases (#30), Pranoy's corrected scenario format (#32), Nelavan's Compose database (#33), and Trisha's security guide (#34) are the planned starting inputs for their next deliverables.

Real implementation dependencies still have an order: schemas/policy precede endpoint integration, shared frontend types precede component integration, and executable checks precede final CI validation. Contributors can start from the fixed interfaces below while prerequisite PRs are prepared.

## Shared request contract

The [Sprint 1 glossary](../tool-call-contract.md) provides the vocabulary. The following decisions resolve its open questions for the local demo:

| Field | Type | Required | Sprint 2 decision |
| --- | --- | --- | --- |
| `request_id` | Non-empty string | Yes | The demo caller supplies it. Server-generated IDs/idempotency can be revisited later. |
| `agent_id` | Non-empty string | Yes | An identifier for the demo; a caller's label alone grants no permission. |
| `user_id` | Non-empty string | Yes | An identifier for the demo; it is not proof of authentication. |
| `session_id` | Non-empty string | Yes | Keep the glossary's grouping ID without implementing tracing yet. |
| `original_goal` | Non-empty string | Yes | The original user task, kept distinct from untrusted content. |
| `tool` | Non-empty string | Yes | Keep this general so policy can return `block` for an unsupported name. The only supported demo tool is `email.send`. |
| `arguments` | JSON object | Yes | Tool arguments. Validate the supported tool's argument shape separately. |
| `trigger_source` | Object or null | No | Optional provenance/context. Missing provenance means unknown. |

An optional `trigger_source` contains `type`, `content`, and `trust_level`. For the request models, these have defaults `unknown`, an empty string, and `unknown`. Supported `type` values are `user_instruction`, `untrusted_email_body`, `untrusted_webpage`, `untrusted_document`, `tool_result`, and `unknown`; `trust_level` values are `trusted`, `untrusted`, and `unknown`.

Provenance is context for analysis. A caller setting `trust_level` to `trusted` must never bypass configured permissions, validation, policy, or security findings. This sprint does not implement an authentication system. Benchmark `context.permitted_tools` is test setup, not a permission grant supplied by a production caller.

`EmailSendArguments` has exactly three required fields: `recipient` validated as an email address, a non-empty `subject` of at most 200 characters, and a non-empty `body` of at most 10,000 characters. Use Pydantic's email validation with its required dependency. Reject extra top-level request keys and extra email-argument keys. IDs and tool names are non-empty strings of at most 128 characters; `original_goal` has at most 4,000 characters and optional provenance `content` at most 10,000. These are initial demo limits and should have boundary tests.

Keep the normalized request and email-argument models reusable. The endpoint validates email arguments for `email.send`; other normalized tool names go to policy for an unsupported-tool block. Attachments, `cc`, real email delivery, and filesystem execution are outside this demo.

Use FastAPI's standard `422` validation response for malformed request data or invalid supported-tool arguments. An unsupported tool with an otherwise valid normalized request becomes a policy `block`; it does not require implementing that tool.

## Demo policy baseline

The Sprint 2 policy evaluator uses this order after request/argument validation:

1. Block an unsupported tool or an unknown/unpermitted demo agent. The server-owned demo table permits `email.send` for `assistant_2` and `support-assistant`, preserving the existing glossary/scenario examples. No caller-supplied permission list can grant access.
2. Block an explicitly denied destination, including the example domain `example.net`.
3. Allow an internal recipient at `example.com` when no rejecting policy or security finding applies.
4. Require approval for other valid external recipients, including `example.org`.

Match the normalized recipient's exact domain, case-insensitively. Do not use substring matching. Invalid addresses fail endpoint validation. Add explicit model/API/policy tests for malformed addresses, mixed case, and misleading domain suffixes. Any later detector integration must preserve block precedence rather than converting a blocked action into allow.

| Fictional recipient | Expected policy decision | Reason |
| --- | --- | --- |
| `teammate@example.com` | `allow` | Internal recipient; no other rejecting condition. |
| `blocked@example.net` | `block` | Explicitly denied destination. |
| `partner@example.org` | `approval_required` | External recipient needs a human decision. |

All three examples use the same simulated `email.send` with a short subject and body. The future executor records a fake send outcome in a local outbox/audit trail and never contacts an email provider.

The original #27 examples were exploratory. The rule baseline above and PROJECT.md now govern implementation. A security finding is separate from a deterministic policy decision: the small January detector is not a guarantee that every prompt injection or sensitive-data leak is caught. Attachment scanning and broader semantic detection remain future work.

## Shared decision summary for the dashboard

Use these fields for TypeScript types, mock data, and the planned API examples:

| Field | Type / values |
| --- | --- |
| `request_id` | String |
| `agent_id` | String |
| `tool` | String; `email.send` in normal demo fixtures |
| `arguments` | JSON object (`Record<string, unknown>` in TypeScript); normal email fixtures contain string `recipient`, `subject`, `body`. |
| `decision` | `allow`, `block`, or `approval_required` |
| `reason` | Short human-readable explanation |
| `timestamp` | ISO 8601 UTC timestamp string, for example `2026-11-03T18:00:00Z` |
| `approval_status` | `not_required`, `pending`, `approved`, or `denied` |

For the three initial fixtures, use `not_required` for allow/block and `pending` for approval-required. `approved` and `denied` are vocabulary for later approval events; mocks do not implement persistence or safe execution.

The Sprint 2 `POST /api/v1/tool-calls` endpoint returns this summary for a valid evaluated request. A `200` response records the policy decision; email execution, audit persistence, detector composition, and approval persistence follow in later integration tasks. The dashboard's Approve/Deny buttons update clearly labelled local demo state in Sprint 2.

## Implementation interfaces

Agree these names at kickoff so work can proceed in parallel:

| Module | Interface | Owner / consumer |
| --- | --- | --- |
| `backend/app/schemas.py` | `TriggerSource`, `ToolCallRequest`, `EmailSendArguments`, `ToolCallSummary` | Nozhin; Sheraz imports the models. |
| `backend/app/policy.py` | `evaluate_policy(agent_id, tool, arguments)` returns a dictionary with `decision` and `reason`. | Billy; Sheraz and Pranoy call it. |
| `backend/app/security/prompt_injection.py` | `detect_prompt_injection(text, source_type="unknown")` returns a list of finding dictionaries using #31's category/severity/confidence/method/reason/evidence fields. | Erfan; detector integration follows in Sprint 3. |
| `frontend/src/types/toolCall.ts` | Export `ToolCallDecision`, `ApprovalStatus`, and `ToolCallSummary` matching the fields above. | MD Tanzeem publishes this early. |
| `frontend/src/components/ActivityList.tsx` | Props: `items: ToolCallSummary[]`, `onSelect(requestId: string)`, optional `loading: boolean`, `error: string`, and `onRetry()`. | Naman; MD Tanzeem integrates it. |
| `frontend/src/components/ApprovalDetails.tsx` | Props: `request` (a `ToolCallSummary` or null), `onDecision(requestId, action)` with action `approve` or `deny`, optional `busy: boolean` and `error: string`. | Barzin; MD Tanzeem integrates it. |
| `backend/app/benchmark.py` | From `backend/`, run `python -m app.benchmark --cases ../evaluation/scenarios`. | Pranoy; reads the base/adversarial fixture files. |

Only pending approval requests can transition to approved/denied in the local UI. Preserve the original `decision` value and update `approval_status`; repeated clicks cannot approve twice. Show the demo-data status so viewers know the buttons do not send email.

The policy module remains independent of FastAPI/Pydantic. It checks the server-owned permission table, rejects obviously missing/malformed recipient data defensively, and compares exact domains. The HTTP route performs full supported-tool input validation and converts validation failures to FastAPI-style 422 errors. No endpoint calls the executor in this sprint.

The first detector follows Erfan's recommendation: normalize case and a documented set of invisible characters, inspect explicit role markers/override phrases, and return bounded evidence plus heuristic findings. Override-only is low, marker-only medium, and both high. These scores are not measured accuracy; known false positives/bypasses stay documented. Detector findings do not grant permission or override a policy block.

## Scenario format and benchmark meaning

Preserve Pranoy's useful separation between context and proposed action. Both scenario files contain arrays of objects with:

- `id`, `type` (`benign` or `adversarial`), and `category`.
- `context` with `agent`, `user_request`, and optional `untrusted_source` containing `source_type` and `content`. Existing explanatory context may remain, but permission lists do not configure the real policy.
- `proposed_call` with `tool` and an `arguments` object.
- `evaluation_scope: "policy_only"`, `expected_decision`, `rule`, and `rationale`.
- Optional `expected_detector_flag` as separate detector metadata.

The runner maps `context.agent` to the policy's `agent_id`. It checks expected policy decisions only. A prompt injection aimed at an otherwise allowed internal send may be allowed by this policy prototype; label the missing detector protection rather than inventing an implemented rule. Report policy-decision agreement and distinguish benign/adversarial totals; do not describe this as end-to-end attack prevention.

Pranoy's six base cases include the four corrected Sprint 1 examples plus two benign controls (at least four benign cases in the base set). Sana contributes eight adversarial cases derived from her five threats. The combined set is fourteen cases, within the January target of ten to twenty, and can be refined during integration. Erfan owns separate detector text cases/tests; a policy decision and a detector flag are different assertions.

## Student assignments

All assignments below are Ready for November 3–10. Each is a complete prototype/module deliverable with tests or demonstration evidence. Completion of previous Sprint 1 work is the planning assumption for every student. Keep changes focused enough to review, and raise integration blockers early.

| Owner | Workstream | Issue | Builds on | Sprint 2 deliverable | Estimated effort |
| --- | --- | --- | --- | --- | --- |
| Nozhin | Backend | #58 | #26 glossary / PR #55 | Validated request/email/response models with tests. | 3–5 hours |
| Sheraz | Backend | #59 | #25 health app / PR #53 | Working policy-decision endpoint, test setup, and API tests. | 4–6 hours |
| Billy | Backend | #60 | #27 decision examples | Real allow/block/approval policy evaluator and tests. | 2–4 hours |
| Naman | Full Stack / Frontend | #61 | #28 React shell / PR #56 | Activity component with loading/empty/error states. | 3–5 hours |
| Barzin | Full Stack / Frontend | #62 | #29 accepted wireframes | Approval detail component with local decision callbacks. | 3–5 hours |
| MD Tanzeem | Full Stack / Frontend | #63 | #35 user journeys | Shared types/mocks and integrated local dashboard flow. | 4–6 hours |
| Erfan | AI/ML & Security | #64 | #31 accepted detector recommendation | Rule-based detector prototype, tests, and limitations. | 3–5 hours |
| Sana | AI/ML & Security | #65 | Corrected #30 threat cases | Eight adversarial fixtures and a threat-to-test map. | 2–3 hours |
| Pranoy | AI/ML & Security | #66 | Corrected #32 scenario format | Six base scenarios and a runnable policy benchmark. | 4–6 hours |
| Nelavan | DevOps & Infrastructure | #67 | #33 PostgreSQL Compose | Backend container/Compose service and backend test/build CI. | 4–6 hours |
| Trisha | DevOps & Infrastructure | #68 | #34 security guide | Frontend lint/tooling ownership and passing lint/type/build CI. | 2–4 hours |

## Effort estimates and Lead time

These are planning ranges for students using AI assistance and starting from completed Sprint 1 deliverables. They include implementation, learning/debugging, relevant tests, PR preparation, and routine review fixes. They exclude the 20–30 minute meeting, time waiting for another PR, and unusually large integration problems. They are estimates, not artificial task-size limits or guaranteed completion times.

Student implementation effort totals approximately **34–55 hours**. The original three-hour weekly commitment includes the meeting, leaving about 2.5 focused hours per student. Several expanded Sprint 2 assignments exceed that original availability even with AI assistance. Keep the full Ready commitments requested for this plan, record actual effort, and check availability at the November 3 meeting; the estimates make the added effort visible.

| Lead work | Related issue | Estimated effort |
| --- | --- | --- |
| Review the plan/contracts and verify assignments with Codex assistance | #57, already completed | 30–45 minutes |
| Review eleven student PRs, answer interface questions, and coordinate merges | Ongoing Sprint 2 Lead responsibility | 3–5 hours |
| Tuesday meeting | Team cadence | 20–30 minutes |

The ongoing review estimate assumes focused PRs and use of the agreed interfaces. The preparation task is already Done; the 3–5 hours of review/coordination plus the meeting still belong to the sprint's Lead workload.

## Integration order and file ownership

1. At kickoff, confirm the interfaces above. Nozhin publishes schemas early, Billy publishes policy early, and Sheraz publishes the test setup before final endpoint integration. Start from the fixed contracts and merge the shared modules before final endpoint integration.
2. MD Tanzeem publishes shared types/mocks early. Naman and Barzin own their component files and styles; MD Tanzeem owns `App.tsx`, selection, and local approval state. Temporary local component previews are useful, but only the integration task commits App changes.
3. Trisha owns frontend dependency/lockfile and ESLint configuration changes. Component owners use those commands when available and coordinate minimal lint fixes. This avoids three conflicting package manifests.
4. Sana and Pranoy agree the published fixture shape at kickoff and own separate files. The benchmark works on the base cases before the adversarial file merges, then is checked against the combined set.
5. Nelavan extends the completed PostgreSQL Compose setup with the backend and adds test/build CI. Runtime requirements belong to Nozhin's model task; development test setup belongs to Sheraz. CI is merged only after the commands it invokes exist and pass.
6. Merge focused PRs in dependency order and validate the combined result. All tasks remain Ready for planning; actual progress should be updated as contributors begin. Existing branch protection remains in effect, and new CI checks become required only once operational and reliable.

The Lead reviews contributors' PRs and handles interface/merge blockers. Use `Closes #number`, include the requested validation evidence, and update issues before Tuesday's meeting. January/March stay focused on the same simulated-email system: Sprint 3 adds detector/API/dashboard integration, Sprint 4 adds persistence, and Sprint 5 reviews a working November slice. Redis, real providers, cloud deployment, and model training remain capacity-dependent later work.

## Useful references

- [Pydantic model documentation](https://docs.pydantic.dev/latest/concepts/models/)
- [TypeScript ESLint quickstart](https://typescript-eslint.io/getting-started/)
- [GitHub Actions Python guide](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
