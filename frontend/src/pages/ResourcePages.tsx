import { useState, type FormEvent, type ReactNode } from 'react'
import { useParams } from 'react-router-dom'
import { ResourceList } from '@/components/ResourceList'
import { RelationList } from '@/components/EditableFields'
import { Button } from '@/components/ui/button'
import { SegmentedControl } from '@/components/SegmentedControl'
import type { Entity } from '@/types'
import { useGetOfferProfileQuery } from '@/features/offerProfiles/offerProfileApi'
import { useCreateAnalysisMutation, useDeleteAnalysisMutation, useDeleteAnalysisQuestionMutation, useGenerateAnalysisAnswersMutation, useGetAnalysisQuery, useListAnalysisForOfferProfileQuery } from '@/features/analysis/analysisApi'
import { useDeleteBrandMarketingMutation, useGenerateBrandMarketingMutation, useListBrandMarketingForOfferProfileQuery } from '@/features/brandMarketing/brandMarketingApi'
import { useCreateChecklistMutation, useDeleteChecklistItemMutation, useDeleteChecklistMutation, useGenerateChecklistMutation, useGetChecklistQuery, useListChecklistsForAnalysisQuery } from '@/features/checklists/checklistsApi'
import { useGetBrandMarketingQuery } from '@/features/brandMarketing/brandMarketingApi'
import { useDeleteMarketingStrategyMutation, useGenerateMarketingStrategyMutation, useListMarketingStrategyForBrandMarketingQuery } from '@/features/marketingStrategy/marketingStrategyApi'
import { useGetMarketingStrategyQuery } from '@/features/marketingStrategy/marketingStrategyApi'
import { useDeleteOfferStrategyMutation, useGenerateOfferStrategyMutation, useListOfferStrategyForMarketingStrategyQuery } from '@/features/offerStrategy/offerStrategyApi'
import { useGetOfferStrategyQuery } from '@/features/offerStrategy/offerStrategyApi'
import { useDeleteMessageStrategyMutation, useGenerateMessageStrategyMutation, useListMessageStrategyForOfferStrategyQuery } from '@/features/messageStrategy/messageStrategyApi'
import { useGetMessageStrategyQuery } from '@/features/messageStrategy/messageStrategyApi'
import { useDeleteAdStrategyMutation, useGenerateAdStrategyMutation, useListAdStrategyForMessageStrategyQuery } from '@/features/adStrategy/adStrategyApi'
import { useDeleteUgcCreativeMutation, useGenerateUgcCreativesMutation, useListUgcCreativesForMessageStrategyQuery } from '@/features/ugcCreatives/ugcCreativesApi'
import { useDeletePageStrategyMutation, useGeneratePageStrategyMutation, useListPageStrategyForMessageStrategyQuery } from '@/features/pageStrategy/pageStrategyApi'
import { useGetAdStrategyQuery } from '@/features/adStrategy/adStrategyApi'
import { useDeleteCreativeStrategyMutation, useGenerateCreativeStrategyMutation, useListCreativeStrategyForAdStrategyQuery } from '@/features/creativeStrategy/creativeStrategyApi'
import { useGetPageStrategyQuery } from '@/features/pageStrategy/pageStrategyApi'
import { useCreatePageRequirementsMutation, useDeletePageRequirementsMutation, useListPageRequirementsForPageStrategyQuery } from '@/features/pageRequirements/pageRequirementsApi'
import { useGetPageRequirementsQuery } from '@/features/pageRequirements/pageRequirementsApi'
import { useDeletePageBlueprintMutation, useGeneratePageBlueprintMutation, useListPageBlueprintForPageRequirementsQuery } from '@/features/pageBlueprint/pageBlueprintApi'
import { useGetPageBlueprintQuery } from '@/features/pageBlueprint/pageBlueprintApi'
import { useDeletePageContentPlanMutation, useGeneratePageContentPlanMutation, useListPageContentPlanForPageBlueprintQuery } from '@/features/pageContentPlan/pageContentPlanApi'
import { useGetPageContentPlanQuery } from '@/features/pageContentPlan/pageContentPlanApi'
import { useDeletePageCopyMutation, useGeneratePageCopyMutation, useListPageCopyForPageContentPlanQuery } from '@/features/pageCopy/pageCopyApi'
import { useCreateAdExecutionMutation, useDeleteAdExecutionMutation, useListAdExecutionForCreativeStrategyQuery } from '@/features/adExecution/adExecutionApi'
import { useGetCreativeStrategyQuery } from '@/features/creativeStrategy/creativeStrategyApi'
import { useGetAdExecutionQuery } from '@/features/adExecution/adExecutionApi'
import { useDeleteCreativeExecutionMutation, useGenerateCreativeExecutionMutation, useListCreativeExecutionForAdExecutionQuery } from '@/features/creativeExecution/creativeExecutionApi'
import { useListExecutionStylesQuery, type ExecutionStyle } from '@/features/executionStyles/executionStylesApi'
import { useListAdFrameworksQuery, type AdFramework } from '@/features/adFrameworks/adFrameworksApi'
import { useListCreativeAnglesQuery, type CreativeAngle } from '@/features/creativeAngels/creativeAnglesApi'
import { useListPlatformsQuery, type Platform } from '@/features/platforms/platformsApi'

function ResourcePage({ title, children }: { backTo: string; backLabel: string; title: string; children: ReactNode }) {
  return <div className="w-full space-y-6 p-6 lg:p-10">
    {title === 'Pytania' && <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>}
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
  return <ResourcePage backTo={`/offer-profiles/${offerProfileId}`} backLabel={(data?.offer_summary as string) ?? 'OfferProfile'} title="Brand marketing">
    <ResourceList title="Brand marketing" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(item) => `/brand-marketing/${item.id}`} itemLabel={(item) => (item.brand_name as string) ?? `#${item.id}`} onGenerate={() => generate({ offerProfileId })} isGenerating={state.isLoading} generateLabel="Generuj brand marketing" onDelete={(item) => remove({ id: item.id as number, offerProfileId })} />
  </ResourcePage>
}

export function AnalysisChecklistsPage() {
  const { offerProfileId, analysisId } = useParams(); const aid = Number(analysisId)
  const list = useListChecklistsForAnalysisQuery(aid); const [create, state] = useCreateChecklistMutation(); const [remove] = useDeleteChecklistMutation()
  return <ResourcePage backTo={`/offer-profiles/${offerProfileId}/analysis/${aid}`} backLabel={`Analiza #${aid}`} title="Checklisty">
    <ResourceList title="Checklisty" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(item) => `/offer-profiles/${offerProfileId}/analysis/${aid}/checklists/${item.id}`} itemLabel={(item) => (item.name as string) ?? `#${item.id}`} onGenerate={() => create({ offerProfileId: Number(offerProfileId), analysisId: aid })} isGenerating={state.isLoading} generateLabel="Utwórz checklistę" onDelete={(item) => remove({ id: item.id as number, analysisId: aid })} />
  </ResourcePage>
}

export function AnalysisQuestionsPage() {
  const { offerProfileId, analysisId } = useParams(); const aid = Number(analysisId)
  const { data, isLoading, error } = useGetAnalysisQuery(aid); const [generate, state] = useGenerateAnalysisAnswersMutation(); const [remove] = useDeleteAnalysisQuestionMutation()
  const questions = (data?.analysis_questions as Entity[] | undefined) ?? []
  return <ResourcePage backTo={`/offer-profiles/${offerProfileId}/analysis/${aid}`} backLabel={`Analiza #${aid}`} title="Pytania">
    <Button size="sm" onClick={() => generate({ offerProfileId: Number(offerProfileId), analysisId: aid })} disabled={state.isLoading}>{state.isLoading ? 'Generowanie…' : 'Generuj odpowiedzi'}</Button>
    {isLoading && <p className="text-sm text-muted-foreground">Ładowanie…</p>}
    {Boolean(error) && <p className="text-sm text-destructive">Nie udało się pobrać pytań.</p>}
    {!isLoading && !error && questions.length === 0 && <p className="text-sm text-muted-foreground">Brak pytań — wygeneruj odpowiedzi.</p>}
    <RelationList fieldKey="analysis_questions" items={questions} onDelete={(item) => remove({ id: item.id as number, analysisId: aid })} showHeading={false} />
  </ResourcePage>
}

export function ChecklistItemsPage() {
  const { offerProfileId, analysisId, checklistId } = useParams(); const cid = Number(checklistId)
  const { data, isLoading, error } = useGetChecklistQuery(cid); const [generate, state] = useGenerateChecklistMutation(); const [remove] = useDeleteChecklistItemMutation()
  return <ResourcePage backTo={`/offer-profiles/${offerProfileId}/analysis/${analysisId}/checklists/${cid}`} backLabel={(data?.name as string) ?? `Checklista #${cid}`} title="Zadania">
    <Button size="sm" onClick={() => generate({ offerProfileId: Number(offerProfileId), analysisId: Number(analysisId), checklistId: cid })} disabled={state.isLoading}>{state.isLoading ? 'Generowanie…' : 'Generuj zadania'}</Button>
    <ResourceList
      title="Zadania"
      eyebrow={(data?.name as string) ?? `Checklista #${cid}`}
      items={data?.checklist_items as Entity[] | undefined}
      isLoading={isLoading}
      error={error}
      itemLabel={(item) => (item.title as string) ?? `Zadanie #${item.id}`}
      itemDescription={(item) => item.description as string | undefined}
      itemDetails={(item) => item.note ? (
        <div>
          <span className="mr-2 text-xs font-semibold tracking-wide text-muted-foreground uppercase">Notatka</span>
          <span className="whitespace-pre-wrap">{String(item.note)}</span>
        </div>
      ) : null}
      onDelete={(item) => remove({ id: item.id as number, checklistId: cid })}
    />
  </ResourcePage>
}

export function BrandMarketingStrategiesPage() { const id=Number(useParams().id); const {data}=useGetBrandMarketingQuery(id); const list=useListMarketingStrategyForBrandMarketingQuery(id); const [generate,state]=useGenerateMarketingStrategyMutation(); const [remove]=useDeleteMarketingStrategyMutation(); return <ResourcePage backTo={`/brand-marketing/${id}`} backLabel={(data?.brand_name as string)??'Brand marketing'} title="Marketing strategy"><ResourceList title="Marketing strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/marketing-strategy/${x.id}`} itemLabel={(x)=>(x.marketing_objective as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj marketing strategy" onDelete={(x)=>remove({id:x.id as number,brandMarketingId:id})}/></ResourcePage> }
export function MarketingOfferStrategiesPage() { const id=Number(useParams().id); const {data}=useGetMarketingStrategyQuery(id); const list=useListOfferStrategyForMarketingStrategyQuery(id); const [generate,state]=useGenerateOfferStrategyMutation(); const [remove]=useDeleteOfferStrategyMutation(); return <ResourcePage backTo={`/marketing-strategy/${id}`} backLabel="Marketing strategy" title="Offer strategy"><ResourceList title="Offer strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/offer-strategy/${x.id}`} itemLabel={(x)=>(x.offer_name as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj offer strategy" onDelete={(x)=>remove({id:x.id as number,marketingStrategyId:id})}/></ResourcePage> }
export function OfferMessageStrategiesPage() { const id=Number(useParams().id); const {data}=useGetOfferStrategyQuery(id); const list=useListMessageStrategyForOfferStrategyQuery(id); const [generate,state]=useGenerateMessageStrategyMutation(); const [remove]=useDeleteMessageStrategyMutation(); return <ResourcePage backTo={`/offer-strategy/${id}`} backLabel={(data?.offer_name as string)??'Offer strategy'} title="Message strategy"><ResourceList title="Message strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/message-strategy/${x.id}`} itemLabel={(x)=>(x.core_message as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj message strategy" onDelete={(x)=>remove({id:x.id as number,offerStrategyId:id})}/></ResourcePage> }

export function MessageAdStrategiesPage() { const id=Number(useParams().id); const {data}=useGetMessageStrategyQuery(id); const list=useListAdStrategyForMessageStrategyQuery(id); const [generate,state]=useGenerateAdStrategyMutation(); const [remove]=useDeleteAdStrategyMutation(); return <ResourcePage backTo={`/message-strategy/${id}`} backLabel="Message strategy" title="Ad strategy"><ResourceList title="Ad strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/ad-strategy/${x.id}`} itemLabel={(x)=>`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj ad strategy" onDelete={(x)=>remove({id:x.id as number,messageStrategyId:id})}/></ResourcePage> }
export function MessageUgcCreativesPage() { const id=Number(useParams().id); const {data}=useGetMessageStrategyQuery(id); const list=useListUgcCreativesForMessageStrategyQuery(id); const [generate,state]=useGenerateUgcCreativesMutation(); const [remove]=useDeleteUgcCreativeMutation(); return <ResourcePage backTo={`/message-strategy/${id}`} backLabel="Message strategy" title="UGC creatives"><ResourceList title="UGC creatives" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/ugc-creatives/${x.id}`} itemLabel={(x)=>(x.name as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj UGC creatives" onDelete={(x)=>remove({id:x.id as number,messageStrategyId:id})}/></ResourcePage> }
export function MessagePageStrategiesPage() { const id=Number(useParams().id); const {data}=useGetMessageStrategyQuery(id); const list=useListPageStrategyForMessageStrategyQuery(id); const [generate,state]=useGeneratePageStrategyMutation(); const [remove]=useDeletePageStrategyMutation(); return <ResourcePage backTo={`/message-strategy/${id}`} backLabel="Message strategy" title="Page strategy"><ResourceList title="Page strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-strategy/${x.id}`} itemLabel={(x)=>(x.goal as string)??`#${x.id}`} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj page strategy" onDelete={(x)=>remove({id:x.id as number,messageStrategyId:id})}/></ResourcePage> }
export function AdCreativeStrategiesPage() { const id=Number(useParams().id); const {data}=useGetAdStrategyQuery(id); const list=useListCreativeStrategyForAdStrategyQuery(id); const [generate,state]=useGenerateCreativeStrategyMutation(); const [remove]=useDeleteCreativeStrategyMutation(); return <ResourcePage backTo={`/ad-strategy/${id}`} backLabel="Ad strategy" title="Creative strategy"><ResourceList title="Creative strategy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/creative-strategy/${x.id}`} itemLabel={(x)=>`#${x.id} ${(x.name as string)??''}`.trim()} onGenerate={()=>data&&generate(data)} isGenerating={state.isLoading} generateLabel="Generuj creative strategy" onDelete={(x)=>remove({id:x.id as number,adStrategyId:id})}/></ResourcePage> }
export function PageRequirementsPage() { const id=Number(useParams().id); const list=useListPageRequirementsForPageStrategyQuery(id); const [create,state]=useCreatePageRequirementsMutation(); const [remove]=useDeletePageRequirementsMutation(); useGetPageStrategyQuery(id); return <ResourcePage backTo={`/page-strategy/${id}`} backLabel="Page strategy" title="Page requirements"><ResourceList title="Page requirements" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-requirements/${x.id}`} itemLabel={(x)=>`#${x.id}`} onGenerate={()=>create(id)} isGenerating={state.isLoading} generateLabel="Dodaj wymagania" onDelete={(x)=>remove({id:x.id as number,pageStrategyId:id})}/></ResourcePage> }
export function PageBlueprintsPage() { const id=Number(useParams().id); const list=useListPageBlueprintForPageRequirementsQuery(id); const [generate,state]=useGeneratePageBlueprintMutation(); const [remove]=useDeletePageBlueprintMutation(); useGetPageRequirementsQuery(id); return <ResourcePage backTo={`/page-requirements/${id}`} backLabel="Page requirements" title="Page blueprint"><ResourceList title="Page blueprint" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-blueprint/${x.id}`} itemLabel={(x)=>(x.page_type as string)??`#${x.id}`} onGenerate={()=>generate(id)} isGenerating={state.isLoading} generateLabel="Generuj page blueprint" onDelete={(x)=>remove({id:x.id as number,pageRequirementsId:id})}/></ResourcePage> }
export function PageContentPlansPage() { const id=Number(useParams().id); const list=useListPageContentPlanForPageBlueprintQuery(id); const [generate,state]=useGeneratePageContentPlanMutation(); const [remove]=useDeletePageContentPlanMutation(); useGetPageBlueprintQuery(id); return <ResourcePage backTo={`/page-blueprint/${id}`} backLabel="Page blueprint" title="Page content plan"><ResourceList title="Page content plan" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-content-plan/${x.id}`} itemLabel={(x)=>`#${x.id}`} onGenerate={()=>generate(id)} isGenerating={state.isLoading} generateLabel="Generuj content plan" onDelete={(x)=>remove({id:x.id as number,pageBlueprintId:id})}/></ResourcePage> }
export function PageCopiesPage() { const id=Number(useParams().id); const list=useListPageCopyForPageContentPlanQuery(id); const [generate,state]=useGeneratePageCopyMutation(); const [remove]=useDeletePageCopyMutation(); useGetPageContentPlanQuery(id); return <ResourcePage backTo={`/page-content-plan/${id}`} backLabel="Page content plan" title="Page copy"><ResourceList title="Page copy" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x)=>`/page-copy/${x.id}`} itemLabel={(x)=>`#${x.id}`} onGenerate={()=>generate(id)} isGenerating={state.isLoading} generateLabel="Generuj page copy" onDelete={(x)=>remove({id:x.id as number,pageContentPlanId:id})}/></ResourcePage> }

export function CreativeAdExecutionsPage() {
  const id = Number(useParams().id); const { data } = useGetCreativeStrategyQuery(id)
  const list = useListAdExecutionForCreativeStrategyQuery(id); const [create, state] = useCreateAdExecutionMutation(); const [remove] = useDeleteAdExecutionMutation(); const platforms = useListPlatformsQuery()
  const submit = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const form = new FormData(event.currentTarget); void create({ creativeStrategyId: id, name: String(form.get('name') || '') || undefined, creative_type: String(form.get('creative_type') || 'video'), platform: String(form.get('platform') || 'tiktok'), format: String(form.get('format') || 'Vertical 9:16') }) }
  return <ResourcePage backTo={`/creative-strategy/${id}`} backLabel={(data?.name as string) ?? 'Creative strategy'} title="Ad execution">
    <form onSubmit={submit} className="flex flex-wrap items-end gap-2">
      <label className="text-xs">Nazwa<input name="name" className="block w-40 rounded-md border px-2 py-1 text-sm" /></label>
      <label className="text-xs">Typ kreacji<select name="creative_type" defaultValue="video" className="block w-32 rounded-md border px-2 py-1 text-sm"><option value="video">video</option><option value="image">image</option><option value="carousel">carousel</option></select></label>
      <label className="text-xs">Platforma<select name="platform" defaultValue="tiktok" className="block w-40 rounded-md border px-2 py-1 text-sm">{platforms.data?.map((x: Platform) => <option key={x.id} value={x.id}>{x.name}</option>)}</select></label>
      <label className="text-xs">Format<input name="format" defaultValue="Vertical 9:16" className="block w-48 rounded-md border px-2 py-1 text-sm" /></label>
      <Button type="submit" size="sm" disabled={state.isLoading}>{state.isLoading ? 'Tworzenie…' : 'Utwórz ad execution'}</Button>
    </form>
    <ResourceList title="Ad execution" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x) => `/ad-execution/${x.id}`} itemLabel={(x) => `#${x.id} ${(x.name as string) ?? ''}`.trim()} onDelete={(x) => remove({ id: x.id as number, creativeStrategyId: id })} />
  </ResourcePage>
}

export function AdCreativeExecutionsPage() {
  const id = Number(useParams().id); const { data } = useGetAdExecutionQuery(id); const isGeneratable = ['video', 'image', 'carousel'].includes(String(data?.creative_type))
  const list = useListCreativeExecutionForAdExecutionQuery(id, { skip: !isGeneratable }); const [generate, state] = useGenerateCreativeExecutionMutation(); const [remove] = useDeleteCreativeExecutionMutation(); const frameworks = useListAdFrameworksQuery(); const angles = useListCreativeAnglesQuery(); const styles = useListExecutionStylesQuery()
  const [frameworkId, setFrameworkId] = useState(''); const [angleId, setAngleId] = useState(''); const [styleId, setStyleId] = useState('')
  const submit = (event: FormEvent<HTMLFormElement>) => { event.preventDefault(); const form = new FormData(event.currentTarget); const duration = form.get('duration_seconds'); const slides = form.get('number_of_slides'); void generate({ adExecutionId: id, ...(duration ? { duration_seconds: Number(duration) } : {}), ...(slides ? { number_of_slides: Number(slides) } : {}), ...(frameworkId ? { ad_framework_id: frameworkId } : {}), ...(angleId ? { creative_angle_id: angleId } : {}), ...(styleId ? { execution_style_id: styleId } : {}) }) }
  return <ResourcePage backTo={`/ad-execution/${id}`} backLabel={(data?.name as string) ?? 'Ad execution'} title="Creative execution">
    {isGeneratable && <form onSubmit={submit} className="space-y-3">
      <div className="flex flex-wrap items-end gap-2">
        <label className="text-xs">Czas trwania (s)<input name="duration_seconds" type="number" defaultValue={15} disabled={data?.creative_type !== 'video'} className="block w-28 rounded-md border px-2 py-1 text-sm disabled:opacity-50" /></label>
        <label className="text-xs">Liczba slajdów<input name="number_of_slides" type="number" defaultValue={5} disabled={data?.creative_type !== 'carousel'} className="block w-28 rounded-md border px-2 py-1 text-sm disabled:opacity-50" /></label>
      </div>
      <div className="space-y-1">
        <p className="text-xs text-muted-foreground">Framework</p>
        <SegmentedControl ariaLabel="Ad framework" value={frameworkId || undefined} options={frameworks.data?.map((x: AdFramework) => ({ value: x.id, label: x.name }))} onValueChange={setFrameworkId} />
      </div>
      <div className="space-y-1">
        <p className="text-xs text-muted-foreground">Creative angle</p>
        <SegmentedControl ariaLabel="Creative angle" value={angleId || undefined} options={angles.data?.map((x: CreativeAngle) => ({ value: x.id, label: x.name }))} onValueChange={setAngleId} />
      </div>
      <div className="space-y-1">
        <p className="text-xs text-muted-foreground">Execution style</p>
        <SegmentedControl ariaLabel="Execution style" value={styleId || undefined} options={styles.data?.map((x: ExecutionStyle) => ({ value: x.id, label: x.name }))} onValueChange={setStyleId} />
      </div>
      <Button type="submit" size="sm" disabled={state.isLoading}>{state.isLoading ? 'Generowanie…' : 'Generuj creative execution'}</Button>
    </form>}
    <ResourceList title="Creative execution" items={list.data} isLoading={list.isLoading} error={list.error} linkTo={(x) => `/creative-execution/${x.id}`} itemLabel={(x) => `#${x.id}`} onDelete={(x) => remove({ id: x.id as number, adExecutionId: id })} />
  </ResourcePage>
}
