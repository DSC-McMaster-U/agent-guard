// @vitest-environment jsdom
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ToolCallSummary } from '../types/toolCall'
import ApprovalDetails from './ApprovalDetails'

const pending: ToolCallSummary = {
  request_id: 'req-pending',
  agent_id: 'assistant_1',
  tool: 'email.send',
  arguments: { recipient: 'partner@example.org', subject: 'Hello', body: 'Fictional body.' },
  decision: 'approval_required',
  reason: 'External recipient requires approval.',
  timestamp: '2026-11-03T18:10:00Z',
  approval_status: 'pending',
}

const approved: ToolCallSummary = { ...pending, request_id: 'req-approved', approval_status: 'approved' }

const blocked: ToolCallSummary = {
  ...pending,
  request_id: 'req-block',
  arguments: { recipient: 'blocked@example.net', subject: 'Hello', body: 'Fictional body.' },
  decision: 'block',
  reason: 'Recipient domain is blocked by policy.',
  approval_status: 'not_required',
}

afterEach(cleanup)

describe('ApprovalDetails', () => {
  it('offers Approve and Deny for a pending request and reports the chosen action', async () => {
    const user = userEvent.setup()
    const onDecision = vi.fn()
    render(<ApprovalDetails request={pending} onDecision={onDecision} />)

    expect(screen.getByRole('status').textContent).toBe('Pending approval')
    expect(screen.getByRole('button', { name: 'Deny' })).toBeTruthy()

    await user.click(screen.getByRole('button', { name: 'Approve' }))

    expect(onDecision).toHaveBeenCalledTimes(1)
    expect(onDecision).toHaveBeenCalledWith('req-pending', 'approve')
  })

  it.each([
    ['approved', approved, 'Approved'],
    ['blocked', blocked, 'Blocked'],
  ])('shows no action buttons for an %s request', (_label, request, status) => {
    const onDecision = vi.fn()
    render(<ApprovalDetails request={request} onDecision={onDecision} />)

    expect(screen.getByRole('status').textContent).toBe(status)
    expect(screen.queryAllByRole('button')).toEqual([])
    expect(onDecision).not.toHaveBeenCalled()
  })
})
