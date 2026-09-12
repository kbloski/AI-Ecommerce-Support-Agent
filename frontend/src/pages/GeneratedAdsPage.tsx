import { EntityList } from '@/components/EntityList'
import { useListAllGenerateAdsQuery } from '@/features/generateAd/generateAdApi'

export default function GeneratedAdsPage() {
  const { data, isLoading, error } = useListAllGenerateAdsQuery()

  return (
    <div className="w-full space-y-8 p-6 lg:p-10">
      <EntityList
        title="Wygenerowane reklamy"
        items={data}
        isLoading={isLoading}
        error={error}
        linkTo={(ad) => `/generate-ad/${ad.id}`}
        itemLabel={(ad) => (ad.name as string) ?? `Reklama #${ad.id}`}
        itemMeta={(ad) => `Creative Execution Setup #${ad.creative_execution_setup_id}`}
        emptyTitle="Brak wygenerowanych reklam"
        emptyDescription="Wygenerowane reklamy ze wszystkich źródeł pojawią się tutaj."
      />
    </div>
  )
}
