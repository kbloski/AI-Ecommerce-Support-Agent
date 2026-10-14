import { useParams } from 'react-router-dom'
import { EntityList } from '@/components/EntityList'
import { Button } from '@/components/ui/button'
import { OfferProfileForm } from '@/features/offerProfiles/OfferProfileForm'
import { useSidePanel } from '@/lib/sidePanel'
import { useListOfferProfilesQuery, useDeleteOfferProfileMutation } from '@/features/offerProfiles/offerProfilesApi'

export default function OfferProfilesPage() {
  const offerSourceId = Number(useParams().offerSourceId)
  const { data, isLoading, error } = useListOfferProfilesQuery(offerSourceId)
  const { openPanel, closePanel } = useSidePanel()
  const [remove] = useDeleteOfferProfileMutation()
  return <div className="w-full p-6 lg:p-10"><EntityList title="Profile oferty" items={data} totalItems={data?.length} isLoading={isLoading} error={error}
    linkTo={(profile) => `/offer-profiles/${profile.id}`}
    onEdit={(profile) => openPanel({ title: 'Edytuj profil oferty', content: <OfferProfileForm offerSourceId={offerSourceId} profile={profile} onCreated={closePanel} /> })}
    onDelete={(profile) => remove({ id: profile.id as number, offerSourceId })}
    emptyTitle="Brak profili oferty" emptyDescription="Utwórz pierwszy profil, nadając mu nazwę."
    actions={<Button onClick={() => openPanel({ title: 'Utwórz profil oferty', content: <OfferProfileForm offerSourceId={offerSourceId} onCreated={closePanel} /> })}>Utwórz profil</Button>}
  /></div>
}

