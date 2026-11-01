# Sprint 2: Contracts and Designs

**Dates:** Tuesday, November 3 to the Tuesday meeting on November 10, 2026.
**Lead:** Aryan (@rinnegannn).
**Capacity:** About three hours per person for the whole week, including the 20–30 minute meeting, setup, handoff, and review preparation.

The goal is to agree the data contracts, finish the first dashboard design handoff, and make existing scaffolds easier to validate. These are implementation decisions for the next small tasks, not a claim that the gateway, policy engine, detector, or approval API already exists.

The milestone dates in [PROJECT.md](../../PROJECT.md) remain the planning targets: a November progress checkpoint, optional December maintenance, the late-January local MVP, and a March release candidate by March 22 before the end-of-March showcase. The exact showcase dates are still unannounced. First policy and detector implementation remain Sprint 3 work; a database migration and broader integration follow later.

## Finish Sprint 1 first

The November 1 review found 8 of 12 Sprint 1 issues complete. The Lead's kickoff decision issue #36 is already complete. Four student issues still need work:

| Issue | Owner | Remaining deliverable |
| --- | --- | --- |
| #30 | Sana | Correct the five threat cases using the posted scope review. |
| #32 | Pranoy | Correct the four benchmark examples using the posted contract/policy review. |
| #33 | Nelavan | Submit the PostgreSQL Compose PR and its observed health result. |
| #34 | Trisha | Submit the security/secrets guide PR. Repository assignment is now active. |

These remain Sprint 1 issues until its November 3 review. New follow-ups for these owners are conditional, rather than extra full commitments. If a current task takes the next week's available time, finish it and leave the follow-up in Backlog. Replan any carryover at the November 3 meeting; do not mark it complete or duplicate it simply to close the sprint.

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

An optional `trigger_source` contains `type`, `content`, and `trust_level`. For the initial models, these have defaults `unknown`, an empty string, and `unknown`. Supported `type` values are `user_instruction`, `untrusted_email_body`, `untrusted_webpage`, `untrusted_document`, `tool_result`, and `unknown`; `trust_level` values are `trusted`, `untrusted`, and `unknown`.

Provenance is context for analysis. A caller setting `trust_level` to `trusted` must never bypass configured permissions, validation, policy, or security findings. This sprint does not implement an authentication system. Benchmark `context.permitted_tools` is test setup, not a permission grant supplied by a production caller.

`EmailSendArguments` has exactly three required, non-empty string fields: `recipient`, `subject`, and `body`. Reject extra argument keys for this tool. Attachments, `cc`, real email delivery, and filesystem execution are outside this demo. Keep the request and email-argument models separate in Sprint 2; Sprint 3 will connect them to the gateway and add full recipient validation.

Use FastAPI's standard `422` validation response when the future API receives malformed request data. Do not design a custom error envelope in Sprint 2. An unsupported tool with an otherwise valid normalized request becomes a policy `block`; it does not require implementing that tool.

## Demo policy baseline

After request/argument validation, the future evaluator will use this order:

1. Block an unsupported tool or a configured permission failure. No caller-supplied field can grant permission.
2. Block an explicitly denied destination, including the example domain `example.net`.
3. Allow an internal recipient at `example.com` when no rejecting policy or security finding applies.
4. Require approval for other valid external recipients, including `example.org`.

Match the normalized recipient's exact domain, case-insensitively. Do not use substring matching. Invalid addresses must fail validation; the Sprint 3 implementation needs explicit tests for malformed addresses and misleading domain suffixes. Any later detector integration must preserve block precedence rather than converting a blocked action into allow.

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
| `arguments` | Object containing string `recipient`, `subject`, `body` |
| `decision` | `allow`, `block`, or `approval_required` |
| `reason` | Short human-readable explanation |
| `timestamp` | ISO 8601 UTC timestamp string, for example `2026-11-03T18:00:00Z` |
| `approval_status` | `not_required`, `pending`, `approved`, or `denied` |

For the three initial fixtures, use `not_required` for allow/block and `pending` for approval-required. `approved` and `denied` are vocabulary for later approval events; mocks do not implement persistence or safe execution.

The future `POST /api/v1/tool-calls` endpoint will return a decision summary for a valid evaluated request. A `200` decision response does not by itself mean an email was delivered. The route and other approval/activity endpoints are not implemented in these Sprint 2 contract tasks.

## Student assignments

Each contributor has one new follow-up matched to their workstream. Ready means defined for the November 3 meeting; it does not require starting before then. Conditional work stays in Backlog until the listed prerequisites are complete and there is time left in the week.

| Owner | Workstream | Issue | Focused work | Planning status |
| --- | --- | --- | --- | --- |
| Nozhin | Backend | #58: First tool-call data models | 1.5–2 hours | Ready; coordinate test setup with #59. |
| Sheraz | Backend | #59: Repeatable health test setup | 1–1.5 hours | Ready. |
| Billy | Backend | #60: Policy/API decision examples | 1–1.5 hours | Ready. |
| Naman | Full Stack / Frontend | #61: Frontend lint command | 1–1.5 hours | Ready. |
| Barzin | Full Stack / Frontend | #62: Dashboard design handoff | 1–1.5 hours | Ready; reuse accepted #29 sketches. |
| MD Tanzeem | Full Stack / Frontend | #63: Dashboard types and mocks | 1–1.5 hours | Ready; uses the published fields above. |
| Erfan | AI/ML & Security | #64: Six detector examples | 1–1.5 hours | Ready; fixture/specification only. |
| Sana | AI/ML & Security | #65: Repository threat-case table | 45–60 minutes | Conditional after corrected #30; budget both together. |
| Pranoy | AI/ML & Security | #66: Four gateway JSON scenarios | About 1 hour | Conditional after corrected #32; budget both together. |
| Nelavan | DevOps & Infrastructure | #67: Backend Actions checks | 45–60 minutes | Conditional after #33 and #59. |
| Trisha | DevOps & Infrastructure | #68: Frontend Actions checks | 45–60 minutes | Conditional after #34 and #61. |

The Lead's preparation task is #57. The Lead also reserves weekly time for reviews and blockers. Code and repository documentation changes use small PRs, `Closes #number`, and review from @rinnegannn. Ask for help after about 20 minutes stuck and update the issue before Tuesday's meeting. Research specifications and fixtures are inputs to later tests; they are not evidence of a working detector.

## Keep parallel work small

- Nozhin owns `backend/app/schemas.py` and schema tests; Sheraz owns development test setup and the health test. They should coordinate commands without editing each other's files.
- Naman owns lint configuration and package changes; MD Tanzeem owns shared types/mock data; Barzin owns the design document. These tasks do not require simultaneous changes to `App.tsx`.
- Erfan's fixtures describe detector flag/no-flag expectations. Pranoy's fixtures describe whole gateway decisions. They serve different tests and should remain separate.
- CI is added only after the matching commands and fixtures exist. Backend CI initially runs syntax/pytest checks; frontend CI runs lint/type/build. Do not create a pretend frontend test command. Keep new checks optional in branch protection until operational and passing reliably.
- No new cloud, Redis, model-training, or deployment work is required. The sprint succeeds when the contracts/designs and available validation foundations are reviewable, even if conditional follow-ups need replanning.

## Useful references

- [Pydantic model documentation](https://docs.pydantic.dev/latest/concepts/models/)
- [TypeScript ESLint quickstart](https://typescript-eslint.io/getting-started/)
- [GitHub Actions Python guide](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)
