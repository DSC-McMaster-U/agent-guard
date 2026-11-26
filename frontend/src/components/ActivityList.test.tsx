// @vitest-environment jsdom
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'

import type { ToolCallSummary } from '../types/toolCall'
import ActivityList from './ActivityList'

function summary(overrides: Partial<ToolCallSummary>): ToolCallSummary {
  return {
    request_id: 'req-000',
    agent_id: 'assistant_1',
    tool: 'email.send',
    arguments: { recipient: 'teammate@example.com', subject: 'Hi', body: 'Hello' },
    decision: 'allow',
    reason: 'Internal recipient is allowed.',
    timestamp: '2026-11-03T18:00:00Z',
    approval_status: 'not_required',
    ...overrides,
  }
}

const allowed = summary({ request_id: 'req-allow' })
const blocked = summary({
  request_id: 'req-block',
  decision: 'block',
  reason: 'Recipient domain is blocked by policy.',
})
const pending = summary({
  request_id: 'req-pending',
  decision: 'approval_required',
  reason: 'External recipient requires approval.',
  approval_status: 'pending',
})
const approved = summary({
  request_id: 'req-approved',
  decision: 'approval_required',
  reason: 'External recipient requires approval.',
  approval_status: 'approved',
})

function visibleRequestIds(): string[] {
  return screen
    .queryAllByRole('button', { name: /^View request / })
    .map((button) => button.getAttribute('aria-label')!.replace('View request ', ''))
}

afterEach(cleanup)

describe('ActivityList', () => {
  it('shows every request until the pending filter is chosen', async () => {
    const user = userEvent.setup()
    render(<ActivityList items={[allowed, blocked, pending, approved]} onSelect={vi.fn()} />)

    expect(visibleRequestIds()).toEqual(['req-allow', 'req-block', 'req-pending', 'req-approved'])

    await user.click(screen.getByRole('button', { name: 'Pending approvals' }))

    expect(screen.getByRole('button', { name: 'Pending approvals' }).getAttribute('aria-pressed')).toBe('true')
    expect(visibleRequestIds()).toEqual(['req-pending'])
  })

  it('drops a request from the pending filter once it is rerendered as approved', async () => {
    const user = userEvent.setup()
    const onSelect = vi.fn()
    const { rerender } = render(<ActivityList items={[allowed, pending]} onSelect={onSelect} />)

    await user.click(screen.getByRole('button', { name: 'Pending approvals' }))
    expect(visibleRequestIds()).toEqual(['req-pending'])

    rerender(<ActivityList items={[allowed, { ...pending, approval_status: 'approved' }]} onSelect={onSelect} />)

    expect(visibleRequestIds()).toEqual([])
    expect(screen.getByText('No pending approvals.')).toBeTruthy()
  })
})
