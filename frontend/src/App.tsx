import { useState } from 'react'
import ActivityList from './components/ActivityList'
import ApprovalDetails, { type ApprovalAction } from './components/ApprovalDetails'
import { mockToolCalls } from './mocks/toolCalls'
import './App.css'

function App() {
  const [items, setItems] = useState(() => structuredClone(mockToolCalls))
  const [selectedRequestId, setSelectedRequestId] = useState<string | null>(null)
  const selectedRequest = items.find((item) => item.request_id === selectedRequestId) ?? null

  function handleDecision(requestId: string, action: ApprovalAction) {
    setItems((currentItems) => {
      const request = currentItems.find((item) => item.request_id === requestId)
      if (request?.decision !== 'approval_required' || request.approval_status !== 'pending') {
        return currentItems
      }

      return currentItems.map((item) =>
        item === request
          ? { ...item, approval_status: action === 'approve' ? 'approved' : 'denied' }
          : item,
      )
    })
  }

  return (
    <main>
      <h1>AgentGuard</h1>
      <p className="dashboard-notice">Local demo — changes reset on refresh; no email is sent.</p>
      <div className="dashboard-panels">
        <section aria-labelledby="activity-heading">
          <h2 id="activity-heading">Activity</h2>
          <div className="dashboard-activity" role="region" aria-label="Activity table" tabIndex={0}>
            <ActivityList items={items} onSelect={setSelectedRequestId} />
          </div>
        </section>
        <section aria-labelledby="approvals-heading">
          <h2 id="approvals-heading">Approvals</h2>
          <ApprovalDetails request={selectedRequest} onDecision={handleDecision} />
        </section>
      </div>
    </main>
  )
}

export default App
