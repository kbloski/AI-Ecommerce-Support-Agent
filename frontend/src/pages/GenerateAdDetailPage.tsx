import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import {
  useGetGenerateAdQuery,
  useUpdateGenerateAdMutation,
} from '@/features/generateAd/generateAdApi'

export default function GenerateAdDetailPage() {
  const id = Number(useParams().id)
  const { data, isLoading, error } = useGetGenerateAdQuery(id)
  const [updateGenerateAd, updateState] = useUpdateGenerateAdMutation()

  return (
    <DetailShell
      title="Generate Ad"
      backTo={data ? `/creative-execution-setup/${data.creative_execution_setup_id}` : undefined}
      backLabel="← Creative Execution Setup"
      data={data}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updateGenerateAd({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
