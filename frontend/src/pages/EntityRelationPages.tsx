import { useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { EntityList } from '@/components/EntityList'
import { ResourceList } from '@/components/ResourceList'
import { MultiToggle } from '@/components/MultiToggle'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import { EditTargetAudienceForm } from '@/features/targetAudiences/TargetAudienceForm'
import {
  useCreateOfferProfileElementMutation,
  useDeleteOfferProfileElementMutation,
  useGenerateOfferProfileElementsMutation,
  useGetOfferProfileQuery,
  useListOfferProfileElementsQuery,
  useListOfferProfileElementTypesQuery,
  useUpdateOfferProfileElementMutation,
} from '@/features/offerProfiles/offerProfileApi'
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
  const [remove] = useDeleteOfferProfileElementMutation()
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
        onEdit={(element) => openPanel({
          title: 'Edytuj element oferty',
          content: <OfferProfileElementForm offerProfileId={offerProfileId} element={element} onSaved={closePanel} />,
        })}
        onDelete={(element) => remove({ id: element.id as number, offerProfileId })}
        actions={
          <>
            <Button
              variant="outline"
              className="h-10 rounded-none px-4"
              onClick={() => openPanel({
                title: 'Generuj elementy oferty',
                content: <GenerateOfferProfileElementsForm offerProfileId={offerProfileId} onGenerated={closePanel} />,
              })}
            >
              Generuj elementy
            </Button>
            <Button className="h-10 rounded-none px-4" onClick={() => openPanel({
              title: 'Dodaj element oferty',
              content: <OfferProfileElementForm offerProfileId={offerProfileId} onSaved={closePanel} />,
            })}>
              Dodaj element
            </Button>
          </>
        }
      />
    </div>
  )
}

function GenerateOfferProfileElementsForm({
  offerProfileId,
  onGenerated,
}: {
  offerProfileId: number
  onGenerated: () => void
}) {
  const { data: types = [], isLoading: areTypesLoading } = useListOfferProfileElementTypesQuery()
  const [generate, generateState] = useGenerateOfferProfileElementsMutation()
  const [selectedTypes, setSelectedTypes] = useState<string[]>([])
  const [examplesPerType, setExamplesPerType] = useState(3)
  const [error, setError] = useState<string | null>(null)

  const submit = async () => {
    setError(null)
    try {
      await generate({
        offerProfileId,
        element_types: selectedTypes,
        examples_per_type: examplesPerType,
      }).unwrap()
      onGenerated()
    } catch {
      setError('Nie udało się wygenerować elementów oferty.')
    }
  }

  return (
    <div className="space-y-5">
      <div className="space-y-2">
        <span className="text-sm font-medium">Typy elementów do wygenerowania</span>
        {areTypesLoading ? (
          <p className="text-sm text-muted-foreground">Ładowanie typów…</p>
        ) : (
          <MultiToggle
            ariaLabel="Typy elementów do wygenerowania"
            values={selectedTypes}
            onValueChange={setSelectedTypes}
            options={types.map((type) => ({ value: type, label: type.replaceAll('_', ' ') }))}
            disabled={generateState.isLoading}
          />
        )}
      </div>
      <label className="block space-y-2">
        <span className="text-sm font-medium">Liczba przykładów na typ</span>
        <Input
          type="number"
          value={examplesPerType}
          onChange={(event) => setExamplesPerType(Number(event.target.value))}
          disabled={generateState.isLoading}
        />
      </label>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <Button
        onClick={() => void submit()}
        disabled={selectedTypes.length === 0 || generateState.isLoading}
      >
        {generateState.isLoading ? 'Generowanie…' : 'Generuj'}
      </Button>
    </div>
  )
}

function OfferProfileElementForm({
  offerProfileId,
  element,
  onSaved,
}: {
  offerProfileId: number
  element?: Entity
  onSaved: () => void
}) {
  const { data: types = [], isLoading: areTypesLoading } = useListOfferProfileElementTypesQuery()
  const [create, createState] = useCreateOfferProfileElementMutation()
  const [update, updateState] = useUpdateOfferProfileElementMutation()
  const [error, setError] = useState<string | null>(null)
  const isEditing = Boolean(element)
  const isSubmitting = isEditing ? updateState.isLoading : createState.isLoading

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setError(null)

    const fields = {
      type: String(form.get('type') ?? ''),
      name: String(form.get('name') ?? ''),
      description: String(form.get('description') ?? ''),
    }

    try {
      if (element) {
        await update({ id: element.id as number, offerProfileId, fields }).unwrap()
      } else {
        await create({ offerProfileId, ...fields }).unwrap()
      }
      onSaved()
    } catch {
      setError(isEditing ? 'Nie udało się zapisać elementu oferty.' : 'Nie udało się dodać elementu oferty.')
    }
  }

  return <form className="space-y-5" onSubmit={(event) => void submit(event)}>
    <label className="block space-y-2">
      <span className="text-sm font-medium">Typ</span>
      <select
        name="type"
        required
        defaultValue={element?.type as string | undefined}
        disabled={areTypesLoading || types.length === 0}
        className="h-8 w-full rounded-lg border border-input bg-transparent px-2.5 text-sm"
      >
        <option value="">{areTypesLoading ? 'Ładowanie typów…' : 'Wybierz typ'}</option>
        {types.map((type) => <option key={type} value={type}>{type.replaceAll('_', ' ')}</option>)}
      </select>
    </label>
    <label className="block space-y-2">
      <span className="text-sm font-medium">Nazwa</span>
      <Input name="name" required maxLength={255} defaultValue={element?.name as string | undefined} placeholder="Np. Darmowa dostawa" />
    </label>
    <label className="block space-y-2">
      <span className="text-sm font-medium">Opis</span>
      <Textarea name="description" defaultValue={element?.description as string | undefined} placeholder="Opcjonalny opis elementu" />
    </label>
    {error && <p className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={isSubmitting || areTypesLoading || types.length === 0}>
      {isSubmitting ? (isEditing ? 'Zapisywanie…' : 'Dodawanie…') : (isEditing ? 'Zapisz' : 'Dodaj element')}
    </Button>
  </form>
}
