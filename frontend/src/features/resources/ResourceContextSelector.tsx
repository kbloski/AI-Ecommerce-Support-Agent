import { useEffect, useState, type Dispatch, type SetStateAction } from 'react'
import { useListMarketingAnglesQuery } from '@/features/marketingAngles/marketingAnglesApi'
import { useListAdConceptsQuery } from '@/features/adConcepts/adConceptsApi'
import { useListCreativePlansQuery } from '@/features/creativePlans/creativePlansApi'
import { useListUgcCreativesForOfferProfileQuery } from '@/features/ugcCreatives/ugcCreativesApi'
import { useListAdCopiesQuery } from '@/features/adCopy/adCopyApi'
import { useListBrandStylesQuery } from '@/features/brandStyles/brandStylesApi'
import { useListAnalysisForOfferProfileQuery } from '@/features/analysis/analysisApi'
import { useListChecklistsForOfferProfileQuery } from '@/features/checklists/checklistsApi'
import { useListPageBlueprintForOfferProfileQuery } from '@/features/pageBlueprint/pageBlueprintApi'
import { useListPagesQuery } from '@/features/pages/pagesApi'
import { useListNotesQuery } from '@/features/notes/notesApi'
import { useListProfileContextsQuery } from '@/features/additionalContexts/additionalContextsApi'
import { useListOfferFactsQuery } from '@/features/offerFacts/offerFactsApi'
import { useGetOfferProfileQuery } from '@/features/offerProfiles/offerProfilesApi'
import { useListAllTargetAudiencesForOfferProfileQuery } from '@/features/targetAudiences/targetAudiencesApi'
import type { ResourceContextInclude, ResourceContextRequest, ResourceContextType } from './resourceContextApi'
import type { Entity } from '@/types'

const resourceNames: Record<ResourceContextType, string> = {
  offer_raw: 'Surowa oferta',
  offer_source: 'Źródło oferty',
  offer_profile: 'Profil oferty',
}

function SelectableResourceSection({ number, title, items, selectedIds, onChange, itemLabel = (item) => String(item.name ?? `#${item.id}`), prefix = '3.' }: {
  number: number
  prefix?: string
  title: string
  items?: Entity[]
  selectedIds: number[]
  onChange: Dispatch<SetStateAction<number[]>>
  itemLabel?: (item: Entity) => string
}) {
  if (!items?.length) return null
  return <div className="mt-3 rounded-md border bg-muted/30 p-3">
    <p className="font-medium">{prefix}{number}. {title}</p>
    <p className="mt-1 text-muted-foreground">Powiązany zasób · {items.length} dostępnych</p>
    <label className="mt-2 flex items-center gap-2"><input type="checkbox" checked={selectedIds.length > 0} onChange={(event) => onChange(event.target.checked ? items.map((item) => Number(item.id)) : [])} />Dołącz do kontekstu</label>
    {selectedIds.length > 0 && <div className="mt-2 space-y-2 border-l pl-3">{items.map((item) => {
      const id = Number(item.id)
      return <label key={id} className="flex items-center gap-2"><input type="checkbox" checked={selectedIds.includes(id)} onChange={() => onChange((current) => current.includes(id) ? current.filter((selected) => selected !== id) : [...current, id])} />{itemLabel(item)}</label>
    })}</div>}
  </div>
}

/** Choose which related data goes into the context of a resource; shared by the export and the chat. */
export function ResourceContextSelector({ initialRequest, onChange, allowNotes = true }: {
  initialRequest: ResourceContextRequest
  onChange: (request: ResourceContextRequest, isReady: boolean) => void
  allowNotes?: boolean
}) {
  const isProfile = initialRequest.type === 'offer_profile'
  const hasEarlierResource = initialRequest.type !== 'offer_raw'
  const [includeRaw, setIncludeRaw] = useState(initialRequest.include?.includes('offer_raw') ?? hasEarlierResource)
  const [includeSource, setIncludeSource] = useState(initialRequest.include?.includes('offer_source') ?? true)
  const [includeFacts, setIncludeFacts] = useState(initialRequest.includeOfferFacts ?? true)
  const [includeAdditionalContexts, setIncludeAdditionalContexts] = useState(initialRequest.includeAdditionalContexts ?? true)
  const [audienceIds, setAudienceIds] = useState<number[]>(initialRequest.targetAudienceIds ?? [])
  const [angleIds, setAngleIds] = useState<number[]>(initialRequest.marketingAngleIds ?? [])
  const [conceptIds, setConceptIds] = useState<number[]>(initialRequest.adConceptIds ?? [])
  const [planIds, setPlanIds] = useState<number[]>(initialRequest.creativePlanIds ?? [])
  const [ugcIds, setUgcIds] = useState<number[]>(initialRequest.ugcCreativeIds ?? [])
  const [copyIds, setCopyIds] = useState<number[]>(initialRequest.adCopyIds ?? [])
  const [brandStyleIds, setBrandStyleIds] = useState<number[]>(initialRequest.brandStyleIds ?? [])
  const [analysisIds, setAnalysisIds] = useState<number[]>(initialRequest.analysisIds ?? [])
  const [checklistIds, setChecklistIds] = useState<number[]>(initialRequest.checklistIds ?? [])
  const [pageBlueprintIds, setPageBlueprintIds] = useState<number[]>(initialRequest.pageBlueprintIds ?? [])
  const [pageIds, setPageIds] = useState<number[]>(initialRequest.pageIds ?? [])
  const [noteIds, setNoteIds] = useState<number[]>(allowNotes ? initialRequest.noteIds ?? [] : [])
  const { data: angles, isLoading: anglesLoading, error: anglesError } = useListMarketingAnglesQuery(initialRequest.id, { skip: !isProfile })
  const { data: concepts, isLoading: conceptsLoading, error: conceptsError } = useListAdConceptsQuery(initialRequest.id, { skip: !isProfile })
  const { data: plans, isLoading: plansLoading, error: plansError } = useListCreativePlansQuery(initialRequest.id, { skip: !isProfile })
  const { data: ugcCreatives, isLoading: ugcLoading, error: ugcError } = useListUgcCreativesForOfferProfileQuery(initialRequest.id, { skip: !isProfile })
  const { data: adCopies, isLoading: copiesLoading, error: copiesError } = useListAdCopiesQuery(initialRequest.id, { skip: !isProfile })
  const { data: brandStyles, isLoading: brandStylesLoading, error: brandStylesError } = useListBrandStylesQuery(initialRequest.id, { skip: !isProfile })
  const { data: analyses, isLoading: analysesLoading, error: analysesError } = useListAnalysisForOfferProfileQuery(initialRequest.id, { skip: !isProfile })
  const { data: checklists, isLoading: checklistsLoading, error: checklistsError } = useListChecklistsForOfferProfileQuery(initialRequest.id, { skip: !isProfile })
  const { data: pageBlueprints, isLoading: blueprintsLoading, error: blueprintsError } = useListPageBlueprintForOfferProfileQuery(initialRequest.id, { skip: !isProfile })
  const { data: pages, isLoading: pagesLoading, error: pagesError } = useListPagesQuery(initialRequest.id, { skip: !isProfile })
  const { data: notes, isLoading: notesLoading, error: notesError } = useListNotesQuery(undefined, { skip: !allowNotes })
  const { data: additionalContexts, error: additionalContextsError } = useListProfileContextsQuery(initialRequest.id, { skip: !isProfile })
  const { data: audiences, isLoading: audiencesLoading, error: audiencesError } = useListAllTargetAudiencesForOfferProfileQuery(initialRequest.id, { skip: !isProfile })
  const { data: profile } = useGetOfferProfileQuery(initialRequest.id, { skip: !isProfile })
  const sourceId = initialRequest.type === 'offer_source' ? initialRequest.id : Number(profile?.offer_source_id)
  const factsQuery = { offerSourceId: sourceId, pageSize: 1 }
  const skipFacts = !hasEarlierResource || !Number.isInteger(sourceId) || sourceId <= 0
  const { data: facts, error: factsError } = useListOfferFactsQuery(
    factsQuery,
    { skip: skipFacts },
  )
  const { data: reviewedFacts } = useListOfferFactsQuery(
    { ...factsQuery, isReviewed: true },
    { skip: skipFacts },
  )
  const hasAdditionalContexts = (additionalContexts?.length ?? 0) > 0
  const hasAudiences = (audiences?.length ?? 0) > 0
  const hasAngles = (angles?.length ?? 0) > 0
  const hasConcepts = (concepts?.length ?? 0) > 0
  const audienceSectionNumber = 1 + Number(hasAdditionalContexts)
  const angleSectionNumber = audienceSectionNumber + Number(hasAudiences)
  const conceptSectionNumber = angleSectionNumber + Number(hasAngles)
  const planSectionNumber = conceptSectionNumber + Number(hasConcepts)
  const ugcSectionNumber = planSectionNumber + Number((plans?.length ?? 0) > 0)
  const copySectionNumber = ugcSectionNumber + Number((ugcCreatives?.length ?? 0) > 0)
  const brandStyleSectionNumber = copySectionNumber + Number((adCopies?.length ?? 0) > 0)
  const analysisSectionNumber = brandStyleSectionNumber + Number((brandStyles?.length ?? 0) > 0)
  const checklistSectionNumber = analysisSectionNumber + Number((analyses?.length ?? 0) > 0)
  const blueprintSectionNumber = checklistSectionNumber + Number((checklists?.length ?? 0) > 0)
  const pageSectionNumber = blueprintSectionNumber + Number((pageBlueprints?.length ?? 0) > 0)
  const isReady = (!allowNotes || !notesLoading) && !(isProfile && (audiencesLoading || anglesLoading || conceptsLoading || plansLoading || ugcLoading || copiesLoading || brandStylesLoading || analysesLoading || checklistsLoading || blueprintsLoading || pagesLoading))

  const include: ResourceContextInclude[] = []
  if (isProfile && includeSource) include.push('offer_source')
  if (hasEarlierResource && includeRaw) include.push('offer_raw')
  if (isProfile && audienceIds.length) include.push('target_audiences')
  if (isProfile && angleIds.length) include.push('marketing_angle')
  if (isProfile && conceptIds.length) include.push('ad_concept')
  if (isProfile && planIds.length) include.push('creative_plan')
  if (isProfile && ugcIds.length) include.push('ugc_creative')
  if (isProfile && copyIds.length) include.push('ad_copy')
  if (isProfile && brandStyleIds.length) include.push('brand_style')
  if (isProfile && analysisIds.length) include.push('analysis')
  if (isProfile && checklistIds.length) include.push('checklist')
  if (isProfile && pageBlueprintIds.length) include.push('page_blueprint')
  if (isProfile && pageIds.length) include.push('page')
  if (allowNotes && noteIds.length) include.push('note')
  const request: ResourceContextRequest = {
    type: initialRequest.type, id: initialRequest.id, include,
    targetAudienceIds: isProfile ? audienceIds : [],
    marketingAngleIds: isProfile ? angleIds : [],
    adConceptIds: isProfile ? conceptIds : [],
    creativePlanIds: isProfile ? planIds : [],
    ugcCreativeIds: isProfile ? ugcIds : [],
    adCopyIds: isProfile ? copyIds : [],
    brandStyleIds: isProfile ? brandStyleIds : [],
    analysisIds: isProfile ? analysisIds : [],
    checklistIds: isProfile ? checklistIds : [],
    pageBlueprintIds: isProfile ? pageBlueprintIds : [],
    pageIds: isProfile ? pageIds : [],
    noteIds: allowNotes ? noteIds : [],
    includeOfferFacts: hasEarlierResource && (!isProfile || includeSource) && includeFacts,
    includeAdditionalContexts: isProfile ? includeAdditionalContexts : undefined,
  }
  const requestKey = JSON.stringify(request)
  useEffect(() => {
    onChange(JSON.parse(requestKey) as ResourceContextRequest, isReady)
  }, [requestKey, isReady, onChange])

  return <div className="space-y-4 text-sm">
    <div className="rounded-md border p-3">
      <p className="font-medium">1. {resourceNames.offer_raw}</p>
      {initialRequest.type === 'offer_raw'
        ? <p className="mt-2 text-muted-foreground">#{initialRequest.id} — wybrany zasób, zawsze dołączony</p>
        : <label className="mt-2 flex items-center gap-2"><input type="checkbox" checked={includeRaw} onChange={(event) => setIncludeRaw(event.target.checked)} />Dołącz do kontekstu</label>}
    </div>
    {hasEarlierResource && <div className="rounded-md border p-3">
      <p className="font-medium">2. {resourceNames.offer_source}</p>
      {initialRequest.type === 'offer_source'
        ? <p className="mt-2 text-muted-foreground">#{initialRequest.id} — wybrany zasób, zawsze dołączony</p>
        : <label className="mt-2 flex items-center gap-2"><input type="checkbox" checked={includeSource} onChange={(event) => setIncludeSource(event.target.checked)} />Dołącz do kontekstu</label>}
      {(!isProfile || includeSource) && Number(facts?.total_items) > 0 && <div className="mt-3 rounded-md border bg-muted/30 p-3">
        <p className="font-medium">2.1. Fakty o produkcie</p>
        <p className="mt-1 text-muted-foreground">Powiązany zasób · {facts?.total_items} faktów. {reviewedFacts ? `${reviewedFacts.total_items} zatwierdzonych może trafić do kontekstu.` : 'Sprawdzanie zatwierdzonych faktów…'}</p>
        <label className="mt-2 flex items-center gap-2"><input type="checkbox" checked={includeFacts} onChange={(event) => setIncludeFacts(event.target.checked)} />Dołącz zatwierdzone fakty do kontekstu</label>
      </div>}
      {(!isProfile || includeSource) && factsError && <p role="alert" className="mt-2 text-destructive">Nie udało się sprawdzić faktów o produkcie.</p>}
    </div>}
    {isProfile && <div className="rounded-md border p-3">
      <p className="font-medium">3. {resourceNames.offer_profile}</p>
      <p className="mt-2 text-muted-foreground">#{initialRequest.id} — wybrany zasób, zawsze dołączony</p>
      {hasAdditionalContexts && <div className="mt-3 rounded-md border bg-muted/30 p-3">
        <p className="font-medium">3.1. Dodatkowe informacje</p>
        <p className="mt-1 text-muted-foreground">Powiązane dane · {additionalContexts?.length} dołączonych do profilu</p>
        <label className="mt-2 flex items-center gap-2"><input type="checkbox" checked={includeAdditionalContexts} onChange={(event) => setIncludeAdditionalContexts(event.target.checked)} />Dołącz do kontekstu</label>
      </div>}
      {hasAudiences && <div className="mt-3 rounded-md border bg-muted/30 p-3">
        <p className="font-medium">3.{audienceSectionNumber}. Grupy docelowe</p>
        <p className="mt-1 text-muted-foreground">Powiązany zasób · {audiences?.length} grup</p>
        <label className="mt-2 flex items-center gap-2"><input type="checkbox" checked={audienceIds.length > 0} onChange={(event) => setAudienceIds(event.target.checked ? (audiences ?? []).map((audience) => Number(audience.id)) : [])} />Dołącz do kontekstu</label>
        {audienceIds.length > 0 && <div className="mt-2 space-y-2 border-l pl-3">{audiences?.map((audience) => {
          const id = Number(audience.id)
          return <label key={id} className="flex items-center gap-2"><input type="checkbox" checked={audienceIds.includes(id)} onChange={() => setAudienceIds((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id])} />{String(audience.name ?? `#${id}`)}</label>
        })}</div>}
      </div>}
      {hasAngles && <div className="mt-3 rounded-md border bg-muted/30 p-3">
        <p className="font-medium">3.{angleSectionNumber}. Marketing angles</p>
        <p className="mt-1 text-muted-foreground">Powiązany zasób · {angles?.length} dostępnych</p>
        <label className="mt-2 flex items-center gap-2"><input type="checkbox" checked={angleIds.length > 0} onChange={(event) => setAngleIds(event.target.checked ? (angles ?? []).map((angle) => Number(angle.id)) : [])} />Dołącz do kontekstu</label>
        {angleIds.length > 0 && <div className="mt-2 space-y-2 border-l pl-3">{angles?.map((angle) => {
          const id = Number(angle.id)
          return <label key={id} className="flex items-center gap-2"><input type="checkbox" checked={angleIds.includes(id)} onChange={() => setAngleIds((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id])} />{String(angle.name)}</label>
        })}</div>}
      </div>}
      {hasConcepts && <div className="mt-3 rounded-md border bg-muted/30 p-3">
        <p className="font-medium">3.{conceptSectionNumber}. Ad Concepts</p>
        <p className="mt-1 text-muted-foreground">Powiązany zasób · {concepts?.length} dostępnych</p>
        <label className="mt-2 flex items-center gap-2"><input type="checkbox" checked={conceptIds.length > 0} onChange={(event) => setConceptIds(event.target.checked ? (concepts ?? []).map((concept) => Number(concept.id)) : [])} />Dołącz do kontekstu</label>
        {conceptIds.length > 0 && <div className="mt-2 space-y-2 border-l pl-3">{concepts?.map((concept) => {
          const id = Number(concept.id)
          return <label key={id} className="flex items-center gap-2"><input type="checkbox" checked={conceptIds.includes(id)} onChange={() => setConceptIds((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id])} />{String(concept.name)}</label>
        })}</div>}
      </div>}
      <SelectableResourceSection number={planSectionNumber} title="Creative plans" items={plans} selectedIds={planIds} onChange={setPlanIds} />
      <SelectableResourceSection number={ugcSectionNumber} title="UGC" items={ugcCreatives} selectedIds={ugcIds} onChange={setUgcIds} />
      <SelectableResourceSection number={copySectionNumber} title="Ad copy" items={adCopies} selectedIds={copyIds} onChange={setCopyIds} />
      <SelectableResourceSection number={brandStyleSectionNumber} title="Brand styles" items={brandStyles} selectedIds={brandStyleIds} onChange={setBrandStyleIds}
        itemLabel={(item) => `${String(item.font_family)} · marka ${String(item.brand_color)} · tekst ${String(item.text_color)} · tło ${String(item.background_color)}`} />
      <SelectableResourceSection number={analysisSectionNumber} title="Analizy" items={analyses} selectedIds={analysisIds} onChange={setAnalysisIds} />
      <SelectableResourceSection number={checklistSectionNumber} title="Checklisty" items={checklists} selectedIds={checklistIds} onChange={setChecklistIds} />
      <SelectableResourceSection number={blueprintSectionNumber} title="Page blueprints" items={pageBlueprints} selectedIds={pageBlueprintIds} onChange={setPageBlueprintIds} />
      <SelectableResourceSection number={pageSectionNumber} title="Pages" items={pages} selectedIds={pageIds} onChange={setPageIds} />
      {(additionalContextsError || audiencesError || anglesError || conceptsError || plansError || ugcError || copiesError || brandStylesError || analysesError || checklistsError || blueprintsError || pagesError) && <p role="alert" className="mt-2 text-destructive">Nie udało się pobrać części powiązanych danych profilu.</p>}
    </div>}
    {allowNotes && <SelectableResourceSection prefix="" number={isProfile ? 4 : hasEarlierResource ? 3 : 2} title="Notatki" items={notes} selectedIds={noteIds} onChange={setNoteIds}
      itemLabel={(item) => String(item.title ?? `#${item.id}`)} />
    }
    {allowNotes && notesError && <p role="alert" className="text-destructive">Nie udało się pobrać notatek.</p>}
  </div>
}
