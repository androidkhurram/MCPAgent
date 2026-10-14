/** Base hues for chunk highlights — 40% opacity (hex alpha 0x66). */
const BASE_HUES = [
  '#0f6e6a',
  '#d9b48f',
  '#6b8cae',
  '#c47d5a',
  '#7a6b9e',
  '#4a8f6a',
  '#b85c5c',
  '#5c8ab8',
  '#9e7b4a',
  '#5a7a9e',
]

const HIGHLIGHT_OPACITY = '66' // 40% in 8-digit hex (#RRGGBBAA)

export const CHUNK_COLORS = BASE_HUES.map((hex) => `${hex}${HIGHLIGHT_OPACITY}`)

export function chunkColor(index: number): string {
  return CHUNK_COLORS[index % CHUNK_COLORS.length] ?? `#0f6e6a${HIGHLIGHT_OPACITY}`
}

export function chunkBorderColor(index: number): string {
  return BASE_HUES[index % BASE_HUES.length] ?? '#0f6e6a'
}
