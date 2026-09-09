import { type ReactNode } from 'react'
import { useParams } from 'react-router-dom'
import { RelationList } from '@/components/EditableFields'
import { Button } from '@/components/ui/button'
import { useListFactStatusesQuery } from '@/features/factStatus/factStatusApi'
import { useListReviewStatusesQuery } from '@/features/reviewStatus/reviewStatusApi'
import { useDeleteKnowledgeInsightMutation, useGetKnowledgeQuery, useUpdateKnowledgeInsightMutation } from '@/features/knowledge/knowledgeApi'
import { useDeleteTargetAudienceMutation, useGenerateTargetAudiencesMutation, useUpdateTargetAudienceMutation } from '@/features/targetAudiences/targetAudiencesApi'
import type { Entity } from '@/types'

function CollectionPage({ title, children }: { title: string; children: ReactNode }) {
  return <div className="w-full space-y-6 p-6 lg:p-10"><h1 className="text-2xl font-semibold">{title}</h1>{children}</div>
}

export function KnowledgeInsightsPage() {
  const knowledgeId = Number(useParams().knowledgeId)
  const { data, isLoading, error } = useGetKnowledgeQuery(knowledgeId)
  const { data: statuses } = useListFactStatusesQuery()
  const { data: reviewStatuses } = useListReviewStatusesQuery()
  const [remove] = useDeleteKnowledgeInsightMutation()
  const [update] = useUpdateKnowledgeInsightMutation()
  const items = (data?.knowledge_insights as Entity[] | undefined) ?? []
  return <CollectionPage title="Insights"><RelationList fieldKey="knowledge_insights" items={items} onEditLink={(item) => `/knowledge-insights/${item.id}/edit`} onDelete={(item) => remove({ id: item.id as number, knowledgeId })} onStatusChange={(item, fact_status) => update({ id: item.id as number, knowledgeId, fact_status }).unwrap()} onReviewStatusChange={(item, review_status) => update({ id: item.id as number, knowledgeId, review_status }).unwrap()} statuses={statuses} reviewStatuses={reviewStatuses} showHeading={false} />{isLoading && <p>Ładowanie…</p>}{error && <p>Nie udało się pobrać danych.</p>}</CollectionPage>
}

export function KnowledgeTargetAudiencesPage() {
  const knowledgeId = Number(useParams().knowledgeId)
  const { data, isLoading, error } = useGetKnowledgeQuery(knowledgeId)
  const { data: statuses } = useListFactStatusesQuery()
  const { data: reviewStatuses } = useListReviewStatusesQuery()
  const [generate, generateState] = useGenerateTargetAudiencesMutation()
  const [remove] = useDeleteTargetAudienceMutation()
  const [update] = useUpdateTargetAudienceMutation()
  const items = (data?.target_audiences as Entity[] | undefined) ?? []
  return <CollectionPage title="Grupy docelowe"><Button size="sm" onClick={() => generate({ knowledgeId })} disabled={generateState.isLoading}>{generateState.isLoading ? 'Generowanie…' : 'Generuj grupy docelowe'}</Button><RelationList fieldKey="target_audiences" items={items} onEditLink={(item) => `/target-audiences/${item.id}/edit`} onDelete={(item) => remove({ id: item.id as number, knowledgeId })} onStatusChange={(item, fact_status) => update({ id: item.id as number, knowledgeId, fact_status }).unwrap()} onReviewStatusChange={(item, review_status) => update({ id: item.id as number, knowledgeId, review_status }).unwrap()} statuses={statuses} reviewStatuses={reviewStatuses} showHeading={false} />{isLoading && <p>Ładowanie…</p>}{error && <p>Nie udało się pobrać danych.</p>}</CollectionPage>
}
