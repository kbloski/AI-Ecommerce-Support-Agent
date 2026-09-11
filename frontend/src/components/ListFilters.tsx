import type { ReactNode } from 'react'

export type ReviewStatusFilterValue = '' | 'true' | 'false'
export type ReviewStatusSort = 'unreviewed_first' | 'reviewed_first'

interface ListFiltersProps {
  children: ReactNode
}

/** Shared layout for controls that narrow a list of entities. */
export function ListFilters({ children }: ListFiltersProps) {
  return <div className="flex flex-wrap items-center gap-3">{children}</div>
}

interface ReviewStatusFilterProps {
  value: ReviewStatusFilterValue
  onChange: (value: ReviewStatusFilterValue) => void
  ariaLabel?: string
}

/** Shared review-status filter used by lists whose entries require human review. */
export function ReviewStatusFilter({
  value,
  onChange,
  ariaLabel = 'Filtruj według sprawdzenia',
}: ReviewStatusFilterProps) {
  return (
    <select
      aria-label={ariaLabel}
      value={value}
      onChange={(event) => onChange(event.target.value as ReviewStatusFilterValue)}
      className="h-9 rounded-lg border border-input bg-transparent px-2.5 text-sm"
    >
      <option value="">Wszystkie</option>
      <option value="true">Sprawdzone</option>
      <option value="false">Nie sprawdzone</option>
    </select>
  )
}

interface ReviewStatusSortSelectProps {
  value: ReviewStatusSort
  onChange: (value: ReviewStatusSort) => void
}

/** Sorts reviewable entries by whether they still require human verification. */
export function ReviewStatusSortSelect({ value, onChange }: ReviewStatusSortSelectProps) {
  return (
    <select
      aria-label="Sortowanie według sprawdzenia"
      value={value}
      onChange={(event) => onChange(event.target.value as ReviewStatusSort)}
      className="h-9 rounded-lg border border-input bg-transparent px-2.5 text-sm"
    >
      <option value="unreviewed_first">Niesprawdzone na górze</option>
      <option value="reviewed_first">Sprawdzone na górze</option>
    </select>
  )
}
