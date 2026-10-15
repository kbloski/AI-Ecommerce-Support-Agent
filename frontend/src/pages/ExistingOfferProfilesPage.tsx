import { EntityList } from '@/components/EntityList'
import { useListAllOfferProfilesQuery } from '@/features/offerProfiles/offerProfilesApi'

export default function ExistingOfferProfilesPage() {
  const { data, isLoading, error } = useListAllOfferProfilesQuery()

  return (
    <div className="w-full p-6 lg:p-10">
      <EntityList
        title="Istniejące profile ofert"
        items={data}
        isLoading={isLoading}
        error={error}
        linkTo={(profile) => `/offer-profiles/${profile.id}`}
        itemMeta={(profile) => `Źródło oferty #${profile.offer_source_id}`}
        emptyTitle="Brak profili ofert"
        emptyDescription="Profile utworzysz na stronie źródła oferty."
      />
    </div>
  )
}
