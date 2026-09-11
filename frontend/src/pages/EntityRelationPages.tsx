import { useState, type FormEvent } from 'react'
import { Search } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { EntityList } from '@/components/EntityList'
import { ResourceList } from '@/components/ResourceList'
import { ListFilters, ReviewStatusFilter, ReviewStatusSortSelect, type ReviewStatusFilterValue, type ReviewStatusSort } from '@/components/ListFilters'
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
  useListOfferProfileElementsQuery,
  useListOfferProfileElementTypesQuery,
  useUpdateOfferProfileElementMutation,
  type OfferProfileElementSort,
} from '@/features/offerProfiles/offerProfileApi'
import { useDeleteTargetAudienceMutation, useGenerateTargetAudiencesMutation, useListTargetAudiencesForOfferProfileQuery, useUpdateTargetAudienceMutation } from '@/features/targetAudiences/targetAudiencesApi'
import type { Entity } from '@/types'

export function OfferProfileTargetAudiencesPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const [page, setPage] = useState(1)
  const [isReviewedFilter, setIsReviewedFilter] = useState<ReviewStatusFilterValue>('')
  const [reviewStatusSort, setReviewStatusSort] = useState<ReviewStatusSort>('unreviewed_first')
  const { data: result, isLoading, error } = useListTargetAudiencesForOfferProfileQuery({
    offerProfileId,
    page,
    pageSize: 6,
    isReviewed: isReviewedFilter === '' ? undefined : isReviewedFilter === 'true',
    sort: reviewStatusSort,
  })
  const { data: unreviewedResult } = useListTargetAudiencesForOfferProfileQuery({
    offerProfileId,
    pageSize: 1,
    isReviewed: false,
  })
  const [generate, generateState] = useGenerateTargetAudiencesMutation()
  const [remove] = useDeleteTargetAudienceMutation()
  const [updateTargetAudience] = useUpdateTargetAudienceMutation()
  const { openPanel, closePanel } = useSidePanel()
  const items = result?.items ?? []

  const updateIsReviewedFilter = (value: ReviewStatusFilterValue) => {
    setIsReviewedFilter(value)
    setPage(1)
  }

  const updateReviewStatusSort = (value: ReviewStatusSort) => {
    setReviewStatusSort(value)
    setPage(1)
  }

  return (
    <div className="w-full p-6 lg:p-10">
      <ResourceList
        title="Grupy docelowe"
        items={items}
        totalItems={result?.total_items}
        attentionItems={unreviewedResult?.total_items}
        isLoading={isLoading}
        error={error}
        itemLabel={(item) => (item.name as string) ?? `#${item.id}`}
        onGenerate={() => generate({ offerProfileId })}
        isGenerating={generateState.isLoading}
        generateLabel="Generuj grupy docelowe"
        contentBeforeList={
          <ListFilters>
            <ReviewStatusFilter value={isReviewedFilter} onChange={updateIsReviewedFilter} />
            <ReviewStatusSortSelect value={reviewStatusSort} onChange={updateReviewStatusSort} />
          </ListFilters>
        }
        footer={result && result.total_pages > 1 ? (
          <div className="flex items-center justify-between gap-3 border-t pt-4">
            <span className="text-sm text-muted-foreground">Strona {result.page} z {result.total_pages}</span>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={result.page <= 1} onClick={() => setPage(result.page - 1)}>Poprzednia</Button>
              <Button variant="outline" size="sm" disabled={result.page >= result.total_pages} onClick={() => setPage(result.page + 1)}>Następna</Button>
            </div>
          </div>
        ) : undefined}
        onEdit={(item) => openPanel({
          title: 'Edytuj grupę docelową',
          content: <EditTargetAudienceForm id={item.id as number} data={item} onSaved={closePanel} />,
        })}
        onDelete={(item) => remove({ id: item.id as number, offerProfileId })}
        itemActions={(item) => (
          <Button
            variant={item.is_reviewed ? 'ghost' : 'default'}
            size="sm"
            className="h-7 px-2.5 text-xs"
            onClick={() => updateTargetAudience({
              id: item.id as number,
              offerProfileId,
              is_reviewed: item.is_reviewed !== true,
            })}
          >
            {item.is_reviewed ? 'Oznacz jako niesprawdzone' : 'Zatwierdź'}
          </Button>
        )}
      />
    </div>
  )
}

export function OfferProfileElementsPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [elementType, setElementType] = useState('')
  const [isReviewedFilter, setIsReviewedFilter] = useState<ReviewStatusFilterValue>('')
  const [sort, setSort] = useState<OfferProfileElementSort>('created_at_desc')
  const { data: elementTypes = [] } = useListOfferProfileElementTypesQuery()
  const { data: result, isLoading, error } = useListOfferProfileElementsQuery({
    offerProfileId,
    page,
    pageSize: 6,
    search,
    elementType,
    isReviewed: isReviewedFilter === '' ? undefined : isReviewedFilter === 'true',
    sort,
  })
  const { data: unreviewedElementsResult } = useListOfferProfileElementsQuery({
    offerProfileId,
    pageSize: 1,
    isReviewed: false,
  })
  const elements = result?.items ?? []
  const [remove] = useDeleteOfferProfileElementMutation()
  const [updateElement] = useUpdateOfferProfileElementMutation()
  const { openPanel, closePanel } = useSidePanel()

  const updateSearch = (value: string) => {
    setSearch(value)
    setPage(1)
  }

  const updateElementType = (value: string) => {
    setElementType(value)
    setPage(1)
  }

  const updateSort = (value: OfferProfileElementSort) => {
    setSort(value)
    setPage(1)
  }

  const updateIsReviewedFilter = (value: ReviewStatusFilterValue) => {
    setIsReviewedFilter(value)
    setPage(1)
  }

  return (
    <div className="w-full p-6 lg:p-10">
      <EntityList
        title="Elementy oferty"
        items={elements}
        totalItems={result?.total_items}
        attentionItems={unreviewedElementsResult?.total_items}
        isLoading={isLoading}
        error={error}
        itemLabel={(element) => (element.name as string) ?? `#${element.id}`}
        itemDescription={(element) => element.description ? String(element.description) : ''}
        itemMeta={(element) => `Identyfikator ${String(element.id)}`}
        emptyTitle="Brak elementów oferty"
        emptyDescription="Dodaj pierwszy element, aby rozpocząć pracę."
        contentBeforeList={<>
          <ListFilters>
            <label className="relative min-w-64 flex-1 max-w-md">
              <Search className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={search}
                onChange={(event) => updateSearch(event.target.value)}
                className="pl-9"
                placeholder="Szukaj w elementach oferty..."
              />
            </label>
            <select
              aria-label="Filtruj według typu"
              value={elementType}
              onChange={(event) => updateElementType(event.target.value)}
              className="sr-only"
            >
              <option value="">Wszystkie typy</option>
              {elementTypes.map((type) => (
                <option key={type} value={type}>{type.replaceAll('_', ' ')}</option>
              ))}
            </select>
            <select
              aria-label="Sortowanie elementów oferty"
              value={sort}
              onChange={(event) => updateSort(event.target.value as OfferProfileElementSort)}
              className="h-9 rounded-lg border border-input bg-transparent px-2.5 text-sm"
            >
              <option value="created_at_desc">Najnowsze</option>
              <option value="created_at_asc">Najstarsze</option>
              <option value="name_asc">Nazwa: A–Z</option>
              <option value="name_desc">Nazwa: Z–A</option>
            </select>
            <ReviewStatusFilter
              value={isReviewedFilter}
              onChange={updateIsReviewedFilter}
              ariaLabel="Filtruj według sprawdzenia elementów oferty"
            />
          </ListFilters>
          <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
            <button type="button" onClick={() => updateElementType('')} className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${!elementType ? 'bg-[#111111] text-white shadow-sm' : 'border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}>Wszystkie typy</button>
            {elementTypes.map((type) => <button key={type} type="button" onClick={() => updateElementType(type)} className={`inline-flex items-center rounded-md border px-2.5 py-1 text-xs font-medium transition-colors ${elementType === type ? 'border-[#111111] bg-[#111111] text-white shadow-sm' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50 hover:text-slate-900'}`}>{formatElementType(type)}</button>)}
          </div>
        </>}
        footer={result && result.total_pages > 1 ? (
          <div className="flex items-center justify-between gap-3 border-t pt-4">
            <span className="text-sm text-muted-foreground">
              Strona {result.page} z {result.total_pages}
            </span>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={result.page <= 1} onClick={() => setPage(result.page - 1)}>
                Poprzednia
              </Button>
              <Button variant="outline" size="sm" disabled={result.page >= result.total_pages} onClick={() => setPage(result.page + 1)}>
                Następna
              </Button>
            </div>
          </div>
        ) : undefined}
        onEdit={(element) => openPanel({
          title: 'Edytuj element oferty',
          content: <OfferProfileElementForm offerProfileId={offerProfileId} element={element} onSaved={closePanel} />,
        })}
        onDelete={(element) => remove({ id: element.id as number, offerProfileId })}
        itemActions={(element) => (
          <Button
            variant={element.is_reviewed ? 'ghost' : 'default'}
            size="sm"
            className="h-7 px-2.5 text-xs"
            onClick={() => updateElement({ id: element.id as number, offerProfileId, fields: { is_reviewed: element.is_reviewed !== true } })}
          >
            {element.is_reviewed ? 'Oznacz jako niesprawdzone' : 'Zatwierdź'}
          </Button>
        )}
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

function formatElementType(type: string) {
  return type.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase())
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
  const [isReviewed, setIsReviewed] = useState(Boolean(element?.is_reviewed))
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
      is_reviewed: isReviewed,
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
    <label className="flex items-center gap-2 text-sm font-medium">
      <Input
        type="checkbox"
        checked={isReviewed}
        onChange={(event) => setIsReviewed(event.target.checked)}
        className="size-4"
      />
      Element został sprawdzony
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
