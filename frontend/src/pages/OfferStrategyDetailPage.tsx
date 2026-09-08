import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetOfferStrategyQuery, useUpdateOfferStrategyMutation } from '@/features/offerStrategy/offerStrategyApi'

export default function OfferStrategyDetailPage() {
  const id = Number(useParams().id)
  const { data: offerStrategy, isLoading, error } = useGetOfferStrategyQuery(id)

  const [updateOfferStrategy, updateState] = useUpdateOfferStrategyMutation()

  return (
    <DetailShell
      title={(offerStrategy?.offer_name as string) ?? 'Offer strategy'}
      backTo={offerStrategy ? `/marketing-strategy/${offerStrategy.marketing_strategy_id}` : undefined}
      backLabel="← Marketing strategy"
      data={offerStrategy}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updateOfferStrategy({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
