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

### Minimum Viable Product

The fall MVP will support:

- A centralized Agent Gateway
- One normalized tool-call request schema
- Agent and user identity fields
- Deterministic allow, block, and approval policies
- Tool argument validation
- Redis-backed asynchronous security analysis
- Prompt-injection detection
- Sensitive-data detection
- Goal-alignment analysis
- A Decision Engine
- A Human Approval Service
- A Restricted Tool Executor
- Two or three demonstration tool integrations
- PostgreSQL audit storage
- A basic React approval and trace dashboard
- A security benchmark with benign and adversarial scenarios
- Docker-based local development
- Cloud deployment of the MVP

### Initial Tool Integrations

The first version should support a small number of integrations:

- A sandboxed file-system tool
- A test email tool or email simulation
- A generic HTTP or API tool
- One MCP server integration if feasible during the fall term

The team should prioritize depth and security over the total number of connectors.

### Winter Product Goals

The winter release may add:

- MCP client and server proxying
- Tool-description validation
- Agent, user, task, and tool-level identity
- OAuth-based authorization
- Scoped and short-lived credentials
- Google Secret Manager integration
- Memory-poisoning protection
- Sequence-based behaviour anomaly detection
- Multi-agent trace support
- Policy templates and policy simulation
- Organization-level policy management
- OpenTelemetry traces
- Prometheus and Grafana dashboards
- External beta testing
- Public deployment templates
- A versioned `v1.0` release

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

The project will run for approximately eight months and will be divided into six major milestones.

### Milestone 1: Foundations and Onboarding

**Target:** September to early October

- Introduce contributors to Git, GitHub, pull requests, and open-source workflows.
- Finalize the threat model and architecture.
- Set up the `agent-guard` repository.
- Configure GitHub Projects and contribution guidelines.
- Create local Docker-based development environments.
- Define the normalized tool-call schema.
- Define shared Pydantic models.
- Create initial dashboard wireframes.
- Create the first benign and adversarial test scenarios.

### Milestone 2: Gateway and Deterministic Policy Enforcement

**Target:** October

- Build the FastAPI Agent Gateway.
- Add agent authentication.
- Validate tool names and arguments.
- Implement allow, block, and approval policies.
- Add session-level budgets.
- Add tool-specific parameter restrictions.
- Store requests and decisions in PostgreSQL.
- Create one sandboxed demonstration tool.
- Add unit tests for policy evaluation.

### Milestone 3: Security Analysis and Decision Pipeline

**Target:** November

- Add Redis job queues.
- Build the Risk Orchestrator.
- Implement prompt-injection detection.
- Implement sensitive-data detection.
- Implement goal-alignment analysis.
- Add structured risk findings.
- Build the Decision Engine.
- Add retries, timeouts, and failure handling.
- Integrate the complete security-analysis flow.

### Milestone 4: Fall MVP Integration and Demonstration

**Target:** Late November to December

- Build the Approval Service.
- Build the initial dashboard.
- Add live approval updates.
- Build the Restricted Tool Executor.
- Add scoped tool credentials.
- Complete two or three demonstration integrations.
- Return sanitized tool results through the Agent Gateway.
- Create at least 50 benchmark scenarios.
- Deploy the fall MVP.
- Demonstrate safe, malicious, and approval-required workflows.

### Milestone 5: MCP, Identity, and Observability

**Target:** January to February

- Add MCP proxy support.
- Validate MCP tool schemas and descriptions.
- Add OAuth-based authorization where appropriate.
- Integrate Google Secret Manager.
- Add short-lived credential handling.
- Add OpenTelemetry traces.
- Add Prometheus metrics.
- Add Grafana dashboards.
- Improve the approval interface.
- Add policy templates and policy simulation.

### Milestone 6: Advanced Security, Evaluation, and Final Release

**Target:** March to April

- Add behaviour sequence analysis.
- Add memory-poisoning scenarios.
- Add multi-agent trace support if feasible.
- Expand the benchmark dataset.
- Measure attack success and benign completion rates.
- Improve false-positive and false-negative performance.
- Conduct external beta testing.
- Harden the GKE deployment.
- Finalize documentation and onboarding.
- Publish a versioned open-source release.
- Prepare the final project demonstration.

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
- Security checks
- Docker image builds
- Image pushes to Google Artifact Registry
- Kubernetes manifest validation
- Deployment to staging
- Deployment to production

### Hosting

- **Frontend:** GKE or another suitable Google Cloud service
- **Backend Services:** GKE
- **Queue:** Redis
- **Database:** PostgreSQL
- **Container Images:** Google Artifact Registry
- **Secrets:** Google Secret Manager
- **Monitoring:** Google Cloud Monitoring, OpenTelemetry, Prometheus, and Grafana

The fall MVP may use a simplified deployment before the full GKE architecture is completed.

---

## Team Management

## Team Members

The project is intended for approximately 10 contributors.

- **Project Lead:** 1
- **Gateway and Integration Developers:** 2
- **Policy and Identity Developers:** 2
- **AI Security Detection Developers:** 3
- **Dashboard and Observability Developers:** 2

Roles may overlap based on contributor interests and experience.

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

### Gateway and Integration Developers

- Build the Agent Gateway.
- Define normalized request schemas.
- Add agent authentication.
- Build MCP and tool adapters.
- Build the Restricted Tool Executor.
- Implement response sanitization.
- Integrate scoped credentials.
- Write integration tests.

### Policy and Identity Developers

- Build the Policy Engine.
- Define policy schemas.
- Add tool and argument authorization.
- Add user, agent, task, and session permissions.
- Add session budgets.
- Integrate PostgreSQL policy storage.
- Support OAuth and scoped identity in winter.
- Write policy tests.

### AI Security Detection Developers

- Build the Risk Orchestrator.
- Build prompt-injection detection.
- Build sensitive-data detection.
- Build goal-alignment analysis.
- Build behaviour-anomaly detection.
- Create adversarial scenarios.
- Measure security performance.
- Improve false-positive and false-negative rates.

### Dashboard and Observability Developers

- Build the approval dashboard.
- Build session timelines.
- Build tool-call graph visualizations.
- Add approve and deny workflows.
- Add live updates.
- Add OpenTelemetry tracing.
- Add Prometheus metrics.
- Build Grafana dashboards.
- Write frontend and end-to-end tests.

---

## Communication

- **Primary communication:** Discord
- **Code collaboration:** GitHub
- **Project tracking:** GitHub Projects
- **Meetings:** Google Meet and in-person sessions

### Suggested Schedule

- Two-week development sprints
- One short asynchronous progress update each week
- One sprint review and planning meeting every two weeks
- Optional in-person or virtual work sessions for contributors who need support
- Monthly project demonstration
- Additional technical workshops during onboarding when needed

The final cadence should be confirmed with contributors after onboarding and adjusted if meetings begin to reduce development time.

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

- Standard sprint length: two weeks
- Weekly check-ins may occur within each sprint

## High-Level Sprint Goals

### Sprint 1: Onboarding and Architecture

- Introduce Git and GitHub workflows.
- Finalize the threat model.
- Finalize the architecture.
- Create the repository structure.
- Configure GitHub Projects.
- Set up local development.
- Create starter issues.

### Sprint 2: Shared Schemas and Gateway Foundations

- Define normalized tool-call schemas.
- Build the initial FastAPI service.
- Add request validation.
- Add trace and session identifiers.
- Build one demonstration tool.

### Sprint 3: Policy Engine

- Implement allow and block rules.
- Implement approval rules.
- Add argument validation.
- Add tool-specific policies.
- Add policy unit tests.

### Sprint 4: Persistence and Audit Events

- Set up PostgreSQL.
- Store sessions and requests.
- Store policy decisions.
- Store audit events.
- Add database migrations.

### Sprint 5: Redis and Risk Orchestration

- Set up Redis.
- Build job schemas.
- Publish analysis jobs.
- Handle retries and timeouts.
- Aggregate worker results.

### Sprint 6: Security Workers

- Build prompt-injection detection.
- Build sensitive-data detection.
- Build goal-alignment analysis.
- Add structured worker outputs.

### Sprint 7: Decision Engine

- Combine policy and worker results.
- Define decision outcomes.
- Add decision explanations.
- Add decision tests.

### Sprint 8: Approval Workflow

- Build the Approval Service.
- Build the approval dashboard.
- Add approve and deny actions.
- Persist reviewer decisions.
- Add live updates.

### Sprint 9: Restricted Tool Execution

- Build the Tool Executor.
- Add one MCP or API adapter.
- Add credential retrieval.
- Add execution limits.
- Add result sanitization.

### Sprint 10: Fall MVP Integration

- Connect the full request flow.
- Add demonstration scenarios.
- Fix integration issues.
- Deploy the MVP.
- Prepare the fall demonstration.

### Sprint 11: MCP and Identity

- Add MCP proxy support.
- Add tool-description validation.
- Add OAuth-based authorization.
- Add scoped credentials.

### Sprint 12: Observability

- Add OpenTelemetry.
- Add Prometheus metrics.
- Add Grafana dashboards.
- Add security alerts.

### Sprint 13: Advanced Security

- Add behaviour anomaly detection.
- Add memory-poisoning scenarios.
- Add policy templates.
- Add policy simulation.

### Sprint 14: Evaluation and External Testing

- Expand the benchmark.
- Measure security metrics.
- Track false positives.
- Conduct beta testing.
- Improve detection and policies.

### Sprint 15: Production Hardening

- Harden GKE deployment.
- Improve credential isolation.
- Add load and latency tests.
- Improve documentation.
- Fix security findings.

### Sprint 16: Final Release

- Finalize CI/CD.
- Publish deployment documentation.
- Complete contributor documentation.
- Prepare the final presentation.
- Publish the open-source release.

---

## Sprint Planning Template

### Sprint Duration

- **Sprint Length:** Two weeks
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
