import { useMemo, useState } from 'react'
import { SAMPLE_DOCUMENTS } from '../rag/documents'
import { chunkDocument, STRATEGY_INFO } from '../rag/index'
import { chunkBorderColor, chunkColor } from '../rag/colors'
import type { Chunk, ChunkStrategy } from '../rag/types'
import { DEFAULT_CHUNK_OPTIONS } from '../rag/types'
import './ChunkingLab.css'

function buildHighlightedSegments(
  content: string,
  chunks: Chunk[],
  activeChunkId: string | null,
): { text: string; chunkId?: string; index?: number; active?: boolean }[] {
  const searchable = chunks.filter((c) => c.metadata.role !== 'parent')
  const sorted = [...searchable].sort((a, b) => a.start - b.start)
  const segments: { text: string; chunkId?: string; index?: number; active?: boolean }[] = []
  let cursor = 0

  sorted.forEach((chunk, index) => {
    if (chunk.start > cursor) {
      segments.push({ text: content.slice(cursor, chunk.start) })
    }
    segments.push({
      text: content.slice(chunk.start, chunk.end),
      chunkId: chunk.id,
      index,
      active: chunk.id === activeChunkId,
    })
    cursor = Math.max(cursor, chunk.end)
  })

  if (cursor < content.length) {
    segments.push({ text: content.slice(cursor) })
  }

  return segments
}

export function ChunkingLab() {
  const [documentId, setDocumentId] = useState(SAMPLE_DOCUMENTS[0]?.id ?? '')
  const [strategy, setStrategy] = useState<ChunkStrategy>('recursive')
  const [chunkSize, setChunkSize] = useState(DEFAULT_CHUNK_OPTIONS.chunkSize)
  const [overlapPercent, setOverlapPercent] = useState(DEFAULT_CHUNK_OPTIONS.overlapPercent)
  const [similarityThreshold, setSimilarityThreshold] = useState(
    DEFAULT_CHUNK_OPTIONS.similarityThreshold,
  )
  const [activeChunkId, setActiveChunkId] = useState<string | null>(null)

  const document = SAMPLE_DOCUMENTS.find((d) => d.id === documentId) ?? SAMPLE_DOCUMENTS[0]

  const result = useMemo(() => {
    if (!document) return { chunks: [], searchableCount: 0, parentCount: 0 }
    return chunkDocument(
      document.content,
      strategy,
      { chunkSize, overlapPercent, similarityThreshold },
      document.title,
    )
  }, [document, strategy, chunkSize, overlapPercent, similarityThreshold])

  const segments = useMemo(
    () => buildHighlightedSegments(document?.content ?? '', result.chunks, activeChunkId),
    [document, result.chunks, activeChunkId],
  )

  const parents = result.chunks.filter((c) => c.metadata.role === 'parent')
  const children = result.chunks.filter((c) => c.metadata.role === 'child')
  const regularChunks = result.chunks.filter((c) => !c.metadata.role)

  return (
    <div className="chunk-lab">
      <header className="chunk-lab-header">
        <div>
          <p className="brand">Samiaa Learning</p>
          <h1>RAG Chunking Lab</h1>
          <p className="tagline">
            Pick a document and chunking strategy. See exactly how text is split — all
            processing runs in your browser (no API yet).
          </p>
        </div>
      </header>

      <section className="chunk-lab-controls">
        <label className="control-field">
          <span>Document</span>
          <select
            value={documentId}
            onChange={(e) => {
              setDocumentId(e.target.value)
              setActiveChunkId(null)
            }}
          >
            {SAMPLE_DOCUMENTS.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.title}
              </option>
            ))}
          </select>
        </label>

        <label className="control-field">
          <span>Strategy</span>
          <select
            value={strategy}
            onChange={(e) => {
              setStrategy(e.target.value as ChunkStrategy)
              setActiveChunkId(null)
            }}
          >
            {(Object.keys(STRATEGY_INFO) as ChunkStrategy[]).map((key) => (
              <option key={key} value={key}>
                {STRATEGY_INFO[key].label}
              </option>
            ))}
          </select>
        </label>

        {(strategy === 'fixed-size' || strategy === 'overlap' || strategy === 'recursive') && (
          <label className="control-field">
            <span>Chunk size (chars): {chunkSize}</span>
            <input
              type="range"
              min={120}
              max={500}
              step={20}
              value={chunkSize}
              onChange={(e) => setChunkSize(Number(e.target.value))}
            />
          </label>
        )}

        {strategy === 'overlap' && (
          <label className="control-field">
            <span>Overlap: {overlapPercent}%</span>
            <input
              type="range"
              min={5}
              max={30}
              step={5}
              value={overlapPercent}
              onChange={(e) => setOverlapPercent(Number(e.target.value))}
            />
          </label>
        )}

        {strategy === 'semantic' && (
          <label className="control-field">
            <span>Similarity threshold: {similarityThreshold.toFixed(2)}</span>
            <input
              type="range"
              min={0.05}
              max={0.6}
              step={0.05}
              value={similarityThreshold}
              onChange={(e) => setSimilarityThreshold(Number(e.target.value))}
            />
          </label>
        )}
      </section>

      {document ? (
        <p className="doc-description">{document.description}</p>
      ) : null}
      <p className="strategy-hint">{STRATEGY_INFO[strategy].description}</p>

      <div className="chunk-lab-stats">
        <span>{result.chunks.length} total chunks</span>
        <span>{result.searchableCount} searchable (embedded)</span>
        {result.parentCount > 0 ? <span>{result.parentCount} parents (text only)</span> : null}
      </div>

      <div className="chunk-lab-grid">
        <section className="panel document-panel">
          <h2>Source document</h2>
          <div className="document-viewer">
            <pre className="document-highlighted">
              {segments.map((seg, i) =>
                seg.chunkId != null && seg.index != null ? (
                  <mark
                    key={`${seg.chunkId}-${i}`}
                    className={seg.active ? 'chunk-mark active' : 'chunk-mark'}
                    style={{
                      backgroundColor: chunkColor(seg.index),
                      borderBottom: `2px solid ${chunkBorderColor(seg.index)}`,
                    }}
                    onClick={() => setActiveChunkId(seg.chunkId ?? null)}
                  >
                    {seg.text}
                  </mark>
                ) : (
                  <span key={`plain-${i}`}>{seg.text}</span>
                ),
              )}
            </pre>
          </div>
        </section>

        <section className="panel chunks-panel">
          <h2>Chunks</h2>

          {strategy === 'parent-child' && parents.length > 0 ? (
            <div className="chunk-group">
              <h3>Parents (stored as text — not embedded)</h3>
              {parents.map((chunk) => (
                <ChunkCard
                  key={chunk.id}
                  chunk={chunk}
                  colorIndex={-1}
                  active={activeChunkId === chunk.id}
                  onSelect={() => setActiveChunkId(chunk.id)}
                  variant="parent"
                />
              ))}
            </div>
          ) : null}

          {strategy === 'parent-child' && children.length > 0 ? (
            <div className="chunk-group">
              <h3>Children (embedded for search)</h3>
              {children.map((chunk, index) => (
                <ChunkCard
                  key={chunk.id}
                  chunk={chunk}
                  colorIndex={index}
                  active={activeChunkId === chunk.id}
                  onSelect={() => setActiveChunkId(chunk.id)}
                />
              ))}
            </div>
          ) : null}

          {regularChunks.length > 0 ? (
            <div className="chunk-group">
              {strategy !== 'parent-child' ? <h3>All chunks</h3> : null}
              {regularChunks.map((chunk, index) => (
                <ChunkCard
                  key={chunk.id}
                  chunk={chunk}
                  colorIndex={index}
                  active={activeChunkId === chunk.id}
                  onSelect={() => setActiveChunkId(chunk.id)}
                />
              ))}
            </div>
          ) : null}
        </section>
      </div>

      {document?.suggestedQuestions.length ? (
        <section className="panel suggested-panel">
          <h2>Suggested questions (for later — retrieval step)</h2>
          <div className="question-chips">
            {document.suggestedQuestions.map((q) => (
              <span key={q} className="question-chip">
                {q}
              </span>
            ))}
          </div>
        </section>
      ) : null}
    </div>
  )
}

function ChunkCard({
  chunk,
  colorIndex,
  active,
  onSelect,
  variant = 'default',
}: {
  chunk: Chunk
  colorIndex: number
  active: boolean
  onSelect: () => void
  variant?: 'default' | 'parent'
}) {
  const displayText =
    chunk.metadata.strategy === 'proposition' ? chunk.text : chunk.text.trim()

  return (
    <button
      type="button"
      className={`chunk-card ${active ? 'active' : ''} ${variant}`}
      onClick={onSelect}
      style={
        variant === 'default' && colorIndex >= 0
          ? { borderLeftColor: chunkBorderColor(colorIndex) }
          : undefined
      }
    >
      <div className="chunk-card-head">
        <span className="chunk-id">{chunk.id}</span>
        {chunk.metadata.label ? (
          <span className="chunk-label">{chunk.metadata.label}</span>
        ) : null}
        {chunk.metadata.splitLevel ? (
          <span className="chunk-meta">{chunk.metadata.splitLevel}</span>
        ) : null}
        {chunk.metadata.embedded === false ? (
          <span className="chunk-badge muted">not embedded</span>
        ) : (
          <span className="chunk-badge">embedded</span>
        )}
      </div>
      <p className="chunk-text">{displayText}</p>
      <p className="chunk-range">
        chars {chunk.start}–{chunk.end} · {chunk.metadata.charCount} chars
        {chunk.metadata.similarityToPrev != null
          ? ` · sim to prev: ${chunk.metadata.similarityToPrev.toFixed(2)}`
          : ''}
        {chunk.metadata.parentId && chunk.metadata.role === 'child'
          ? ` · parent: ${chunk.metadata.parentId}`
          : ''}
      </p>
    </button>
  )
}
