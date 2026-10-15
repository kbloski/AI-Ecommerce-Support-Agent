import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useListMarketingAnglesQuery } from '@/features/marketingAngles/marketingAnglesApi'
import { useListAdConceptsQuery } from '@/features/adConcepts/adConceptsApi'
import { useListProfileContextsQuery } from '@/features/additionalContexts/additionalContextsApi'
import { useListOfferFactsQuery } from '@/features/offerFacts/offerFactsApi'
import { useGetOfferProfileQuery } from '@/features/offerProfiles/offerProfilesApi'
import { useListTargetAudiencesForOfferProfileQuery } from '@/features/targetAudiences/targetAudiencesApi'
import { useLazyDownloadResourceContextQuery, useLazyGetResourceContextQuery } from './resourceContextApi'
import type { ResourceContextInclude, ResourceContextRequest, ResourceContextType } from './resourceContextApi'
import { downloadTextFile } from '@/lib/downloadTextFile'

const resourceNames: Record<ResourceContextType, string> = {
  offer_raw: 'Surowa oferta',
  offer_source: 'Źródło oferty',
  offer_profile: 'Profil oferty',
}

export function ResourceContextExportPanel({ initialRequest }: { initialRequest: ResourceContextRequest }) {
  const isProfile = initialRequest.type === 'offer_profile'
  const hasEarlierResource = initialRequest.type !== 'offer_raw'
  const [includeRaw, setIncludeRaw] = useState(initialRequest.include?.includes('offer_raw') ?? hasEarlierResource)
  const [includeSource, setIncludeSource] = useState(initialRequest.include?.includes('offer_source') ?? true)
  const [includeFacts, setIncludeFacts] = useState(initialRequest.includeOfferFacts ?? true)
  const [includeAdditionalContexts, setIncludeAdditionalContexts] = useState(initialRequest.includeAdditionalContexts ?? true)
  const [includeAudiences, setIncludeAudiences] = useState(initialRequest.include?.includes('target_audiences') ?? false)
  const [angleIds, setAngleIds] = useState<number[]>(initialRequest.marketingAngleIds ?? [])
  const [conceptIds, setConceptIds] = useState<number[]>(initialRequest.adConceptIds ?? [])
  const [step, setStep] = useState<'select' | 'preview'>('select')
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [getContext, { isFetching: isPreviewing }] = useLazyGetResourceContextQuery()
  const [downloadContext, { isFetching: isDownloading }] = useLazyDownloadResourceContextQuery()
  const { data: angles, isLoading: anglesLoading, error: anglesError } = useListMarketingAnglesQuery(initialRequest.id, { skip: !isProfile })
  const { data: concepts, isLoading: conceptsLoading, error: conceptsError } = useListAdConceptsQuery(initialRequest.id, { skip: !isProfile })
  const { data: additionalContexts, error: additionalContextsError } = useListProfileContextsQuery(initialRequest.id, { skip: !isProfile })
  const { data: audiences, error: audiencesError } = useListTargetAudiencesForOfferProfileQuery(
    { offerProfileId: initialRequest.id, pageSize: 1 }, { skip: !isProfile },
  )
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
  const hasAudiences = (audiences?.total_items ?? 0) > 0
  const hasAngles = (angles?.length ?? 0) > 0
  const hasConcepts = (concepts?.length ?? 0) > 0
  const audienceSectionNumber = 1 + Number(hasAdditionalContexts)
  const angleSectionNumber = audienceSectionNumber + Number(hasAudiences)
  const conceptSectionNumber = angleSectionNumber + Number(hasAngles)

  const request = (): ResourceContextRequest => {
    const include: ResourceContextInclude[] = []
    if (isProfile && includeSource) include.push('offer_source')
    if (hasEarlierResource && includeRaw) include.push('offer_raw')
    if (isProfile && includeAudiences) include.push('target_audiences')
    if (isProfile && angleIds.length) include.push('marketing_angle')
    if (isProfile && conceptIds.length) include.push('ad_concept')
    return {
      type: initialRequest.type, id: initialRequest.id, include,
      marketingAngleIds: isProfile ? angleIds : [],
      adConceptIds: isProfile ? conceptIds : [],
      includeOfferFacts: hasEarlierResource && (!isProfile || includeSource) && includeFacts,
      includeAdditionalContexts: isProfile ? includeAdditionalContexts : undefined,
    }
  }

  const showPreview = async () => {
    setError(null)
    try {
      const content = await getContext(request()).unwrap()
      setPreview(content)
      setStep('preview')
    } catch {
      setError('Nie udało się złożyć kontekstu. Sprawdź wybrane dane i spróbuj ponownie.')
    }
  }

  const download = async () => {
    setError(null)
    try {
      const content = await downloadContext(request()).unwrap()
      downloadTextFile(`${initialRequest.type}_${initialRequest.id}_context.txt`, content)
    } catch {
      setError('Nie udało się pobrać kontekstu.')
    }
  }

  return <div className="flex h-full min-h-0 flex-col gap-4 text-sm">
    <p className="text-muted-foreground">{step === 'select' ? 'Wybierz dane, które mają znaleźć się w kontekście. Następnie sprawdź wynik przed pobraniem.' : 'Sprawdź złożony kontekst, a następnie pobierz go jako plik TXT.'}</p>
    {step === 'select' ? <div className="min-h-0 flex-1 space-y-4 overflow-auto">
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
          <p className="mt-1 text-muted-foreground">Powiązany zasób · {audiences?.total_items} grup</p>
          <label className="mt-2 flex items-center gap-2"><input type="checkbox" checked={includeAudiences} onChange={(event) => setIncludeAudiences(event.target.checked)} />Dołącz wszystkie grupy do kontekstu</label>
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
        {(additionalContextsError || audiencesError || anglesError || conceptsError) && <p role="alert" className="mt-2 text-destructive">Nie udało się pobrać części powiązanych danych profilu.</p>}
      </div>}
    </div> : <pre className="min-h-0 flex-1 overflow-auto whitespace-pre-wrap break-words rounded-md border bg-muted/30 p-3 text-xs">{preview}</pre>}
    {error && <p role="alert" className="text-destructive">{error}</p>}
    <div className="flex flex-wrap gap-2 border-t pt-4">
      {step === 'select' ? <Button type="button" onClick={() => void showPreview()} disabled={isPreviewing || (isProfile && (anglesLoading || conceptsLoading))}>{isPreviewing ? 'Składanie kontekstu…' : 'Złóż i zobacz kontekst'}</Button> : <>
        <Button type="button" variant="outline" onClick={() => { setStep('select'); setError(null) }}>Zmień wybór</Button>
        <Button type="button" onClick={() => void download()} disabled={isDownloading}>{isDownloading ? 'Pobieranie…' : 'Pobierz TXT'}</Button>
      </>}
    </div>
  </div>
}
