import { useEffect, useRef, useState, type FormEvent } from 'react'
import {
  evaluateToolCall,
  getRecentToolCalls,
  ToolCallApiError,
  type ToolCallRequest,
} from './api/toolCalls'
import ActivityList from './components/ActivityList'
import ApprovalDetails, { type ApprovalAction } from './components/ApprovalDetails'
import type { ToolCallSummary } from './types/toolCall'
import './App.css'

interface EmailFields {
  original_goal: string
  recipient: string
  subject: string
  body: string
}

interface DemoEmailFormProps {
  onSubmit: (fields: EmailFields) => void
  busy: boolean
  error: string | null
}

type History =
  | { status: 'loading' }
  | { status: 'ready'; items: ToolCallSummary[] }
  | { status: 'error'; message: string }

type ReviewPreview = 'approved' | 'denied'

function DemoEmailForm({ onSubmit, busy, error }: DemoEmailFormProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const fields = new FormData(event.currentTarget)
    onSubmit({
      original_goal: String(fields.get('original_goal') ?? ''),
      recipient: String(fields.get('recipient') ?? ''),
      subject: String(fields.get('subject') ?? ''),
      body: String(fields.get('body') ?? ''),
    })
  }

  return (
    <form onSubmit={handleSubmit} aria-busy={busy}>
      <fieldset className="dashboard-email-fields" disabled={busy}>
        <legend>Email details</legend>
        <label>
          Original goal
          <input name="original_goal" required maxLength={4000} />
        </label>
        <label>
          Recipient
          <input name="recipient" type="email" required />
        </label>
        <label>
          Subject
          <input name="subject" required maxLength={200} />
        </label>
        <label>
          Body
          <textarea name="body" required maxLength={10000} rows={3} />
        </label>
        <button
          type="submit"
          onClick={(event) => {
            // A fast response can re-enable the button before the second click.
            if (event.detail > 1) event.preventDefault()
          }}
        >
          {busy ? 'Evaluating…' : 'Evaluate policy'}
        </button>
      </fieldset>
      {error !== null && <p role="alert">{error}</p>}
    </form>
  )
}

function App() {
  const [history, setHistory] = useState<History>({ status: 'loading' })
  const [historyAttempt, setHistoryAttempt] = useState(0)
  const [submitted, setSubmitted] = useState<ToolCallSummary[]>([])
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(null)
  const [reviews, setReviews] = useState(() => new Map<string, ReviewPreview>())
  const [busy, setBusy] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)
  const submitting = useRef(false)

  useEffect(() => {
    const controller = new AbortController()
    const { signal } = controller

    async function loadHistory() {
      try {
        const items = await getRecentToolCalls(signal)
        if (!signal.aborted) setHistory({ status: 'ready', items })
      } catch (error) {
        if (signal.aborted) return
        const message = error instanceof ToolCallApiError && error.status === 405
          ? 'Activity history is unavailable because the server does not support it yet (HTTP 405).'
          : 'Could not load activity history. Try again.'
        setHistory({ status: 'error', message })
      }
    }

    void loadHistory()
    return () => controller.abort()
  }, [historyAttempt])

  // Prefer fresh POST responses for IDs that also appear in a history snapshot.
  const serverItems = new Map<string, ToolCallSummary>()
  for (const item of [...submitted, ...(history.status === 'ready' ? history.items : [])]) {
    if (!serverItems.has(item.request_id)) serverItems.set(item.request_id, item)
  }

  const items = Array.from(serverItems.values(), (item) => {
    const review = reviews.get(item.request_id)
    return item.decision === 'approval_required' && item.approval_status === 'pending' && review
      ? { ...item, approval_status: review }
      : item
  })
  const selectedRequest = items.find((item) => item.request_id === selectedRequestId) ?? null

  function retryHistory() {
    setHistory({ status: 'loading' })
    setHistoryAttempt((attempt) => attempt + 1)
  }

  async function submitEmail({ original_goal, recipient, subject, body }: EmailFields) {
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

      const result = await evaluateToolCall(request)
      setSubmitted((previous) => [
        result,
        ...previous.filter((item) => item.request_id !== result.request_id),
      ])
      setSelectedRequestId(result.request_id)
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
    if (request?.decision !== 'approval_required' || request.approval_status !== 'pending') return

    setReviews((previous) => {
      if (previous.has(requestId)) return previous
      const next = new Map(previous)
      next.set(requestId, action === 'approve' ? 'approved' : 'denied')
      return next
    })
  }

  return (
    <main>
      <h1>AgentGuard</h1>
      <section aria-labelledby="evaluate-heading">
        <h2 id="evaluate-heading">Evaluate an email request</h2>
        {/* Temporary form until Issue #107 supplies ToolCallForm. */}
        <DemoEmailForm onSubmit={submitEmail} busy={busy} error={submitError} />
      </section>
      <p className="dashboard-notice">Local review preview — not saved; no email is sent.</p>
      <div className="dashboard-panels">
        <section aria-labelledby="activity-heading">
          <h2 id="activity-heading">Activity</h2>
          {history.status === 'loading' && <p role="status">Loading activity history…</p>}
          {history.status === 'error' && (
            <div>
              <p role="alert">{history.message}</p>
              <button type="button" onClick={retryHistory}>Retry history</button>
            </div>
          )}
          {history.status === 'ready' || items.length > 0 ? (
            <div className="dashboard-activity" role="region" aria-label="Activity table" tabIndex={0}>
              <ActivityList items={items} onSelect={setSelectedRequestId} />
            </div>
          ) : null}
        </section>
        <section aria-labelledby="approvals-heading">
          <h2 id="approvals-heading">Approvals</h2>
          {selectedRequest !== null && selectedRequest.approval_status !==
            serverItems.get(selectedRequest.request_id)?.approval_status && (
              <p>Server status: Pending approval</p>
            )}
          <ApprovalDetails request={selectedRequest} onDecision={handleDecision} />
        </section>
      </div>
    </main>
  )
}

export default App
