import { useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { EntityList } from '@/components/EntityList'
import { ResourceList } from '@/components/ResourceList'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import { EditTargetAudienceForm } from '@/features/targetAudiences/TargetAudienceForm'
import { useCreateOfferProfileElementMutation, useGetOfferProfileQuery, useListOfferProfileElementsQuery, useListOfferProfileElementTypesQuery } from '@/features/offerProfiles/offerProfileApi'
import { useDeleteTargetAudienceMutation, useGenerateTargetAudiencesMutation } from '@/features/targetAudiences/targetAudiencesApi'
import type { Entity } from '@/types'

export function OfferProfileTargetAudiencesPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data, isLoading, error } = useGetOfferProfileQuery(offerProfileId)
  const [generate, generateState] = useGenerateTargetAudiencesMutation()
  const [remove] = useDeleteTargetAudienceMutation()
  const { openPanel, closePanel } = useSidePanel()
  const items = (data?.target_audiences as Entity[] | undefined) ?? []

  return (
    <div className="w-full p-6 lg:p-10">
      <ResourceList
        title="Grupy docelowe"
        items={items}
        isLoading={isLoading}
        error={error}
        linkTo={(item) => `/target-audiences/${item.id}`}
        itemLabel={(item) => (item.name as string) ?? `#${item.id}`}
        onGenerate={() => generate({ offerProfileId })}
        isGenerating={generateState.isLoading}
        generateLabel="Generuj grupy docelowe"
        onEdit={(item) => openPanel({
          title: 'Edytuj grupę docelową',
          content: <EditTargetAudienceForm id={item.id as number} data={item} onSaved={closePanel} />,
        })}
        onDelete={(item) => remove({ id: item.id as number, offerProfileId })}
      />
    </div>
  )
}

export function OfferProfileElementsPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data: elements = [], isLoading, error } = useListOfferProfileElementsQuery(offerProfileId)
  const { openPanel, closePanel } = useSidePanel()

  return (
    <div className="w-full p-6 lg:p-10">
      <EntityList
        title="Elementy oferty"
        items={elements}
        isLoading={isLoading}
        error={error}
        itemLabel={(element) => (element.name as string) ?? `#${element.id}`}
        itemDescription={(element) => [
          String(element.type ?? '').replaceAll('_', ' '),
          element.description ? String(element.description) : null,
        ].filter(Boolean).join(' — ')}
        emptyTitle="Brak elementów oferty"
        emptyDescription="Dodaj pierwszy element, aby rozpocząć pracę."
        actions={
          <Button className="h-10 rounded-none px-4" onClick={() => openPanel({
            title: 'Dodaj element oferty',
            content: <OfferProfileElementForm offerProfileId={offerProfileId} onCreated={closePanel} />,
          })}>
            Dodaj element
          </Button>
        }
      />
    </div>
  )
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
