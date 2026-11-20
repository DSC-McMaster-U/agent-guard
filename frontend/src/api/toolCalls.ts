import type {
  ApprovalStatus,
  ToolCallDecision,
  ToolCallSummary,
} from '../types/toolCall'

// Relative on purpose: the Vite dev server proxies /api to the local backend.
export const TOOL_CALLS_PATH = '/api/v1/tool-calls'

export type TriggerSourceType =
  | 'user_instruction'
  | 'untrusted_email_body'
  | 'untrusted_webpage'
  | 'untrusted_document'
  | 'tool_result'
  | 'unknown'

export type TrustLevel = 'trusted' | 'untrusted' | 'unknown'

// Mirrors backend/app/schemas.py TriggerSource. Every field has a server default.
export interface TriggerSource {
  type?: TriggerSourceType
  content?: string
  trust_level?: TrustLevel
}

// Mirrors backend/app/schemas.py ToolCallRequest. The backend rejects extra keys.
export interface ToolCallRequest {
  request_id: string
  agent_id: string
  user_id: string
  session_id: string
  original_goal: string
  tool: string
  arguments: Record<string, unknown>
  trigger_source?: TriggerSource | null
}

export type ToolCallApiErrorKind =
  | 'network'
  | 'validation'
  | 'conflict'
  | 'unavailable'
  | 'http'
  | 'malformed'

export class ToolCallApiError extends Error {
  readonly kind: ToolCallApiErrorKind
  readonly status: number | null

  constructor(kind: ToolCallApiErrorKind, message: string, status: number | null = null) {
    super(message)
    this.name = 'ToolCallApiError'
    this.kind = kind
    this.status = status
  }
}

const DECISIONS: readonly ToolCallDecision[] = ['allow', 'block', 'approval_required']
const APPROVAL_STATUSES: readonly ApprovalStatus[] = [
  'not_required',
  'pending',
  'approved',
  'denied',
]

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === 'string' && value.length > 0
}

export function isToolCallSummary(value: unknown): value is ToolCallSummary {
  if (!isRecord(value)) return false
  return (
    isNonEmptyString(value.request_id) &&
    isNonEmptyString(value.agent_id) &&
    isNonEmptyString(value.tool) &&
    isRecord(value.arguments) &&
    typeof value.decision === 'string' &&
    (DECISIONS as readonly string[]).includes(value.decision) &&
    typeof value.reason === 'string' &&
    isNonEmptyString(value.timestamp) &&
    !Number.isNaN(Date.parse(value.timestamp)) &&
    typeof value.approval_status === 'string' &&
    (APPROVAL_STATUSES as readonly string[]).includes(value.approval_status)
  )
}

// Copies only the contract keys so unexpected fields never reach the UI.
function toSummary(value: ToolCallSummary): ToolCallSummary {
  return {
    request_id: value.request_id,
    agent_id: value.agent_id,
    tool: value.tool,
    arguments: value.arguments,
    decision: value.decision,
    reason: value.reason,
    timestamp: value.timestamp,
    approval_status: value.approval_status,
  }
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === 'AbortError'
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json()
  } catch (error) {
    if (isAbortError(error)) throw error
    return undefined
  }
}

// FastAPI 422 bodies look like {"detail": [{"loc": [...], "msg": "..."}]}.
function describeValidationError(body: unknown): string {
  if (!isRecord(body)) return 'Request failed validation.'
  const { detail } = body
  if (typeof detail === 'string' && detail) return detail
  if (Array.isArray(detail) && detail.length > 0) {
    const first: unknown = detail[0]
    if (isRecord(first) && typeof first.msg === 'string') {
      const loc = Array.isArray(first.loc) ? first.loc.join('.') : ''
      const more = detail.length > 1 ? ` (+${detail.length - 1} more)` : ''
      return `${loc ? `${loc}: ` : ''}${first.msg}${more}`
    }
  }
  return 'Request failed validation.'
}

function errorForStatus(status: number, body: unknown): ToolCallApiError {
  switch (status) {
    case 422:
      return new ToolCallApiError('validation', describeValidationError(body), status)
    case 409:
      return new ToolCallApiError('conflict', 'A tool call with this request ID already exists.', status)
    // 502/504 are what the dev proxy returns when the backend is not running.
    case 502:
    case 503:
    case 504:
      return new ToolCallApiError('unavailable', 'The AgentGuard service is temporarily unavailable.', status)
    default:
      return new ToolCallApiError('http', `Unexpected response from AgentGuard (HTTP ${status}).`, status)
  }
}

async function requestJson(init: RequestInit): Promise<unknown> {
  let response: Response
  try {
    response = await fetch(TOOL_CALLS_PATH, init)
  } catch (error) {
    // Let callers ignore their own cancellations.
    if (isAbortError(error)) throw error
    throw new ToolCallApiError('network', 'Could not reach the AgentGuard API.')
  }

  const body = await readJson(response)
  if (!response.ok) throw errorForStatus(response.status, body)
  return body
}

export async function evaluateToolCall(
  request: ToolCallRequest,
  signal?: AbortSignal,
): Promise<ToolCallSummary> {
  const body = await requestJson({
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    signal,
  })
  if (!isToolCallSummary(body)) {
    throw new ToolCallApiError('malformed', 'AgentGuard returned an invalid tool call summary.')
  }
  return toSummary(body)
}

export async function getRecentToolCalls(signal?: AbortSignal): Promise<ToolCallSummary[]> {
  const body = await requestJson({
    method: 'GET',
    headers: { Accept: 'application/json' },
    signal,
  })
  if (!Array.isArray(body) || !body.every(isToolCallSummary)) {
    throw new ToolCallApiError('malformed', 'AgentGuard returned an invalid tool call list.')
  }
  return body.map(toSummary)
}
