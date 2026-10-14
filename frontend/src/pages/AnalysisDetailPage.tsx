import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetAnalysisQuery } from '@/features/analysis/analysisApi'

export default function AnalysisDetailPage() {
  const { offerSourceId: offerSourceIdParam, analysisId: analysisIdParam } = useParams()
  const offerSourceId = Number(offerSourceIdParam)
  const analysisId = Number(analysisIdParam)

  const { data: analysis, isLoading, error } = useGetAnalysisQuery(analysisId)

  return (
    <DetailShell
      title={`Analiza #${analysisId}`}
      backTo={`/offer-sources/${offerSourceId}`}
      backLabel="← OfferSource"
      data={analysis}
      isLoading={isLoading}
      error={error}
      exclude={['analysis_questions']}
    />
  )
}
