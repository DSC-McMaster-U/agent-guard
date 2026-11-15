# Tool-Call Contract

This glossary describes the current local-demo contract. The [Pydantic models](../backend/app/schemas.py) and [email validation helper](../backend/app/validation.py) implement it; the [Sprint 2 handoff](sprints/sprint-2.md#shared-request-contract) records the design decisions. The HTTP endpoint is tracked separately in [#83](https://github.com/DSC-McMaster-U/agent-guard/issues/83).

A normalized tool call is the standard JSON format AgentGuard uses to describe an action an AI agent wants to take, before that action runs. Using this format, every request has the same set of fields, no matter which agent sent it. AgentGuard's policies and security checks use these fields to allow the action, block it, or send it to a person for approval.


## Fields

| Field | Meaning | Required |
|---|---|---|
| `request_id` | A unique ID for this one tool call | Yes |
| `agent_id` | The ID of the AI agent making the request | Yes |
| `user_id` | The ID of the user the agent is acting for | Yes |
| `session_id` | Groups related requests, such as all tool calls from one conversation | Yes |
| `original_goal` | What the user originally asked the agent to do, in plain text | Yes |
| `tool` | The name of the tool the agent wants to call, such as `email.send` | Yes |
| `arguments` | The inputs for that tool. For `email.send`: `recipient`, `subject`, and `body` | Yes |
| `trigger_source` | What led the agent to make this call and how much it can be trusted, such as a direct user instruction (`trusted`) | No |


## Agreed validation rules

- The demo caller supplies `request_id`; `session_id` groups related requests.
  Neither ID nor a caller-supplied `agent_id` authenticates a user or agent.
- The seven required fields are listed above. Unknown top-level request keys are
  rejected. `arguments` is an object so unsupported tools can reach policy and be
  blocked without pretending their arguments are email arguments.
- For `email.send`, validate `arguments` separately with `EmailSendArguments` (or
  `validate_email_arguments`). It requires a valid recipient, subject (1–200
  characters), and body (1–10,000 characters); extra keys such as `cc` are rejected.
  The demo has no attachment support.
- Missing `trigger_source` defaults to type/trust_level `unknown` and empty
  content. Explicit `null` is also accepted; callers of the model must handle it.
  Supported source types are `user_instruction`, `untrusted_email_body`,
  `untrusted_webpage`, `untrusted_document`, `tool_result`, and `unknown`.
  Trust levels are `trusted`, `untrusted`, and `unknown`; source content is limited
  to 10,000 characters. Caller-provided trust must never bypass policy.
- Models raise Pydantic `ValidationError`. The planned HTTP route translates
  invalid payloads to FastAPI's normal `422` detail array. Unsupported tools are
  policy blocks, not email-shape validation errors.

## Valid Example

```json
{
  "request_id": "req_1",
  "agent_id": "assistant_2",
  "user_id": "user_13",
  "session_id": "session_2",
  "original_goal": "Send the approved report to the project lead",
  "tool": "email.send",
  "arguments": {
    "recipient": "lead@example.com",
    "subject": "Approved Report",
    "body": "Hi, here is the fictional report summary."
  },
  "trigger_source": {
    "type": "user_instruction",
    "trust_level": "trusted"
  }
}
```


## Invalid Example

```json
{
  "request_id": "req_1",
  "agent_id": "assistant_2",
  "session_id": "session_2",
  "original_goal": "Send the approved report to the project lead",
  "tool": "email.send",
  "arguments": {
    "recipient": "lead@example.com",
    "subject": "Approved Report",
    "body": "Hi, here is the fictional report summary."
  },
  "trigger_source": {
    "type": "user_instruction",
    "trust_level": "trusted"
  }
}
```

- **Why it's invalid:** `user_id` is a required field, but it's missing from this request.
- **Planned HTTP response:** `422 Unprocessable Entity`, using FastAPI's normal
  validation detail array identifying `body.user_id`. The HTTP endpoint must be
  implemented before this can be tested as a live request. At the model layer,
  `ToolCallRequest.model_validate(...)` raises `ValidationError` now.

## Decision response

`ToolCallSummary` matches the [frontend summary type](../frontend/src/types/toolCall.ts):
`request_id`, `agent_id`, `tool`, `arguments`, `decision`, `reason`, `timestamp`,
and `approval_status`. Decisions are `allow`, `block`, or `approval_required`.
Approval status is `not_required`, `pending`, `approved`, or `denied`. Timestamps
must be timezone-aware and serialize in UTC. Initial evaluated decisions use
`pending` only for `approval_required`, and `not_required` otherwise.

These models define data, not approval persistence or execution. See the
[dated checkpoint](sprints/sprint-3-checkpoint.md) for current implementation limits.
