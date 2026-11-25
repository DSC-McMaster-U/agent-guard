import { afterEach, beforeEach, describe, expect, it, vi, type Mock } from 'vitest'

import type { ToolCallSummary } from '../types/toolCall'
import {
  TOOL_CALLS_PATH,
  ToolCallApiError,
  evaluateToolCall,
  getRecentToolCalls,
  type ToolCallApiErrorKind,
  type ToolCallRequest,
} from './toolCalls'

const request: ToolCallRequest = {
  request_id: 'req-001',
  agent_id: 'email-assistant',
  user_id: 'user-1',
  session_id: 'session-1',
  original_goal: 'Summarize my inbox',
  tool: 'send_email',
  arguments: { to: 'alice@example.com', subject: 'Hi', body: 'Hello' },
  trigger_source: { type: 'user_instruction', trust_level: 'trusted' },
}

const summary: ToolCallSummary = {
  request_id: 'req-001',
  agent_id: 'email-assistant',
  tool: 'send_email',
  arguments: { to: 'alice@example.com', subject: 'Hi', body: 'Hello' },
  decision: 'allow',
  reason: 'Recipient is on the allow list.',
  timestamp: '2026-11-23T12:00:00Z',
  approval_status: 'not_required',
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function abortError(): DOMException {
  return new DOMException('The operation was aborted.', 'AbortError')
}

type Call = (signal?: AbortSignal) => Promise<unknown>

const calls: Array<[string, Call]> = [
  ['evaluateToolCall', (signal) => evaluateToolCall(request, signal)],
  ['getRecentToolCalls', (signal) => getRecentToolCalls(signal)],
]

let fetchMock: Mock<typeof fetch>

beforeEach(() => {
  fetchMock = vi.fn<typeof fetch>()
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

describe('request contract', () => {
  it('POSTs the JSON request with the caller signal', async () => {
    fetchMock.mockResolvedValue(jsonResponse(summary))
    const controller = new AbortController()

    await evaluateToolCall(request, controller.signal)

    expect(fetchMock).toHaveBeenCalledTimes(1)
    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe(TOOL_CALLS_PATH)
    expect(url).toBe('/api/v1/tool-calls')
    expect(init?.method).toBe('POST')
    expect(init?.headers).toMatchObject({ 'Content-Type': 'application/json' })
    expect(JSON.parse(init?.body as string)).toEqual(request)
    expect(init?.signal).toBe(controller.signal)
  })

  it('GETs recent tool calls with the caller signal and no body', async () => {
    fetchMock.mockResolvedValue(jsonResponse([]))
    const controller = new AbortController()

    await getRecentToolCalls(controller.signal)

    const [url, init] = fetchMock.mock.calls[0]
    expect(url).toBe(TOOL_CALLS_PATH)
    expect(init?.method).toBe('GET')
    expect(init?.body).toBeUndefined()
    expect(init?.signal).toBe(controller.signal)
  })
})

describe('successful responses', () => {
  it('returns a valid POST summary', async () => {
    fetchMock.mockResolvedValue(jsonResponse(summary))
    await expect(evaluateToolCall(request)).resolves.toEqual(summary)
  })

  it('returns a valid GET list', async () => {
    const second = { ...summary, request_id: 'req-002', decision: 'block' }
    fetchMock.mockResolvedValue(jsonResponse([summary, second]))
    await expect(getRecentToolCalls()).resolves.toEqual([summary, second])
  })

  it('returns an empty GET list', async () => {
    fetchMock.mockResolvedValue(jsonResponse([]))
    await expect(getRecentToolCalls()).resolves.toEqual([])
  })

  it('drops fields outside the summary contract', async () => {
    const extra = { ...summary, user_id: 'user-1', internal_score: 0.9 }
    fetchMock.mockResolvedValueOnce(jsonResponse(extra))
    fetchMock.mockResolvedValueOnce(jsonResponse([extra]))

    const posted = await evaluateToolCall(request)
    const [listed] = await getRecentToolCalls()

    for (const result of [posted, listed]) {
      expect(result).toEqual(summary)
      expect(result).not.toHaveProperty('user_id')
      expect(result).not.toHaveProperty('internal_score')
    }
  })
})

describe('malformed responses', () => {
  const malformed: Array<[string, unknown]> = [
    ['unknown decision', { ...summary, decision: 'maybe' }],
    ['unknown approval status', { ...summary, approval_status: 'escalated' }],
    ['null arguments', { ...summary, arguments: null }],
    ['array arguments', { ...summary, arguments: ['to', 'alice@example.com'] }],
    ['unparseable timestamp', { ...summary, timestamp: 'yesterday-ish' }],
    ['missing timestamp', { ...summary, timestamp: undefined }],
  ]

  it.each(malformed)('rejects a POST summary with %s', async (_label, body) => {
    fetchMock.mockResolvedValue(jsonResponse(body))
    await expect(evaluateToolCall(request)).rejects.toMatchObject({
      name: 'ToolCallApiError',
      kind: 'malformed',
    })
  })

  it.each(malformed)('rejects a GET list where one member has %s', async (_label, body) => {
    fetchMock.mockResolvedValue(jsonResponse([summary, body]))
    await expect(getRecentToolCalls()).rejects.toMatchObject({ kind: 'malformed' })
  })

  it('rejects a GET body that is not an array', async () => {
    fetchMock.mockResolvedValue(jsonResponse(summary))
    await expect(getRecentToolCalls()).rejects.toMatchObject({ kind: 'malformed' })
  })

  it.each(calls)('%s rejects a 200 response with a non-JSON body', async (_name, call) => {
    fetchMock.mockResolvedValue(new Response('<html>ok</html>', { status: 200 }))
    await expect(call()).rejects.toMatchObject({ kind: 'malformed' })
  })
})

describe('HTTP error statuses', () => {
  const statuses: Array<[number, ToolCallApiErrorKind]> = [
    [409, 'conflict'],
    [422, 'validation'],
    [503, 'unavailable'],
    [502, 'unavailable'],
    [504, 'unavailable'],
    [500, 'http'],
  ]
  const cases = calls.flatMap(([name, call]) =>
    statuses.map(([status, kind]) => [name, status, kind, call] as const),
  )

  it.each(cases)('%s maps HTTP %i to %s', async (_name, status, kind, call) => {
    fetchMock.mockResolvedValue(jsonResponse({ detail: 'nope' }, status))
    const error = await call().catch((e: unknown) => e)
    expect(error).toBeInstanceOf(ToolCallApiError)
    expect(error).toMatchObject({ kind, status })
  })

  it.each(cases)('%s maps HTTP %i with a non-JSON body to %s', async (_name, status, kind, call) => {
    fetchMock.mockResolvedValue(new Response('<html>Bad Gateway</html>', { status }))
    await expect(call()).rejects.toMatchObject({ kind, status })
  })

  it('surfaces the first FastAPI validation message', async () => {
    fetchMock.mockResolvedValue(
      jsonResponse(
        {
          detail: [
            { loc: ['body', 'tool'], msg: 'Field required' },
            { loc: ['body', 'agent_id'], msg: 'Field required' },
          ],
        },
        422,
      ),
    )
    await expect(evaluateToolCall(request)).rejects.toMatchObject({
      kind: 'validation',
      message: 'body.tool: Field required (+1 more)',
    })
  })
})

describe('network failure and cancellation', () => {
  it.each(calls)('%s reports a network failure without a status', async (_name, call) => {
    fetchMock.mockRejectedValue(new TypeError('Failed to fetch'))
    await expect(call()).rejects.toMatchObject({ kind: 'network', status: null })
  })

  it.each(calls)('%s rethrows an AbortError raised before the response', async (_name, call) => {
    const controller = new AbortController()
    fetchMock.mockImplementation(
      (_input, init) =>
        new Promise((_resolve, reject) => {
          init?.signal?.addEventListener('abort', () => reject(abortError()))
        }),
    )

    const pending = call(controller.signal)
    controller.abort()

    const error = await pending.catch((e: unknown) => e)
    expect(error).not.toBeInstanceOf(ToolCallApiError)
    expect(error).toBeInstanceOf(DOMException)
    expect(error).toMatchObject({ name: 'AbortError' })
  })

  it.each(calls)('%s rethrows an AbortError raised while reading JSON', async (_name, call) => {
    const cancelled = abortError()
    const response = jsonResponse(summary)
    vi.spyOn(response, 'json').mockRejectedValue(cancelled)
    fetchMock.mockResolvedValue(response)

    await expect(call()).rejects.toBe(cancelled)
  })

  it('rethrows an AbortError raised while reading an error body', async () => {
    const cancelled = abortError()
    const response = jsonResponse({ detail: 'down' }, 503)
    vi.spyOn(response, 'json').mockRejectedValue(cancelled)
    fetchMock.mockResolvedValue(response)

    await expect(getRecentToolCalls()).rejects.toBe(cancelled)
  })
})
