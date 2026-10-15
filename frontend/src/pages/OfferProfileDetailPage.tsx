import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { OfferProfileForm } from '@/features/offerProfiles/OfferProfileForm'
import { OfferProfileContextJsonPanel } from '@/features/offerProfiles/OfferProfileContextJsonPanel'
import { useGetOfferProfileQuery, useUpdateOfferProfileMutation } from '@/features/offerProfiles/offerProfilesApi'

export default function OfferProfileDetailPage() {
  const id = Number(useParams().offerProfileId)
  const { data, isLoading, error } = useGetOfferProfileQuery(id)
  const [update, updateState] = useUpdateOfferProfileMutation()
  const offerSourceId = Number(data?.offer_source_id)
  return <DetailShell title={String(data?.name ?? 'Profil oferty')} data={data} isLoading={isLoading} error={error} exclude={['additional_contexts']}
    jsonPanelContent={<OfferProfileContextJsonPanel offerProfileId={id} />}
    editable={data ? { onSave: (fields) => update({ id, offerSourceId, name: String(fields.name) }).unwrap(), isSaving: updateState.isLoading, content: (onSaved) => <OfferProfileForm offerSourceId={offerSourceId} profile={data} onCreated={onSaved} /> } : undefined}
  />
}
