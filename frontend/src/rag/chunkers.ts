import type { Chunk, ChunkOptions } from './types'

let chunkCounter = 0

export function resetChunkCounter(): void {
  chunkCounter = 0
}

export function nextChunkId(prefix: string): string {
  chunkCounter += 1
  return `${prefix}_${chunkCounter}`
}

export function makeChunk(
  prefix: string,
  text: string,
  start: number,
  end: number,
  metadata: Chunk['metadata'],
): Chunk {
  return {
    id: nextChunkId(prefix),
    text: text.trim(),
    start,
    end,
    metadata: {
      ...metadata,
      charCount: text.trim().length,
    },
  }
}

/** Split text on a regex but keep delimiter positions for offset tracking. */
export function splitWithOffsets(
  text: string,
  pattern: RegExp,
): { text: string; start: number; end: number }[] {
  const parts: { text: string; start: number; end: number }[] = []
  let lastIndex = 0
  const re = new RegExp(pattern.source, pattern.flags.includes('g') ? pattern.flags : pattern.flags + 'g')

  let match: RegExpExecArray | null
  while ((match = re.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({
        text: text.slice(lastIndex, match.index),
        start: lastIndex,
        end: match.index,
      })
    }
    parts.push({
      text: match[0],
      start: match.index,
      end: match.index + match[0].length,
    })
    lastIndex = match.index + match[0].length
  }

  if (lastIndex < text.length) {
    parts.push({
      text: text.slice(lastIndex),
      start: lastIndex,
      end: text.length,
    })
  }

  return parts.filter((p) => p.text.trim().length > 0)
}

export function splitSentences(text: string): { text: string; start: number; end: number }[] {
  const sentences: { text: string; start: number; end: number }[] = []
  const re = /[^.!?]+[.!?]+(?:\s+|$)|[^.!?]+$/g
  let match: RegExpExecArray | null
  while ((match = re.exec(text)) !== null) {
    const slice = match[0]
    if (slice.trim()) {
      sentences.push({
        text: slice,
        start: match.index,
        end: match.index + slice.length,
      })
    }
  }
  return sentences
}

export function splitParagraphs(text: string): { text: string; start: number; end: number }[] {
  const parts = text.split(/(\n\s*\n+)/)
  const result: { text: string; start: number; end: number }[] = []
  let offset = 0
  for (const part of parts) {
    if (part.trim()) {
      result.push({ text: part, start: offset, end: offset + part.length })
    }
    offset += part.length
  }
  return result
}

export function splitByHeadings(
  text: string,
): { heading: string; body: string; start: number; end: number }[] {
  const sections: { heading: string; body: string; start: number; end: number }[] = []
  const re = /^(#{1,3}\s+.+)$/gm
  const matches = [...text.matchAll(re)]

  if (matches.length === 0) {
    return [{ heading: '', body: text, start: 0, end: text.length }]
  }

  const preamble = text.slice(0, matches[0].index ?? 0).trim()
  if (preamble) {
    sections.push({
      heading: '(intro)',
      body: preamble,
      start: 0,
      end: matches[0].index ?? 0,
    })
  }

  for (let i = 0; i < matches.length; i += 1) {
    const start = matches[i].index ?? 0
    const end = i + 1 < matches.length ? (matches[i + 1].index ?? text.length) : text.length
    const block = text.slice(start, end)
    const lines = block.split('\n')
    const heading = lines[0]?.trim() ?? ''
    const body = lines.slice(1).join('\n').trim()
    sections.push({ heading, body: body || block, start, end })
  }

  return sections
}

export function fixedSizeChunks(
  text: string,
  strategy: Chunk['metadata']['strategy'],
  options: ChunkOptions,
): Chunk[] {
  const size = options.chunkSize
  const chunks: Chunk[] = []
  let start = 0

  while (start < text.length) {
    let end = Math.min(start + size, text.length)
    if (end < text.length) {
      const slice = text.slice(start, end)
      const lastSpace = slice.lastIndexOf(' ')
      if (lastSpace > size * 0.5) {
        end = start + lastSpace
      }
    }
    const chunkText = text.slice(start, end)
    if (chunkText.trim()) {
      chunks.push(
        makeChunk('fixed', chunkText, start, end, {
          strategy,
          splitLevel: 'character',
          charCount: chunkText.length,
          embedded: true,
        }),
      )
    }
    if (end >= text.length) break
    start = end
  }

  return chunks
}

export function overlapChunks(text: string, options: ChunkOptions): Chunk[] {
  const size = options.chunkSize
  const overlap = Math.floor(size * (options.overlapPercent / 100))
  const step = Math.max(size - overlap, 1)
  const chunks: Chunk[] = []
  let start = 0

  while (start < text.length) {
    let end = Math.min(start + size, text.length)
    if (end < text.length) {
      const slice = text.slice(start, end)
      const lastSpace = slice.lastIndexOf(' ')
      if (lastSpace > size * 0.5) {
        end = start + lastSpace
      }
    }
    const chunkText = text.slice(start, end)
    if (chunkText.trim()) {
      chunks.push(
        makeChunk('overlap', chunkText, start, end, {
          strategy: 'overlap',
          splitLevel: 'character',
          charCount: chunkText.length,
          embedded: true,
          label: overlap > 0 ? `overlap ${overlap} chars with previous` : undefined,
        }),
      )
    }
    if (end >= text.length) break
    start += step
  }

  return chunks
}

export function recursiveChunks(text: string, options: ChunkOptions): Chunk[] {
  const maxSize = options.chunkSize
  const chunks: Chunk[] = []

  function addChunk(
    chunkText: string,
    start: number,
    end: number,
    splitLevel: Chunk['metadata']['splitLevel'],
    label?: string,
  ) {
    if (!chunkText.trim()) return
    if (chunkText.length <= maxSize) {
      chunks.push(
        makeChunk('recursive', chunkText, start, end, {
          strategy: 'recursive',
          splitLevel,
          charCount: chunkText.length,
          embedded: true,
          label,
        }),
      )
      return
    }

    if (splitLevel !== 'paragraph') {
      const paragraphs = splitParagraphs(chunkText)
      if (paragraphs.length > 1) {
        for (const p of paragraphs) {
          addChunk(p.text, start + p.start, start + p.end, 'paragraph')
        }
        return
      }
    }

    if (splitLevel !== 'sentence') {
      const sentences = splitSentences(chunkText)
      if (sentences.length > 1) {
        for (const s of sentences) {
          addChunk(s.text, start + s.start, start + s.end, 'sentence')
        }
        return
      }
    }

    fixedSizeChunks(chunkText, 'recursive', options).forEach((c) => {
      chunks.push({
        ...c,
        start: start + c.start,
        end: start + c.end,
        metadata: { ...c.metadata, splitLevel: 'character' },
      })
    })
  }

  const sections = splitByHeadings(text)
  for (const section of sections) {
    const sectionText = section.heading
      ? `${section.heading}\n${section.body}`.trim()
      : section.body
    addChunk(
      sectionText,
      section.start,
      section.end,
      'heading',
      section.heading || undefined,
    )
  }

  return chunks
}

export function parentChildChunks(text: string): Chunk[] {
  const chunks: Chunk[] = []
  const sections = splitByHeadings(text)

  sections.forEach((section, index) => {
    const parentId = `parent_${index + 1}`
    const sectionText = section.heading
      ? `${section.heading}\n${section.body}`.trim()
      : section.body

    chunks.push(
      makeChunk(parentId, sectionText, section.start, section.end, {
        strategy: 'parent-child',
        role: 'parent',
        parentId,
        splitLevel: 'heading',
        charCount: sectionText.length,
        embedded: false,
        label: section.heading || '(intro)',
      }),
    )

    const bodyStart = section.heading
      ? section.start + section.heading.length + 1
      : section.start
    const sentences = splitSentences(section.body || sectionText)
    sentences.forEach((sentence) => {
      const absStart = section.heading ? bodyStart + sentence.start : section.start + sentence.start
      const absEnd = section.heading ? bodyStart + sentence.end : section.start + sentence.end
      chunks.push(
        makeChunk('child', sentence.text, absStart, absEnd, {
          strategy: 'parent-child',
          role: 'child',
          parentId,
          splitLevel: 'sentence',
          charCount: sentence.text.length,
          embedded: true,
          label: `→ ${parentId}`,
        }),
      )
    })
  })

  return chunks
}

/** Rule-based atomic facts: one sentence per chunk, prefixed for standalone readability. */
export function propositionChunks(text: string, subject: string): Chunk[] {
  const sentences = splitSentences(text)
  return sentences.map((sentence, index) => {
    const trimmed = sentence.text.trim()
    const standalone = ensureStandalone(trimmed, subject)
    return makeChunk('prop', standalone, sentence.start, sentence.end, {
      strategy: 'proposition',
      splitLevel: 'sentence',
      charCount: standalone.length,
      embedded: true,
      propositionIndex: index + 1,
      label: `atomic fact ${index + 1}`,
    })
  })
}

function ensureStandalone(sentence: string, subject: string): string {
  const lower = sentence.toLowerCase()
  const vague = /\b(it|this|that|they|these|those|the above)\b/i.test(sentence)
  const hasSubject = lower.includes(subject.toLowerCase().split(' ')[0] ?? '')
  if (vague || (!hasSubject && sentence.length < 120)) {
    return `${subject}: ${sentence.charAt(0).toLowerCase()}${sentence.slice(1)}`
  }
  return sentence
}
