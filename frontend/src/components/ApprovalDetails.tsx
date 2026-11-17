import { useEffect, useRef } from 'react'
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

function formatTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) return timestamp
  return `${date.toISOString().slice(0, 16).replace('T', ' ')} UTC`
}

function statusText(request: ToolCallSummary): string {
  if (request.decision === 'allow') return 'Allowed'
  if (request.decision === 'block') return 'Blocked'
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

function resultText(request: ToolCallSummary): string | null {
  if (request.decision === 'allow') return 'Policy allowed this request; no review was needed.'
  if (request.decision === 'block') return 'Policy blocked this request; it cannot be approved.'
  if (request.approval_status === 'approved') return 'A reviewer approved this request.'
  if (request.approval_status === 'denied') return 'A reviewer denied this request.'
  return null
}

function ApprovalDetails({ request, onDecision }: ApprovalDetailsProps) {
  const statusRef = useRef<HTMLParagraphElement>(null)
  const decidedRequestId = useRef<string | null>(null)

  const requestId = request?.request_id
  const approvalStatus = request?.approval_status

  // The action buttons disappear once a decision lands, so move keyboard focus
  // to the status instead of letting it fall back to the page body.
  useEffect(() => {
    if (decidedRequestId.current !== null && decidedRequestId.current === requestId && approvalStatus !== 'pending') {
      statusRef.current?.focus()
    }
    decidedRequestId.current = null
  }, [requestId, approvalStatus])

  if (request === null) {
    return <p className="approval-details-empty">Select a request</p>
  }

  const canDecide =
    request.decision === 'approval_required' && request.approval_status === 'pending'
  const result = resultText(request)

  function decide(action: ApprovalAction) {
    if (request === null) return
    decidedRequestId.current = request.request_id
    onDecision(request.request_id, action)
  }

  return (
    <div className="approval-details" role="group" aria-labelledby="approval-details-reason">
      <section className="approval-card approval-card-request">
        <h3 id="approval-details-reason">Reason: {request.reason}</h3>
        <dl className="approval-details-meta">
          <dt>Request ID</dt>
          <dd>{request.request_id}</dd>
          <dt>Time</dt>
          <dd>
            <time dateTime={request.timestamp}>{formatTimestamp(request.timestamp)}</time>
          </dd>
          <dt>Agent</dt>
          <dd>{request.agent_id}</dd>
        </dl>
        <div className="approval-details-action">
          <p>Would like to send an email</p>
          <p>Recipient: {getString(request.arguments, 'recipient')}</p>
          <p>Subject: {getString(request.arguments, 'subject')}</p>
          <p className="approval-details-body">{getString(request.arguments, 'body')}</p>
        </div>
      </section>

      <section className="approval-card approval-card-tools">
        <p>Tools:</p>
        <p className="approval-details-tool">{request.tool}</p>
      </section>

      <section className="approval-card approval-card-decision">
        {canDecide && <h3 className="approval-details-prompt">Approve?</h3>}
        <p ref={statusRef} className="approval-details-status" role="status" tabIndex={-1}>
          {statusText(request)}
        </p>
        {result !== null && <p className="approval-details-result">{result}</p>}
        {canDecide && (
          <div className="approval-details-actions">
            <button type="button" onClick={() => decide('approve')}>
              Approve
            </button>
            <button type="button" onClick={() => decide('deny')}>
              Deny
            </button>
          </div>
        )}
      </section>

      <p className="approval-details-note">Simulated request — no email is sent.</p>
    </div>
  )
}

export default ApprovalDetails
