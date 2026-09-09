import { Plus } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { EntityList } from '@/components/EntityList'
import {
  useDeleteOfferProfileMutation,
  useGenerateOfferProfileMutation,
  useListOfferProfileForOfferQuery,
  useUpdateOfferProfileMutation,
} from '@/features/offerProfiles/offerProfileApi'
import { useEditEntityPanel } from '@/lib/useEditEntityPanel'

export default function OfferProfilesPage() {
  const offerId = Number(useParams().offerId)
  const offer_profileList = useListOfferProfileForOfferQuery(offerId)
  const [generateOfferProfile, { isLoading: isGenerating }] = useGenerateOfferProfileMutation()
  const [deleteOfferProfile] = useDeleteOfferProfileMutation()
  const [updateOfferProfile] = useUpdateOfferProfileMutation()
  const editEntity = useEditEntityPanel()

  return (
    <div className="w-full p-6 lg:p-10">
      <EntityList
        title="OfferProfiles"
        eyebrow="Baza wiedzy"
        items={offer_profileList.data}
        isLoading={offer_profileList.isLoading}
        error={offer_profileList.error}
        linkTo={(item) => `/offer-profiles/${item.id}`}
        itemLabel={(item) => (item.offer_summary as string) ?? `OfferProfile #${item.id}`}
        emptyTitle="Brak bazy wiedzy"
        emptyDescription="Wygeneruj pierwszy element, aby rozpocząć pracę."
        onEdit={(item) => editEntity('OfferProfile', item, (fields) => updateOfferProfile({ id: item.id as number, fields }).unwrap())}
        onDelete={(item) => deleteOfferProfile({ id: item.id as number, offerId })}
        actions={
          <Button
            onClick={() => generateOfferProfile({ offerId })}
            disabled={isGenerating}
            className="h-10 rounded-none px-4"
          >
            <Plus className="size-4" />
            {isGenerating ? 'Generowanie…' : 'Generuj offer_profile'}
          </Button>
        }
      />
    </div>
  )
}
