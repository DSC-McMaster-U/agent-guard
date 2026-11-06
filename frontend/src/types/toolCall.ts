// Shared dashboard types from the Sprint 2 handoff (docs/sprints/sprint-2.md).
// #63 owns this file; keep its version if the two conflict.
export type ToolCallDecision = 'allow' | 'block' | 'approval_required'

export type ApprovalStatus = 'not_required' | 'pending' | 'approved' | 'denied'

export interface ToolCallSummary {
  request_id: string
  agent_id: string
  tool: string
  arguments: Record<string, unknown>
  decision: ToolCallDecision
  reason: string
  timestamp: string
  approval_status: ApprovalStatus
}
