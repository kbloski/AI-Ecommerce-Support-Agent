import { GeneratePageBlueprintForm } from '@/features/pageBlueprint/GeneratePageBlueprintForm'
import { useState, type ReactNode } from 'react'
import { useParams } from 'react-router-dom'
import { ResourceList } from '@/components/ResourceList'
import { ListFilters, ReviewStatusFilter, ReviewStatusSortSelect, type ReviewStatusFilterValue, type ReviewStatusSort } from '@/components/ListFilters'
import { Button } from '@/components/ui/button'
import type { Entity } from '@/types'
import { useEditEntityPanel } from '@/lib/useEditEntityPanel'
import { useSidePanel } from '@/lib/sidePanel'
import { useCreateAnalysisMutation, useDeleteAnalysisMutation, useDeleteAnalysisQuestionMutation, useGenerateAnalysisAnswersMutation, useListAnalysisForOfferProfileQuery, useListAnalysisQuestionsQuery, useUpdateAnalysisQuestionMutation } from '@/features/analysis/analysisApi'
import { useCreateChecklistMutation, useDeleteChecklistItemMutation, useDeleteChecklistMutation, useGenerateChecklistMutation, useGetChecklistQuery, useListChecklistsForOfferProfileQuery, useUpdateChecklistItemMutation } from '@/features/checklists/checklistsApi'
import { useDeleteUgcCreativeMutation, useListUgcCreativesForOfferProfileQuery, useUpdateUgcCreativeMutation } from '@/features/ugcCreatives/ugcCreativesApi'
import { GenerateUgcCreativesForm } from '@/features/ugcCreatives/GenerateUgcCreativesForm'
import { useDeletePageBlueprintMutation, useListPageBlueprintForOfferProfileQuery } from '@/features/pageBlueprint/pageBlueprintApi'
import { EditPageBlueprintForm } from '@/features/pageBlueprint/EditPageBlueprintForm'

function ResourcePage({ title: _title, children }: { backTo: string; backLabel: string; title: string; children: ReactNode }) {
  return <div className="w-full space-y-6 p-6 lg:p-10">
    {children}
  </div>
}

export function OfferProfileAnalysesPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const list = useListAnalysisForOfferProfileQuery(offerProfileId)
  const [create, state] = useCreateAnalysisMutation()
  const [remove] = useDeleteAnalysisMutation()
  return <ResourcePage backTo={`/offer-profiles/${offerProfileId}`} backLabel="OfferProfile" title="Analizy">
    <ResourceList title="Analizy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(item) => `/offer-profiles/${offerProfileId}/analysis/${item.id}`} itemLabel={(item) => `Analiza #${item.id}`} onGenerate={() => create({ offerProfileId })} isGenerating={state.isLoading} generateLabel="Utwórz analizę" onDelete={(item) => remove({ id: item.id as number, offerProfileId })} />
  </ResourcePage>
}


export function OfferProfileChecklistsPage() {
  const { offerProfileId } = useParams(); const id = Number(offerProfileId)
  const list = useListChecklistsForOfferProfileQuery(id); const [create, state] = useCreateChecklistMutation(); const [remove] = useDeleteChecklistMutation()
  return <ResourcePage backTo={`/offer-profiles/${id}`} backLabel="OfferProfile" title="Checklisty">
    <ResourceList title="Checklisty" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(item) => `/offer-profiles/${id}/checklists/${item.id}`} itemLabel={(item) => checklistLabel(item, item.id as number)} onGenerate={() => create({ offerProfileId: id })} isGenerating={state.isLoading} generateLabel="Utwórz checklistę" onDelete={(item) => remove({ id: item.id as number, offerProfileId: id })} />
  </ResourcePage>
}

export function AnalysisQuestionsPage() {
  const { offerProfileId, analysisId } = useParams(); const aid = Number(analysisId)
  const [page, setPage] = useState(1)
  const [isReviewedFilter, setIsReviewedFilter] = useState<ReviewStatusFilterValue>('')
  const [reviewStatusSort, setReviewStatusSort] = useState<ReviewStatusSort>('unreviewed_first')
  const { data: result, isLoading, error } = useListAnalysisQuestionsQuery({ analysisId: aid, page, pageSize: 6, isReviewed: isReviewedFilter === '' ? undefined : isReviewedFilter === 'true', sort: reviewStatusSort })
  const { data: unreviewedResult } = useListAnalysisQuestionsQuery({ analysisId: aid, pageSize: 1, isReviewed: false })
  const [generate, state] = useGenerateAnalysisAnswersMutation(); const [remove] = useDeleteAnalysisQuestionMutation()
  const [update] = useUpdateAnalysisQuestionMutation()
  const questions = result?.items ?? []
  return <ResourcePage backTo={`/offer-profiles/${offerProfileId}/analysis/${aid}`} backLabel={`Analiza #${aid}`} title="Pytania">
    <ResourceList
      title="Pytania"
      items={questions}
      totalItems={result?.total_items}
      attentionItems={unreviewedResult?.total_items}
      isLoading={isLoading}
      error={error}
      itemLabel={(item) => String(item.question ?? `Pytanie #${item.id}`)}
      itemDescription={(item) => item.answer ? String(item.answer) : 'Brak odpowiedzi'}
      onGenerate={() => { void generate({ offerProfileId: Number(offerProfileId), analysisId: aid }) }}
      isGenerating={state.isLoading}
      generateLabel="Generuj odpowiedzi"
      contentBeforeList={<ReviewFilters value={isReviewedFilter} sort={reviewStatusSort} onValueChange={(value) => { setIsReviewedFilter(value); setPage(1) }} onSortChange={(value) => { setReviewStatusSort(value); setPage(1) }} />}
      onDelete={(item) => remove({ id: item.id as number, analysisId: aid })}
      itemActions={(item) => <ReviewButton item={item} onToggle={() => update({ id: item.id as number, analysisId: aid, fields: { is_reviewed: item.is_reviewed !== true } })} />}
      footer={result && result.total_pages > 1 ? <div className="flex items-center justify-between gap-3 border-t pt-4"><span className="text-sm text-muted-foreground">Strona {result.page} z {result.total_pages}</span><div className="flex gap-2"><Button variant="outline" size="sm" disabled={result.page <= 1} onClick={() => setPage(result.page - 1)}>Poprzednia</Button><Button variant="outline" size="sm" disabled={result.page >= result.total_pages} onClick={() => setPage(result.page + 1)}>Następna</Button></div></div> : undefined}
    />
  </ResourcePage>
}

function reviewableItems(items: Entity[], filter: ReviewStatusFilterValue, sort: ReviewStatusSort) {
  return items
    .filter((item) => filter === '' || item.is_reviewed === (filter === 'true'))
    .toSorted((left, right) => {
      const result = Number(left.is_reviewed === true) - Number(right.is_reviewed === true)
      return sort === 'unreviewed_first' ? result : -result
    })
}

function unreviewedCount(items: Entity[]) {
  return items.filter((item) => item.is_reviewed !== true).length
}

function ReviewFilters({ value, sort, onValueChange, onSortChange }: { value: ReviewStatusFilterValue; sort: ReviewStatusSort; onValueChange: (value: ReviewStatusFilterValue) => void; onSortChange: (value: ReviewStatusSort) => void }) {
  return <ListFilters><ReviewStatusFilter value={value} onChange={onValueChange} /><ReviewStatusSortSelect value={sort} onChange={onSortChange} /></ListFilters>
}

function ReviewButton({ item, onToggle }: { item: Entity; onToggle: () => void }) {
  return <Button variant={item.is_reviewed ? 'ghost' : 'default'} size="sm" className="h-7 px-2.5 text-xs" onClick={onToggle}>{item.is_reviewed ? 'Oznacz jako niesprawdzone' : 'Zatwierdź'}</Button>
}

export function ChecklistItemsPage() {
  const { offerProfileId, checklistId } = useParams(); const cid = Number(checklistId)
  const { data, isLoading, error } = useGetChecklistQuery(cid); const [generate, state] = useGenerateChecklistMutation(); const [remove] = useDeleteChecklistItemMutation()
  const [update] = useUpdateChecklistItemMutation()
  const [isReviewedFilter, setIsReviewedFilter] = useState<ReviewStatusFilterValue>('')
  const [reviewStatusSort, setReviewStatusSort] = useState<ReviewStatusSort>('unreviewed_first')
  const items = reviewableItems((data?.checklist_items as Entity[] | undefined) ?? [], isReviewedFilter, reviewStatusSort)
  return <ResourcePage backTo={`/offer-profiles/${offerProfileId}/checklists/${cid}`} backLabel={checklistLabel(data, cid)} title="Zadania">
    <ResourceList
      title="Zadania"
      items={items}
      totalItems={items.length}
      attentionItems={unreviewedCount((data?.checklist_items as Entity[] | undefined) ?? [])}
      isLoading={isLoading}
      error={error}
      onGenerate={() => { void generate({ offerProfileId: Number(offerProfileId), checklistId: cid }) }}
      isGenerating={state.isLoading}
      generateLabel="Generuj zadania"
      itemLabel={(item) => (item.title as string) ?? `Zadanie #${item.id}`}
      itemDescription={(item) => item.description as string | undefined}
      itemDetails={(item) => item.note ? (
        <div>
          <span className="mr-2 text-xs font-semibold tracking-wide text-muted-foreground uppercase">Notatka</span>
          <span className="whitespace-pre-wrap">{String(item.note)}</span>
        </div>
      ) : null}
      contentBeforeList={<ReviewFilters value={isReviewedFilter} sort={reviewStatusSort} onValueChange={setIsReviewedFilter} onSortChange={setReviewStatusSort} />}
      onDelete={(item) => remove({ id: item.id as number, checklistId: cid })}
      itemActions={(item) => <ReviewButton item={item} onToggle={() => update({ id: item.id as number, checklistId: cid, fields: { is_reviewed: item.is_reviewed !== true } })} />}
    />
  </ResourcePage>
}

function checklistLabel(data: Entity | undefined, checklistId: number) {
  const name = data?.name as string | undefined
  return name && name !== 'analysis_checklist' ? name : `Checklista #${checklistId}`
}


export function OfferProfileUgcCreativesPage() {
  const id = Number(useParams().offerProfileId)
  const list = useListUgcCreativesForOfferProfileQuery(id)
  const { openPanel, closePanel } = useSidePanel()
  const editEntity = useEditEntityPanel()
  const [remove] = useDeleteUgcCreativeMutation()
  const [update] = useUpdateUgcCreativeMutation()
  const [isReviewedFilter, setIsReviewedFilter] = useState<ReviewStatusFilterValue>('')
  const [reviewStatusSort, setReviewStatusSort] = useState<ReviewStatusSort>('unreviewed_first')
  const creatives = reviewableItems(list.data ?? [], isReviewedFilter, reviewStatusSort)

  return <ResourcePage backTo={`/offer-profiles/${id}`} backLabel="Profil oferty" title="UGC creatives">
    <ResourceList
      title="UGC creatives"
      items={creatives}
      totalItems={creatives.length}
      attentionItems={unreviewedCount(list.data ?? [])}
      isLoading={list.isLoading}
      error={list.error}
      linkTo={(item) => `/ugc-creatives/${item.id}`}
      itemLabel={(item) => (item.name as string) ?? `#${item.id}`}
      onGenerate={() => openPanel({ title: 'Generuj UGC creatives', content: <GenerateUgcCreativesForm offerProfileId={id} onSaved={closePanel} /> })}
      generateLabel="Generuj UGC creatives"
      onEdit={(item) => editEntity('UGC creative', item, (fields) => update({ id: Number(item.id), offerProfileId: id, fields }).unwrap(), ['is_reviewed'])}
      contentBeforeList={<ReviewFilters value={isReviewedFilter} sort={reviewStatusSort} onValueChange={setIsReviewedFilter} onSortChange={setReviewStatusSort} />}
      onDelete={(item) => remove({ id: item.id as number, offerProfileId: id })}
      itemActions={(item) => <ReviewButton item={item} onToggle={() => update({ id: item.id as number, offerProfileId: id, fields: { is_reviewed: item.is_reviewed !== true } })} />}
    />
  </ResourcePage>
}
export function OfferProfilePageBlueprintsPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const list = useListPageBlueprintForOfferProfileQuery(offerProfileId)
  const [remove] = useDeletePageBlueprintMutation()
  const { openPanel, closePanel } = useSidePanel()

  return <ResourcePage backTo={`/offer-profiles/${offerProfileId}`} backLabel="Profil oferty" title="Page blueprints">
    <ResourceList
      title="Page blueprints"
      items={list.data}
      isLoading={list.isLoading}
      error={list.error}
      linkTo={(item) => `/page-blueprints/${item.id}`}
      itemLabel={(item) => (item.name as string) ?? `#${item.id}`}
      onGenerate={() => openPanel({ title: "Generuj page blueprint", content: <GeneratePageBlueprintForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}
      generateLabel="Generuj page blueprint"
      additionalActions={(
        <Button variant="outline" className="h-9" onClick={() => openPanel({
          title: 'Nowy page blueprint',
          content: <EditPageBlueprintForm offerProfileId={offerProfileId} onSaved={closePanel} />,
        })}>Dodaj blueprint</Button>
      )}
      onEdit={(item) => openPanel({
        title: 'Edytuj page blueprint',
        content: <EditPageBlueprintForm pageBlueprint={item} onSaved={closePanel} />,
      })}
      onDelete={(item) => remove({ id: Number(item.id), offerProfileId })}
    />
  </ResourcePage>
}
