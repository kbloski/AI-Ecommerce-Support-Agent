import { useState, type FormEvent, type ReactNode } from 'react'
import { useParams } from 'react-router-dom'
import { ResourceList } from '@/components/ResourceList'
import { ListFilters, ReviewStatusFilter, ReviewStatusSortSelect, type ReviewStatusFilterValue, type ReviewStatusSort } from '@/components/ListFilters'
import { Button } from '@/components/ui/button'
import { SegmentedControl } from '@/components/SegmentedControl'
import type { Entity } from '@/types'
import { useGetOfferProfileQuery } from '@/features/offerProfiles/offerProfileApi'
import { useEditEntityPanel } from '@/lib/useEditEntityPanel'
import { useSidePanel } from '@/lib/sidePanel'
import { useCreateAnalysisMutation, useDeleteAnalysisMutation, useDeleteAnalysisQuestionMutation, useGenerateAnalysisAnswersMutation, useListAnalysisForOfferProfileQuery, useListAnalysisQuestionsQuery, useUpdateAnalysisQuestionMutation } from '@/features/analysis/analysisApi'
import { useDeleteBrandMarketingMutation, useGenerateBrandMarketingMutation, useListBrandMarketingForOfferProfileQuery, useUpdateBrandMarketingMutation } from '@/features/brandMarketing/brandMarketingApi'
import { useCreateChecklistMutation, useDeleteChecklistItemMutation, useDeleteChecklistMutation, useGenerateChecklistMutation, useGetChecklistQuery, useListChecklistsForOfferProfileQuery, useUpdateChecklistItemMutation } from '@/features/checklists/checklistsApi'
import { useGetBrandMarketingQuery } from '@/features/brandMarketing/brandMarketingApi'
import { useDeleteMarketingStrategyMutation, useGenerateMarketingStrategyMutation, useListMarketingStrategyForBrandMarketingQuery, useUpdateMarketingStrategyMutation } from '@/features/marketingStrategy/marketingStrategyApi'
import { useGetMarketingStrategyQuery } from '@/features/marketingStrategy/marketingStrategyApi'
import { useDeleteOfferStrategyMutation, useGenerateOfferStrategyMutation, useListOfferStrategyForMarketingStrategyQuery, useUpdateOfferStrategyMutation } from '@/features/offerStrategy/offerStrategyApi'
import { useGetOfferStrategyQuery } from '@/features/offerStrategy/offerStrategyApi'
import { useDeleteMessageStrategyMutation, useGenerateMessageStrategyMutation, useListMessageStrategyForOfferStrategyQuery, useUpdateMessageStrategyMutation } from '@/features/messageStrategy/messageStrategyApi'
import { useGetMessageStrategyQuery } from '@/features/messageStrategy/messageStrategyApi'
import { useDeleteAdStrategyMutation, useGenerateAdStrategyMutation, useListAdStrategyForMessageStrategyQuery, useUpdateAdStrategyMutation } from '@/features/adStrategy/adStrategyApi'
import { useDeleteUgcCreativeMutation, useGenerateUgcCreativesMutation, useListUgcCreativesForMessageStrategyQuery, useUpdateUgcCreativeMutation } from '@/features/ugcCreatives/ugcCreativesApi'
import { useDeletePageStrategyMutation, useGeneratePageStrategyMutation, useListPageStrategyForMessageStrategyQuery, useUpdatePageStrategyMutation } from '@/features/pageStrategy/pageStrategyApi'
import { useGetAdStrategyQuery } from '@/features/adStrategy/adStrategyApi'
import { useDeleteCreativeStrategyMutation, useGenerateCreativeStrategyMutation, useListCreativeStrategyForAdStrategyQuery, useUpdateCreativeStrategyMutation } from '@/features/creativeStrategy/creativeStrategyApi'
import { useGetPageStrategyQuery } from '@/features/pageStrategy/pageStrategyApi'
import { useCreatePageRequirementsMutation, useDeletePageRequirementsMutation, useListPageRequirementsForPageStrategyQuery } from '@/features/pageRequirements/pageRequirementsApi'
import { useGetPageRequirementsQuery } from '@/features/pageRequirements/pageRequirementsApi'
import { useDeletePageBlueprintMutation, useGeneratePageBlueprintMutation, useListPageBlueprintForPageRequirementsQuery, useUpdatePageBlueprintMutation } from '@/features/pageBlueprint/pageBlueprintApi'
import { useGetPageBlueprintQuery } from '@/features/pageBlueprint/pageBlueprintApi'
import { useDeletePageContentPlanMutation, useGeneratePageContentPlanMutation, useListPageContentPlanForPageBlueprintQuery, useUpdatePageContentPlanMutation } from '@/features/pageContentPlan/pageContentPlanApi'
import { useGetPageContentPlanQuery } from '@/features/pageContentPlan/pageContentPlanApi'
import { useDeletePageCopyMutation, useGeneratePageCopyMutation, useListPageCopyForPageContentPlanQuery, useUpdatePageCopyMutation } from '@/features/pageCopy/pageCopyApi'
import { useCreateAdSetupMutation, useDeleteAdSetupMutation, useListAdSetupForCreativeStrategyQuery, useListCreativeTypesQuery, useUpdateAdSetupMutation } from '@/features/adSetup/adSetupApi'
import { useGetCreativeStrategyQuery } from '@/features/creativeStrategy/creativeStrategyApi'
import { useGetAdSetupQuery } from '@/features/adSetup/adSetupApi'
import { useCreateCreativeExecutionSetupMutation, useDeleteCreativeExecutionSetupMutation, useGetCreativeExecutionSetupQuery, useListCreativeExecutionSetupsForAdSetupQuery } from '@/features/creativeExecutionSetup/creativeExecutionSetupApi'
import { useDeleteGenerateAdMutation, useGenerateAdMutation, useListGenerateAdsForSetupQuery, useUpdateGenerateAdMutation } from '@/features/generateAd/generateAdApi'
import { useListExecutionStylesQuery, type ExecutionStyle } from '@/features/executionStyles/executionStylesApi'
import { useListAdFrameworksQuery, type AdFramework } from '@/features/adFrameworks/adFrameworksApi'
import { useListCreativeAnglesQuery, type CreativeAngle } from '@/features/creativeAngels/creativeAnglesApi'
import { useListPlatformsQuery, type Platform } from '@/features/platforms/platformsApi'

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

export function OfferProfileBrandMarketingPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data } = useGetOfferProfileQuery(offerProfileId)
  const list = useListBrandMarketingForOfferProfileQuery(offerProfileId)
  const [generate, state] = useGenerateBrandMarketingMutation()
  const [remove] = useDeleteBrandMarketingMutation()
  const [update] = useUpdateBrandMarketingMutation()
  const editEntity = useEditEntityPanel()
  return <ResourcePage backTo={`/offer-profiles/${offerProfileId}`} backLabel={(data?.offer_summary as string) ?? 'OfferProfile'} title="Brand marketing">
    <ResourceList title="Brand marketing" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(item) => `/brand-marketing/${item.id}`} itemLabel={(item) => (item.brand_name as string) ?? `#${item.id}`} onGenerate={() => generate({ offerProfileId })} isGenerating={state.isLoading} generateLabel="Generuj brand marketing" onEdit={(item) => editEntity('Brand marketing', item, (fields) => update({ id: item.id as number, fields }).unwrap())} onDelete={(item) => remove({ id: item.id as number, offerProfileId })} />
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

export function MessageAdStrategiesPage() { const id=Number(useParams().id); const {data}=useGetMessageStrategyQuery(id); const list=useListAdStrategyForMessageStrategyQuery(id); const [generate,state]=useGenerateAdStrategyMutation(); const [remove]=useDeleteAdStrategyMutation(); const [update]=useUpdateAdStrategyMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/message-strategy/${id}`} backLabel="Message strategy" title="Ad strategy"><ResourceList title="Ad strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/ad-strategy/${x.id}`} itemLabel={(x)=>(x.name as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj ad strategy" onEdit={(x)=>editEntity('Ad strategy',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,messageStrategyId:id})}/></ResourcePage> }
export function MessageUgcCreativesPage() {
  const id = Number(useParams().id)
  const { data } = useGetMessageStrategyQuery(id)
  const list = useListUgcCreativesForMessageStrategyQuery(id)
  const [generate, state] = useGenerateUgcCreativesMutation()
  const [remove] = useDeleteUgcCreativeMutation()
  const [update] = useUpdateUgcCreativeMutation()
  const [isReviewedFilter, setIsReviewedFilter] = useState<ReviewStatusFilterValue>('')
  const [reviewStatusSort, setReviewStatusSort] = useState<ReviewStatusSort>('unreviewed_first')
  const creatives = reviewableItems(list.data ?? [], isReviewedFilter, reviewStatusSort)

  return <ResourcePage backTo={`/message-strategy/${id}`} backLabel="Message strategy" title="UGC creatives">
    <ResourceList
      title="UGC creatives"
      items={creatives}
      totalItems={creatives.length}
      attentionItems={unreviewedCount(list.data ?? [])}
      isLoading={list.isLoading}
      error={list.error}
      linkTo={(item) => `/ugc-creatives/${item.id}`}
      itemLabel={(item) => (item.name as string) ?? `#${item.id}`}
      onGenerate={() => data && generate(data)}
      isGenerating={state.isLoading}
      generateLabel="Generuj UGC creatives"
      contentBeforeList={<ReviewFilters value={isReviewedFilter} sort={reviewStatusSort} onValueChange={setIsReviewedFilter} onSortChange={setReviewStatusSort} />}
      onDelete={(item) => remove({ id: item.id as number, messageStrategyId: id })}
      itemActions={(item) => <ReviewButton item={item} onToggle={() => update({ id: item.id as number, messageStrategyId: id, fields: { is_reviewed: item.is_reviewed !== true } })} />}
    />
  </ResourcePage>
}
export function MessagePageStrategiesPage() { const id=Number(useParams().id); const {data}=useGetMessageStrategyQuery(id); const list=useListPageStrategyForMessageStrategyQuery(id); const [generate,state]=useGeneratePageStrategyMutation(); const [remove]=useDeletePageStrategyMutation(); const [update]=useUpdatePageStrategyMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/message-strategy/${id}`} backLabel="Message strategy" title="Page strategy"><ResourceList title="Page strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-strategy/${x.id}`} itemLabel={(x)=>(x.goal as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj page strategy" onEdit={(x)=>editEntity('Page strategy',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,messageStrategyId:id})}/></ResourcePage> }
export function AdCreativeStrategiesPage() { const id=Number(useParams().id); const {data}=useGetAdStrategyQuery(id); const list=useListCreativeStrategyForAdStrategyQuery(id); const [generate,state]=useGenerateCreativeStrategyMutation(); const [remove]=useDeleteCreativeStrategyMutation(); const [update]=useUpdateCreativeStrategyMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/ad-strategy/${id}`} backLabel="Ad strategy" title="Creative strategy"><ResourceList title="Creative strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/creative-strategy/${x.id}`} itemLabel={(x)=>(x.name as string)??'Bez nazwy'} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj creative strategy" onEdit={(x)=>editEntity('Creative strategy',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,adStrategyId:id})}/></ResourcePage> }
export function PageRequirementsPage() { const id=Number(useParams().id); const list=useListPageRequirementsForPageStrategyQuery(id); const [create,state]=useCreatePageRequirementsMutation(); const [remove]=useDeletePageRequirementsMutation(); useGetPageStrategyQuery(id); return <ResourcePage backTo={`/page-strategy/${id}`} backLabel="Page strategy" title="Page requirements"><ResourceList title="Page requirements" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-requirements/${x.id}`} itemLabel={(x)=>`#${x.id}`} onGenerate={()=>create(id)} isGenerating={state.isLoading} generateLabel="Dodaj wymagania" onDelete={(x)=>remove({id:x.id as number,pageStrategyId:id})}/></ResourcePage> }
export function PageBlueprintsPage() { const id=Number(useParams().id); const list=useListPageBlueprintForPageRequirementsQuery(id); const [generate,state]=useGeneratePageBlueprintMutation(); const [remove]=useDeletePageBlueprintMutation(); useGetPageRequirementsQuery(id); const [update]=useUpdatePageBlueprintMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/page-requirements/${id}`} backLabel="Page requirements" title="Page blueprint"><ResourceList title="Page blueprint" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-blueprint/${x.id}`} itemLabel={(x)=>(x.page_type as string)??`#${x.id}`} onGenerate={()=>generate(id)} isGenerating={state.isLoading} generateLabel="Generuj page blueprint" onEdit={(x)=>editEntity('Page blueprint',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,pageRequirementsId:id})}/></ResourcePage> }
export function PageContentPlansPage() { const id=Number(useParams().id); const list=useListPageContentPlanForPageBlueprintQuery(id); const [generate,state]=useGeneratePageContentPlanMutation(); const [remove]=useDeletePageContentPlanMutation(); useGetPageBlueprintQuery(id); const [update]=useUpdatePageContentPlanMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/page-blueprint/${id}`} backLabel="Page blueprint" title="Page content plan"><ResourceList title="Page content plan" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-content-plan/${x.id}`} itemLabel={(x)=>`#${x.id}`} onGenerate={()=>generate(id)} isGenerating={state.isLoading} generateLabel="Generuj content plan" onEdit={(x)=>editEntity('Page content plan',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,pageBlueprintId:id})}/></ResourcePage> }
export function PageCopiesPage() { const id=Number(useParams().id); const list=useListPageCopyForPageContentPlanQuery(id); const [generate,state]=useGeneratePageCopyMutation(); const [remove]=useDeletePageCopyMutation(); useGetPageContentPlanQuery(id); const [update]=useUpdatePageCopyMutation(); const editEntity=useEditEntityPanel(); return <ResourcePage backTo={`/page-content-plan/${id}`} backLabel="Page content plan" title="Page copy"><ResourceList title="Page copy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-copy/${x.id}`} itemLabel={(x)=>`#${x.id}`} onGenerate={()=>generate(id)} isGenerating={state.isLoading} generateLabel="Generuj page copy" onEdit={(x)=>editEntity('Page copy',x,(fields)=>update({id:x.id as number,fields}).unwrap())} onDelete={(x)=>remove({id:x.id as number,pageContentPlanId:id})}/></ResourcePage> }

export function CreativeAdSetupsPage() {
  const id = Number(useParams().id); const { data } = useGetCreativeStrategyQuery(id)
  const list = useListAdSetupForCreativeStrategyQuery(id); const [remove] = useDeleteAdSetupMutation(); const [update] = useUpdateAdSetupMutation(); const editEntity = useEditEntityPanel(); const { openPanel, closePanel } = useSidePanel()
  return <ResourcePage backTo={`/creative-strategy/${id}`} backLabel={(data?.name as string) ?? 'Creative strategy'} title="Ad Setup">
    <ResourceList title="Ad Setup" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x) => `/ad-setup/${x.id}`} itemLabel={(x) => (x.name as string) ?? 'Bez nazwy'} onGenerate={() => openPanel({ title: 'Dodaj Ad Setup', content: <AdSetupForm creativeStrategyId={id} onSaved={closePanel} /> })} generateLabel="Dodaj Ad Setup" onEdit={(x) => editEntity('Ad Setup', x, (fields) => update({ id: x.id as number, fields }).unwrap())} onDelete={(x) => remove({ id: x.id as number, creativeStrategyId: id })} />
  </ResourcePage>
}

export function AdSetupCreativeExecutionSetupsPage() {
  const id = Number(useParams().id); const { data } = useGetAdSetupQuery(id)
  const list = useListCreativeExecutionSetupsForAdSetupQuery(id); const [remove] = useDeleteCreativeExecutionSetupMutation(); const { openPanel, closePanel } = useSidePanel()
  return <ResourcePage backTo={`/ad-setup/${id}`} backLabel={(data?.name as string) ?? 'Ad Setup'} title="Creative Execution Setup">
    <ResourceList title="Creative Execution Setup" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(item) => `/creative-execution-setup/${item.id}`} itemLabel={(item) => (item.name as string) ?? 'Bez nazwy'} onGenerate={() => data && openPanel({ title: 'Dodaj Creative Execution Setup', content: <CreativeExecutionSetupForm adSetup={data} onSaved={closePanel} /> })} generateLabel="Dodaj konfigurację" onDelete={(item) => remove({ id: item.id as number, adSetupId: id })} />
  </ResourcePage>
}

export function CreativeExecutionSetupGenerateAdsPage() {
  const id = Number(useParams().id); const { data } = useGetCreativeExecutionSetupQuery(id)
  const list = useListGenerateAdsForSetupQuery(id); const [generate, state] = useGenerateAdMutation(); const [remove] = useDeleteGenerateAdMutation(); const [update] = useUpdateGenerateAdMutation(); const editEntity = useEditEntityPanel()
  return <ResourcePage backTo={`/creative-execution-setup/${id}`} backLabel={(data?.name as string) ?? 'Creative Execution Setup'} title="Generate Ad">
    <ResourceList title="Generate Ad" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(item) => `/generate-ad/${item.id}`} itemLabel={(item) => `#${item.id}`} onGenerate={() => generate({ setupId: id })} isGenerating={state.isLoading} generateLabel="Generuj reklamę" onEdit={(item) => editEntity('Generate Ad', item, (fields) => update({ id: item.id as number, fields }).unwrap())} onDelete={(item) => remove({ id: item.id as number, setupId: id })} />
  </ResourcePage>
}

function AdSetupForm({ creativeStrategyId, onSaved }: { creativeStrategyId: number; onSaved: () => void }) {
  const { data: platforms = [] } = useListPlatformsQuery()
  const { data: creativeTypes = [] } = useListCreativeTypesQuery()
  const [create, state] = useCreateAdSetupMutation()
  const [error, setError] = useState<string | null>(null)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setError(null)
    try {
      await create({
        creativeStrategyId,
        name: String(form.get('name') || '') || undefined,
        creative_type: String(form.get('creative_type') || 'video'),
        platform: String(form.get('platform') || 'tiktok'),
        format: String(form.get('format') || 'Vertical 9:16'),
      }).unwrap()
      onSaved()
    } catch {
      setError('Nie udało się dodać Ad Setup.')
    }
  }

  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Nazwa</span><input name="name" className="h-9 w-full rounded-md border px-2.5 text-sm" placeholder="Np. TikTok product demo" /></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Typ kreacji</span><select name="creative_type" defaultValue="video" className="h-9 w-full rounded-md border px-2.5 text-sm">{creativeTypes.map((creativeType) => <option key={creativeType.id} value={creativeType.id}>{creativeType.name}</option>)}</select></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Platforma</span><select name="platform" defaultValue="tiktok" className="h-9 w-full rounded-md border px-2.5 text-sm">{platforms.map((platform: Platform) => <option key={platform.id} value={platform.id}>{platform.name}</option>)}</select></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Format</span><input name="format" defaultValue="Vertical 9:16" className="h-9 w-full rounded-md border px-2.5 text-sm" /></label>
    {error && <p className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={state.isLoading}>{state.isLoading ? 'Dodawanie…' : 'Dodaj Ad Setup'}</Button>
  </form>
}

function CreativeExecutionSetupForm({ adSetup, onSaved }: { adSetup: Entity; onSaved: () => void }) {
  const [create, state] = useCreateCreativeExecutionSetupMutation()
  const { data: frameworks = [] } = useListAdFrameworksQuery()
  const { data: angles = [] } = useListCreativeAnglesQuery()
  const { data: styles = [] } = useListExecutionStylesQuery()
  const [frameworkId, setFrameworkId] = useState('')
  const [angleId, setAngleId] = useState('')
  const [styleId, setStyleId] = useState('')
  const [error, setError] = useState<string | null>(null)
  const creativeType = String(adSetup.creative_type)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const duration = form.get('duration_seconds')
    const slides = form.get('number_of_slides')
    setError(null)
    try {
      await create({
        adSetupId: adSetup.id as number,
        fields: {
          name: String(form.get('name') || '') || 'Default setup',
          ...(creativeType === 'video' && duration ? { duration_seconds: Number(duration) } : {}),
          ...(creativeType === 'carousel' && slides ? { number_of_slides: Number(slides) } : {}),
          ...(frameworkId ? { ad_framework_id: frameworkId } : {}),
          ...(angleId ? { creative_angle_id: angleId } : {}),
          ...(styleId ? { execution_style_id: styleId } : {}),
          additional_instructions: String(form.get('additional_instructions') || '') || undefined,
        },
      }).unwrap()
      onSaved()
    } catch {
      setError('Nie udało się dodać Creative Execution Setup.')
    }
  }

  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Nazwa</span><input name="name" defaultValue="Default setup" className="h-9 w-full rounded-md border px-2.5 text-sm" /></label>
    <div className="grid gap-4 sm:grid-cols-2">
      <label className="block space-y-2"><span className="text-sm font-medium">Czas trwania (s)</span><input name="duration_seconds" type="number" defaultValue={15} disabled={creativeType !== 'video'} className="h-9 w-full rounded-md border px-2.5 text-sm disabled:opacity-50" /></label>
      <label className="block space-y-2"><span className="text-sm font-medium">Liczba slajdów</span><input name="number_of_slides" type="number" defaultValue={5} disabled={creativeType !== 'carousel'} className="h-9 w-full rounded-md border px-2.5 text-sm disabled:opacity-50" /></label>
    </div>
    <div className="space-y-2"><span className="text-sm font-medium">Framework</span><SegmentedControl ariaLabel="Ad framework" value={frameworkId || undefined} options={frameworks.map((item: AdFramework) => ({ value: item.id, label: item.name }))} onValueChange={setFrameworkId} /></div>
    <div className="space-y-2"><span className="text-sm font-medium">Creative angle</span><SegmentedControl ariaLabel="Creative angle" value={angleId || undefined} options={angles.map((item: CreativeAngle) => ({ value: item.id, label: item.name }))} onValueChange={setAngleId} /></div>
    <div className="space-y-2"><span className="text-sm font-medium">Execution style</span><SegmentedControl ariaLabel="Execution style" value={styleId || undefined} options={styles.map((item: ExecutionStyle) => ({ value: item.id, label: item.name }))} onValueChange={setStyleId} /></div>
    <label className="block space-y-2"><span className="text-sm font-medium">Dodatkowe instrukcje</span><textarea name="additional_instructions" rows={4} className="w-full rounded-md border px-2.5 py-2 text-sm" /></label>
    {error && <p className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={state.isLoading}>{state.isLoading ? 'Dodawanie…' : 'Dodaj konfigurację'}</Button>
  </form>
}
