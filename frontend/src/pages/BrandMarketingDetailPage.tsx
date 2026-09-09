import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetBrandMarketingQuery, useUpdateBrandMarketingMutation } from '@/features/brandMarketing/brandMarketingApi'

export default function BrandMarketingDetailPage() {
  const id = Number(useParams().id)
  const { data: brandMarketing, isLoading, error } = useGetBrandMarketingQuery(id)

  const [updateBrandMarketing, updateState] = useUpdateBrandMarketingMutation()

  return (
    <DetailShell
      title={(brandMarketing?.brand_name as string) ?? 'Brand marketing'}
      backTo={brandMarketing ? `/offer-profiles/${brandMarketing.offer_profile_id}` : undefined}
      backLabel="← OfferProfile"
      data={brandMarketing}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updateBrandMarketing({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
