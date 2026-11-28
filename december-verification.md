# December showcase verification

Use this checklist on the commit we intend to demo. Aryan runs the browser walkthrough and chooses what to present. Codex runs the automated checks, reproduces failures, and links fixes to the [December tasks](tasks.md). Use a fresh copy of this checklist for each rehearsal.

**Run date** __________  **Commit** __________  **Tester / machine** __________

Tick a box only after observing the expected result on this commit. Record failed, blocked, or skipped checks in the findings table. After a fix, record the new commit and rerun the affected checks.

## 1. Start with a clean setup

- [ ] Follow the [local backend setup](README.md#local-backend) on a clean checkout with a disposable database. Apply the documented migration. Verify that Compose shows healthy backend and database services and that `GET /health` returns `{"status":"ok"}`.
- [ ] Open the dashboard using the [frontend setup](frontend/README.md#setup). With a fresh demo database, refresh activity. An empty list should load successfully. Record the startup commands that worked so a second teammate can repeat them.

## 2. Walk through the demo in a browser

Use each preset with the provided fictional message. First select the preset and verify that it only fills the form. Then submit it. Check the decision and its reason in the dashboard and record the saved ID.

| Checked | Preset and recipient | Expected decision | Saved request ID |
| --- | --- | --- | --- |
| ☐ | Internal · `teammate@example.com` | Allowed | |
| ☐ | Denied · `blocked@example.net` | Blocked | |
| ☐ | External · `partner@example.org` | Approval required, pending | |

- [ ] Use the keyboard to submit once. A second press while the request is pending must leave one activity row. Try an invalid recipient and confirm that no row is added.
- [ ] Refresh the page and restart the backend. Match all three saved IDs and decisions to the table. In the pending filter, only the external request from this walkthrough should appear.
- [ ] With the three rows visible, stop the **disposable** database and refresh activity. The dashboard should explain the failure and retain the rows. Restart the database and refresh again. The same IDs should return without duplicates. Save browser evidence with [the walkthrough issue](https://github.com/DSC-McMaster-U/agent-guard/issues/134).

## 3. Check server-backed approval and simulated execution

Run these after the review API and outbox are connected. If the tested build only previews reviews locally, record that limit and use section 2 for the live demo.

- [ ] Submit two new external requests. Approve one and deny the other in the dashboard. Reload and restart the backend. Verify the two decisions and one saved review event per ID. A failed review write must leave the request pending.
- [ ] Attempt a repeated review and two conflicting reviews of the same pending request. Verify that at most one transition is accepted and that the saved status agrees with its review event.
- [ ] Inspect the simulated outbox by request ID. Expect one entry for an allowed or approved request and zero for blocked, pending, or denied requests. Retry the successful operation and verify the count stays at one.

## 4. Run the automated checks

Record the test totals, skips, and CI link for this commit.

- [ ] From `frontend/`, run `npm ci`, `npm run lint`, `npm run typecheck`, `npm test`, and `npm run build`. Each command must succeed.
- [ ] From `backend/`, run `python -m pytest -q -rs` with `TEST_DATABASE_URL` set to a disposable PostgreSQL database whose name ends in `_test`. Confirm the storage tests ran. Check duplicate request ID (409), invalid email arguments (422), database unavailable (503), and successful history retrieval after recovery.
- [ ] From the repository root in the backend Python environment, run `python -m pytest evaluation/`, `python evaluation/run_policy_cases.py`, and `python evaluation/run_detector_cases.py`. Record policy cases passed/total and the detector’s true positives, false positives, true negatives, and false negatives, including documented misses. [Evaluation guide](evaluation/README.md)
- [ ] Match the commit to its [GitHub Actions runs](https://github.com/DSC-McMaster-U/agent-guard/actions). Check repository integrity, backend, frontend, and evaluation results. Confirm the setup guide matches the startup steps actually used.

## 5. Record findings and choose the demo

| Check | Result and evidence (request IDs, screenshot, test output or CI link) | Issue / owner | Retest commit and result |
| --- | --- | --- | --- |
| Browser walkthrough and recovery | | | |
| Saved approvals and outbox | | | |
| Automated checks and benchmark counts | | | |

- [ ] **Codex** links a reproducible issue or existing fix for each failure and records which checks passed on retest.
- [ ] **Aryan** has a second teammate repeat the chosen walkthrough from a fresh setup. Record the demo commit, the paths they reproduced, and any limitations in [the showcase handoff](https://github.com/DSC-McMaster-U/agent-guard/issues/141). Use the January 5 handoff to schedule a final rehearsal before January 18.
