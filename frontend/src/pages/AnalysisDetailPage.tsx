import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetAnalysisQuery } from '@/features/analysis/analysisApi'

export default function AnalysisDetailPage() {
  const { offerProfileId: offerProfileIdParam, analysisId: analysisIdParam } = useParams()
  const offerProfileId = Number(offerProfileIdParam)
  const analysisId = Number(analysisIdParam)

  const { data: analysis, isLoading, error } = useGetAnalysisQuery(analysisId)

  return (
    <DetailShell
      title={`Analiza #${analysisId}`}
      backTo={`/offer-profiles/${offerProfileId}`}
      backLabel="← OfferProfile"
      data={analysis}
      isLoading={isLoading}
      error={error}
      exclude={['analysis_questions']}
    />
  )
}
