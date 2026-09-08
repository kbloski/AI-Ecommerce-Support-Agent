import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { RelationCards } from '@/components/RelationCards'
import { useGetChecklistQuery } from '@/features/checklists/checklistsApi'
import type { Entity } from '@/types'

export default function ChecklistDetailPage() {
  const { knowledgeId: knowledgeIdParam, analysisId: analysisIdParam, checklistId: checklistIdParam } =
    useParams()
  const knowledgeId = Number(knowledgeIdParam)
  const analysisId = Number(analysisIdParam)
  const checklistId = Number(checklistIdParam)

  const { data, isLoading, error } = useGetChecklistQuery(checklistId)

  return (
    <DetailShell
      title={(data?.name as string) ?? `Checklista #${checklistId}`}
      backTo={`/knowledges/${knowledgeId}/analysis/${analysisId}`}
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
              to: `/knowledges/${knowledgeId}/analysis/${analysisId}/checklists/${checklistId}/items`,
            },
          ]}
        />
      }
    />
  )
}
