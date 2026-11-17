# Sprint 3 checkpoint

Integration closeout verified November 16, 2026, against application commit
`695a3444f7fc7f9a13c0521d239daa41dccb54b2`, plus the redundant live-region
removal in this documentation/closeout change.
This is a dated snapshot, not a live board. Update this guide when the linked
integration tasks land. Sprint 3 runs November 10–17; Sprint 4 runs November 17–24.

## Run what exists today

Begin with [Start here](../getting-started.md), which links the component setup
instructions. Activate the backend virtual environment before Python commands.
No running database or API is needed for the tests or policy examples below.

| Working directory | Command | Observed result |
| --- | --- | --- |
| `backend/` | `python -m pytest -q` | 151 passed; one existing Starlette/httpx deprecation warning |
| Repository root | `python -m pytest evaluation/test_run_policy_cases.py -q` | 28 passed |
| Repository root | `python evaluation/run_policy_cases.py` | Eight policy cases passed; exit 0 |
| `frontend/` | `npm ci` | Lockfile install succeeded |
| `frontend/` | `npm run typecheck` | Passed |
| `frontend/` | `npm run build` | Passed |

Validation used Python 3.14.4 and Node.js 24.22.2. A real local uvicorn process
was started and stopped for this check: health returned200, all three decision
paths below returned200, and invalid email arguments returned422. Temporary React
integration checks exercised selection, immutable fixtures, approve/deny guards,
repeated callbacks, pending-filter synchronization, reset, and a single status
announcement region. These were component checks, not a new browser test suite.

PR #123 supplies author evidence of a healthy built backend container and CI
Compose validation. Docker startup could not be independently repeated in the
Lead's WSL environment; this limit remains explicit. Frontend lint is still
pending in #92, so there is no claimed lint pass or fully completed sprint.

## Three HTTP policy paths

Start the backend using [its setup guide](../../backend/README.md). From another
terminal, run this request (the backend normally listens on port8000):

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tool-calls \
  -H "Content-Type: application/json" \
  -d '{"request_id":"demo-allow","agent_id":"assistant_2","user_id":"demo-user","session_id":"demo-session","original_goal":"Send a fictional report","tool":"email.send","arguments":{"recipient":"teammate@example.com","subject":"Demo","body":"Fictional summary"}}'
```

Repeat with `blocked@example.net` and `partner@example.org` as the recipient
(and distinct request IDs). The independent verification used an isolated local
port18765; the route and payload are the same.

| Recipient | HTTP status | Decision | Approval status |
| --- | --- | --- | --- |
| `teammate@example.com` | 200 | `allow` | `not_required` |
| `blocked@example.net` | 200 | `block` | `not_required` |
| `partner@example.org` | 200 | `approval_required` | `pending` |
| Invalid address, such as `not-an-email` | 422 | Validation error | No summary |

This route evaluates policy only. It neither saves the decision nor calls the
detector, combiner, or simulated adapter. Reusing a request ID is not currently
rejected because persistence/idempotency has not been implemented.

## Three policy paths

From `backend/`, with the Python environment active:

```bash
python -c "from app.policy import evaluate_policy; recipients = ['teammate@example.com', 'blocked@example.net', 'partner@example.org']; print(*[(r, evaluate_policy('assistant_2', 'email.send', {'recipient': r, 'subject': 'Demo', 'body': 'Fictional showcase message.'})['decision']) for r in recipients], sep='\n')"
```

Observed output:

```text
('teammate@example.com', 'allow')
('blocked@example.net', 'block')
('partner@example.org', 'approval_required')
```

This invokes the pure policy function. It does not send mail, create an approval,
or save an audit record. `assistant_2` is a configured demo identity, not an
authenticated user. The policy's permission table remains server-owned.

The initial detector is a separate narrow heuristic. Policy-case agreement does
not measure detector accuracy or end-to-end attack prevention. An allowed
internal send can still originate from malicious instructions.

## Working, mocked, or missing

| Area | State on the verified commit | Next issue |
| --- | --- | --- |
| Request/response models, email validation | Implemented and tested | [#82](https://github.com/DSC-McMaster-U/agent-guard/issues/82) completed |
| HTTP decision endpoint | Implemented and verified for three policy paths plus invalid-data errors; policy only | [#83](https://github.com/DSC-McMaster-U/agent-guard/issues/83) completed |
| Policies and decision combiner | HTTP invokes policy; combiner is tested separately and not wired into HTTP | [#84](https://github.com/DSC-McMaster-U/agent-guard/issues/84) completed |
| Dashboard | Activity selection and local approve/deny state work; request metadata and review status displayed; refresh resets state | [#85](https://github.com/DSC-McMaster-U/agent-guard/issues/85), [#87](https://github.com/DSC-McMaster-U/agent-guard/issues/87) completed |
| Prompt-injection detector | Normalization implemented; all six regression scenarios run normally, including a documented missed paraphrase | [#88](https://github.com/DSC-McMaster-U/agent-guard/issues/88), [#89](https://github.com/DSC-McMaster-U/agent-guard/issues/89) completed |
| Policy evaluation | Eight scenarios; checker and 28 evaluation tests work | [#90](https://github.com/DSC-McMaster-U/agent-guard/issues/90) completed |
| Containers | Non-root backend and PostgreSQL services defined; both ports localhost-only; author startup evidence accepted, local Docker rerun unavailable | [#91](https://github.com/DSC-McMaster-U/agent-guard/issues/91) completed |
| CI | Backend tests/syntax/Compose config and frontend types/build run in Actions | [#92](https://github.com/DSC-McMaster-U/agent-guard/issues/92) adds lint |
| Evaluation CI | Evaluation tests run locally but are outside the backend CI discovery directory | [#110](https://github.com/DSC-McMaster-U/agent-guard/issues/110) |
| Simulated tool adapter | Tested allow-only in-process adapter; no network delivery or HTTP execution connection | [#104](https://github.com/DSC-McMaster-U/agent-guard/issues/104) completed early |
| Persistence and approval service | No application audit storage or stored approval API yet | Sprint 4 storage foundations below; approval integration follows |

The dashboard is interactive with fictional local data; it does not fetch the
HTTP endpoint yet. Approve/Deny changes local review status while preserving the
original policy decision. A single component status region announces changes;
the redundant App-wide live wrapper was removed in this closeout. These local
callbacks remain a preview until backend approval events are implemented and persisted.

## Next handoffs

Use the [project board](https://github.com/orgs/DSC-McMaster-U/projects/22) for
current ownership and progress. The full Sprint 4 assignment index is in
[#113](https://github.com/DSC-McMaster-U/agent-guard/issues/113).

- Storage: Nozhin [#102](https://github.com/DSC-McMaster-U/agent-guard/issues/102) publishes the migration/save/list contract; Sheraz [#103](https://github.com/DSC-McMaster-U/agent-guard/issues/103) adds HTTP persistence and history. Nelavan [#111](https://github.com/DSC-McMaster-U/agent-guard/issues/111) verifies the container connection.
- Dashboard: Naman [#105](https://github.com/DSC-McMaster-U/agent-guard/issues/105) provides the client; Barzin [#107](https://github.com/DSC-McMaster-U/agent-guard/issues/107) provides the form; Tanzeem [#106](https://github.com/DSC-McMaster-U/agent-guard/issues/106) integrates them. Trisha [#112](https://github.com/DSC-McMaster-U/agent-guard/issues/112) adds component tests after lint.
- Security: Sprint 3 #88/#89 feed Erfan's detector reporting [#108](https://github.com/DSC-McMaster-U/agent-guard/issues/108). Sana [#109](https://github.com/DSC-McMaster-U/agent-guard/issues/109) expands policy scenarios; Pranoy [#110](https://github.com/DSC-McMaster-U/agent-guard/issues/110) protects evaluation in CI.
- Simulated tool: Billy [#104](https://github.com/DSC-McMaster-U/agent-guard/issues/104) has completed the tested adapter; API execution wiring remains a later integration step.

The Lead review/guide deliverable in #93 is complete. #92 remains the independent
Sprint 3 lint task owned by Trisha; its completion is not implied by this closeout.
Sprint 4 should prioritize storage and the live dashboard/API connection.

Close prerequisites with verified evidence before claiming an end-to-end path.
Carryover and new work share each person's three-hour weekly budget, including
the meeting; agree a smaller deliverable if necessary.

## Showcase checkpoints

[PROJECT.md](../../PROJECT.md#project-timeline) remains the milestone source of truth.

- Late November: internal progress checkpoint; state what is integrated and mocked.
- December: reduced-capacity optional maintenance, with no required weekly sprints.
- Late January: local MVP target with allow/block/approval, initial detection,
  stored activity/approval events, and a simulated email flow. The January
  showcase day is unannounced; an early event uses the verified subset available.
- March 22: release-candidate target. Stabilize and rehearse for the end-of-March
  showcase; its exact day is also unannounced.

The guide documents current evidence, not a guarantee of milestone completion.
