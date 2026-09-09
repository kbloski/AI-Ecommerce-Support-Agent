const LABEL_OVERRIDES: Record<string, string> = {
  id: 'ID',
  cta: 'CTA',
  knowledge_insights: 'Insights',
  fact_status: 'Status faktyczny',
  review_status: 'Weryfikacja statusu',
  target_audiences: 'Grupy docelowe',
  question: 'Pytanie',
  answer: 'Odpowiedź',
  score: 'Ocena',
  confidence: 'Pewność',
}

export function label(key: string): string {
  if (LABEL_OVERRIDES[key]) return LABEL_OVERRIDES[key]
  return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export function isPrimitive(value: unknown): value is string | number | boolean {
  return typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean'
}

/** Array-of-objects fields whose items carry their own `id` are relations (child entities with their own lifecycle), not plain JSON data. */
export function isRelationArray(value: unknown): value is Record<string, unknown>[] {
  return (
    Array.isArray(value) &&
    value.length > 0 &&
    value.every((item) => typeof item === 'object' && item !== null && 'id' in (item as object))
  )
}
