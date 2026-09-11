import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetCreativeExecutionSetupQuery, useUpdateCreativeExecutionSetupMutation } from '@/features/creativeExecutionSetup/creativeExecutionSetupApi'

export default function CreativeExecutionSetupDetailPage() {
  const id = Number(useParams().id)
  const { data, isLoading, error } = useGetCreativeExecutionSetupQuery(id)
  const [update, updateState] = useUpdateCreativeExecutionSetupMutation()

  return <DetailShell
    title={(data?.name as string) ?? 'Creative Execution Setup'}
    backTo={data ? `/ad-setup/${data.ad_setup_id}` : undefined}
    backLabel="← Ad Setup"
    data={data}
    includeRelationIds={['ad_framework_id', 'creative_angle_id', 'execution_style_id']}
    isLoading={isLoading}
    error={error}
    editable={{ onSave: (fields) => update({ id, fields }).unwrap(), isSaving: updateState.isLoading }}
  />
}
