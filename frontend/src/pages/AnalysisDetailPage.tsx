import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { RelationCards } from '@/components/RelationCards'
import type { Entity } from '@/types'
import { useGetAnalysisQuery } from '@/features/analysis/analysisApi'
import { useListChecklistsForAnalysisQuery } from '@/features/checklists/checklistsApi'

export default function AnalysisDetailPage() {
  const { offerProfileId: offerProfileIdParam, analysisId: analysisIdParam } = useParams()
  const offerProfileId = Number(offerProfileIdParam)
  const analysisId = Number(analysisIdParam)

  const { data: analysis, isLoading, error } = useGetAnalysisQuery(analysisId)
  const checklists = useListChecklistsForAnalysisQuery(analysisId)

  return (
    <DetailShell
      title={`Analiza #${analysisId}`}
      backTo={`/offer-profiles/${offerProfileId}`}
      backLabel="← OfferProfile"
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
              to: `/offer-profiles/${offerProfileId}/analysis/${analysisId}/checklists`,
            },
            {
              id: 'resources',
              label: 'Zasoby',
              count: (analysis?.analysis_questions as Entity[] | undefined)?.length ?? 0,
              to: `/offer-profiles/${offerProfileId}/analysis/${analysisId}/questions`,
            },
          ]}
        />
      }
    />
  )
}
