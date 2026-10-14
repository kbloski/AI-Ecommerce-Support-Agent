import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import {
  useGetOfferSourceQuery,
  useUpdateOfferSourceMutation,
} from '@/features/offerSources/offerSourceApi'
import {
  useDeleteTargetAudienceMutation,
  useUpdateTargetAudienceMutation,
} from '@/features/targetAudiences/targetAudiencesApi'

export default function OfferSourceDetailPage() {
  const offerSourceId = Number(useParams().offerSourceId)
  const { data: offer_source, isLoading, error } = useGetOfferSourceQuery(offerSourceId)

  const [deleteTargetAudience] = useDeleteTargetAudienceMutation()
  const [updateTargetAudience] = useUpdateTargetAudienceMutation()

  const [updateOfferSource, updateOfferSourceState] = useUpdateOfferSourceMutation()

  return (
    <DetailShell
      title="OfferSource"
      backTo={offer_source ? `/offers/${offer_source.offer_id}` : undefined}
      backLabel="← Oferta"
      data={offer_source}
      isLoading={isLoading}
      error={error}
      itemActions={{
        target_audiences: (item) => deleteTargetAudience({ id: item.id as number, offerSourceId }),
      }}
      itemStatusActions={{
        target_audiences: (item, factStatus) =>
          updateTargetAudience({
            id: item.id as number,
            offerSourceId,
            fact_status: factStatus,
          }).unwrap(),
      }}
      editable={{
        onSave: (fields) => updateOfferSource({ id: offerSourceId, fields }).unwrap(),
        isSaving: updateOfferSourceState.isLoading,
      }}
    />
  )
}
