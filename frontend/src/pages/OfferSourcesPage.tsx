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
import { useEditEntityPanel } from '@/lib/useEditEntityPanel'

export default function OfferSourcesPage() {
  const offerId = Number(useParams().offerId)
  const offer_sourceList = useListOfferSourceForOfferQuery(offerId)
  const [generateOfferSource, { isLoading: isGenerating }] = useGenerateOfferSourceMutation()
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
        itemLabel={(item) => (item.offer_summary as string) ?? `OfferSource #${item.id}`}
        emptyTitle="Brak bazy wiedzy"
        emptyDescription="Wygeneruj pierwszy element, aby rozpocząć pracę."
        onEdit={(item) => editEntity('OfferSource', item, (fields) => updateOfferSource({ id: item.id as number, fields }).unwrap())}
        onDelete={(item) => deleteOfferSource({ id: item.id as number, offerId })}
        actions={
          <Button
            onClick={() => generateOfferSource({ offerId })}
            disabled={isGenerating}
            className="h-10 rounded-none px-4"
          >
            <Plus className="size-4" />
            {isGenerating ? 'Generowanie…' : 'Generuj offer_source'}
          </Button>
        }
      />
    </div>
  )
}
