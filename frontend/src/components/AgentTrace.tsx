import type { TraceEvent } from '../api/client'

interface AgentTraceProps {
  traces: TraceEvent[]
  loading?: boolean
}

function formatDetail(detail?: Record<string, unknown>): string | null {
  if (!detail || !Object.keys(detail).length) return null
  try {
    return JSON.stringify(detail, null, 2)
  } catch {
    return String(detail)
  }
}

export function AgentTrace({ traces, loading }: AgentTraceProps) {
  if (!traces.length && !loading) return null

  return (
    <section className="agent-trace" aria-label="Agent traces">
      <div className="agent-trace-header">
        <h2>Agent trace</h2>
        {loading ? <span className="trace-live">Live</span> : null}
      </div>
      {!traces.length && loading ? (
        <p className="trace-waiting">Waiting for first step…</p>
      ) : (
        <ol className="trace-list">
          {traces.map((trace, index) => {
            const detail = formatDetail(trace.detail)
            return (
              <li key={`${trace.step}-${trace.ts ?? index}`} className="trace-item">
                <div className="trace-meta">
                  <span className={`trace-step step-${trace.step}`}>{trace.step}</span>
                  {typeof trace.ts === 'number' ? (
                    <time dateTime={new Date(trace.ts * 1000).toISOString()}>
                      {new Date(trace.ts * 1000).toLocaleTimeString()}
                    </time>
                  ) : null}
                </div>
                <p className="trace-message">{trace.message}</p>
                {detail ? <pre className="trace-detail">{detail}</pre> : null}
              </li>
            )
          })}
        </ol>
      )}
    </section>
  )
}
