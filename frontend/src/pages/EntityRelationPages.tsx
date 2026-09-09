import { useState, type FormEvent, type ReactNode } from 'react'
import { useParams } from 'react-router-dom'
import { RelationList } from '@/components/EditableFields'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import { useListFactStatusesQuery } from '@/features/factStatus/factStatusApi'
import { useListReviewStatusesQuery } from '@/features/reviewStatus/reviewStatusApi'
import { useCreateOfferProfileElementMutation, useGetOfferProfileQuery, useListOfferProfileElementsQuery, useListOfferProfileElementTypesQuery } from '@/features/offerProfiles/offerProfileApi'
import { useDeleteTargetAudienceMutation, useGenerateTargetAudiencesMutation, useUpdateTargetAudienceMutation } from '@/features/targetAudiences/targetAudiencesApi'
import type { Entity } from '@/types'

function CollectionPage({ title, children }: { title: string; children: ReactNode }) {
  return <div className="w-full space-y-6 p-6 lg:p-10"><h1 className="text-2xl font-semibold">{title}</h1>{children}</div>
}

export function OfferProfileTargetAudiencesPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data, isLoading, error } = useGetOfferProfileQuery(offerProfileId)
  const { data: statuses } = useListFactStatusesQuery()
  const { data: reviewStatuses } = useListReviewStatusesQuery()
  const [generate, generateState] = useGenerateTargetAudiencesMutation()
  const [remove] = useDeleteTargetAudienceMutation()
  const [update] = useUpdateTargetAudienceMutation()
  const items = (data?.target_audiences as Entity[] | undefined) ?? []
  return <CollectionPage title="Grupy docelowe"><Button size="sm" onClick={() => generate({ offerProfileId })} disabled={generateState.isLoading}>{generateState.isLoading ? 'Generowanie…' : 'Generuj grupy docelowe'}</Button><RelationList fieldKey="target_audiences" items={items} onEditLink={(item) => `/target-audiences/${item.id}/edit`} onDelete={(item) => remove({ id: item.id as number, offerProfileId })} onStatusChange={(item, fact_status) => update({ id: item.id as number, offerProfileId, fact_status }).unwrap()} onReviewStatusChange={(item, review_status) => update({ id: item.id as number, offerProfileId, review_status }).unwrap()} statuses={statuses} reviewStatuses={reviewStatuses} showHeading={false} />{isLoading && <p>Ładowanie…</p>}{error && <p>Nie udało się pobrać danych.</p>}</CollectionPage>
}

export function OfferProfileElementsPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data: elements = [], isLoading, error } = useListOfferProfileElementsQuery(offerProfileId)
  const { openPanel, closePanel } = useSidePanel()

  return <CollectionPage title="Elementy oferty">
    <Button size="sm" onClick={() => openPanel({
      title: 'Dodaj element oferty',
      content: <OfferProfileElementForm offerProfileId={offerProfileId} onCreated={closePanel} />,
    })}>Dodaj element</Button>
    {isLoading && <p>Ładowanie…</p>}
    {error && <p>Nie udało się pobrać elementów oferty.</p>}
    {!isLoading && !error && elements.length === 0 && <p>Brak elementów oferty.</p>}
    <div className="grid gap-4 md:grid-cols-2">
      {elements.map((element) => <article key={String(element.id)} className="rounded-lg border bg-card p-5 shadow-sm">
        <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">{String(element.type).replaceAll('_', ' ')}</p>
        <h2 className="text-lg font-semibold">{String(element.name)}</h2>
        {element.description ? <p className="mt-2 whitespace-pre-wrap text-sm text-muted-foreground">{String(element.description)}</p> : null}
      </article>)}
    </div>
  </CollectionPage>
}

function OfferProfileElementForm({ offerProfileId, onCreated }: { offerProfileId: number; onCreated: () => void }) {
  const { data: types = [], isLoading: areTypesLoading } = useListOfferProfileElementTypesQuery()
  const [create, createState] = useCreateOfferProfileElementMutation()
  const [error, setError] = useState<string | null>(null)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setError(null)
    try {
      await create({
        offerProfileId,
        type: String(form.get('type') ?? ''),
        name: String(form.get('name') ?? ''),
        description: String(form.get('description') ?? ''),
      }).unwrap()
      onCreated()
    } catch {
      setError('Nie udało się dodać elementu oferty.')
    }
  }

  return <form className="space-y-5" onSubmit={(event) => void submit(event)}>
    <label className="block space-y-2"><span className="text-sm font-medium">Typ</span><select name="type" required disabled={areTypesLoading || types.length === 0} className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm"><option value="">{areTypesLoading ? 'Ładowanie typów…' : 'Wybierz typ'}</option>{types.map((type) => <option key={type} value={type}>{type.replaceAll('_', ' ')}</option>)}</select></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Nazwa</span><Input name="name" required maxLength={255} placeholder="Np. Darmowa dostawa" /></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Opis</span><Textarea name="description" placeholder="Opcjonalny opis elementu" /></label>
    {error && <p className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={createState.isLoading || areTypesLoading || types.length === 0}>{createState.isLoading ? 'Dodawanie…' : 'Dodaj element'}</Button>
  </form>
}
