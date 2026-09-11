export const PAGE_REQUIREMENT_OPTIONS = [
  { value: 'required', label: 'Wymagana' },
  { value: 'optional', label: 'Opcjonalna' },
  { value: 'excluded', label: 'Wykluczona' },
] as const

export const PAGE_REQUIREMENT_LABELS: Record<string, string> = Object.fromEntries(
  PAGE_REQUIREMENT_OPTIONS.map((option) => [option.value, option.label]),
)

export interface PageSectionRequirement {
  page_section_type_id: string
  requirement_type: string
  position: number | null
}
