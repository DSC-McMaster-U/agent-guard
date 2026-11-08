import type { ToolCallDecision, ToolCallSummary } from '../types/toolCall'
import './ActivityList.css'

export interface ActivityListProps {
  items: ToolCallSummary[]
  onSelect: (requestId: string) => void
}

const decisionLabels: Record<ToolCallDecision, string> = {
  allow: 'Allowed',
  block: 'Blocked',
  approval_required: 'Pending approval',
}

const timeFormat = new Intl.DateTimeFormat('en-GB', {
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'UTC',
})

function formatTime(timestamp: string): string {
  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) {
    return timestamp
  }
  return `${timeFormat.format(date)} UTC`
}

function ActivityList({ items, onSelect }: ActivityListProps) {
  if (items.length === 0) {
    return <p className="activity-empty">No activity yet.</p>
  }

  return (
    <table className="activity-list">
      <thead>
        <tr>
          <th scope="col">Time</th>
          <th scope="col">Agent</th>
          <th scope="col">Tool</th>
          <th scope="col">Decision</th>
          <th scope="col">Details</th>
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.request_id}>
            <td>
              <time dateTime={item.timestamp}>{formatTime(item.timestamp)}</time>
            </td>
            <td>{item.agent_id}</td>
            <td>
              <code>{item.tool}</code>
            </td>
            <td>{decisionLabels[item.decision]}</td>
            <td>
              <button
                type="button"
                onClick={() => onSelect(item.request_id)}
                aria-label={`View request ${item.request_id}`}
              >
                View
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default ActivityList
