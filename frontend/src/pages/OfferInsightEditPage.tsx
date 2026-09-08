import { useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { JsonPanelRegistration } from '@/components/JsonPanelRegistration'
import { useGetOfferInsightQuery, useUpdateOfferInsightMutation } from '@/features/offers/offersApi'
import { useListFactStatusesQuery } from '@/features/factStatus/factStatusApi'
import { useListReviewStatusesQuery } from '@/features/reviewStatus/reviewStatusApi'

export default function OfferInsightEditPage() {
  const id = Number(useParams().id)
  const navigate = useNavigate()

  const { data, isLoading, error } = useGetOfferInsightQuery(id)
  const { data: statuses } = useListFactStatusesQuery()
  const { data: reviewStatuses } = useListReviewStatusesQuery()
  const [updateOfferInsight, updateState] = useUpdateOfferInsightMutation()

  const [factStatus, setFactStatus] = useState<string | undefined>(undefined)
  const [reviewStatus, setReviewStatus] = useState<string | undefined>(undefined)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!data) return

    await updateOfferInsight({
      id,
      offerId: data.offer_id as number,
      fact_status: factStatus,
      review_status: reviewStatus,
    }).unwrap()

    navigate(`/offers/${data.offer_id}`)
  }

  return (
    <div className="w-full space-y-6 p-6 lg:p-10">
      <h1 className="text-2xl font-semibold">Edytuj insight oferty</h1>

      {data && (
        <JsonPanelRegistration data={data} title="JSON insightu oferty" />
      )}

      {isLoading && <p className="text-sm text-muted-foreground">Ładowanie…</p>}
      {Boolean(error) && <p className="text-sm text-destructive">Nie udało się pobrać danych.</p>}

      {data && (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <Label>Typ</Label>
            <p className="text-sm text-muted-foreground">{data.type as string}</p>
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

          <div className="space-y-1">
            <Label>Wartość</Label>
            <p className="text-sm whitespace-pre-wrap">{data.value as string}</p>
          </div>

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

          <div className="flex gap-2">
            <Button type="submit" disabled={updateState.isLoading}>
              {updateState.isLoading ? 'Zapisywanie…' : 'Zapisz'}
            </Button>
            <Button type="button" variant="black" onClick={() => navigate(`/offers/${data.offer_id}`)}>
              Anuluj
            </Button>
          </div>
        </form>
      )}
    </div>
  )
}
