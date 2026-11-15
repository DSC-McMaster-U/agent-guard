
import type { ToolCallSummary } from '../types/toolCall'

export const mockToolCalls: ToolCallSummary[] = [
  {
    request_id: 'req-001',
    agent_id: 'assistant_2',
    tool: 'email.send',
    arguments: {
      recipient: 'teammate@example.com',
      subject: 'Team Update',
      body: 'Here is the latest project update.'
    },
    decision: 'allow',
    reason: 'Internal recipient is allowed.',
    timestamp: '2026-11-03T18:00:00Z',
    approval_status: 'not_required'
  },
  {
    request_id: 'req-002',
    agent_id: 'assistant_2',
    tool: 'email.send',
    arguments: {
      recipient: 'blocked@example.net',
      subject: 'Project Information',
      body: 'This is a simulated blocked email.'
    },
    decision: 'block',
    reason: 'Recipient domain is blocked by policy.',
    timestamp: '2026-11-03T18:05:00Z',
    approval_status: 'not_required'
  },
  {
    request_id: 'req-003',
    agent_id: 'assistant_2',
    tool: 'email.send',
    arguments: {
      recipient: 'partner@example.org',
      subject: 'Collaboration Request',
      body: 'Would you like to discuss our project?'
    },
    decision: 'approval_required',
    reason: 'External recipient requires approval.',
    timestamp: '2026-11-03T18:10:00Z',
    approval_status: 'pending'
  }
]
