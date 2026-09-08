import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetAdExecutionQuery, useUpdateAdExecutionMutation } from '@/features/adExecution/adExecutionApi'

export default function AdExecutionDetailPage() {
  const id = Number(useParams().id)
  const { data, isLoading, error } = useGetAdExecutionQuery(id)

  const [updateAdExecution, updateState] = useUpdateAdExecutionMutation()
  const displayData = data
    ? {
        ...data,
        format:
          typeof data.format === 'string'
            ? data.format.replace(/\bvideo\b\s*/i, '').trim()
            : data.format,
      }
    : undefined

  return (
    <DetailShell
      title={(data?.name as string) ?? 'Ad execution'}
      backTo={data ? `/creative-strategy/${data.creative_strategy_id}` : undefined}
      backLabel="← Creative strategy"
      data={displayData}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updateAdExecution({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
