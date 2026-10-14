import { useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { EntityList } from '@/components/EntityList'
import { ListFilters, ReviewStatusFilter, type ReviewStatusFilterValue } from '@/components/ListFilters'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import { useListOfferFactsQuery, useGenerateOfferFactsMutation, useCreateOfferFactMutation, useUpdateOfferFactMutation, useDeleteOfferFactMutation, type FactSort } from '@/features/offerFacts/offerFactsApi'
import type { Entity } from '@/types'

function errorMessage(error: unknown): string {
  const detail = (error as { data?: { detail?: unknown } })?.data?.detail
  return typeof detail === 'string' ? detail : 'Nie udaÃ…â€šo siÃ„â„¢ zapisaÃ„â€¡ zmian. SprawdÃ…Âº dane i sprÃƒÂ³buj ponownie.'
}

export default function OfferFactsPage() {
  const offerSourceId = Number(useParams().offerSourceId)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [review, setReview] = useState<ReviewStatusFilterValue>('')
  const [sort, setSort] = useState<FactSort>('created_at_desc')
  const [message, setMessage] = useState('')
  const [actionError, setActionError] = useState('')
  const { data: result, isLoading, error } = useListOfferFactsQuery({ offerSourceId, page, pageSize: 10, search, sort, isReviewed: review === '' ? undefined : review === 'true' })
  const { data: unreviewed } = useListOfferFactsQuery({ offerSourceId, pageSize: 1, isReviewed: false })
  const [generate, generation] = useGenerateOfferFactsMutation()
  const [update] = useUpdateOfferFactMutation()
  const [remove] = useDeleteOfferFactMutation()
  const { openPanel, closePanel } = useSidePanel()
  const run = async (action: () => Promise<unknown>) => {
    setActionError('')
    try { await action() } catch (err) { setActionError(errorMessage(err)) }
  }
  const generateFacts = () => run(async () => {
    setMessage('')
    const response = await generate(offerSourceId).unwrap()
    setPage(1)
    setMessage(response.created_count ? `Dodano ${response.created_count} faktÃƒÂ³w do sprawdzenia.` : 'Nie znaleziono nowych faktÃƒÂ³w potwierdzonych w źródle oferty.')
  })
  return <div className="w-full p-6 lg:p-10">
    <EntityList title="Fakty o produkcie" items={result?.items} totalItems={result?.total_items} attentionItems={unreviewed?.total_items} isLoading={isLoading} error={error}
      emptyTitle="Brak faktÃƒÂ³w" emptyDescription="Wygeneruj fakty ze źródła oferty lub dodaj je z cytatem ze Ã…ÂºrÃƒÂ³dÃ…â€ša."
      itemDescription={(fact) => String(fact.description)}
      itemDetails={(fact) => fact.evidence ? <blockquote className="border-l-2 pl-3 text-sm text-muted-foreground"><span className="block text-xs">Cytat ze źródła oferty</span>{String(fact.evidence)}</blockquote> : null}
      contentBeforeList={<><p className="mb-4 text-sm text-muted-foreground">Tylko informacje potwierdzone w źródle oferty. Zatwierdzone fakty sÃ„â€¦ dostÃ„â„¢pne w kontekÃ…â€ºcie dalszego generowania.</p>
        <ListFilters>
          <Input aria-label="Szukaj faktÃƒÂ³w" placeholder="Szukaj faktÃƒÂ³w..." value={search} onChange={(e) => { setSearch(e.target.value); setPage(1) }} className="max-w-md" />
          <ReviewStatusFilter value={review} onChange={(value) => { setReview(value); setPage(1) }} />
          <select aria-label="Sortowanie faktÃƒÂ³w" value={sort} onChange={(e) => { setSort(e.target.value as FactSort); setPage(1) }} className="h-9 rounded-lg border px-2.5 text-sm">
            <option value="created_at_desc">Najnowsze</option><option value="created_at_asc">Najstarsze</option><option value="name_asc">Nazwa: A-Z</option><option value="name_desc">Nazwa: Z-A</option>
          </select>
        </ListFilters>
        {message && <p role="status" className="mt-3 text-sm">{message}</p>}{actionError && <p role="alert" className="mt-3 text-sm text-destructive">{actionError}</p>}
      </>}
      actions={<><Button variant="outline" disabled={generation.isLoading} onClick={generateFacts}>{generation.isLoading ? 'Generowanie...' : 'Generuj fakty'}</Button><Button onClick={() => openPanel({ title: 'Dodaj fakt', content: <FactForm offerSourceId={offerSourceId} onSaved={closePanel} /> })}>Dodaj fakt</Button></>}
      onEdit={(fact) => openPanel({ title: 'Edytuj fakt', content: <FactForm offerSourceId={offerSourceId} fact={fact} onSaved={closePanel} /> })}
      onDelete={(fact) => run(async () => { await remove({ offerSourceId, id: fact.id as number }).unwrap(); if (result?.items.length === 1 && page > 1) setPage(page - 1) })}
      itemActions={(fact) => <Button size="sm" variant={fact.is_reviewed ? 'ghost' : 'default'} onClick={() => run(() => update({ offerSourceId, id: fact.id as number, fields: { is_reviewed: !fact.is_reviewed } }).unwrap())}>{fact.is_reviewed ? 'Oznacz jako niesprawdzone' : 'ZatwierdÃ…Âº'}</Button>}
      footer={result && result.total_pages > 1 ? <div className="flex items-center justify-between border-t pt-4"><span>Strona {page} z {result.total_pages}</span><div className="flex gap-2"><Button variant="outline" disabled={page <= 1} onClick={() => setPage(page - 1)}>Poprzednia</Button><Button variant="outline" disabled={page >= result.total_pages} onClick={() => setPage(page + 1)}>NastÃ„â„¢pna</Button></div></div> : undefined}
    />
  </div>
}

function FactForm({ offerSourceId, fact, onSaved }: { offerSourceId: number; fact?: Entity; onSaved: () => void }) {
  const [create, createState] = useCreateOfferFactMutation()
  const [update, updateState] = useUpdateOfferFactMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError('')
    const data = new FormData(event.currentTarget)
    const fields = { name: String(data.get('name')).trim(), description: String(data.get('description')).trim(), evidence: String(data.get('evidence') ?? '').trim() || null, is_reviewed: false }
    try {
      if (fact) await update({ offerSourceId, id: fact.id as number, fields }).unwrap()
      else await create({ offerSourceId, fields }).unwrap()
      onSaved()
    } catch (err) { setError(errorMessage(err)) }
  }
  return <form onSubmit={submit} className="space-y-4">
    <label className="block space-y-2"><span>Nazwa faktu</span><Input name="name" required maxLength={255} defaultValue={String(fact?.name ?? '')} /></label>
    <label className="block space-y-2"><span>Fakt</span><Textarea name="description" required defaultValue={String(fact?.description ?? '')} /></label>
    <label className="block space-y-2"><span>Cytat potwierdzajÃ„â€¦cy fakt</span><Textarea name="evidence" defaultValue={String(fact?.evidence ?? '')} /><span className="text-xs text-muted-foreground">Wklej dokÃ…â€šadny fragment oryginalnych danych produktu.</span></label>
    <p className="text-sm text-muted-foreground">Nowy lub zmieniony fakt wymaga zatwierdzenia na liÃ…â€ºcie.</p>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={createState.isLoading || updateState.isLoading}>Zapisz fakt</Button>
  </form>
}
