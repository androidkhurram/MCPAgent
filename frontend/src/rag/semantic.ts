import type { Chunk, ChunkOptions } from './types'
import { makeChunk, splitSentences } from './chunkers'

const STOP_WORDS = new Set([
  'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
  'her', 'was', 'one', 'our', 'out', 'day', 'has', 'him', 'his', 'how',
  'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy',
  'did', 'get', 'let', 'put', 'say', 'she', 'too', 'use', 'with', 'that',
  'this', 'from', 'they', 'have', 'been', 'will', 'your', 'than', 'them',
  'into', 'only', 'over', 'such', 'after', 'most', 'also', 'made', 'before',
  'when', 'what', 'were', 'there', 'their', 'about', 'which', 'would',
])

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter((w) => w.length > 2 && !STOP_WORDS.has(w))
}

type SparseVector = Map<string, number>

function buildTfidfVectors(sentences: string[]): SparseVector[] {
  const docs = sentences.map((s) => tokenize(s))
  const df = new Map<string, number>()

  for (const doc of docs) {
    const seen = new Set(doc)
    for (const word of seen) {
      df.set(word, (df.get(word) ?? 0) + 1)
    }
  }

  const n = docs.length
  return docs.map((doc) => {
    const tf = new Map<string, number>()
    for (const word of doc) {
      tf.set(word, (tf.get(word) ?? 0) + 1)
    }

    const vec: SparseVector = new Map()
    const len = Math.max(doc.length, 1)
    for (const [word, count] of tf) {
      const idf = Math.log((n + 1) / ((df.get(word) ?? 0) + 1)) + 1
      vec.set(word, (count / len) * idf)
    }
    return vec
  })
}

function cosineSimilarity(a: SparseVector, b: SparseVector): number {
  let dot = 0
  let normA = 0
  let normB = 0

  for (const val of a.values()) normA += val * val
  for (const val of b.values()) normB += val * val

  const smaller = a.size < b.size ? a : b
  const other = a.size < b.size ? b : a
  for (const [word, valA] of smaller) {
    const valB = other.get(word)
    if (valB != null) dot += valA * valB
  }

  if (normA === 0 || normB === 0) return 0
  return dot / (Math.sqrt(normA) * Math.sqrt(normB))
}

/**
 * Semantic chunking: vectorize each sentence (TF-IDF), then start a new chunk
 * when cosine similarity to the previous sentence drops below the threshold.
 * Browser-only — no API. Production systems use neural embedding models instead.
 */
export function semanticChunks(text: string, options: ChunkOptions): Chunk[] {
  const sentences = splitSentences(text)
  if (sentences.length === 0) return []
  if (sentences.length === 1) {
    const s = sentences[0]
    return [
      makeChunk('semantic', s.text, s.start, s.end, {
        strategy: 'semantic',
        splitLevel: 'sentence',
        charCount: s.text.length,
        embedded: true,
        label: 'single sentence',
      }),
    ]
  }

  const threshold = options.similarityThreshold
  const vectors = buildTfidfVectors(sentences.map((s) => s.text))
  const chunks: Chunk[] = []
  let groupStart = 0

  for (let i = 1; i <= sentences.length; i += 1) {
    const isLast = i === sentences.length
    let shouldSplit = isLast

    if (!isLast) {
      const sim = cosineSimilarity(vectors[i - 1], vectors[i])
      shouldSplit = sim < threshold
    }

    if (shouldSplit) {
      const group = sentences.slice(groupStart, i)
      const start = group[0].start
      const end = group[group.length - 1].end
      const chunkText = text.slice(start, end)

      const simToPrev =
        groupStart > 0
          ? cosineSimilarity(vectors[groupStart - 1], vectors[groupStart])
          : undefined

      const label =
        groupStart === 0
          ? 'topic start'
          : `topic break · sim ${simToPrev!.toFixed(2)} < ${threshold.toFixed(2)}`

      chunks.push(
        makeChunk('semantic', chunkText, start, end, {
          strategy: 'semantic',
          splitLevel: 'sentence',
          charCount: chunkText.length,
          embedded: true,
          label,
          similarityToPrev: simToPrev,
        }),
      )
      groupStart = i
    }
  }

  return chunks
}
