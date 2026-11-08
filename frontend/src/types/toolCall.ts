
export type ToolCallDecision =
  | 'allow'
  | 'block'
  | 'approval_required'

export type ApprovalStatus =
  | 'not_required'
  | 'pending'
  | 'approved'
  | 'denied'

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
