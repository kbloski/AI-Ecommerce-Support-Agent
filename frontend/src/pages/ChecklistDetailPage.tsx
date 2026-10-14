import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetChecklistQuery } from '@/features/checklists/checklistsApi'

export default function ChecklistDetailPage() {
  const { offerSourceId: offerSourceIdParam, checklistId: checklistIdParam } =
    useParams()
  const offerSourceId = Number(offerSourceIdParam)
  const checklistId = Number(checklistIdParam)

  const { data, isLoading, error } = useGetChecklistQuery(checklistId)

  return (
    <DetailShell
      title={data?.name === 'analysis_checklist' ? `Checklista #${checklistId}` : (data?.name as string) ?? `Checklista #${checklistId}`}
      backTo={`/offer-sources/${offerSourceId}/checklists`}
      backLabel="← Checklisty"
      data={data}
      isLoading={isLoading}
      error={error}
      exclude={['checklist_items']}
    />
  )
}
