import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { EntityViewer } from '@/components/EntityViewer'
import { useListMarketingAnglesQuery } from '@/features/marketingAngles/marketingAnglesApi'
import { useListAdConceptsQuery } from '@/features/adConcepts/adConceptsApi'
import { useGetOfferProfileLlmContextQuery } from './offerProfilesApi'

export function OfferProfileContextJsonPanel({ offerProfileId }: { offerProfileId: number }) {
  const [includeSource, setIncludeSource] = useState(true)
  const [includeRaw, setIncludeRaw] = useState(true)
  const [includeAudiences, setIncludeAudiences] = useState(false)
  const [marketingAngleIds, setMarketingAngleIds] = useState<number[]>([])
  const [adConceptIds, setAdConceptIds] = useState<number[]>([])
  const { data: angles, isLoading: anglesLoading, error: anglesError } = useListMarketingAnglesQuery(offerProfileId)
  const { data: concepts, isLoading: conceptsLoading, error: conceptsError } = useListAdConceptsQuery(offerProfileId)
  const include: Array<'offer_source' | 'offer_raw' | 'target_audiences' | 'marketing_angle' | 'ad_concept'> = []
  if (includeSource) include.push('offer_source')
  if (includeRaw) include.push('offer_raw')
  if (includeAudiences) include.push('target_audiences')
  if (marketingAngleIds.length) include.push('marketing_angle')
  if (adConceptIds.length) include.push('ad_concept')
  const { currentData, isFetching, error, refetch } = useGetOfferProfileLlmContextQuery({
    id: offerProfileId, include, marketingAngleIds, adConceptIds,
  }, { refetchOnMountOrArgChange: true })

  const toggleAngle = (id: number) => setMarketingAngleIds((current) =>
    current.includes(id) ? current.filter((item) => item !== id) : [...current, id],
  )
  const toggleConcept = (id: number) => setAdConceptIds((current) =>
    current.includes(id) ? current.filter((item) => item !== id) : [...current, id],
  )

  return <div className="space-y-4">
    <fieldset className="space-y-2 rounded-md border p-3">
      <legend className="px-1 text-sm font-medium">Dołącz do kontekstu</legend>
      <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={includeSource} onChange={(event) => setIncludeSource(event.target.checked)} />Źródło oferty</label>
      <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={includeRaw} onChange={(event) => setIncludeRaw(event.target.checked)} />Surowa oferta</label>
      <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={includeAudiences} onChange={(event) => setIncludeAudiences(event.target.checked)} />Grupy docelowe</label>
      <p className="pt-2 text-sm font-medium">Marketing angles</p>
      {anglesLoading && <p className="text-xs text-muted-foreground">Ładowanie…</p>}
      {anglesError && <p role="alert" className="text-xs text-destructive">Nie udało się pobrać marketing angles.</p>}
      {angles?.map((angle) => <label key={String(angle.id)} className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={marketingAngleIds.includes(Number(angle.id))} onChange={() => toggleAngle(Number(angle.id))} />{String(angle.name)}
      </label>)}
      <p className="pt-2 text-sm font-medium">Ad Concepts</p>
      {conceptsLoading && <p className="text-xs text-muted-foreground">Ładowanie…</p>}
      {conceptsError && <p role="alert" className="text-xs text-destructive">Nie udało się pobrać Ad Concepts.</p>}
      {concepts?.map((concept) => <label key={String(concept.id)} className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={adConceptIds.includes(Number(concept.id))} onChange={() => toggleConcept(Number(concept.id))} />{String(concept.name)}
      </label>)}
    </fieldset>
    <div className="flex flex-wrap items-center gap-2">
      <Button type="button" variant="outline" size="sm" onClick={() => void refetch()}>Odśwież</Button>
    </div>
    {isFetching && <p className="text-sm text-muted-foreground">Pobieranie kontekstu…</p>}
    {error && <p role="alert" className="text-sm text-destructive">Nie udało się pobrać kontekstu profilu.</p>}
    {currentData && <EntityViewer data={currentData.sections} />}
  </div>
}
