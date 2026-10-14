import type { Chunk, ChunkOptions, ChunkStrategy } from './types'
import { DEFAULT_CHUNK_OPTIONS } from './types'
import {
  fixedSizeChunks,
  overlapChunks,
  parentChildChunks,
  propositionChunks,
  recursiveChunks,
  resetChunkCounter,
} from './chunkers'
import { semanticChunks } from './semantic'

export interface ChunkResult {
  chunks: Chunk[]
  searchableCount: number
  parentCount: number
}

export function chunkDocument(
  text: string,
  strategy: ChunkStrategy,
  options: ChunkOptions = DEFAULT_CHUNK_OPTIONS,
  subject = 'This policy',
): ChunkResult {
  resetChunkCounter()

  let chunks: Chunk[]
  switch (strategy) {
    case 'fixed-size':
      chunks = fixedSizeChunks(text, 'fixed-size', options)
      break
    case 'overlap':
      chunks = overlapChunks(text, options)
      break
    case 'recursive':
      chunks = recursiveChunks(text, options)
      break
    case 'semantic':
      chunks = semanticChunks(text, options)
      break
    case 'parent-child':
      chunks = parentChildChunks(text)
      break
    case 'proposition':
      chunks = propositionChunks(text, subject)
      break
    default:
      chunks = []
  }

  return {
    chunks,
    searchableCount: chunks.filter((c) => c.metadata.embedded !== false).length,
    parentCount: chunks.filter((c) => c.metadata.role === 'parent').length,
  }
}

export const STRATEGY_INFO: Record<
  ChunkStrategy,
  { label: string; description: string }
> = {
  'fixed-size': {
    label: 'Fixed-size',
    description: 'Split every N characters (breaks on word boundaries).',
  },
  overlap: {
    label: 'Overlap',
    description: 'Sliding window with shared text between adjacent chunks.',
  },
  recursive: {
    label: 'Recursive',
    description: 'Prefer headings → paragraphs → sentences → characters.',
  },
  semantic: {
    label: 'Semantic',
    description:
      'Split when sentence similarity drops (TF-IDF vectors in-browser). Try Company Update doc.',
  },
  'parent-child': {
    label: 'Parent–child',
    description: 'Section = parent (stored, not embedded). Sentences = children (embedded).',
  },
  proposition: {
    label: 'Proposition',
    description: 'One atomic fact per sentence, rewritten to stand alone.',
  },
}
