import type { ToolCallSummary } from '../types/toolCall'
import './ApprovalDetails.css'

export type ApprovalAction = 'approve' | 'deny'

interface ApprovalDetailsProps {
  request: ToolCallSummary | null
  onDecision: (requestId: string, action: ApprovalAction) => void
}

function getString(args: Record<string, unknown>, key: string): string {
  const value = args[key]
  return typeof value === 'string' && value !== '' ? value : '—'
}

function statusText(request: ToolCallSummary): string {
  if (request.decision === 'allow') return 'Allowed — no approval needed'
  if (request.decision === 'block') return 'Blocked by policy'
  switch (request.approval_status) {
    case 'pending':
      return 'Pending approval'
    case 'approved':
      return 'Approved'
    case 'denied':
      return 'Denied'
    default:
      return 'Approval not required'
  }
}

function ApprovalDetails({ request, onDecision }: ApprovalDetailsProps) {
  if (request === null) {
    return <p className="approval-details-empty">Select a request</p>
  }

  const canDecide =
    request.decision === 'approval_required' && request.approval_status === 'pending'

  return (
    <div className="approval-details" role="group" aria-labelledby="approval-details-reason">
      <section className="approval-card approval-card-request">
        <h3 id="approval-details-reason">Reason: {request.reason}</h3>
        <p className="approval-details-agent">Agent: {request.agent_id}</p>
        <div className="approval-details-action">
          <p>
            Would like to send an email [Recipient: {getString(request.arguments, 'recipient')}]
          </p>
          <p>Subject: {getString(request.arguments, 'subject')}</p>
          <p className="approval-details-body">{getString(request.arguments, 'body')}</p>
        </div>
      </section>

      <section className="approval-card approval-card-tools">
        <p>Tools:</p>
        <p className="approval-details-tool">{request.tool}</p>
      </section>

      <section className="approval-card approval-card-decision">
        {canDecide ? (
          <>
            <h3 className="approval-details-prompt">Approve?</h3>
            <p className="approval-details-status">Pending approval</p>
            <div className="approval-details-actions">
              <button type="button" onClick={() => onDecision(request.request_id, 'approve')}>
                Approve
              </button>
              <button type="button" onClick={() => onDecision(request.request_id, 'deny')}>
                Deny
              </button>
            </div>
          </>
        ) : (
          <p className="approval-details-status">{statusText(request)}</p>
        )}
      </section>

      <p className="approval-details-note">Simulated request — no email is sent.</p>
    </div>
  )
}

export default ApprovalDetails
