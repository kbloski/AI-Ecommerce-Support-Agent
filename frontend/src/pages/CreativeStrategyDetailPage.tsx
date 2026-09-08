import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import {
  useGetCreativeStrategyQuery,
  useUpdateCreativeStrategyMutation,
} from '@/features/creativeStrategy/creativeStrategyApi'

export default function CreativeStrategyDetailPage() {
  const id = Number(useParams().id)
  const { data: creativeStrategy, isLoading, error } = useGetCreativeStrategyQuery(id)

  const [updateCreativeStrategy, updateState] = useUpdateCreativeStrategyMutation()

  return (
    <DetailShell
      title={(creativeStrategy?.name as string) ?? 'Creative strategy'}
      backTo={creativeStrategy ? `/ad-strategy/${creativeStrategy.ad_strategy_id}` : undefined}
      backLabel="← Ad strategy"
      data={creativeStrategy}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updateCreativeStrategy({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
