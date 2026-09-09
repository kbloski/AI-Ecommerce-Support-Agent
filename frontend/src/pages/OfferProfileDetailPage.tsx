import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import {
  useGetOfferProfileQuery,
  useUpdateOfferProfileMutation,
} from '@/features/offerProfiles/offerProfileApi'
import {
  useDeleteTargetAudienceMutation,
  useUpdateTargetAudienceMutation,
} from '@/features/targetAudiences/targetAudiencesApi'

export default function OfferProfileDetailPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data: offer_profile, isLoading, error } = useGetOfferProfileQuery(offerProfileId)

  const [deleteTargetAudience] = useDeleteTargetAudienceMutation()
  const [updateTargetAudience] = useUpdateTargetAudienceMutation()

  const [updateOfferProfile, updateOfferProfileState] = useUpdateOfferProfileMutation()

  return (
    <DetailShell
      title="OfferProfile"
      backTo={offer_profile ? `/offers/${offer_profile.offer_id}` : undefined}
      backLabel="← Oferta"
      data={offer_profile}
      isLoading={isLoading}
      error={error}
      itemActions={{
        target_audiences: (item) => deleteTargetAudience({ id: item.id as number, offerProfileId }),
      }}
      itemStatusActions={{
        target_audiences: (item, factStatus) =>
          updateTargetAudience({
            id: item.id as number,
            offerProfileId,
            fact_status: factStatus,
          }).unwrap(),
      }}
      editable={{
        onSave: (fields) => updateOfferProfile({ id: offerProfileId, fields }).unwrap(),
        isSaving: updateOfferProfileState.isLoading,
      }}
    />
  )
}
