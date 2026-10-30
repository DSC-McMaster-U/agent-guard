# Tool-Call Contract

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


## Assumptions

- **Field names:** In issue #26, the two fields are mentioned as "original user task" and "tool name". I used `original_goal` and `tool` to match the example in PROJECT.md.
- **Required fields:** PROJECT.md doesn't say which fields are required, so I marked the six fields named in issue #26 as required. I also made `session_id` required, because the session trace endpoints and session-based policies in PROJECT.md depend on it. `trigger_source` appears in the PROJECT.md example but wasn't in the issue's list, so I left it optional for now.
- **Arguments:** `arguments` is an object, and its keys depend on the tool. For `email.send` they are `recipient`, `subject`, and `body`. The PROJECT.md example doesn't include `body`, but the MVP scope section lists it, so I included it in the examples.
- **Request ID:** It isn't decided whether the agent or AgentGuard creates `request_id`. I assumed the agent sends it with each request, which is why it's marked required. If AgentGuard ends up generating it instead, it would come back in the response rather than being required in the request.


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
    "body": "Hi, please see the report attached."
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
    "body": "Hi, please see the report attached."
  },
  "trigger_source": {
    "type": "user_instruction",
    "trust_level": "trusted"
  }
}
```

- **Why it's invalid:** `user_id` is a required field, but it's missing from this request.
- **Expected API response:** `422 Unprocessable Entity`, with an error that names the missing field. Below is an example error response, though the exact format has not been decided yet:

```json
{
  "error": "validation_error",
  "field": "user_id",
  "message": "user_id is required."
}
```


## Open Questions for Sprint 2

1. **What should validation errors look like?** Should we keep FastAPI's default `422` error format, or define our own simpler one with the field name and a message, like the example above?
2. **Where are each tool's arguments defined?** PROJECT.md says every tool will have a tool definition with an input schema. Should the gateway check `arguments` against that definition, and reject any keys it doesn't list?
3. **Should `trigger_source` be required, and what values can it have?** PROJECT.md lists possible trust levels, such as untrusted email or webpage, but the exact values for `type` and `trust_level` are not clear.
