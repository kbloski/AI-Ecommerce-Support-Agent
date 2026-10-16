import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { useListOffersQuery } from '@/features/offers/offersApi'
import { useListOfferSourceForOfferQuery } from '@/features/offerSources/offerSourceApi'
import { offerSourceLabel } from '@/features/offerSources/offerSourceLabel'
import { useListOfferProfilesQuery } from '@/features/offerProfiles/offerProfilesApi'
import { ResourceContextExportPanel } from '@/features/resources/ResourceContextExportPanel'
import type { ResourceContextRequest } from '@/features/resources/resourceContextApi'

const selectClassName = 'mt-2 h-10 w-full rounded-md border border-input bg-background px-3 text-sm'

export function ResourceExportPanel() {
  const [offerPage, setOfferPage] = useState(1)
  const [offerId, setOfferId] = useState<number | null>(null)
  const [offerName, setOfferName] = useState('')
  const [sourceId, setSourceId] = useState<number | null>(null)
  const [profileId, setProfileId] = useState<number | null>(null)
  const { currentData: offers, isFetching: offersLoading, error: offersError } = useListOffersQuery({ page: offerPage })
  const { currentData: sources, isFetching: sourcesLoading, error: sourcesError } = useListOfferSourceForOfferQuery(
    offerId ?? 0, { skip: offerId === null },
  )
  const { currentData: profiles, isFetching: profilesLoading, error: profilesError } = useListOfferProfilesQuery(
    sourceId ?? 0, { skip: sourceId === null },
  )

  const request: ResourceContextRequest | null = profileId !== null
    ? { type: 'offer_profile', id: profileId }
    : sourceId !== null
      ? { type: 'offer_source', id: sourceId }
      : offerId !== null
        ? { type: 'offer_raw', id: offerId }
        : null

  return <div className="w-full min-w-0 space-y-5 pb-4">
    <div>
      <p className="text-sm text-muted-foreground">Wybierz ścieżkę zasobów, zdecyduj co dołączyć, a następnie sprawdź i pobierz kontekst jako plik TXT.</p>
    </div>
    <div className="space-y-4 rounded-md border p-4">
      <h2 className="font-semibold">Wybierz zasoby</h2>
      <div>
        <label htmlFor="export-offer" className="text-sm font-medium">1. Surowa oferta</label>
        <select id="export-offer" className={selectClassName} value={offerId ?? ''} disabled={offersLoading} onChange={(event) => {
          const id = Number(event.target.value)
          setOfferId(id || null)
          setOfferName(event.target.selectedOptions[0]?.textContent ?? '')
          setSourceId(null)
          setProfileId(null)
        }}>
          <option value="">Wybierz surową ofertę</option>
          {offerId !== null && !offers?.items.some((offer) => Number(offer.id) === offerId) && <option value={offerId}>{offerName}</option>}
          {offers?.items.map((offer) => <option key={offer.id} value={Number(offer.id)}>{String(offer.name ?? `Oferta #${offer.id}`)}</option>)}
        </select>
        <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
          <Button type="button" variant="outline" size="sm" disabled={offerPage === 1 || offersLoading} onClick={() => setOfferPage((page) => page - 1)}>Poprzednie</Button>
          <span>Strona {offerPage}</span>
          <Button type="button" variant="outline" size="sm" disabled={offersLoading || !offers || offerPage * offers.page_size >= offers.total_items} onClick={() => setOfferPage((page) => page + 1)}>Następne</Button>
        </div>
        {offersError && <p role="alert" className="mt-2 text-sm text-destructive">Nie udało się pobrać ofert.</p>}
      </div>
      {offerId !== null && <div>
        <label htmlFor="export-source" className="text-sm font-medium">2. Źródło oferty</label>
        <select id="export-source" className={selectClassName} value={sourceId ?? ''} onChange={(event) => {
          setSourceId(Number(event.target.value) || null)
          setProfileId(null)
        }} disabled={sourcesLoading || !!sourcesError}>
          <option value="">Bez źródła oferty</option>
          {sources?.map((source) => <option key={source.id} value={Number(source.id)}>#{source.id} — {offerSourceLabel({ offer_details: source.offer_details }, 'Źródło oferty')}</option>)}
        </select>
        {sourcesError && <p role="alert" className="mt-2 text-sm text-destructive">Nie udało się pobrać źródeł oferty.</p>}
      </div>}
      {sourceId !== null && <div>
        <label htmlFor="export-profile" className="text-sm font-medium">3. Profil oferty</label>
        <select id="export-profile" className={selectClassName} value={profileId ?? ''} onChange={(event) => setProfileId(Number(event.target.value) || null)} disabled={profilesLoading || !!profilesError}>
          <option value="">Bez profilu oferty</option>
          {profiles?.map((profile) => <option key={profile.id} value={Number(profile.id)}>{String(profile.name ?? `Profil #${profile.id}`)}</option>)}
        </select>
        {profilesError && <p role="alert" className="mt-2 text-sm text-destructive">Nie udało się pobrać profili oferty.</p>}
      </div>}
    </div>
    {request ? <div className="rounded-md border p-4">
      <h2 className="mb-4 font-semibold">Zawartość eksportu</h2>
      <ResourceContextExportPanel key={`${request.type}:${request.id}`} initialRequest={request} />
    </div> : <p className="rounded-md border border-dashed p-6 text-sm text-muted-foreground">Wybierz surową ofertę, aby rozpocząć składanie kontekstu.</p>}
  </div>
}
