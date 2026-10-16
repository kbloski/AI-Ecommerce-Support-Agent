import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetUgcCreativeQuery, useUpdateUgcCreativeMutation } from '@/features/ugcCreatives/ugcCreativesApi'

export default function UgcCreativeDetailPage() {
  const id = Number(useParams().id)
  const { data, isLoading, error } = useGetUgcCreativeQuery(id)
  const [update, { isLoading: isSaving }] = useUpdateUgcCreativeMutation()

  return (
    <DetailShell
      title={(data?.name as string) ?? 'UGC creative'}
      backTo={data ? `/offer-profiles/${data.offer_profile_id}` : undefined}
      backLabel="← Profil oferty"
      data={data}
      isLoading={isLoading}
      error={error}
      editable={{
        exclude: ['is_reviewed'],
        isSaving,
        onSave: (fields) => update({ id, offerProfileId: Number(data?.offer_profile_id), fields }).unwrap(),
      }}
    />
  )
}
