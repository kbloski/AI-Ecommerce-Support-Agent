import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import {
  useDeleteKnowledgeInsightMutation,
  useGetKnowledgeQuery,
  useUpdateKnowledgeInsightMutation,
  useUpdateKnowledgeMutation,
} from '@/features/knowledge/knowledgeApi'
import {
  useDeleteTargetAudienceMutation,
  useUpdateTargetAudienceMutation,
} from '@/features/targetAudiences/targetAudiencesApi'

export default function KnowledgeDetailPage() {
  const knowledgeId = Number(useParams().knowledgeId)
  const { data: knowledge, isLoading, error } = useGetKnowledgeQuery(knowledgeId)

  const [deleteKnowledgeInsight] = useDeleteKnowledgeInsightMutation()
  const [updateKnowledgeInsight] = useUpdateKnowledgeInsightMutation()
  const [deleteTargetAudience] = useDeleteTargetAudienceMutation()
  const [updateTargetAudience] = useUpdateTargetAudienceMutation()

  const [updateKnowledge, updateKnowledgeState] = useUpdateKnowledgeMutation()

  return (
    <DetailShell
      title="Knowledge"
      backTo={knowledge ? `/offers/${knowledge.offer_id}` : undefined}
      backLabel="← Oferta"
      data={knowledge}
      isLoading={isLoading}
      error={error}
      itemActions={{
        knowledge_insights: (item) => deleteKnowledgeInsight({ id: item.id as number, knowledgeId }),
        target_audiences: (item) => deleteTargetAudience({ id: item.id as number, knowledgeId }),
      }}
      itemLinks={{
        knowledge_insights: (item) => `/knowledge-insights/${item.id}/edit`,
        target_audiences: (item) => `/target-audiences/${item.id}/edit`,
      }}
      relationLinks={{
        knowledge_insights: `/knowledges/${knowledgeId}/insights`,
        target_audiences: `/knowledges/${knowledgeId}/target-audiences`,
      }}
      itemStatusActions={{
        knowledge_insights: (item, factStatus) =>
          updateKnowledgeInsight({
            id: item.id as number,
            knowledgeId,
            fact_status: factStatus,
          }).unwrap(),
        target_audiences: (item, factStatus) =>
          updateTargetAudience({
            id: item.id as number,
            knowledgeId,
            fact_status: factStatus,
          }).unwrap(),
      }}
      editable={{
        onSave: (fields) => updateKnowledge({ id: knowledgeId, fields }).unwrap(),
        isSaving: updateKnowledgeState.isLoading,
      }}
    />
  )
}
