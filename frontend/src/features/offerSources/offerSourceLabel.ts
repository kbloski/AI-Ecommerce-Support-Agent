const MAX_LABEL_LENGTH = 100

/** Short label from offer_details: the first bullet (usually the product name), not the section header. */
export function offerSourceLabel(source: { id?: unknown; offer_details?: unknown } | undefined, fallback = 'OfferSource') {
  const id = source?.id != null ? ` #${source.id}` : ''
  const lines = String(source?.offer_details ?? '').split('\n').map((line) => line.trim()).filter(Boolean)
  const line = lines.find((item) => item.startsWith('- ')) ?? lines[0]
  if (!line) return `${fallback}${id}`
  const text = line.replace(/^-\s*/, '')
  return text.length > MAX_LABEL_LENGTH ? `${text.slice(0, MAX_LABEL_LENGTH)}…` : text
}
