import { useState, type ReactNode } from 'react'
import { useParams } from 'react-router-dom'
import { ResourceList } from '@/components/ResourceList'
import { ListFilters, ReviewStatusFilter, ReviewStatusSortSelect, type ReviewStatusFilterValue, type ReviewStatusSort } from '@/components/ListFilters'
import { Button } from '@/components/ui/button'
import type { Entity } from '@/types'
import { useGetOfferSourceQuery } from '@/features/offerSources/offerSourceApi'
import { offerSourceLabel } from '@/features/offerSources/offerSourceLabel'
import { useEditEntityPanel } from '@/lib/useEditEntityPanel'
import { useSidePanel } from '@/lib/sidePanel'
import { useCreateAnalysisMutation, useDeleteAnalysisMutation, useDeleteAnalysisQuestionMutation, useGenerateAnalysisAnswersMutation, useListAnalysisForOfferProfileQuery, useListAnalysisQuestionsQuery, useUpdateAnalysisQuestionMutation } from '@/features/analysis/analysisApi'
import { useDeleteBrandMarketingMutation, useGenerateBrandMarketingMutation, useListBrandMarketingForOfferSourceQuery, useUpdateBrandMarketingMutation } from '@/features/brandMarketing/brandMarketingApi'
import { useCreateChecklistMutation, useDeleteChecklistItemMutation, useDeleteChecklistMutation, useGenerateChecklistMutation, useGetChecklistQuery, useListChecklistsForOfferProfileQuery, useUpdateChecklistItemMutation } from '@/features/checklists/checklistsApi'
import { useGetBrandMarketingQuery } from '@/features/brandMarketing/brandMarketingApi'
import { useDeleteMarketingStrategyMutation, useGenerateMarketingStrategyMutation, useListMarketingStrategyForBrandMarketingQuery, useUpdateMarketingStrategyMutation } from '@/features/marketingStrategy/marketingStrategyApi'
import { useGetMarketingStrategyQuery } from '@/features/marketingStrategy/marketingStrategyApi'
import { useDeleteOfferStrategyMutation, useGenerateOfferStrategyMutation, useListOfferStrategyForMarketingStrategyQuery, useUpdateOfferStrategyMutation } from '@/features/offerStrategy/offerStrategyApi'
import { useGetOfferStrategyQuery } from '@/features/offerStrategy/offerStrategyApi'
import { useDeleteMessageStrategyMutation, useGenerateMessageStrategyMutation, useListMessageStrategyForOfferStrategyQuery, useUpdateMessageStrategyMutation } from '@/features/messageStrategy/messageStrategyApi'
import { useGetMessageStrategyQuery } from '@/features/messageStrategy/messageStrategyApi'
import { useDeleteUgcCreativeMutation, useListUgcCreativesForOfferProfileQuery, useUpdateUgcCreativeMutation } from '@/features/ugcCreatives/ugcCreativesApi'
import { GenerateUgcCreativesForm } from '@/features/ugcCreatives/GenerateUgcCreativesForm'
import { useDeletePageStrategyMutation, useGeneratePageStrategyMutation, useListPageStrategyForMessageStrategyQuery, useUpdatePageStrategyMutation } from '@/features/pageStrategy/pageStrategyApi'
import { useGetPageStrategyQuery } from '@/features/pageStrategy/pageStrategyApi'
import { useDeletePageRequirementsMutation, useGeneratePageRequirementsMutation, useListPageRequirementsForPageStrategyQuery } from '@/features/pageRequirements/pageRequirementsApi'
import { useGetPageRequirementsQuery } from '@/features/pageRequirements/pageRequirementsApi'
import { EditPageRequirementsForm } from '@/features/pageRequirements/EditPageRequirementsForm'
import { useDeletePageBlueprintMutation, useGeneratePageBlueprintMutation, useListPageBlueprintForPageRequirementsQuery, useUpdatePageBlueprintMutation } from '@/features/pageBlueprint/pageBlueprintApi'
import { useGetPageBlueprintQuery } from '@/features/pageBlueprint/pageBlueprintApi'
import { useDeletePageContentPlanMutation, useGeneratePageContentPlanMutation, useListPageContentPlanForPageBlueprintQuery, useUpdatePageContentPlanMutation } from '@/features/pageContentPlan/pageContentPlanApi'
import { useGetPageContentPlanQuery } from '@/features/pageContentPlan/pageContentPlanApi'
import { useDeletePageCopyMutation, useGeneratePageCopyMutation, useListPageCopyForPageContentPlanQuery, useUpdatePageCopyMutation } from '@/features/pageCopy/pageCopyApi'

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

export function OfferSourceBrandMarketingPage() {
  const offerSourceId = Number(useParams().offerSourceId)
  const { data } = useGetOfferSourceQuery(offerSourceId)
  const list = useListBrandMarketingForOfferSourceQuery(offerSourceId)
  const [generate, state] = useGenerateBrandMarketingMutation()
  const [remove] = useDeleteBrandMarketingMutation()
  const [update] = useUpdateBrandMarketingMutation()
  const editEntity = useEditEntityPanel()
  return <ResourcePage backTo={`/offer-sources/${offerSourceId}`} backLabel={offerSourceLabel(data)} title="Brand marketing">
    <ResourceList title="Brand marketing" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(item) => `/brand-marketing/${item.id}`} itemLabel={(item) => (item.brand_name as string) ?? `#${item.id}`} onGenerate={() => generate({ offerSourceId })} isGenerating={state.isLoading} generateLabel="Generuj brand marketing" onEdit={(item) => editEntity('Brand marketing', item, (fields) => update({ id: item.id as number, fields }).unwrap())} onDelete={(item) => remove({ id: item.id as number, offerSourceId })} />
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

export function BrandMarketingStrategiesPage() { const id=Number(useParams().id); const {data}=useGetBrandMarketingQuery(id); const list=useListMarketingStrategyForBrandMarketingQuery(id); const [generate,state]=useGenerateMarketingStrategyMutation(); const [remove]=useDeleteMarketingStrategyMutation(); const [update]=useUpdateMarketingStrategyMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/brand-marketing/${id}`} backLabel={(data?.brand_name as string)??'Brand marketing'} title="Marketing strategy"><ResourceList title="Marketing strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/marketing-strategy/${x.id}`} itemLabel={(x)=>(x.marketing_objective as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj marketing strategy" onEdit={(x)=>editEntity('Marketing strategy',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,brandMarketingId:id})}/></ResourcePage> }
export function MarketingOfferStrategiesPage() { const id=Number(useParams().id); const {data}=useGetMarketingStrategyQuery(id); const list=useListOfferStrategyForMarketingStrategyQuery(id); const [generate,state]=useGenerateOfferStrategyMutation(); const [remove]=useDeleteOfferStrategyMutation(); const [update]=useUpdateOfferStrategyMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/marketing-strategy/${id}`} backLabel="Marketing strategy" title="Offer strategy"><ResourceList title="Offer strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/offer-strategy/${x.id}`} itemLabel={(x)=>(x.offer_name as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj offer strategy" onEdit={(x)=>editEntity('Offer strategy',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,marketingStrategyId:id})}/></ResourcePage> }
export function OfferMessageStrategiesPage() { const id=Number(useParams().id); const {data}=useGetOfferStrategyQuery(id); const list=useListMessageStrategyForOfferStrategyQuery(id); const [generate,state]=useGenerateMessageStrategyMutation(); const [remove]=useDeleteMessageStrategyMutation(); const [update]=useUpdateMessageStrategyMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/offer-strategy/${id}`} backLabel={(data?.offer_name as string)??'Offer strategy'} title="Message strategy"><ResourceList title="Message strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/message-strategy/${x.id}`} itemLabel={(x)=>(x.core_message as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj message strategy" onEdit={(x)=>editEntity('Message strategy',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,offerStrategyId:id})}/></ResourcePage> }

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
export function MessagePageStrategiesPage() { const id=Number(useParams().id); const {data}=useGetMessageStrategyQuery(id); const list=useListPageStrategyForMessageStrategyQuery(id); const [generate,state]=useGeneratePageStrategyMutation(); const [remove]=useDeletePageStrategyMutation(); const [update]=useUpdatePageStrategyMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/message-strategy/${id}`} backLabel="Message strategy" title="Page strategy"><ResourceList title="Page strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-strategy/${x.id}`} itemLabel={(x)=>(x.name as string)??(x.goal as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj page strategy" onEdit={(x)=>editEntity('Page strategy',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,messageStrategyId:id})}/></ResourcePage> }
export function PageRequirementsPage() { const id=Number(useParams().id); const list=useListPageRequirementsForPageStrategyQuery(id); const [generate,state]=useGeneratePageRequirementsMutation(); const [remove]=useDeletePageRequirementsMutation(); const { openPanel, closePanel } = useSidePanel(); useGetPageStrategyQuery(id); return <ResourcePage backTo={`/page-strategy/${id}`} backLabel="Page strategy" title="Page requirements"><ResourceList title="Page requirements" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-requirements/${x.id}`} itemLabel={(x)=>(x.name as string)??`#${x.id}`} onGenerate={()=>generate(id)} isGenerating={state.isLoading} generateLabel="Generuj wymagania" additionalActions={<Button variant="outline" className="h-9" onClick={()=>openPanel({title:'Dodaj Page Requirements ręcznie',content:<EditPageRequirementsForm pageStrategyId={id} onSaved={closePanel}/>})}>Dodaj ręcznie</Button>} onEdit={(x)=>openPanel({title:'Edytuj wymagania dotyczące sekcji',content:<EditPageRequirementsForm pageRequirements={x} onSaved={closePanel}/>})} onDelete={(x)=>remove({id:x.id as number,pageStrategyId:id})}/></ResourcePage> }
export function PageBlueprintsPage() { const id=Number(useParams().id); const list=useListPageBlueprintForPageRequirementsQuery(id); const [generate,state]=useGeneratePageBlueprintMutation(); const [remove]=useDeletePageBlueprintMutation(); useGetPageRequirementsQuery(id); const [update]=useUpdatePageBlueprintMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/page-requirements/${id}`} backLabel="Page requirements" title="Page blueprint"><ResourceList title="Page blueprint" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-blueprint/${x.id}`} itemLabel={(x)=>(x.page_type as string)??`#${x.id}`} onGenerate={()=>generate(id)} isGenerating={state.isLoading} generateLabel="Generuj page blueprint" onEdit={(x)=>editEntity('Page blueprint',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,pageRequirementsId:id})}/></ResourcePage> }
export function PageContentPlansPage() { const id=Number(useParams().id); const list=useListPageContentPlanForPageBlueprintQuery(id); const [generate,state]=useGeneratePageContentPlanMutation(); const [remove]=useDeletePageContentPlanMutation(); useGetPageBlueprintQuery(id); const [update]=useUpdatePageContentPlanMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/page-blueprint/${id}`} backLabel="Page blueprint" title="Page content plan"><ResourceList title="Page content plan" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-content-plan/${x.id}`} itemLabel={(x)=>(x.name as string)??`#${x.id}`} onGenerate={()=>generate(id)} isGenerating={state.isLoading} generateLabel="Generuj content plan" onEdit={(x)=>editEntity('Page content plan',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,pageBlueprintId:id})}/></ResourcePage> }
export function PageCopiesPage() { const id=Number(useParams().id); const list=useListPageCopyForPageContentPlanQuery(id); const [generate,state]=useGeneratePageCopyMutation(); const [remove]=useDeletePageCopyMutation(); useGetPageContentPlanQuery(id); const [update]=useUpdatePageCopyMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/page-content-plan/${id}`} backLabel="Page content plan" title="Page copy"><ResourceList title="Page copy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-copy/${x.id}`} itemLabel={(x)=>`#${x.id}`} onGenerate={()=>generate(id)} isGenerating={state.isLoading} generateLabel="Generuj page copy" onEdit={(x)=>editEntity('Page copy',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,pageContentPlanId:id})}/></ResourcePage> }
