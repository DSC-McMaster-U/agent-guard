import { useEffect, useRef, useState } from 'react'
import {
  evaluateToolCall,
  getRecentToolCalls,
  ToolCallApiError,
  type ToolCallRequest,
} from './api/toolCalls'
import ActivityList from './components/ActivityList'
import ApprovalDetails, { type ApprovalAction } from './components/ApprovalDetails'
import ToolCallForm, { type ToolCallFormValues } from './components/ToolCallForm'
import type { ToolCallSummary } from './types/toolCall'
import './App.css'

interface History {
  items: ToolCallSummary[] | null
  loading: boolean
  error: string | null
}

interface SubmittedCall {
  summary: ToolCallSummary
  revision: number
}

type ReviewPreview = 'approved' | 'denied'

function isPendingReview(summary: ToolCallSummary) {
  return summary.decision === 'approval_required' && summary.approval_status === 'pending'
}

function hasSavedReview(summary: ToolCallSummary) {
  return summary.approval_status === 'approved' || summary.approval_status === 'denied'
}

function App() {
  const [history, setHistory] = useState<History>({ items: null, loading: true, error: null })
  const [historyAttempt, setHistoryAttempt] = useState(0)
  const [submitted, setSubmitted] = useState<SubmittedCall[]>([])
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(null)
  const [reviews, setReviews] = useState(() => new Map<string, ReviewPreview>())
  const [busy, setBusy] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const submitting = useRef(false)
  const postRevision = useRef(0)

  useEffect(() => {
    const controller = new AbortController()
    const { signal } = controller
    const revisionAtStart = postRevision.current

    async function loadHistory() {
      try {
        const items = await getRecentToolCalls(signal)
        if (signal.aborted) return

        const stored = new Map(items.map((item) => [item.request_id, item]))
        // A GET started before a POST completed can carry an older snapshot.
        // A stored final review is authoritative regardless of request order.
        setSubmitted((previous) => previous.filter(({ summary, revision }) => {
          const saved = stored.get(summary.request_id)
          return saved === undefined || (
            revision > revisionAtStart &&
            !hasSavedReview(saved)
          )
        }))
        setReviews((previous) => {
          const next = new Map(previous)
          for (const [id, item] of stored) {
            if (!isPendingReview(item)) next.delete(id)
          }
          return next
        })
        setHistory({ items, loading: false, error: null })
      } catch (error) {
        if (signal.aborted) return
        let message = 'Could not load activity history. Try again.'
        if (error instanceof ToolCallApiError) {
          if (error.status === 405) {
            message = 'Activity history is unavailable because the server does not support it yet (HTTP 405).'
          } else if (error.status === 503) {
            message = 'Stored activity is temporarily unavailable (HTTP 503). Try again.'
          }
        }
        setHistory((previous) => ({ ...previous, loading: false, error: message }))
      }
    }

    void loadHistory()
    return () => controller.abort()
  }, [historyAttempt])

  const serverItems = new Map<string, ToolCallSummary>()
  for (const item of submitted) serverItems.set(item.summary.request_id, item.summary)
  for (const item of history.items ?? []) {
    if (!serverItems.has(item.request_id) || hasSavedReview(item)) {
      serverItems.set(item.request_id, item)
    }
  }
  const items = Array.from(serverItems.values())
  const selectedRequest = selectedRequestId === null ? null : serverItems.get(selectedRequestId) ?? null
  const preview = selectedRequest && isPendingReview(selectedRequest)
    ? reviews.get(selectedRequest.request_id)
    : undefined

  function refreshHistory() {
    if (history.loading) return
    setHistory((previous) => ({ ...previous, loading: true }))
    setHistoryAttempt((attempt) => attempt + 1)
  }

  async function submitEmail({ original_goal, recipient, subject, body }: ToolCallFormValues) {
    if (submitting.current) return
    submitting.current = true
    setBusy(true)
    setSubmitError(null)

    try {
      const request: ToolCallRequest = {
        request_id: crypto.randomUUID(),
        agent_id: 'assistant_2',
        user_id: 'demo-user',
        session_id: 'demo-session',
        original_goal,
        tool: 'email.send',
        arguments: { recipient, subject, body },
      }

      const summary = await evaluateToolCall(request)
      const revision = ++postRevision.current
      setSubmitted((previous) => [
        { summary, revision },
        ...previous.filter((item) => item.summary.request_id !== summary.request_id),
      ])
      setSelectedRequestId(summary.request_id)
    } catch (error) {
      const detail = error instanceof ToolCallApiError ? ` ${error.message}` : ''
      setSubmitError(`Policy evaluation failed.${detail}`)
    } finally {
      submitting.current = false
      setBusy(false)
    }
  }

  function handleDecision(requestId: string, action: ApprovalAction) {
    const request = serverItems.get(requestId)
    if (request === undefined || !isPendingReview(request)) return

    setReviews((previous) => {
      const next = new Map(previous)
      next.set(requestId, action === 'approve' ? 'approved' : 'denied')
      return next
    })
  }

  return (
    <main>
      <h1>AgentGuard</h1>
      <ToolCallForm onSubmit={submitEmail} busy={busy} error={submitError} />
      <div className="dashboard-panels">
        <section aria-labelledby="activity-heading">
          <div className="dashboard-activity-header">
            <h2 id="activity-heading">Activity</h2>
            <button type="button" onClick={refreshHistory} disabled={history.loading}>
              Refresh activity
            </button>
          </div>
          {history.loading && <p role="status">Loading activity history…</p>}
          {history.error !== null && <p role="alert">{history.error}</p>}
          {(history.items !== null || items.length > 0) && (
            <div className="dashboard-activity" role="region" aria-label="Activity table" tabIndex={0}>
              <ActivityList items={items} onSelect={setSelectedRequestId} />
            </div>
          )}
        </section>
        <section aria-labelledby="approvals-heading">
          <h2 id="approvals-heading">Approvals</h2>
          <p className="dashboard-notice">Local review preview — not saved; no email is sent.</p>
          <div role="status">
            {preview && <p>Local preview: {preview === 'approved' ? 'Approved' : 'Denied'} (not saved)</p>}
          </div>
          <ApprovalDetails request={selectedRequest} onDecision={handleDecision} />
        </section>
      </div>
    </main>
  )
}

export default App
