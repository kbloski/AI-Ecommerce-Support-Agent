import { useState, type FormEvent } from 'react'
import { Plus } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { EntityList } from '@/components/EntityList'
import {
  useDeleteOfferSourceMutation,
  useGenerateOfferSourceMutation,
  useListOfferSourceForOfferQuery,
  useUpdateOfferSourceMutation,
} from '@/features/offerSources/offerSourceApi'
import { offerSourceLabel } from '@/features/offerSources/offerSourceLabel'
import { useEditEntityPanel } from '@/lib/useEditEntityPanel'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'

export default function OfferSourcesPage() {
  const offerId = Number(useParams().offerId)
  const offer_sourceList = useListOfferSourceForOfferQuery(offerId)
  const { openPanel, closePanel } = useSidePanel()
  const [deleteOfferSource] = useDeleteOfferSourceMutation()
  const [updateOfferSource] = useUpdateOfferSourceMutation()
  const editEntity = useEditEntityPanel()

  return (
    <div className="w-full p-6 lg:p-10">
      <EntityList
        title="OfferSources"
        eyebrow="Baza wiedzy"
        items={offer_sourceList.data}
        isLoading={offer_sourceList.isLoading}
        error={offer_sourceList.error}
        linkTo={(item) => `/offer-sources/${item.id}`}
        itemLabel={(item) => offerSourceLabel(item)}
        emptyTitle="Brak bazy wiedzy"
        emptyDescription="Wygeneruj pierwszy element, aby rozpocząć pracę."
        onEdit={(item) => editEntity('OfferSource', item, (fields) => updateOfferSource({ id: item.id as number, fields }).unwrap())}
        onDelete={(item) => deleteOfferSource({ id: item.id as number, offerId })}
        actions={
          <Button
            onClick={() => openPanel({ title: 'Generuj offer_source', content: <GenerateOfferSourceForm offerId={offerId} onSaved={closePanel} /> })}
            className="h-10 rounded-none px-4"
          >
            <Plus className="size-4" />
            Generuj offer_source
          </Button>
        }
      />
    </div>
  )
}

function GenerateOfferSourceForm({ offerId, onSaved }: { offerId: number; onSaved: () => void }) {
  const [generate, { isLoading }] = useGenerateOfferSourceMutation()
  const [error, setError] = useState('')

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const generationInstructions = String(form.get('generation_instructions') ?? '').trim()
    setError('')
    try {
      await generate({ offerId, generationInstructions }).unwrap()
      onSaved()
    } catch {
      setError('Nie udało się wygenerować offer source. Spróbuj ponownie.')
    }
  }

  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2">
      <span className="text-sm font-medium">Wskazówki do generowania (opcjonalnie)</span>
      <Textarea name="generation_instructions" maxLength={4000} rows={5} placeholder="Np. zwróć szczególną uwagę na materiały, parametry techniczne i warunki zakupu." />
    </label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={isLoading}>{isLoading ? 'Generowanie…' : 'Generuj offer_source'}</Button>
  </form>
}
