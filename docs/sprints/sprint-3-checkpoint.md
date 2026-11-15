# Sprint 3 checkpoint

Verified November 15, 2026, against `f05a72723591f96354ef337f30bb1e27102ba415`.
This is a dated snapshot, not a live board. Update this guide when the linked
integration tasks land. Sprint 3 runs November 10–17; Sprint 4 runs November 17–24.

## Run what exists today

Begin with [Start here](../getting-started.md), which links the component setup
instructions. Activate the backend virtual environment before Python commands.
No running database or API is needed for the tests or policy examples below.

| Working directory | Command | Observed result |
| --- | --- | --- |
| `backend/` | `python -m pytest -q` | 101 passed; one existing Starlette/httpx deprecation warning |
| Repository root | `python -m pytest evaluation/test_run_policy_cases.py -q` | 28 passed |
| Repository root | `python evaluation/run_policy_cases.py` | Eight policy cases passed; exit 0 |
| `frontend/` | `npm ci` | Lockfile install succeeded |
| `frontend/` | `npm run typecheck` | Passed |
| `frontend/` | `npm run build` | Passed |

Validation used Python 3.14.4 and Node.js 24.22.2. Backend HTTP checks using
FastAPI TestClient returned `200 {"status":"ok"}` for `GET /health` and `404`
for `POST /api/v1/tool-calls`, because the latter route is not implemented yet.
Docker startup was not rerun for this checkpoint; a configured PostgreSQL service
does not establish application persistence.

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
| HTTP decision endpoint | Missing; only `/health` is exposed | [#83](https://github.com/DSC-McMaster-U/agent-guard/issues/83) |
| Policies and decision combiner | Tested Python functions; not wired into HTTP | [#84](https://github.com/DSC-McMaster-U/agent-guard/issues/84) completed |
| Dashboard | Activity/Approval components and typed fictional fixtures exist; `App.tsx` still renders placeholders | [#85](https://github.com/DSC-McMaster-U/agent-guard/issues/85) integration, [#87](https://github.com/DSC-McMaster-U/agent-guard/issues/87) details |
| Prompt-injection detector | Initial role-marker plus override-phrase check implemented; normalization and separate regressions pending | [#88](https://github.com/DSC-McMaster-U/agent-guard/issues/88), [#89](https://github.com/DSC-McMaster-U/agent-guard/issues/89) |
| Policy evaluation | Eight scenarios; checker and 28 evaluation tests work | [#90](https://github.com/DSC-McMaster-U/agent-guard/issues/90) completed |
| Containers | Compose defines PostgreSQL only; backend service not yet merged | [#91](https://github.com/DSC-McMaster-U/agent-guard/issues/91) |
| CI | Backend tests/syntax/Compose config and frontend types/build run in Actions | [#92](https://github.com/DSC-McMaster-U/agent-guard/issues/92) adds lint |
| Evaluation CI | Evaluation tests run locally but are outside the backend CI discovery directory | [#110](https://github.com/DSC-McMaster-U/agent-guard/issues/110) |
| Persistence, approval service, execution | No application audit storage, stored approvals, or email executor yet | Sprint 4 foundations below; approval/execution integration follows |

Passing the frontend build confirms compilability. It does not mean the dashboard
components are visible or connected. A local Approve callback will remain a
preview until a backend approval event is implemented and persisted.

## Next handoffs

Use the [project board](https://github.com/orgs/DSC-McMaster-U/projects/22) for
current ownership and progress. The full Sprint 4 assignment index is in
[#113](https://github.com/DSC-McMaster-U/agent-guard/issues/113).

- Storage: Nozhin [#102](https://github.com/DSC-McMaster-U/agent-guard/issues/102) publishes the migration/save/list contract; Sheraz [#103](https://github.com/DSC-McMaster-U/agent-guard/issues/103) adds HTTP persistence and history. Nelavan [#111](https://github.com/DSC-McMaster-U/agent-guard/issues/111) verifies the container connection.
- Dashboard: Naman [#105](https://github.com/DSC-McMaster-U/agent-guard/issues/105) provides the client; Barzin [#107](https://github.com/DSC-McMaster-U/agent-guard/issues/107) provides the form; Tanzeem [#106](https://github.com/DSC-McMaster-U/agent-guard/issues/106) integrates them. Trisha [#112](https://github.com/DSC-McMaster-U/agent-guard/issues/112) adds component tests after lint.
- Security: Sprint 3 #88/#89 feed Erfan's detector reporting [#108](https://github.com/DSC-McMaster-U/agent-guard/issues/108). Sana [#109](https://github.com/DSC-McMaster-U/agent-guard/issues/109) expands policy scenarios; Pranoy [#110](https://github.com/DSC-McMaster-U/agent-guard/issues/110) protects evaluation in CI.
- Simulated tool: Billy [#104](https://github.com/DSC-McMaster-U/agent-guard/issues/104) builds the tested adapter; API execution wiring remains a later integration step.

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
