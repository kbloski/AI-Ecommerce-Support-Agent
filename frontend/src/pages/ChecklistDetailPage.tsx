import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { RelationCards } from '@/components/RelationCards'
import { useGetChecklistQuery } from '@/features/checklists/checklistsApi'
import type { Entity } from '@/types'

export default function ChecklistDetailPage() {
  const { offerProfileId: offerProfileIdParam, analysisId: analysisIdParam, checklistId: checklistIdParam } =
    useParams()
  const offerProfileId = Number(offerProfileIdParam)
  const analysisId = Number(analysisIdParam)
  const checklistId = Number(checklistIdParam)

  const { data, isLoading, error } = useGetChecklistQuery(checklistId)

  return (
    <DetailShell
      title={(data?.name as string) ?? `Checklista #${checklistId}`}
      backTo={`/offer-profiles/${offerProfileId}/analysis/${analysisId}`}
      backLabel="← Analiza"
      data={data}
      isLoading={isLoading}
      error={error}
      exclude={['checklist_items']}
      overview={
        <RelationCards
          cards={[
            {
              id: 'items',
              label: 'Zadania',
              count: (data?.checklist_items as Entity[] | undefined)?.length ?? 0,
              to: `/offer-profiles/${offerProfileId}/analysis/${analysisId}/checklists/${checklistId}/items`,
            },
          ]}
        />
      }
    />
  )
}
