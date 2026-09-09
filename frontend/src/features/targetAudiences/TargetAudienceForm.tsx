import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  useUpdateTargetAudienceMutation,
  type UpdateTargetAudienceArgs,
} from '@/features/targetAudiences/targetAudiencesApi'
import { useListFactStatusesQuery } from '@/features/factStatus/factStatusApi'
import { useListReviewStatusesQuery } from '@/features/reviewStatus/reviewStatusApi'
import type { Entity } from '@/types'

const LIST_FIELDS = [
  'lifestyles',
  'values',
  'pain_points',
  'motivations',
  'buying_triggers',
  'objections',
  'message_angles',
  'marketing_channels',
] as const

const TEXT_FIELDS = [
  'name',
  'gender',
  'location',
  'purchasing_power',
  'awareness_level',
  'price_sensitivity',
  'research_level',
  'decision_time',
] as const

const NUMBER_FIELDS = ['score', 'confidence', 'age_min', 'age_max'] as const

function toJson(value: unknown): string {
  return JSON.stringify(Array.isArray(value) ? value : [], null, 2)
}

function label(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

/** Shared "edit target audience" form used both on its detail page and from any list that shows target audiences. */
export function EditTargetAudienceForm({
  id,
  data,
  onSaved,
}: {
  id: number
  data: Entity
  onSaved: () => void
}) {
  const { data: statuses } = useListFactStatusesQuery()
  const { data: reviewStatuses } = useListReviewStatusesQuery()
  const [updateTargetAudience, updateState] = useUpdateTargetAudienceMutation()

  const [factStatus, setFactStatus] = useState<string | undefined>(undefined)
  const [reviewStatus, setReviewStatus] = useState<string | undefined>(undefined)
  const [formError, setFormError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setFormError(null)

    const formData = new FormData(e.currentTarget)

    const payload: UpdateTargetAudienceArgs = { id, offerProfileId: data.offer_profile_id as number }

    if (factStatus) payload.fact_status = factStatus
    if (reviewStatus) payload.review_status = reviewStatus

    for (const field of TEXT_FIELDS) {
      const raw = formData.get(field)
      if (raw !== null) payload[field] = String(raw)
    }

    payload.reason = String(formData.get('reason') ?? '')

    for (const field of NUMBER_FIELDS) {
      const raw = formData.get(field)
      if (raw !== null && raw !== '') payload[field] = Number(raw)
    }

    for (const field of LIST_FIELDS) {
      const raw = String(formData.get(field) ?? '')
      try {
        const parsed: unknown = JSON.parse(raw)
        if (!Array.isArray(parsed)) {
          setFormError(`Pole „${label(field)}” musi zawierać tablicę JSON.`)
          return
        }
        payload[field] = parsed
      } catch {
        setFormError(`Pole „${label(field)}” zawiera nieprawidłowy JSON.`)
        return
      }
    }

    try {
      await updateTargetAudience(payload).unwrap()
      onSaved()
    } catch {
      setFormError('Nie udało się zapisać grupy docelowej.')
    }
  }

  return (
    <form onSubmit={(event) => void handleSubmit(event)} className="space-y-4">
      <div className="space-y-1">
        <Label htmlFor="fact_status">Status faktu</Label>
        <Select
          value={factStatus ?? (data.fact_status as string)}
          onValueChange={(value) => {
            if (value !== null) setFactStatus(value)
          }}
        >
          <SelectTrigger id="fact_status">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {statuses?.map((status) => (
              <SelectItem key={status.value} value={status.value}>
                {status.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-1">
        <Label htmlFor="review_status">Status weryfikacji</Label>
        <Select
          value={reviewStatus ?? (data.review_status as string)}
          onValueChange={(value) => {
            if (value !== null) setReviewStatus(value)
          }}
        >
          <SelectTrigger id="review_status">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {reviewStatuses?.map((status) => (
              <SelectItem key={status.value} value={status.value}>
                {status.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {TEXT_FIELDS.map((field) => (
        <div key={field} className="space-y-1">
          <Label htmlFor={field}>{label(field)}</Label>
          <Input id={field} name={field} defaultValue={(data[field] as string) ?? ''} />
        </div>
      ))}

      <div className="space-y-1">
        <Label htmlFor="reason">Reason</Label>
        <Textarea id="reason" name="reason" defaultValue={(data.reason as string) ?? ''} />
      </div>

      <div className="grid grid-cols-2 gap-4">
        {NUMBER_FIELDS.map((field) => (
          <div key={field} className="space-y-1">
            <Label htmlFor={field}>{label(field)}</Label>
            <Input
              id={field}
              name={field}
              type="number"
              defaultValue={(data[field] as number | undefined)?.toString() ?? ''}
            />
          </div>
        ))}
      </div>

      {LIST_FIELDS.map((field) => (
        <div key={field} className="space-y-1">
          <Label htmlFor={field}>{label(field)} (JSON)</Label>
          <Textarea
            id={field}
            name={field}
            defaultValue={toJson(data[field])}
            rows={5}
            className="font-mono"
          />
        </div>
      ))}

      {formError && <p className="text-sm text-destructive">{formError}</p>}

      <Button type="submit" disabled={updateState.isLoading}>
        {updateState.isLoading ? 'Zapisywanie…' : 'Zapisz'}
      </Button>
    </form>
  )
}
