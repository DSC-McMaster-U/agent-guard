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

### March v0.1 Goals

The release targeted for the end of March should add:

- Redis-backed asynchronous security analysis
- A Risk Orchestrator with timeouts and structured worker results
- Improved prompt-injection and sensitive-data detection
- A Restricted Tool Executor with execution limits and result sanitization
- One or two demonstration tool integrations, including basic MCP support if feasible
- Scoped application credentials or API keys for the supported integrations
- Improved approval, activity, and trace views
- Basic OpenTelemetry traces and service health metrics
- Thirty to fifty benign and adversarial benchmark scenarios
- A repeatable deployment for one demonstration environment
- Contributor, architecture, security, and deployment documentation
- A versioned `v0.1` open-source release

### Stretch Goals

The following features should be attempted only after the March goals are stable:

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

A typical AgentGuard workflow will follow these steps:

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
Risk Orchestrator
    |
    v
Redis Security Analysis Queue
    |
    v
Security Analysis Workers
    |
    v
Risk Orchestrator
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
        External MCP or Tool API
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

### Milestone 5: Product Expansion

**Target:** January to February

- Add Redis-backed analysis jobs and a Risk Orchestrator.
- Improve prompt-injection and sensitive-data detection.
- Build the Restricted Tool Executor with execution limits and result sanitization.
- Add one real API or basic MCP integration.
- Improve the approval, activity, and trace interfaces.
- Add scoped credentials for supported integrations.
- Add basic OpenTelemetry traces and service health metrics.
- Expand integration and security tests.

### Milestone 6: Evaluation and v0.1 Release

**Target:** March

- Expand the benchmark to thirty to fifty scenarios.
- Measure attack success and benign completion rates.
- Improve false-positive and false-negative performance.
- Stabilize one repeatable demonstration deployment.
- Complete end-to-end, failure-path, and security testing.
- Finalize documentation and onboarding.
- Publish a versioned `v0.1` open-source release.
- Prepare the final project demonstration.

Advanced anomaly detection, complete OAuth support, production GKE hardening, multi-agent tracing, and extensive external testing remain stretch goals.

---

## Technical Architecture

AgentGuard will use a modular, cloud-native architecture.

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

Possible decisions include:

- Allow
- Block
- Require approval
- Rewrite
- Restrict
- Sandbox
- Rate limit

#### Risk Orchestrator

The Risk Orchestrator will:

- Create security-analysis jobs
- Publish jobs to Redis
- Track worker completion
- Aggregate worker findings
- Handle worker timeouts and failures
- Normalize risk evidence
- Forward findings to the Decision Engine

#### Security Analysis Workers

The MVP will include four planned workers.

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

- Compare the proposed action with the original user request.
- Detect actions outside the authorized task scope.
- Identify unrelated tool usage.
- Produce a structured alignment score and explanation.

##### Behaviour Anomaly Worker

- Detect repeated blocked actions.
- Detect unusual tool sequences.
- Detect sudden escalation from read to write operations.
- Detect suspicious external destinations.
- Detect abnormal session behaviour.

This worker may begin with rules and expand to statistical or ML-based methods during winter.

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
- Retrieve scoped credentials from Secret Manager.
- Call external MCP servers or APIs.
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

Redis will store:

- Security-analysis jobs
- Temporary worker state
- Short-lived approval state where appropriate
- Rate-limit counters
- Session coordination data

#### Credential Layer

Google Secret Manager will store:

- OAuth client secrets
- API credentials
- Tool integration secrets
- Service credentials

Short-lived access tokens should be issued or retrieved at execution time and should not be exposed to the AI model.

#### Observability Layer

The system will use:

- OpenTelemetry for distributed traces
- Prometheus for metrics
- Grafana for dashboards
- Google Cloud Monitoring for infrastructure visibility
- Structured application logs for security events

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

- Redis
- PostgreSQL

### Cloud and Infrastructure

- Google Kubernetes Engine
- Google Artifact Registry
- Google Secret Manager
- Google Cloud Monitoring
- Docker
- Kubernetes

### Observability

- OpenTelemetry
- Prometheus
- Grafana
- Structured logging

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
- Risk Orchestrator to Redis
- Redis to Security Workers
- Security Workers to Decision Engine
- Decision Engine to Approval Service
- Approval Service to Tool Executor
- Tool Executor to MCP or external API
- Audit events to PostgreSQL
- Secret Manager access from Tool Executor
- Dashboard live updates

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

- **Frontend:** A suitable static or container hosting service
- **Backend Services:** One container-based demonstration environment
- **Queue:** Redis
- **Database:** PostgreSQL
- **Secrets:** Environment or platform-managed secrets for the supported demonstration integrations
- **Monitoring:** Basic health checks, structured logs, metrics, and OpenTelemetry traces

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
- Integrate PostgreSQL and Redis.
- Build the Restricted Tool Executor and supported tool adapters.
- Implement response sanitization and scoped credentials.
- Write unit and integration tests.

### AI/ML & Security Developers

- Build prompt-injection detection.
- Build sensitive-data detection.
- Define structured risk findings and help build the Risk Orchestrator.
- Create adversarial scenarios.
- Measure security performance.
- Improve false-positive and false-negative rates.
- Review threat models, attack paths, and security-sensitive changes.

### DevOps & Infrastructure Developers

- Maintain Docker and Docker Compose development environments.
- Maintain GitHub Actions and repository checks.
- Support PostgreSQL and Redis service configuration.
- Create and document the demonstration deployment.
- Add OpenTelemetry tracing.
- Add basic metrics, health checks, logs, and monitoring.
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
| January–February expansion | Trace views, richer approval states, integration UX | Redis orchestration, executor, integrations, basic MCP support | Improve detectors, expand attack coverage, evaluate errors | Service health, deployment environment, tracing, logs, CI expansion |
| March release | Usability fixes, release screenshots and demo flow | Reliability fixes, API freeze, integration tests | Final benchmark, metrics, security review | Release pipeline, deployment stabilization, documentation and release artifacts |

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

#### Sprint 8: Asynchronous Analysis Foundations

- Add Redis and security job contracts.
- Add worker health checks and development configuration.
- Design dashboard states for pending and failed analysis.

#### Sprint 9: Risk Orchestration

- Build the Risk Orchestrator and worker result aggregation.
- Integrate improved prompt-injection and sensitive-data workers.
- Display structured findings in the dashboard.

#### Sprint 10: Approval Reliability

- Improve approval persistence and failure handling.
- Complete approval UI states and accessibility checks.
- Expand audit and decision tests.

#### Sprint 11: Restricted Execution

- Build the Restricted Tool Executor.
- Add execution limits, timeouts, and result sanitization.
- Test executor security boundaries.

#### Sprint 12: First Real Integration

- Add one supported API or tool integration.
- Add scoped application credentials.
- Add the integration to activity and trace views.

#### Sprint 13: MCP Prototype

- Add basic MCP proxy support if the core system is stable.
- Validate tool schemas and descriptions.
- Add MCP-specific benign and adversarial scenarios.

#### Sprint 14: Cross-Workstream Hardening

- Improve policies and detector accuracy.
- Fix integration and dashboard usability problems.
- Exercise timeout, unavailable-service, and malformed-input paths.

#### Sprint 15: Essential Observability

- Add basic traces, structured logs, service health, and decision metrics.
- Surface useful operational state without building a large monitoring platform.
- Document local and deployed troubleshooting.

#### Sprint 16: Benchmark and Evaluation

- Expand the benchmark to thirty to fifty scenarios.
- Measure attack success, benign completion, false positives, and false negatives.
- Address the most important findings.

#### Sprint 17: Release Candidate

- Stabilize one repeatable demonstration deployment.
- Complete onboarding, architecture, security, and deployment documentation.
- Run the full test and benchmark suite.

#### Sprint 18: Final Release

- Freeze features and fix release-blocking defects only.
- Publish the `v0.1` release.
- Rehearse the final demonstration and prepare fallback materials.

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
