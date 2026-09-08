import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import {
  useGetMessageStrategyQuery,
  useUpdateMessageStrategyMutation,
} from '@/features/messageStrategy/messageStrategyApi'

export default function MessageStrategyDetailPage() {
  const id = Number(useParams().id)
  const { data: messageStrategy, isLoading, error } = useGetMessageStrategyQuery(id)
  const [updateMessageStrategy, updateState] = useUpdateMessageStrategyMutation()

  return (
    <DetailShell
      title={(messageStrategy?.core_message as string) ?? 'Message strategy'}
      backTo={messageStrategy ? `/offer-strategy/${messageStrategy.offer_strategy_id}` : undefined}
      backLabel="← Offer strategy"
      data={messageStrategy}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updateMessageStrategy({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
