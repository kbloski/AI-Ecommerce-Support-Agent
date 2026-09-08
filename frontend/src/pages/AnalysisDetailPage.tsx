import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { RelationCards } from '@/components/RelationCards'
import type { Entity } from '@/types'
import { useGetAnalysisQuery } from '@/features/analysis/analysisApi'
import { useListChecklistsForAnalysisQuery } from '@/features/checklists/checklistsApi'

export default function AnalysisDetailPage() {
  const { knowledgeId: knowledgeIdParam, analysisId: analysisIdParam } = useParams()
  const knowledgeId = Number(knowledgeIdParam)
  const analysisId = Number(analysisIdParam)

  const { data: analysis, isLoading, error } = useGetAnalysisQuery(analysisId)
  const checklists = useListChecklistsForAnalysisQuery(analysisId)

  return (
    <DetailShell
      title={`Analiza #${analysisId}`}
      backTo={`/knowledges/${knowledgeId}`}
      backLabel="← Knowledge"
      data={analysis}
      isLoading={isLoading}
      error={error}
      exclude={['analysis_questions']}
      overview={
        <RelationCards
          cards={[
            {
              id: 'checklists',
              label: 'Checklisty',
              count: checklists.data?.length ?? 0,
              to: `/knowledges/${knowledgeId}/analysis/${analysisId}/checklists`,
            },
            {
              id: 'resources',
              label: 'Zasoby',
              count: (analysis?.analysis_questions as Entity[] | undefined)?.length ?? 0,
              to: `/knowledges/${knowledgeId}/analysis/${analysisId}/questions`,
            },
          ]}
        />
      }
    />
  )
}
