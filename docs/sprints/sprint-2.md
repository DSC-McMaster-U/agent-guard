# Sprint 2: Foundations and First Components

**Dates:** Tuesday, November 3 to the Tuesday meeting on November 10, 2026.
**Lead:** Aryan (@rinnegannn).
**Weekly cap:** Three hours per person total, including the 20–30 minute meeting, implementation, testing, PR preparation, and handoff. Aim for 2–2.5 hours of task work; stop and record remaining work when the cap is reached.

The goal is a set of tested foundations that can be connected next sprint: request models, health-test setup, a policy function, basic Activity/Approval components, shared mocks, a narrow detector, scenario files/checker, and CI for commands that already exist. Each task is scoped to the three-hour total week with AI assistance.

The milestone dates in [PROJECT.md](../../PROJECT.md) remain the planning targets: a November progress checkpoint, optional December maintenance, the late-January local MVP, and a March release candidate by March 22 before the end-of-March showcase. Exact showcase dates are still unannounced. Sprint 3 adds the policy endpoint, dashboard state/integration, backend container, and the next validation increments; Sprint 4 focuses on persistence and broader API integration.

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

The planned Sprint 3 `POST /api/v1/tool-calls` endpoint will return this summary for a valid evaluated request. A `200` response records the policy decision; execution, audit persistence, detector composition, and approval persistence follow in later integration tasks. Sprint 2 builds the separate components and typed mocks; the Approval component emits callbacks, with parent state/integration added in Sprint 3.

## Implementation interfaces

Agree these names at kickoff so work can proceed in parallel:

| Module | Interface | Owner / consumer |
| --- | --- | --- |
| `backend/app/schemas.py` | `TriggerSource`, `ToolCallRequest`, `EmailSendArguments`; response models follow in Sprint 3. | Nozhin; Sheraz uses them when adding the endpoint. |
| `backend/app/policy.py` | `evaluate_policy(agent_id, tool, arguments)` returns a dictionary with `decision` and `reason`. | Billy; Sheraz and Pranoy call it. |
| `backend/app/security/prompt_injection.py` | `detect_prompt_injection(text, source_type="unknown")` returns a list of finding dictionaries using #31's category/severity/confidence/method/reason/evidence fields. | Erfan; detector integration follows in Sprint 3. |
| `frontend/src/types/toolCall.ts` | Export `ToolCallDecision`, `ApprovalStatus`, and `ToolCallSummary` matching the fields above. | MD Tanzeem publishes this early. |
| `frontend/src/components/ActivityList.tsx` | Sprint 2 props: `items: ToolCallSummary[]` and `onSelect(requestId: string)`; loading/error/retry follow later. | Naman; MD Tanzeem integrates it next sprint. |
| `frontend/src/components/ApprovalDetails.tsx` | Sprint 2 props: `request` (a `ToolCallSummary` or null), `onDecision(requestId, action)` with action `approve` or `deny`; busy/error handling follows later. | Barzin; MD Tanzeem integrates it next sprint. |
| `evaluation/run_policy_cases.py` | From the repo root, run `python evaluation/run_policy_cases.py`; load `base.json`, call the policy, and fail on a mismatch. | Pranoy; broader file loading/reporting follows in Sprint 3. |

The basic Approval component offers actions only for pending approvals and emits a callback. In Sprint 3, App state will preserve the original decision, update approval_status once, and prevent repeated transitions. Preview data and screenshots must be labelled as simulated; no email is sent.

The policy module remains independent of FastAPI/Pydantic. It checks the server-owned permission table, rejects obviously missing/malformed recipient data defensively, and compares exact domains. The Sprint 3 HTTP route will perform supported-tool validation and convert failures to FastAPI-style 422 errors. No executor is required for these policy/validation tasks.

The first detector implements one narrow part of Erfan's recommendation: normalize case and flag text containing both an explicit fake role marker and an override phrase. Return a high-severity heuristic finding with bounded evidence and otherwise no findings. Four focused tests cover a clear attack, case variation, a benign message, and empty text. Unicode handling, lower-severity partial matches, and a larger fixture suite are tracked for Sprint 3. This limited signal cannot override policy or claim complete injection coverage.

## Scenario format and benchmark meaning

Preserve Pranoy's useful separation between context and proposed action. Both scenario files contain arrays of objects with:

- `id`, `type` (`benign` or `adversarial`), and `category`.
- `context` with `agent`, `user_request`, and optional `untrusted_source` containing `source_type` and `content`. Existing explanatory context may remain, but permission lists do not configure the real policy.
- `proposed_call` with `tool` and an `arguments` object.
- `evaluation_scope: "policy_only"`, `expected_decision`, `rule`, and `rationale`.
- Optional `expected_detector_flag` as separate detector metadata.

The checker maps `context.agent` to the policy's `agent_id` and checks expected policy decisions only. A prompt injection aimed at an otherwise allowed internal send may pass this policy alone; label that gap rather than inventing a rule. Describe results as policy-decision agreement, not end-to-end attack prevention.

Pranoy saves the four corrected Sprint 1 cases in `base.json` and implements a script that reads that file, prints expected/actual decisions and pass/fail counts, and exits nonzero on a mismatch. Sana writes four additional adversarial cases in `adversarial.json`. Multi-file loading, detailed input validation, reports, detector integration, and expansion toward the January ten-to-twenty scenario target follow in later sprints. The Sprint 2 checker does not need a database, live server, or benchmark dependency.

## Student assignments and time

All eleven assignments remain Ready for November 3–10, assuming Sprint 1 completion. The scope below targets **2–2.5 hours per issue with AI assistance**, including validation and PR preparation. The meeting and handoff use the remainder of the **three-hour maximum weekly commitment**. If work exceeds that cap, record the remaining step and replan it; extra hours are not required.

| Owner | Workstream | Issue | Builds on | Sprint 2 deliverable | Task effort |
| --- | --- | --- | --- | --- | --- |
| Nozhin | Backend | #58 | #26 glossary / PR #55 | Request/email models and representative tests. | 2–2.5 hours |
| Sheraz | Backend | #59 | #25 health app / PR #53 | Health/404 tests and repeatable dev test setup. | 2–2.5 hours |
| Billy | Backend | #60 | #27 decision examples | First policy function and focused tests. | 2–2.5 hours |
| Naman | Full Stack / Frontend | #61 | #28 React shell / PR #56 | Activity rows, View callback, and empty state. | 2–2.5 hours |
| Barzin | Full Stack / Frontend | #62 | #29 accepted wireframes | Basic Approval panel and callbacks. | 2–2.5 hours |
| MD Tanzeem | Full Stack / Frontend | #63 | #35 user journeys | Shared types and three mock requests. | 2–2.5 hours |
| Erfan | AI/ML & Security | #64 | #31 detector recommendation | One combined-pattern detector and four tests. | 2–2.5 hours |
| Sana | AI/ML & Security | #65 | Corrected #30 threat cases | Four adversarial fixtures and source mapping. | 2–2.5 hours |
| Pranoy | AI/ML & Security | #66 | Corrected #32 scenario format | Four base cases and a single-file policy checker. | 2–2.5 hours |
| Nelavan | DevOps & Infrastructure | #67 | #33 PostgreSQL Compose | Backend syntax/test CI and Compose config validation. | 2–2.5 hours |
| Trisha | DevOps & Infrastructure | #68 | #34 security guide | Frontend type/build CI using existing commands. | 2–2.5 hours |

These are planning estimates with a real stopping point. The eleven student tasks total 22–27.5 focused hours; meetings and handoff fit within the team's existing weekly availability. All issues retain the Sprint 1 description format, their original assignees, and clear completion checks.

## Lead time

| Lead work | Related issue | Budget |
| --- | --- | --- |
| Preparation/contracts/assigned-plan review with Codex | #57, already completed before Sprint 2 | 30–45 minutes already spent |
| Batch PR reviews, interface questions, and merge coordination with Codex assistance | Ongoing Lead responsibility | About 2 hours during Sprint 2 |
| Tuesday meeting | Team cadence | 20–30 minutes |
| Blocker/handoff buffer | Weekly budget | Remaining time, up to a three-hour total week |

Prioritize the shared models, policy, types, and test setup when reviewing. If the review queue reaches the weekly cap, record its order and continue in the next budget; do not waive checks or assume extra Lead hours.

## Integration order and ownership

1. Nozhin owns schemas and schema tests. Sheraz owns the development test manifest and health tests. Billy's pure policy function is independent of both, while Pranoy can draft the checker against its fixed interface.
2. MD Tanzeem publishes shared types/mocks early. Naman and Barzin own their component files and can preview locally; committed App integration belongs to Sprint 3.
3. Sana and Pranoy use the agreed scenario wrapper and separate files. Erfan owns detector code/tests and keeps its findings separate from policy decisions.
4. Nelavan merges CI after Sheraz's real test commands exist; Trisha uses the existing frontend type/build commands now. No invented passing tests or changes to required branch checks are needed.
5. Merge focused PRs in dependency order, update progress before Tuesday, and keep the whole weekly contribution at or below three hours. Sprint 1 completion remains the planning assumption; actual issue closure still requires reviewed evidence.

## Deferred work and milestone path

The reduced task estimates come from moving these implementation steps into later weekly assignments:

| Next work | Planned timing / workstream |
| --- | --- |
| Policy-decision endpoint, response model, and API tests | Sprint 3 Backend, using #58–#60 outputs. |
| App selection/approval state and component integration | Sprint 3 Full Stack, using #61–#63 outputs. |
| Loading/error/busy/reviewed states and layout polish | Sprint 3 onward Frontend. |
| Wider detector patterns, normalization, and detector/API composition | Sprint 3 onward Backend + AI/ML & Security. |
| Multi-file checker, fixture validation/reporting, and more scenarios | Sprint 3–5 AI/ML & Security; ten to twenty total by January MVP. |
| Backend Docker/Compose service and image-build checks | Sprint 3 DevOps, after the backend foundation. |
| ESLint setup and frontend lint CI | Sprint 3 DevOps. |
| Storage models/migration, activity API wiring, and simulated executor integration | Sprint 4 onward; demonstrate the working subset at the November checkpoint. |

At the November 10 planning meeting, turn the next steps into assignments sized within the same three-hour weekly cap. December stays light. January completes and stabilizes the local allow/block/approval flow with the required audit trail, and February–March hardens that same core for the final showcase. Deferred work stays visible without promising that every larger feature fits into a single week.

## Useful references

- [Pydantic model documentation](https://docs.pydantic.dev/latest/concepts/models/)
- [TypeScript ESLint quickstart](https://typescript-eslint.io/getting-started/)
- [GitHub Actions Python guide](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
