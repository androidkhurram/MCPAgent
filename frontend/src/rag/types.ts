export type ChunkStrategy =
  | 'fixed-size'
  | 'overlap'
  | 'recursive'
  | 'semantic'
  | 'parent-child'
  | 'proposition'

export interface ChunkMetadata {
  strategy: ChunkStrategy
  parentId?: string
  role?: 'parent' | 'child'
  splitLevel?: 'heading' | 'paragraph' | 'sentence' | 'character'
  charCount: number
  embedded?: boolean
  label?: string
  propositionIndex?: number
  similarityToPrev?: number
}

export interface Chunk {
  id: string
  text: string
  start: number
  end: number
  metadata: ChunkMetadata
}

export interface SampleDocument {
  id: string
  title: string
  description: string
  bestStrategies: ChunkStrategy[]
  suggestedQuestions: string[]
  content: string
}

export interface ChunkOptions {
  chunkSize: number
  overlapPercent: number
  similarityThreshold: number
}

export const DEFAULT_CHUNK_OPTIONS: ChunkOptions = {
  chunkSize: 280,
  overlapPercent: 15,
  similarityThreshold: 0.25,
}
