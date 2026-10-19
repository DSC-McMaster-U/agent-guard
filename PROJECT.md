# AgentGuard Open Source Project Plan

## Table of Contents

- [Project Description](#project-description)
- [Objectives](#objectives)
- [Stakeholders](#stakeholders)
- [Scope](#scope)
- [System Workflow](#system-workflow)
- [Implementation Plan](#implementation-plan)
- [Project Timeline](#project-timeline)
- [Technical Architecture](#technical-architecture)
- [Security Model](#security-model)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [MCP and Tool Integration Design](#mcp-and-tool-integration-design)
- [API Design](#api-design)
- [Testing and Evaluation](#testing-and-evaluation)
- [CI/CD and Hosting](#cicd-and-hosting)
- [Team Management](#team-management)
- [Roles and Responsibilities](#roles-and-responsibilities)
- [Communication](#communication)
- [Definition of Done](#definition-of-done)
- [Sprint Planning](#sprint-planning)

---

## Project Description

AgentGuard is an open-source runtime authorization and security gateway for AI agents that interact with external tools and services.

AI agents are increasingly being connected to email services, databases, file systems, browsers, code execution environments, APIs, and Model Context Protocol servers. These integrations make agents more capable, but they also introduce risks such as unauthorized actions, excessive permissions, indirect prompt injection, sensitive-data exposure, unsafe tool parameters, and credential misuse.

AgentGuard will sit between an AI agent and the tools it attempts to call. Every proposed tool action will be intercepted before execution and evaluated using deterministic authorization policies, argument validation, security analysis, scoped credentials, and optional human approval.

The system will be capable of allowing, blocking, restricting, rewriting, sandboxing, rate-limiting, or pausing an action for approval.

AgentGuard will also include an open security benchmark so that its protection can be measured using repeatable benign and adversarial scenarios rather than relying only on qualitative claims.

The benchmark is a central part of AgentGuard's strategy, not only a testing utility. Runtime security gateways for AI agents and MCP tools are becoming an increasingly competitive product category. AgentGuard will differentiate itself by publishing transparent scenarios, expected decisions, evaluation metrics, and reproducible results that allow contributors and users to verify how effectively the system blocks malicious actions while preserving legitimate agent tasks.

### Objectives

1. Build an open-source runtime security gateway for AI agent tool calls.
2. Prevent AI agents from directly accessing protected tools and credentials.
3. Enforce deterministic policies before high-impact actions execute.
4. Detect prompt injection, sensitive-data exposure, goal misalignment, and suspicious behaviour.
5. Require human approval for high-risk or irreversible actions.
6. Provide secure MCP and external tool integration through a restricted executor.
7. Use scoped credentials and short-lived access tokens wherever possible.
8. Record complete audit trails for actions, decisions, approvals, and tool results.
9. Create an open benchmark for measuring security and usability.
10. Give contributors experience with AI security, distributed systems, cloud infrastructure, frontend development, and open-source collaboration.

### Stakeholders

- AI application developers
- Agent framework developers
- Security-conscious development teams
- Organizations experimenting with MCP integrations
- Developers building internal AI assistants
- Open-source maintainers
- Student contributors
- GDG McMaster members
- Security researchers

---

## Scope

### Fall Showcase MVP

The fall MVP is a focused end-to-end demonstration targeted for the final week of November. It will support:

- A small FastAPI Agent Gateway
- One normalized tool-call request schema with agent and user metadata
- Deterministic allow, block, and approval-required policies
- Basic tool argument validation
- One initial prompt-injection or sensitive-data detector with structured findings
- A synchronous Decision Engine that combines policy and security findings
- A basic Human Approval API and React approval interface
- PostgreSQL storage for requests, decisions, and approval events
- One simulated or sandboxed demonstration tool
- An activity view showing recent requests and decisions
- Ten to twenty benign and adversarial benchmark scenarios
- Docker Compose-based local development
- GitHub Actions checks for the components that exist

The showcase should demonstrate a safe request, a blocked request, and an approval-required request. A reliable local demonstration is required; public cloud deployment is optional for the showcase.

### Initial Tool Integrations

The first version should support one or two integrations:

- A simulated email or sandboxed file-system tool for the fall showcase
- One generic API or MCP integration for the March release

The team should prioritize depth and security over the total number of connectors.

### Committed March v0.1 Scope

The release targeted for the end of March commits to a stable and documented version of the core showcase system:

- A modular FastAPI backend containing the gateway, policies, decisions, approvals, and audit APIs
- A normalized tool-call schema with clear validation errors
- Deterministic allow, block, and approval-required policies
- Documented prompt-injection and sensitive-data checks with structured findings
- A React approval, activity, and basic trace dashboard
- PostgreSQL storage for requests, findings, decisions, and approval events
- A Restricted Tool Executor for one simulated or sandboxed tool
- Execution limits, timeouts, and basic result sanitization
- Twenty to thirty benign and adversarial benchmark scenarios
- Docker Compose-based local development
- Reliable linting, tests, and build checks in GitHub Actions
- Contributor, architecture, security, and local deployment documentation
- A versioned `v0.1` open-source release

These items define release completion. Optional infrastructure must not delay the release.

### Target Enhancements

The team may add the following features when the committed scope is stable and capacity remains:

- Redis-backed asynchronous security analysis and a Risk Orchestrator
- One real API or basic MCP integration
- Scoped application credentials for the supported integration
- Basic OpenTelemetry traces and service health metrics
- A repeatable hosted demonstration environment
- Expansion to thirty to fifty benchmark scenarios

### Stretch Goals

The following features should be attempted only after the committed scope and target enhancements are stable:

- Complete OAuth-based authorization
- Google Secret Manager integration
- Production-grade GKE hardening
- Full Prometheus and Grafana dashboards
- Sequence-based behaviour anomaly detection
- Memory-poisoning protection beyond benchmark scenarios
- Multi-agent trace support
- Organization-level policy management
- Extensive external beta testing
- More than two production-quality tool integrations

### Out of Scope for the MVP

The MVP will not attempt to provide:

- A guarantee against every possible AI-agent attack
- Support for every agent framework
- Support for every MCP transport
- Fully autonomous policy generation
- Production-grade multi-tenant billing
- Universal malware detection
- Unrestricted shell execution
- A replacement for traditional identity and access management systems

---

## System Workflow

The committed AgentGuard workflow will follow these steps:

```text
User Request
    |
    v
AI Agent
    |
    v
Proposed Tool Call
    |
    v
Agent Gateway
    |
    v
Policy Engine
    |
    v
Prompt-Injection and
Sensitive-Data Checks
    |
    v
Decision Engine
    |
    +-------------------------+
    |                         |
    v                         v
Allowed Action          Approval Required
    |                         |
    v                         v
Restricted Tool         Approval Service
Executor                      |
    |                         v
    |                  Dashboard and Reviewer
    |                         |
    +------------+------------+
                 |
                 v
        Simulated or Sandboxed Tool
                 |
                 v
          Sanitized Tool Result
                 |
                 v
            Agent Gateway
                 |
                 v
               Agent
```

Target enhancements may insert a Redis-backed Risk Orchestrator and replace the simulated tool with one real API or basic MCP integration.

The system will use deterministic authorization before relying on AI-based security analysis.

For example:

- If the requested tool is not permitted for the current agent, block the action.
- If a tool argument violates an explicit rule, block or rewrite the action.
- If the action sends sensitive information externally, require approval.
- If a tool call does not match the user’s original request, increase the risk score or block it.
- If a tool result contains suspicious embedded instructions, prevent the agent from following them automatically.
- If a tool integration is unsupported, return a clear error rather than allowing the model to guess.

---

## Implementation Plan

## Project Timeline

The active development period runs from late October through the end of March. The schedule assumes approximately 12 students contributing about three hours of total project time per week, including one short team meeting, with reduced availability during exams and holidays. AI-assisted development may speed up scaffolding and routine tasks, but the schedule still reserves time for learning, review, testing, and integration.

### Milestone 1: Foundations and Onboarding

**Target:** Late October

- Introduce contributors to Git, GitHub, pull requests, and open-source workflows.
- Finalize the threat model and architecture.
- Set up the `agent-guard` repository.
- Configure GitHub Projects and contribution guidelines.
- Create the initial backend, frontend, and local development structure.
- Define the normalized tool-call schema.
- Define shared Pydantic models.
- Create initial dashboard wireframes.
- Create the first benign and adversarial test scenarios.

### Milestone 2: Showcase Foundations

**Target:** Late October to early November

- Build the FastAPI Agent Gateway.
- Add agent and user metadata to requests.
- Validate tool names and arguments.
- Implement allow, block, and approval policies.
- Add a small set of tool-specific parameter restrictions.
- Store requests and decisions in PostgreSQL.
- Create one simulated or sandboxed demonstration tool.
- Add unit tests for policy evaluation.

### Milestone 3: Showcase Security and Approval Flow

**Target:** Early to mid-November

- Implement one initial prompt-injection or sensitive-data detector.
- Add structured risk findings.
- Build a synchronous Decision Engine.
- Build the initial approval API and React approval interface.
- Add activity and decision views.
- Create the first ten to twenty benchmark scenarios.

### Milestone 4: Fall Showcase Integration and Stabilization

**Target:** Mid to late November

- Connect the gateway, policy engine, detector, decision flow, approval interface, and audit storage.
- Complete one reliable simulated or sandboxed tool integration.
- Run the application locally with Docker Compose.
- Add component tests and a small end-to-end test path.
- Fix integration issues and document known limitations.
- Demonstrate safe, malicious, and approval-required workflows.
- Freeze showcase features during the final week and rehearse the demonstration.

### Milestone 5: Core Product Hardening

**Target:** January to February

- Harden request validation, policies, and decision explanations.
- Complete documented prompt-injection and sensitive-data checks.
- Build the Restricted Tool Executor for one simulated or sandboxed tool.
- Add execution limits, timeouts, and basic result sanitization.
- Improve the approval, activity, and basic trace interfaces.
- Expand unit, integration, failure-path, and security tests.
- Improve Docker Compose, CI, and contributor documentation.
- Attempt Redis, a real integration, and telemetry only after the committed work is stable.

### Milestone 6: Evaluation and v0.1 Release

**Target:** March

- Complete twenty to thirty benchmark scenarios.
- Measure attack success and benign completion rates.
- Improve false-positive and false-negative performance.
- Stabilize the Docker Compose demonstration and release process.
- Complete end-to-end, failure-path, and security testing.
- Finalize documentation and onboarding.
- Publish a versioned `v0.1` open-source release.
- Prepare the final project demonstration.

Redis orchestration, a real API or MCP integration, telemetry, and hosted deployment are capacity-dependent target enhancements. Advanced anomaly detection, complete OAuth support, production GKE hardening, multi-agent tracing, and extensive external testing remain stretch goals.

---

## Technical Architecture

AgentGuard will use clear modular boundaries. The committed `v0.1` may keep gateway, policy, detection, decision, approval, and execution modules inside one FastAPI deployment. Redis workers and separate cloud services are capacity-dependent enhancements rather than release requirements.

The following reference flow shows how the modules can evolve when asynchronous analysis is added:

```text
AI Agent Client
      |
      v
Agent Gateway
      |
      v
Policy Engine
      |
      v
Risk Orchestrator
      |
      v
Redis Queue
      |
      v
Security Analysis Workers
      |
      v
Decision Engine
      |
      +----------------------+
      |                      |
      v                      v
Approval Service      Restricted Tool Executor
      |                      |
      v                      v
Dashboard             MCP Servers and Tool APIs
      |
      v
Human Reviewer
```

The architecture diagram will be stored at:

```text
images/architecture.png
```

### Main Services

#### Dashboard Frontend

The dashboard will provide:

- Pending approval requests
- Proposed tool names and arguments
- Triggering source information
- Detected sensitive data
- Policy findings
- Risk findings
- Approve and deny controls
- Session timelines
- Tool-call graphs
- Audit history
- Basic system metrics

#### Agent Gateway

The Agent Gateway will manage:

- Agent authentication
- Tool-call interception
- Request validation
- Schema normalization
- Trace identifiers
- Session context
- Rate limiting
- Response sanitization
- Communication between agents and AgentGuard

The Agent Gateway will be the only supported entry point for protected tool calls.

#### Policy Engine

The Policy Engine will evaluate deterministic rules based on:

- User identity
- Agent identity
- Session identity
- Original user task
- Requested tool
- Tool arguments
- Destination
- Data classification
- Session budget
- Organization policy

Committed decisions include:

- Allow
- Block
- Require approval

Future target or stretch decisions may include:

- Rewrite
- Restrict
- Sandbox
- Rate limit

#### Risk Orchestrator (Target Enhancement)

If implemented, the Risk Orchestrator will:

- Create security-analysis jobs
- Publish jobs to Redis
- Track worker completion
- Aggregate worker findings
- Handle worker timeouts and failures
- Normalize risk evidence
- Forward findings to the Decision Engine

#### Security Analysis Workers

The committed MVP includes prompt-injection and sensitive-data checks, which may run as modules inside the FastAPI application. Moving them into dedicated workers is a target enhancement. Goal-alignment and behaviour-anomaly workers are stretch goals.

##### Prompt Injection Worker

- Inspect untrusted text that influenced the action.
- Detect instruction override attempts.
- Detect requests for hidden actions.
- Detect cross-tool manipulation.
- Detect attempted secret extraction.
- Return structured evidence and confidence.

##### Sensitive Data Worker

- Detect credentials and secrets.
- Detect personal information.
- Detect financial or confidential data.
- Inspect attachments or tool payloads where supported.
- Recommend blocking, approval, or redaction.

##### Goal Alignment Worker

This worker is a stretch goal.

- Compare the proposed action with the original user request.
- Detect actions outside the authorized task scope.
- Identify unrelated tool usage.
- Produce a structured alignment score and explanation.

##### Behaviour Anomaly Worker

This worker is a stretch goal.

- Detect repeated blocked actions.
- Detect unusual tool sequences.
- Detect sudden escalation from read to write operations.
- Detect suspicious external destinations.
- Detect abnormal session behaviour.

This worker may begin with rules and expand to statistical or ML-based methods after the committed release is stable.

#### Decision Engine

The Decision Engine will combine:

- Deterministic policy results
- Security-worker findings
- Data sensitivity
- Requested action impact
- Destination trust
- Session history
- Human-approval requirements

It will produce one final decision for each action.

#### Approval Service

The Approval Service will:

- Create approval requests.
- Display the proposed action and relevant evidence.
- Record reviewer decisions.
- Prevent parameter changes after approval.
- Expire old approvals.
- Forward approved actions to the Restricted Tool Executor.
- Store approval events in PostgreSQL.

#### Restricted Tool Executor

The Restricted Tool Executor will:

- Receive only approved or allowed actions.
- Use synthetic or local credentials for the committed simulated tool.
- Retrieve scoped credentials and call external MCP servers or APIs only for implemented target enhancements.
- Enforce timeouts and execution limits.
- Sanitize tool responses.
- Record execution outcomes.
- Return results through the Agent Gateway.

The AI agent will not receive direct access to external credentials.

#### Persistence Layer

PostgreSQL will store:

- Users
- Agents
- Sessions
- Policies
- Tool-call requests
- Risk findings
- Decisions
- Approval requests
- Approval outcomes
- Execution results
- Audit events
- Benchmark results

If the Redis target enhancement is implemented, Redis will store:

- Security-analysis jobs
- Temporary worker state
- Short-lived approval state where appropriate
- Rate-limit counters
- Session coordination data

#### Credential Layer

If the Google Secret Manager stretch goal is implemented, it will store:

- OAuth client secrets
- API credentials
- Tool integration secrets
- Service credentials

Short-lived access tokens should be issued or retrieved at execution time and should not be exposed to the AI model.

#### Observability Layer

The committed release will use structured application logs. Target and stretch work may add:

- OpenTelemetry for distributed traces
- Prometheus for metrics
- Grafana for dashboards
- Google Cloud Monitoring for infrastructure visibility
- Additional security-event aggregation and alerting

---

## Security Model

AgentGuard will follow a layered security model.

### Core Principles

- Deny by default
- Least privilege
- Explicit authorization
- No direct agent access to credentials
- No direct agent access to protected tools
- Human approval for high-impact actions
- Independent tool argument validation
- Complete auditability
- Clear failure behaviour
- Minimal storage of sensitive data

### Effective Permission Model

The effective permission for an action will be the intersection of:

```text
User Permissions
∩ Agent Permissions
∩ Task Permissions
∩ Tool Policy
∩ Argument Policy
```

An action will be denied if any required authorization layer rejects it.

### Trust Levels

Potential trust levels include:

- User-provided instruction
- System policy
- Agent-generated plan
- Trusted tool result
- Untrusted email
- Untrusted webpage
- Untrusted uploaded document
- Another agent
- Persistent memory

Security workers should consider the source that influenced each action.

### Threat Scenarios

The project benchmark should include:

- Indirect prompt injection from an email
- Malicious instructions inside a webpage
- Tool-response poisoning
- Sensitive attachment exfiltration
- Unauthorized file access
- Unauthorized email sending
- Dangerous shell arguments
- Repeated attempts after a block
- Credential extraction attempts
- Unrelated cross-tool actions
- Benign actions that should complete normally

---

## Tech Stack

### Frontend

- React
- TypeScript
- React Flow
- Tailwind CSS
- WebSockets or Server-Sent Events

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic

### Security Analysis

- Presidio or custom PII detection
- Secret-scanning rules
- Deterministic security rules
- Small language model for semantic classification where useful
- Structured output schemas

### Queue and Database

- PostgreSQL (committed)
- Redis (target enhancement)

### Cloud and Infrastructure

- Docker and Docker Compose (committed)
- A simple hosted demonstration environment (target enhancement)
- Google Kubernetes Engine (stretch)
- Google Artifact Registry (stretch)
- Google Secret Manager (stretch)
- Google Cloud Monitoring (stretch)
- Kubernetes (stretch)

### Observability

- Structured logging (committed)
- Basic OpenTelemetry traces and service health metrics (target enhancement)
- Prometheus (stretch)
- Grafana (stretch)

### Development and Collaboration

- GitHub
- GitHub Projects
- GitHub Actions
- Discord
- Google Meet

---

## Project Structure

```text
agent-guard/
├── apps/
│   ├── dashboard/
│   └── sample-agent/
│
├── services/
│   ├── agent-gateway/
│   ├── policy-engine/
│   ├── risk-orchestrator/
│   ├── security-workers/
│   │   ├── prompt-injection/
│   │   ├── sensitive-data/
│   │   ├── goal-alignment/
│   │   └── behaviour-anomaly/
│   ├── decision-engine/
│   ├── approval-service/
│   └── tool-executor/
│
├── packages/
│   ├── shared-schemas/
│   ├── python-sdk/
│   ├── policy-language/
│   └── telemetry/
│
├── integrations/
│   ├── mcp/
│   ├── email/
│   ├── filesystem/
│   └── http/
│
├── evaluation/
│   ├── benign-scenarios/
│   ├── adversarial-scenarios/
│   ├── expected-decisions/
│   └── metrics/
│
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   ├── github-actions/
│   └── monitoring/
│
├── docs/
│   ├── architecture/
│   ├── onboarding/
│   ├── policies/
│   └── security/
│
├── images/
│   ├── logo.png
│   └── architecture.png
│
├── README.md
├── PROJECT.md
├── CONTRIBUTING.md
├── SECURITY.md
└── docker-compose.yml
```

---

## MCP and Tool Integration Design

AgentGuard should treat every MCP server and external API as a potentially sensitive integration.

### Integration Requirements

Each integration should define:

- Tool name
- Tool description
- Input schema
- Output schema
- Required permissions
- Risk level
- Allowed destinations
- Argument restrictions
- Timeout
- Credential scope
- Whether approval is required
- Response sanitization rules

### Example Tool Definition

```json
{
  "tool": "email.send",
  "risk_level": "high",
  "required_permissions": ["email.write"],
  "requires_approval": true,
  "argument_rules": {
    "recipient": {
      "type": "email",
      "required": true
    },
    "attachments": {
      "max_items": 3,
      "scan_for_sensitive_data": true
    }
  }
}
```

### Example Normalized Tool Call

```json
{
  "request_id": "req_123",
  "agent_id": "assistant_1",
  "user_id": "user_42",
  "session_id": "session_8",
  "original_goal": "Send the approved report to the project lead",
  "tool": "email.send",
  "arguments": {
    "recipient": "lead@example.com",
    "subject": "Approved Report"
  },
  "trigger_source": {
    "type": "user_instruction",
    "trust_level": "trusted"
  }
}
```

### Adapter Pattern

Tool integrations should follow a shared interface:

```text
ToolAdapter
├── MCPAdapter
├── EmailAdapter
├── FileSystemAdapter
├── HTTPAdapter
└── DatabaseAdapter
```

Unsupported tools should be rejected clearly rather than executed through generic model reasoning.

---

## API Design

### Example Endpoints

```text
POST /api/v1/tool-calls
GET  /api/v1/tool-calls/{request_id}
GET  /api/v1/sessions/{session_id}
GET  /api/v1/sessions/{session_id}/trace
GET  /api/v1/approvals
GET  /api/v1/approvals/{approval_id}
POST /api/v1/approvals/{approval_id}/approve
POST /api/v1/approvals/{approval_id}/deny
GET  /api/v1/policies
POST /api/v1/policies
PUT  /api/v1/policies/{policy_id}
POST /api/v1/evaluations/run
GET  /api/v1/evaluations/{evaluation_id}
```

### Documentation

- OpenAPI
- Swagger UI
- Example SDK usage
- Postman collection where useful
- Policy examples
- Integration examples

---

## Testing and Evaluation

AgentGuard requires both standard software testing and adversarial security evaluation.

### Unit Testing

- Request schema validation
- Policy evaluation
- Argument rules
- Risk aggregation
- Decision logic
- Approval expiration
- Credential access controls
- Tool adapters
- Redaction logic
- Benchmark metric calculations

Potential frameworks:

- Pytest
- Vitest
- Playwright

### Integration Testing

- Agent Gateway to Policy Engine
- Security checks to Decision Engine
- Decision Engine to Approval Service
- Approval Service to Tool Executor
- Tool Executor to the simulated or sandboxed tool
- Audit events to PostgreSQL
- Dashboard requests, approvals, activity, and error states

Conditional integration tests should be added with target or stretch features:

- Risk Orchestrator to Redis and security workers
- Tool Executor to MCP or an external API
- Secret Manager access from Tool Executor
- Hosted dashboard live updates

### Evaluation Dataset

The team will create scenarios such as:

- Safe read-only tool call
- Safe email draft creation
- Explicitly approved email sending
- Malicious email requesting file exfiltration
- Website instructing the agent to reveal credentials
- Uploaded document requesting a shell command
- External tool result attempting to change the user’s goal
- Sensitive attachment sent to an unknown destination
- Repeated blocked calls
- Legitimate high-risk action requiring approval
- Benign action that should not be blocked

### Evaluation Metrics

- Attack success rate
- Benign task completion rate
- False-positive rate
- False-negative rate
- Sensitive-data leakage rate
- Unauthorized tool-call rate
- Approval bypass rate
- Decision latency
- Worker latency
- Tool-call success rate
- Policy evaluation accuracy
- Reviewer decision time

### Initial Benchmark Goal

An initial internal target may be:

- Block at least 90% of defined attack scenarios
- Preserve at least 85% completion on benign scenarios
- Keep decision latency low enough for interactive use

These numbers are project goals and should not be presented as production security guarantees.

---

## CI/CD and Hosting

### CI/CD

GitHub Actions will be used for:

- Formatting
- Linting
- Unit tests
- Integration tests
- Applicable security checks
- Docker image builds when Dockerfiles are available
- Optional deployment to one demonstration environment after the application is stable

Artifact publishing, Kubernetes validation, and automated production deployment are stretch goals.

### Hosting

- **Committed environment:** Docker Compose running the frontend, backend, and PostgreSQL locally
- **Target hosting:** One suitable static or container-based demonstration environment
- **Target queue:** Redis
- **Target secrets:** Environment or platform-managed secrets for one supported integration
- **Target monitoring:** Basic health checks, structured logs, metrics, and OpenTelemetry traces

The fall showcase must run reliably through Docker Compose and does not require cloud deployment. GKE, Google Artifact Registry, Google Secret Manager, Prometheus, and Grafana may be added later as stretch goals.

---

## Team Management

## Team Members

The project is intended for approximately 12 contributors, including the Project Lead.

- **Project Lead:** 1
- **Frontend:** 2
- **Backend:** 3
- **AI/ML & Security:** 3
- **DevOps & Infrastructure:** 1–2
- **Full-Stack or flexible contributors:** Work across Frontend and Backend where capacity is needed

Roles may overlap based on contributor interests and experience. The Project Lead coordinates integration and may contribute across workstreams.

---

## Roles and Responsibilities

### Project Lead

- Maintain the project vision.
- Define and prioritize the backlog.
- Finalize architecture decisions.
- Break milestones into achievable issues.
- Assign and review tickets.
- Facilitate sprint planning and retrospectives.
- Support blocked contributors.
- Review pull requests.
- Coordinate integrations between squads.
- Coordinate project demonstrations and documentation.

### Frontend Developers

- Build the React dashboard and application shell.
- Build approval, activity, and trace views.
- Handle loading, error, empty, and decision states.
- Connect the interface to backend APIs.
- Improve accessibility and responsive behaviour.
- Write frontend and end-to-end tests.

### Backend Developers

- Build the Agent Gateway.
- Define normalized request schemas.
- Build the Policy Engine.
- Define policy schemas.
- Add tool and argument authorization.
- Build approval and audit APIs.
- Integrate PostgreSQL and add Redis only as a target enhancement.
- Build the Restricted Tool Executor for the simulated or sandboxed tool.
- Implement response sanitization and support target integration credentials if capacity remains.
- Write unit and integration tests.

### AI/ML & Security Developers

- Build prompt-injection detection.
- Build sensitive-data detection.
- Define structured risk findings and help build the Risk Orchestrator if the Redis target is started.
- Create adversarial scenarios.
- Measure security performance.
- Improve false-positive and false-negative rates.
- Review threat models, attack paths, and security-sensitive changes.

### DevOps & Infrastructure Developers

- Maintain Docker and Docker Compose development environments.
- Maintain GitHub Actions and repository checks.
- Support PostgreSQL and optional Redis service configuration.
- Maintain the reliable local demonstration and attempt hosted deployment only as a target enhancement.
- Add structured logs and target telemetry only when committed checks are stable.
- Document setup, deployment, and troubleshooting.

### Full-Stack and Flexible Contributors

- Take small issues across Frontend and Backend.
- Help connect API responses to dashboard views.
- Add integration tests and developer documentation.
- Support another workstream when it has a short-term capacity gap.

---

## Communication

- **Primary communication:** Discord
- **Code collaboration:** GitHub
- **Project tracking:** GitHub Projects
- **Meetings:** Google Meet and in-person sessions

### Suggested Schedule

- One-week development sprints
- One 20–30 minute sprint review and planning meeting each week
- One short asynchronous progress update before each meeting
- Optional in-person or virtual work sessions for contributors who need support
- Monthly project demonstration
- Additional technical workshops during onboarding when needed

Each contributor should normally receive one issue or sub-issue sized for one to three hours of work. Larger tasks should be divided across weeks or contributors. Meetings should focus on decisions, blockers, and coordination rather than lengthy status reports.

### In-Person Sessions

In-person work sessions may be used to:

- Help contributors resolve blockers
- Pair newer and experienced developers
- Review architecture decisions
- Test integrations
- Conduct security exercises
- Demonstrate completed work
- Improve collaboration between squads

---

## Definition of Done

A pull request is considered complete when:

- The assigned issue requirements are satisfied.
- The code follows formatting and linting standards.
- Relevant unit or integration tests are included.
- Existing tests pass.
- Input validation and error handling are included.
- Security-sensitive behaviour is documented.
- No secrets or credentials are committed.
- Audit logging is added where appropriate.
- Documentation is updated.
- The pull request has a clear description.
- The pull request is reviewed by at least one contributor.
- The Project Lead or assigned reviewer approves the change.
- The branch has no unresolved merge conflicts.

---

## Sprint Planning

### Sprint Length

- Standard sprint length: one week
- Each sprint ends with a 20–30 minute review, blocker discussion, and planning meeting
- Contributors update their issues before the meeting
- Tasks should normally fit within one to three hours and be divided when they are larger
- Contributors should have no more than one main implementation issue in progress at a time

The schedule assumes students have competing coursework, exams, and personal commitments. December is treated as a reduced-capacity maintenance period rather than a sequence of required sprints. Unfinished work returns to planning instead of automatically carrying an unrealistic commitment into the next week.

## Workstream Plan

Each workstream has useful parallel work throughout the project. When implementation is blocked by another workstream, contributors can work on tests, fixtures, documentation, interface contracts, or review tasks that support the same milestone.

| Phase | Frontend | Backend | AI/ML & Security | DevOps & Infrastructure |
| --- | --- | --- | --- | --- |
| Fall showcase | Application shell, approval flow, activity view, API integration | FastAPI gateway, schema, policies, decisions, audit storage | Threat cases, one initial detector, structured findings, benchmark scenarios | Repository workflow, CI, Docker Compose, PostgreSQL, local runbook |
| December maintenance | UI fixes, accessibility checks, component tests | Refactoring, API documentation, test coverage | Review results and improve test fixtures | Setup fixes, dependency updates, contributor documentation |
| January–February hardening | Trace views, approval states, accessibility, component tests | Validation, audit APIs, executor safety, integration tests | Improve both detectors, expand attack coverage, evaluate errors | Docker Compose, CI expansion, setup reliability, release documentation |
| March release | Usability fixes, release screenshots and demo flow | Reliability fixes, API freeze, integration tests | Final benchmark, metrics, security review | Release pipeline, deployment stabilization, documentation and release artifacts |

If committed work finishes early, contributors may take target enhancement issues for Redis, a real API or MCP integration, basic telemetry, or a hosted demonstration.

## High-Level Weekly Sprint Goals

### Fall Showcase

#### Sprint 1: Foundations

- Complete onboarding and architecture decisions.
- Create the backend and frontend application skeletons.
- Confirm local development, issue, branch, and review workflows.

#### Sprint 2: Contracts and Designs

- Define the normalized tool-call schema and API contract.
- Complete approval and activity wireframes.
- Define the initial threat cases and benchmark format.

#### Sprint 3: First Decisions

- Implement allow, block, and approval-required policy outcomes.
- Build the first detector prototype.
- Build the approval interface with representative mock data.

#### Sprint 4: Persistence and Integration

- Store requests, decisions, and approval events in PostgreSQL.
- Connect the dashboard to the backend API.
- Run the implemented services through Docker Compose.

#### Sprint 5: End-to-End Flow

- Connect one simulated or sandboxed tool to the complete decision path.
- Complete ten to twenty benchmark scenarios.
- Add integration tests and component-aware CI checks.

#### Sprint 6: Showcase Stabilization

- Freeze showcase features.
- Fix blocking defects and document known limitations.
- Rehearse safe, blocked, and approval-required demonstrations.
- Prepare a fallback recording and setup instructions.

### Winter Development

#### Sprint 7: Winter Restart

- Review the architecture and showcase feedback.
- Resolve high-priority technical debt.
- Confirm the March backlog and interface contracts.

#### Sprint 8: Core Contract Hardening

- Improve schema validation and policy edge cases.
- Stabilize API contracts between the backend and dashboard.
- Complete loading, empty, invalid, and failed-request UI states.

#### Sprint 9: Security Detection

- Complete documented prompt-injection and sensitive-data checks.
- Standardize structured security findings.
- Display structured findings in the dashboard.

#### Sprint 10: Approval Reliability

- Improve approval persistence and failure handling.
- Complete approval UI states and accessibility checks.
- Expand audit and decision tests.

#### Sprint 11: Restricted Execution

- Build the Restricted Tool Executor.
- Add execution limits, timeouts, and result sanitization.
- Test executor security boundaries.

#### Sprint 12: Audit and Activity

- Complete audit storage and query APIs.
- Complete activity and basic trace views.
- Test database migrations and common recovery paths.

#### Sprint 13: Integrated Release Path

- Connect the complete request, decision, approval, and tool-result flow.
- Add end-to-end tests for safe, blocked, and approval-required requests.
- Verify setup from a fresh clone with Docker Compose.

#### Sprint 14: Cross-Workstream Hardening

- Improve policies and detector accuracy.
- Fix integration and dashboard usability problems.
- Exercise timeout, unavailable-service, and malformed-input paths.

#### Sprint 15: CI and Documentation

- Complete component-aware linting, tests, and build checks.
- Complete contributor, architecture, security, and local setup documentation.
- Document common failures and troubleshooting steps.

#### Sprint 16: Benchmark and Evaluation

- Complete twenty to thirty benchmark scenarios.
- Measure attack success, benign completion, false positives, and false negatives.
- Address the most important findings.

#### Sprint 17: Release Candidate

- Stabilize the Docker Compose demonstration and release process.
- Complete onboarding, architecture, security, and deployment documentation.
- Run the full test and benchmark suite.

#### Sprint 18: Final Release

- Freeze features and fix release-blocking defects only.
- Publish the `v0.1` release.
- Rehearse the final demonstration and prepare fallback materials.

### Optional Target Enhancements

Target enhancements are pulled into a weekly sprint only when the committed sprint work is complete and stable:

- Redis-backed asynchronous analysis and a Risk Orchestrator
- One real API or basic MCP integration
- Scoped application credentials
- Basic OpenTelemetry traces and service health metrics
- One hosted demonstration environment
- Expansion beyond thirty benchmark scenarios

---

## Sprint Planning Template

### Sprint Duration

- **Sprint Length:** One week
- **Start Date:** TBD
- **End Date:** TBD

### Sprint Goals

1. Goal 1
2. Goal 2
3. Goal 3

### User Stories

| ID | User Story | Priority | Story Points | Assignee |
| --- | --- | --- | --- | --- |
| US01 | As an agent developer, I want all tool calls to pass through AgentGuard so that unauthorized actions can be prevented. | High | 5 | TBD |
| US02 | As a security administrator, I want deterministic policies so that sensitive tools cannot be called without authorization. | High | 5 | TBD |
| US03 | As a reviewer, I want to see why an action was flagged so that I can make an informed approval decision. | High | 3 | TBD |
| US04 | As a contributor, I want clear local setup instructions so that I can begin development quickly. | Medium | 2 | TBD |

### Sprint Review Questions

- What was completed?
- What remains unfinished?
- What technical blockers were discovered?
- Were any security assumptions invalidated?
- What should change in the next sprint?
- Are contributors receiving enough support and ownership?
