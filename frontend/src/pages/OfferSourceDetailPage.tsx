import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import {
  useGetOfferSourceQuery,
  useUpdateOfferSourceMutation,
} from '@/features/offerSources/offerSourceApi'


export default function OfferSourceDetailPage() {
  const offerSourceId = Number(useParams().offerSourceId)
  const { data: offer_source, isLoading, error } = useGetOfferSourceQuery(offerSourceId)


  const [updateOfferSource, updateOfferSourceState] = useUpdateOfferSourceMutation()

  return (
    <DetailShell
      title="OfferSource"
      backTo={offer_source ? `/offers/${offer_source.offer_id}` : undefined}
      backLabel="← Oferta"
      data={offer_source}
      isLoading={isLoading}
      error={error}
      exclude={['offer_facts']}
      editable={{
        exclude: ['offer_facts'],
        onSave: (fields) => updateOfferSource({ id: offerSourceId, fields }).unwrap(),
        isSaving: updateOfferSourceState.isLoading,
      }}
    />
  )
}
