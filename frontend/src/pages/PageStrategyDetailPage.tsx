import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetPageStrategyQuery, useUpdatePageStrategyMutation } from '@/features/pageStrategy/pageStrategyApi'

export default function PageStrategyDetailPage() {
  const id = Number(useParams().id)
  const { data: pageStrategy, isLoading, error } = useGetPageStrategyQuery(id)

  const [updatePageStrategy, updateState] = useUpdatePageStrategyMutation()

  return (
    <DetailShell
      title={(pageStrategy?.goal as string) ?? 'Page strategy'}
      backTo={pageStrategy ? `/message-strategy/${pageStrategy.message_strategy_id}` : undefined}
      backLabel="← Message strategy"
      data={pageStrategy}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updatePageStrategy({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
