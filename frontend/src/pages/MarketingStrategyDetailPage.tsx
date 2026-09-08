import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import {
  useGetMarketingStrategyQuery,
  useUpdateMarketingStrategyMutation,
} from '@/features/marketingStrategy/marketingStrategyApi'

export default function MarketingStrategyDetailPage() {
  const id = Number(useParams().id)
  const { data: marketingStrategy, isLoading, error } = useGetMarketingStrategyQuery(id)

  const [updateMarketingStrategy, updateState] = useUpdateMarketingStrategyMutation()

  return (
    <DetailShell
      title="Marketing strategy"
      backTo={marketingStrategy ? `/brand-marketing/${marketingStrategy.brand_marketing_id}` : undefined}
      backLabel="← Brand marketing"
      data={marketingStrategy}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updateMarketingStrategy({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
