# Contributing to AgentGuard

Thank you for contributing to AgentGuard. This guide describes how our team plans work, writes code, and reviews changes.

## Before You Start

- Join the project Discord channel for announcements and questions.
- Read the [README](README.md) for an overview and [project plan](PROJECT.md) for the architecture and scope.
- Open the [AgentGuard Development project](https://github.com/orgs/DSC-McMaster-U/projects/22) and find an issue in **Ready**.
- Assign yourself to the issue, or ask the Project Lead to assign it to you.
- Ask questions early if the task or acceptance criteria are unclear.

## Standard Contribution Workflow

1. Find an issue on the GitHub Project board.
2. Assign yourself or request assignment.
3. Move the issue to **In Progress**.
4. Update your local `main` branch and create a feature branch from it.
5. Implement the required changes.
6. Run the relevant tests and checks.
7. Commit your work and push the branch.
8. Open a pull request into `main`.
9. Link the pull request to its issue with a closing keyword such as `Closes #12`.
10. Request a review from the Project Lead.
11. Address requested changes and resolve review conversations.
12. Squash merge after approval and after all required checks pass.
13. Confirm the linked issue is closed and appears in **Done**.

Do not commit directly to `main`. All changes should go through a pull request.

## Branch Names

Use this format:

```text
type/issue-number-short-description
```

Examples:

```text
feature/12-agent-gateway
feature/18-approval-dashboard
fix/24-policy-validation
docs/31-contributing-guide
```

Common types are `feature`, `fix`, `docs`, `test`, and `chore`. Use lowercase words separated by hyphens and include the GitHub issue number.

## Pull Requests

- Keep each pull request focused on one issue and reasonably small.
- Write a clear summary of what changed and why.
- Add or update tests where applicable.
- Include screenshots for visual UI changes.
- Add `Closes #ISSUE_NUMBER` to the pull request description so GitHub closes the issue when the pull request is merged.
- Update documentation when behaviour, setup, or contributor workflows change.
- The Project Lead is the sole required reviewer for contributor pull requests.
- Pull requests authored by the Project Lead may be merged by the Project Lead after all required checks pass.
- Respond respectfully and constructively to code review feedback.

## Development Expectations

- Never commit API keys, passwords, access tokens, private keys, or other secrets.
- Run the relevant checks before requesting review.
- Keep your assigned GitHub issues updated, including status and blockers.
- Ask in the project Discord channel when you are blocked.
- Discuss technical questions and review feedback respectfully.
- Coordinate changes that affect another workstream before implementation.

## Project Board and Sprints

AgentGuard uses one-week sprints and these board statuses:

- **Backlog:** Ideas and tasks that have not been prioritized.
- **Ready:** Defined tasks that contributors may begin.
- **In Progress:** Assigned work that is actively being developed.
- **In Review:** Work with an open pull request awaiting review.
- **Done:** Completed work, normally with a merged pull request.

New issues begin in **Backlog**. The Project Lead moves sufficiently defined and approved issues to **Ready** during planning. Most sprint tasks should fit within one to three hours; larger work should be divided into smaller issues or sub-issues. The initial broad starter issues are parent tasks and should be split this way before assignment to a weekly sprint. Contributors should update issue status and leave a short progress note before each weekly meeting.

Some research and design issues specify an issue comment or linked design as their deliverable. Post that evidence on the issue; the Project Lead checks the acceptance criteria and closes it. Code and repository documentation changes still use pull requests.

## Weekly Team Meeting

The team meets weekly for approximately 20–30 minutes. The meeting closes the current sprint and plans the next one:

1. **Progress updates (8 minutes):** Each workstream shares completed and ongoing work.
2. **Blockers (7 minutes):** Discuss technical issues and dependencies.
3. **Task planning (7 minutes):** Review the Kanban board and upcoming work.
4. **Announcements and Q&A (3 minutes).**

Discord is the primary communication channel. GitHub Issues remain the source of truth for task scope, ownership, and progress.

## Continuous Integration

The current repository contains project documentation, so CI performs repository integrity checks on pull requests and pushes to `main`. As implementation is added, CI should be expanded only when the matching dependency manifest and configuration exist:

- Python: Ruff, Pytest, and import or syntax checks.
- React and TypeScript: TypeScript type checking, ESLint, tests, and a production build.
- Docker: image build validation for committed Dockerfiles.

New checks must pass reliably before they become required branch protection checks.
