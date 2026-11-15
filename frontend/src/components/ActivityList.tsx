import { useState } from 'react'
import type { ToolCallSummary } from '../types/toolCall'
import './ActivityList.css'

export interface ActivityListProps {
  items: ToolCallSummary[]
  onSelect: (requestId: string) => void
}

type ActivityFilter = 'all' | 'pending'

const filterOptions: { value: ActivityFilter; label: string }[] = [
  { value: 'all', label: 'All activity' },
  { value: 'pending', label: 'Pending approvals' },
]

function statusLabel(item: ToolCallSummary): string {
  switch (item.decision) {
    case 'allow':
      return 'Allowed'
    case 'block':
      return 'Blocked'
    case 'approval_required':
      switch (item.approval_status) {
        case 'approved':
          return 'Approved'
        case 'denied':
          return 'Denied'
        case 'pending':
          return 'Pending approval'
        default:
          return 'Approval required'
      }
  }
}

function isPendingApproval(item: ToolCallSummary): boolean {
  return (
    item.decision === 'approval_required' && item.approval_status === 'pending'
  )
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
  const [filter, setFilter] = useState<ActivityFilter>('all')

  const visibleItems =
    filter === 'pending' ? items.filter(isPendingApproval) : items

  let emptyMessage: string | null = null
  if (items.length === 0) {
    emptyMessage = 'No activity yet.'
  } else if (visibleItems.length === 0) {
    emptyMessage = 'No pending approvals.'
  }

  return (
    <div className="activity">
      <div
        className="activity-filter"
        role="group"
        aria-label="Filter activity"
      >
        {filterOptions.map((option) => (
          <button
            key={option.value}
            type="button"
            aria-pressed={filter === option.value}
            onClick={() => setFilter(option.value)}
          >
            {option.label}
          </button>
        ))}
      </div>
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
          {emptyMessage !== null ? (
            <tr>
              <td colSpan={5} className="activity-empty">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            visibleItems.map((item) => (
              <tr key={item.request_id}>
                <td>
                  <time dateTime={item.timestamp}>
                    {formatTime(item.timestamp)}
                  </time>
                </td>
                <td>{item.agent_id}</td>
                <td>
                  <code>{item.tool}</code>
                </td>
                <td>{statusLabel(item)}</td>
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
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}

export default ActivityList
