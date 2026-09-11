import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import {
  useGetPageContentPlanQuery,
  useUpdatePageContentPlanMutation,
} from '@/features/pageContentPlan/pageContentPlanApi'

export default function PageContentPlanDetailPage() {
  const id = Number(useParams().id)
  const { data: pageContentPlan, isLoading, error } = useGetPageContentPlanQuery(id)

  const [updatePageContentPlan, updateState] = useUpdatePageContentPlanMutation()

  return (
    <DetailShell
      title={(pageContentPlan?.name as string | undefined) ?? 'Page content plan'}
      backTo={pageContentPlan ? `/page-blueprint/${pageContentPlan.page_blueprint_id}` : undefined}
      backLabel="← Page blueprint"
      data={pageContentPlan}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updatePageContentPlan({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
