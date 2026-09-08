import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetAdStrategyQuery, useUpdateAdStrategyMutation } from '@/features/adStrategy/adStrategyApi'

export default function AdStrategyDetailPage() {
  const id = Number(useParams().id)
  const { data: adStrategy, isLoading, error } = useGetAdStrategyQuery(id)

  const [updateAdStrategy, updateState] = useUpdateAdStrategyMutation()

  return (
    <DetailShell
      title="Ad strategy"
      backTo={adStrategy ? `/message-strategy/${adStrategy.message_strategy_id}` : undefined}
      backLabel="← Message strategy"
      data={adStrategy}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updateAdStrategy({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
