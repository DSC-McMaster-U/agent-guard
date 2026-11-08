
## Shared Dashboard Types and Mock Data

Shared types are located in `src/types/toolCall.ts`.

Exports:
- `ToolCallDecision`
- `ApprovalStatus`
- `ToolCallSummary`

Mock requests are exported as `mockToolCalls` from
`src/mocks/toolCalls.ts`.

The three mock requests demonstrate:
- An allowed internal email
- A blocked email to example.net
- An external email requiring approval

These shared types and mocks are intended for the
ActivityList and ApprovalDetails components.

All mock requests are simulated. No actual emails are sent.
