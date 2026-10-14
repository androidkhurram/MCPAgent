export type ChatRole = 'user' | 'assistant'

export interface ChatMessage {
  role: ChatRole
  content: string
}

export interface HotelCard {
  name: string
  price_hint?: string | null
  rating?: string | null
  review_count?: number | null
  address?: string | null
  why?: string
  link?: string
  snippet?: string
}

export interface TraceEvent {
  type: 'trace'
  step: string
  message: string
  detail?: Record<string, unknown>
  ts?: number
}

export interface FlightCard {
  airline: string
  flight_numbers?: string
  from_airport?: string
  to_airport?: string
  departure_time?: string | null
  arrival_time?: string | null
  duration?: string | null
  stops?: number | null
  price?: string | null
  why?: string
  link?: string
}

export interface ChatResponse {
  message: string
  hotels: HotelCard[]
  status?: string | null
  traces?: TraceEvent[]
}

export interface FlightChatResponse {
  message: string
  flights: FlightCard[]
  status?: string | null
  traces?: TraceEvent[]
}

export type StreamHandlers = {
  onTrace?: (trace: TraceEvent) => void
  onStatus?: (message: string) => void
  onFinal?: (result: { message: string; hotels: HotelCard[] }) => void
  onError?: (message: string) => void
}

export type FlightStreamHandlers = {
  onTrace?: (trace: TraceEvent) => void
  onStatus?: (message: string) => void
  onFinal?: (result: { message: string; flights: FlightCard[] }) => void
  onError?: (message: string) => void
}

function parseSseChunk(buffer: string): { events: unknown[]; rest: string } {
  const parts = buffer.split('\n\n')
  const rest = parts.pop() ?? ''
  const events: unknown[] = []

  for (const part of parts) {
    const dataLines = part
      .split('\n')
      .filter((line) => line.startsWith('data:'))
      .map((line) => line.slice(5).trimStart())
    if (!dataLines.length) continue
    const raw = dataLines.join('\n')
    try {
      events.push(JSON.parse(raw))
    } catch {
      // ignore malformed SSE payloads
    }
  }

  return { events, rest }
}

export async function sendChatStream(
  messages: ChatMessage[],
  handlers: StreamHandlers = {},
): Promise<ChatResponse> {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({ messages }),
  })

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const data = await response.json()
      if (typeof data?.detail === 'string') detail = data.detail
    } catch {
      // ignore
    }
    throw new Error(detail)
  }

  if (!response.body) {
    throw new Error('Streaming response body is empty')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  const traces: TraceEvent[] = []
  let message = ''
  let hotels: HotelCard[] = []
  let status: string | null = null
  let streamError: string | null = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parsed = parseSseChunk(buffer)
    buffer = parsed.rest

    for (const event of parsed.events) {
      if (!event || typeof event !== 'object') continue
      const data = event as Record<string, unknown>
      const type = data.type

      if (type === 'trace') {
        const trace = data as unknown as TraceEvent
        traces.push(trace)
        handlers.onTrace?.(trace)
      } else if (type === 'status' && typeof data.message === 'string') {
        status = data.message
        handlers.onStatus?.(data.message)
      } else if (type === 'final') {
        message = typeof data.message === 'string' ? data.message : ''
        hotels = Array.isArray(data.hotels) ? (data.hotels as HotelCard[]) : []
        handlers.onFinal?.({ message, hotels })
      } else if (type === 'error') {
        streamError =
          typeof data.message === 'string' ? data.message : 'Unknown stream error'
        handlers.onError?.(streamError)
      }
    }
  }

  if (streamError) {
    throw new Error(streamError)
  }

  return { message, hotels, status, traces }
}

export async function sendFlightChatStream(
  messages: ChatMessage[],
  handlers: FlightStreamHandlers = {},
): Promise<FlightChatResponse> {
  const response = await fetch('/api/flights/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify({ messages }),
  })

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const data = await response.json()
      if (typeof data?.detail === 'string') detail = data.detail
    } catch {
      // ignore
    }
    throw new Error(detail)
  }

  if (!response.body) {
    throw new Error('Streaming response body is empty')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  const traces: TraceEvent[] = []
  let message = ''
  let flights: FlightCard[] = []
  let status: string | null = null
  let streamError: string | null = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parsed = parseSseChunk(buffer)
    buffer = parsed.rest

    for (const event of parsed.events) {
      if (!event || typeof event !== 'object') continue
      const data = event as Record<string, unknown>
      const type = data.type

      if (type === 'trace') {
        const trace = data as unknown as TraceEvent
        traces.push(trace)
        handlers.onTrace?.(trace)
      } else if (type === 'status' && typeof data.message === 'string') {
        status = data.message
        handlers.onStatus?.(data.message)
      } else if (type === 'final') {
        message = typeof data.message === 'string' ? data.message : ''
        flights = Array.isArray(data.flights) ? (data.flights as FlightCard[]) : []
        handlers.onFinal?.({ message, flights })
      } else if (type === 'error') {
        streamError =
          typeof data.message === 'string' ? data.message : 'Unknown stream error'
        handlers.onError?.(streamError)
      }
    }
  }

  if (streamError) {
    throw new Error(streamError)
  }

  return { message, flights, status, traces }
}
