import { useEffect, useState } from 'react'

type McpTool = {
  name: string
  description: string
  parameters?: Record<string, unknown>
}

type McpInfo = {
  host: string
  client: string
  server: string
  tools: McpTool[]
  resources: { uri: string; name: string; description: string }[]
  prompts: { name: string; description: string }[]
}

export function McpToolsPanel() {
  const [info, setInfo] = useState<McpInfo | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const res = await fetch('/api/flights/mcp/tools')
        if (!res.ok) {
          const data = await res.json().catch(() => ({}))
          throw new Error(data.detail || `Failed (${res.status})`)
        }
        const data = (await res.json()) as McpInfo
        if (!cancelled) setInfo(data)
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Could not load MCP tools')
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <section className="mcp-panel" aria-label="MCP tools">
      <h2>MCP concepts (live)</h2>
      {loading ? <p className="results-placeholder">Discovering tools via MCP client…</p> : null}
      {error ? <p className="error-banner">{error}</p> : null}
      {info ? (
        <>
          <div className="mcp-roles">
            <div>
              <strong>Host</strong>
              <span>{info.host}</span>
            </div>
            <div>
              <strong>Client</strong>
              <span>{info.client}</span>
            </div>
            <div>
              <strong>Server</strong>
              <span>{info.server}</span>
            </div>
          </div>

          <h3>Tools (model can call)</h3>
          <ul className="mcp-tool-list">
            {info.tools.map((tool) => (
              <li key={tool.name}>
                <code>{tool.name}</code>
                <p>{tool.description}</p>
              </li>
            ))}
          </ul>

          {info.resources.length ? (
            <>
              <h3>Resources (read-only context)</h3>
              <ul className="mcp-tool-list">
                {info.resources.map((r) => (
                  <li key={r.uri}>
                    <code>{r.uri}</code>
                    <p>{r.description || r.name}</p>
                  </li>
                ))}
              </ul>
            </>
          ) : null}

          {info.prompts.length ? (
            <>
              <h3>Prompts (user workflows)</h3>
              <ul className="mcp-tool-list">
                {info.prompts.map((p) => (
                  <li key={p.name}>
                    <code>{p.name}</code>
                    <p>{p.description}</p>
                  </li>
                ))}
              </ul>
            </>
          ) : null}
        </>
      ) : null}
    </section>
  )
}
