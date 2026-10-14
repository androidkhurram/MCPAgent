import { useState } from 'react'
import { Chat } from './components/Chat'
import { HotelCards } from './components/HotelCards'
import { FlightCards } from './components/FlightCards'
import { McpToolsPanel } from './components/McpToolsPanel'
import { AgentTrace } from './components/AgentTrace'
import { ChunkingLab } from './components/ChunkingLab'
import {
  sendChatStream,
  sendFlightChatStream,
  type ChatMessage,
  type FlightCard,
  type HotelCard,
  type TraceEvent,
} from './api/client'
import './App.css'

const HOTEL_HINT =
  'Tell me where you want to go, your dates, and any room preferences.'

const FLIGHT_HINT =
  'Best flight ISB to JED next Friday under $700, prefer fewest stops.'

type AppView = 'hotels' | 'flights' | 'chunking'

function HotelFinderApp() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [hotels, setHotels] = useState<HotelCard[]>([])
  const [traces, setTraces] = useState<TraceEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [statusText, setStatusText] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleSend(text: string) {
    const nextMessages: ChatMessage[] = [...messages, { role: 'user', content: text }]
    setMessages(nextMessages)
    setLoading(true)
    setStatusText('Starting agent…')
    setError(null)
    setHotels([])
    setTraces([])

    try {
      const result = await sendChatStream(nextMessages, {
        onTrace: (trace) => {
          setTraces((prev) => [...prev, trace])
          if (
            trace.step === 'llm_request' ||
            trace.step === 'tool_call' ||
            trace.step === 'tool_result' ||
            trace.step === 'llm_response' ||
            trace.step === 'started'
          ) {
            setStatusText(trace.message)
          }
        },
        onStatus: (message) => setStatusText(message),
      })

      setMessages([
        ...nextMessages,
        { role: 'assistant', content: result.message || HOTEL_HINT },
      ])
      setHotels(result.hotels || [])
      if (result.traces?.length) setTraces(result.traces)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong'
      setError(message)
      setMessages([
        ...nextMessages,
        {
          role: 'assistant',
          content: `I could not complete that search. ${message}`,
        },
      ])
    } finally {
      setLoading(false)
      setStatusText(null)
    }
  }

  return (
    <>
      <header className="app-header">
        <p className="brand">Samiaa</p>
        <h1>Hotel Finder</h1>
        <p className="tagline">
          Natural-language hotel search powered by Azure AI Foundry and live Google
          results.
        </p>
      </header>

      <main className="app-main">
        <Chat
          messages={messages}
          loading={loading}
          statusText={statusText}
          onSend={handleSend}
          ariaLabel="Hotel finder chat"
          placeholder="Where and when do you want to stay?"
        />
        <aside className="results-panel">
          {error ? <p className="error-banner">{error}</p> : null}
          <AgentTrace traces={traces} loading={loading} />
          <HotelCards hotels={hotels} />
          {!hotels.length && !loading && !traces.length ? (
            <p className="results-placeholder">
              Hotel cards and live agent traces will appear here after a search.
            </p>
          ) : null}
        </aside>
      </main>
    </>
  )
}

function FlightBuddyApp() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [flights, setFlights] = useState<FlightCard[]>([])
  const [traces, setTraces] = useState<TraceEvent[]>([])
  const [loading, setLoading] = useState(false)
  const [statusText, setStatusText] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleSend(text: string) {
    const nextMessages: ChatMessage[] = [...messages, { role: 'user', content: text }]
    setMessages(nextMessages)
    setLoading(true)
    setStatusText('Starting Flight Buddy (MCP host)…')
    setError(null)
    setFlights([])
    setTraces([])

    try {
      const result = await sendFlightChatStream(nextMessages, {
        onTrace: (trace) => {
          setTraces((prev) => [...prev, trace])
          if (
            trace.step === 'mcp_connect' ||
            trace.step === 'mcp_tools' ||
            trace.step === 'llm_request' ||
            trace.step === 'tool_call' ||
            trace.step === 'tool_result' ||
            trace.step === 'llm_response' ||
            trace.step === 'started'
          ) {
            setStatusText(trace.message)
          }
        },
        onStatus: (message) => setStatusText(message),
      })

      setMessages([
        ...nextMessages,
        { role: 'assistant', content: result.message || FLIGHT_HINT },
      ])
      setFlights(result.flights || [])
      if (result.traces?.length) setTraces(result.traces)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong'
      setError(message)
      setMessages([
        ...nextMessages,
        {
          role: 'assistant',
          content: `I could not complete that flight search. ${message}`,
        },
      ])
    } finally {
      setLoading(false)
      setStatusText(null)
    }
  }

  return (
    <>
      <header className="app-header">
        <p className="brand">Samiaa · MCP</p>
        <h1>Flight Buddy</h1>
        <p className="tagline">
          Web agent host that calls an MCP server for live Google Flights via SerpApi.
        </p>
      </header>

      <main className="app-main">
        <Chat
          messages={messages}
          loading={loading}
          statusText={statusText}
          onSend={handleSend}
          emptyHint={`“${FLIGHT_HINT}”`}
          ariaLabel="Flight Buddy chat"
          placeholder="Origin, destination, date, budget…"
        />
        <aside className="results-panel">
          {error ? <p className="error-banner">{error}</p> : null}
          <McpToolsPanel />
          <AgentTrace traces={traces} loading={loading} />
          <FlightCards flights={flights} />
          {!flights.length && !loading && !traces.length ? (
            <p className="results-placeholder">
              Watch MCP connect → tools/list → search_flights → rank_flights in the
              trace panel.
            </p>
          ) : null}
        </aside>
      </main>
    </>
  )
}

function App() {
  const [view, setView] = useState<AppView>('flights')

  return (
    <div className={view === 'chunking' ? '' : 'app-shell'}>
      <nav
        className="app-nav"
        style={{ padding: view === 'chunking' ? '1.25rem 1.25rem 0' : undefined }}
      >
        <button
          type="button"
          className={view === 'flights' ? 'active' : ''}
          onClick={() => setView('flights')}
        >
          Flight Buddy (MCP)
        </button>
        <button
          type="button"
          className={view === 'hotels' ? 'active' : ''}
          onClick={() => setView('hotels')}
        >
          Hotel Finder
        </button>
        <button
          type="button"
          className={view === 'chunking' ? 'active' : ''}
          onClick={() => setView('chunking')}
        >
          RAG Chunking Lab
        </button>
      </nav>

      {view === 'flights' ? (
        <FlightBuddyApp />
      ) : view === 'hotels' ? (
        <HotelFinderApp />
      ) : (
        <ChunkingLab />
      )}
    </div>
  )
}

export default App
