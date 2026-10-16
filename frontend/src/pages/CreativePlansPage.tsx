import { useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { EntityList } from '@/components/EntityList'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import { useListAdConceptsQuery } from '@/features/adConcepts/adConceptsApi'
import { useListAdFrameworksQuery } from '@/features/adFrameworks/adFrameworksApi'
import {
  useListCreativePlansQuery, useGenerateCreativePlansMutation, useCreateCreativePlanMutation,
  useUpdateCreativePlanMutation, useDeleteCreativePlanMutation,
  type CreativePlanFields,
} from '@/features/creativePlans/creativePlansApi'
import type { Entity } from '@/types'

const selectClass = 'flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm'
const planFields = (item: Entity): CreativePlanFields => ({
  name: String(item.name ?? ''), description: String(item.description ?? ''),
  format: item.format === 'video' ? 'video' : 'image', plan: String(item.plan ?? ''),
  ad_concept_id: item.ad_concept_id == null ? null : Number(item.ad_concept_id),
})

export default function CreativePlansPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data, isLoading, error } = useListCreativePlansQuery(offerProfileId)
  const { data: concepts } = useListAdConceptsQuery(offerProfileId)
  const [remove] = useDeleteCreativePlanMutation()
  const [update] = useUpdateCreativePlanMutation()
  const { openPanel, closePanel } = useSidePanel()
  const [actionError, setActionError] = useState('')

  return <div className="w-full p-6 lg:p-10"><EntityList
    title="Creative plans" items={data} totalItems={data?.length}
    attentionItems={data?.filter((item) => !item.is_reviewed).length}
    isLoading={isLoading} error={error}
    emptyTitle="Brak creative plans" emptyDescription="Wygeneruj plan realizacji kreacji lub dodaj go ręcznie."
    itemDescription={(item) => String(item.description ?? '')}
    itemDetails={(item) => <div className="space-y-3 text-sm">
      <p><strong>Format:</strong> {String(item.format)}</p>
      <p><strong>Ad concept:</strong> {item.ad_concept_id == null ? 'Bez wybranej koncepcji' : String(concepts?.find((concept) => Number(concept.id) === Number(item.ad_concept_id))?.name ?? `#${item.ad_concept_id}`)}</p>
      <div className="whitespace-pre-wrap">{String(item.plan ?? '')}</div>
    </div>}
    contentBeforeList={actionError ? <p role="alert" className="text-sm text-destructive">{actionError}</p> : undefined}
    actions={<>
      <Button variant="outline" onClick={() => openPanel({ title: 'Dodaj creative plan', content: <PlanForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Dodaj ręcznie</Button>
      <Button onClick={() => openPanel({ title: 'Generuj creative plans', content: <GeneratePlansForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Generuj</Button>
    </>}
    onEdit={(item) => openPanel({ title: 'Edytuj creative plan', content: <PlanForm offerProfileId={offerProfileId} item={item} onSaved={closePanel} /> })}
    onDelete={(item) => { void remove({ id: Number(item.id), offerProfileId }).unwrap().catch(() => setActionError('Nie udało się usunąć planu.')) }}
    itemActions={(item) => <Button size="sm" variant={item.is_reviewed ? 'ghost' : 'default'} onClick={() => {
      void update({ id: Number(item.id), offerProfileId, fields: planFields(item), isReviewed: !item.is_reviewed }).unwrap().catch(() => setActionError('Nie udało się zmienić stanu planu.'))
    }}>{item.is_reviewed ? 'Oznacz jako niesprawdzone' : 'Zatwierdź'}</Button>}
  /></div>
}

function ConceptSelect({ concepts, defaultValue }: { concepts?: Entity[]; defaultValue?: number | null }) {
  if (!concepts) return <p className="text-sm text-muted-foreground">Ładowanie koncepcji…</p>
  return <label className="block space-y-2"><span className="text-sm font-medium">Ad concept (opcjonalnie)</span>
    <select name="ad_concept_id" defaultValue={defaultValue ?? ''} className={selectClass}>
      <option value="">Bez koncepcji — na podstawie profilu oferty</option>
      {concepts?.map((concept) => <option key={String(concept.id)} value={Number(concept.id)}>{String(concept.name)} ({String(concept.format)})</option>)}
    </select>
  </label>
}

function GeneratePlansForm({ offerProfileId, onSaved }: { offerProfileId: number; onSaved: () => void }) {
  const { data: concepts, isLoading, error: conceptsError } = useListAdConceptsQuery(offerProfileId)
  const { data: frameworks, isLoading: frameworksLoading, error: frameworksError } = useListAdFrameworksQuery()
  const [format, setFormat] = useState('')
  const [frameworkId, setFrameworkId] = useState('')
  const selectedFramework = frameworks?.find((framework) => framework.id === frameworkId)
  const [generate, state] = useGenerateCreativePlansMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const format = form.get('preferred_format')
    const preferredFormat = format === 'image' || format === 'video' ? format : null
    setError('')
    try {
      await generate({ offerProfileId, count: Number(form.get('count')), adConceptId: Number(form.get('ad_concept_id')) || null,
        preferredFormat: preferredFormat || null, adFrameworkId: frameworkId || null, generationInstructions: String(form.get('generation_instructions') ?? '').trim() }).unwrap()
      onSaved()
    } catch { setError('Nie udało się wygenerować planów. Spróbuj ponownie.') }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Liczba planów</span><Input name="count" type="number" min={1} max={10} defaultValue={1} required /></label>
    <ConceptSelect concepts={concepts} />
    {conceptsError && <p role="alert" className="text-sm text-destructive">Nie udało się pobrać koncepcji.</p>}
    <label className="block space-y-2"><span className="text-sm font-medium">Format</span><select name="preferred_format" value={format} onChange={(event) => { setFormat(event.target.value); setFrameworkId('') }} className={selectClass}>
      <option value="">Z koncepcji lub według wskazówek</option><option value="image">Obraz</option><option value="video">Wideo</option>
    </select></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Ad framework (opcjonalnie)</span>
      <select value={frameworkId} onChange={(event) => setFrameworkId(event.target.value)} className={selectClass} disabled={frameworksLoading || !!frameworksError}>
        <option value="">Bez wybranego frameworka</option>
        {frameworks?.filter((framework) => !format || !framework.format || framework.format === format).map((framework) => <option key={framework.id} value={framework.id}>{framework.name}{framework.format ? ` (${framework.format})` : ''}</option>)}
      </select>
    </label>
    {selectedFramework && <div className="space-y-2 text-sm text-muted-foreground">
      <p>{selectedFramework.description}</p>
      {selectedFramework.structure && <p>{selectedFramework.structure.map((step) => step.name).join(' → ')}</p>}
    </div>}
    {frameworksError && <p role="alert" className="text-sm text-destructive">Nie udało się pobrać frameworków.</p>}
    <label className="block space-y-2"><span className="text-sm font-medium">Wskazówki dla AI (opcjonalnie)</span><Textarea name="generation_instructions" rows={5} maxLength={4000} placeholder="Np. 15-sekundowe wideo: pokaż działanie usługi krok po kroku, bez lektora." /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={state.isLoading || isLoading || frameworksLoading || !!conceptsError}>{state.isLoading ? 'Generowanie…' : 'Generuj creative plans'}</Button>
  </form>
}

function PlanForm({ offerProfileId, item, onSaved }: { offerProfileId: number; item?: Entity; onSaved: () => void }) {
  const { data: concepts, isLoading, error: conceptsError } = useListAdConceptsQuery(offerProfileId)
  const [create, createState] = useCreateCreativePlanMutation()
  const [update, updateState] = useUpdateCreativePlanMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const fields: CreativePlanFields = {
      name: String(form.get('name') ?? '').trim(), description: String(form.get('description') ?? '').trim(),
      format: form.get('format') === 'video' ? 'video' : 'image', plan: String(form.get('plan') ?? '').trim(),
      ad_concept_id: Number(form.get('ad_concept_id')) || null,
    }
    if (!fields.name || !fields.description || !fields.plan) { setError('Uzupełnij nazwę, opis i plan.'); return }
    setError('')
    try {
      if (item) await update({ id: Number(item.id), offerProfileId, fields, isReviewed: Boolean(item.is_reviewed) }).unwrap()
      else await create({ offerProfileId, fields }).unwrap()
      onSaved()
    } catch { setError('Nie udało się zapisać planu.') }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-4">
    <label className="block space-y-2"><span>Nazwa</span><Input name="name" maxLength={255} defaultValue={String(item?.name ?? '')} required /></label>
    <label className="block space-y-2"><span>Opis</span><Textarea name="description" rows={3} defaultValue={String(item?.description ?? '')} required /></label>
    <ConceptSelect concepts={concepts} defaultValue={item?.ad_concept_id == null ? null : Number(item.ad_concept_id)} />
    {conceptsError && <p role="alert" className="text-sm text-destructive">Nie udało się pobrać koncepcji.</p>}
    <label className="block space-y-2"><span>Format</span><select name="format" defaultValue={String(item?.format ?? 'image')} className={selectClass} required><option value="image">Obraz</option><option value="video">Wideo</option></select></label>
    <label className="block space-y-2"><span>Pełny plan realizacji</span><Textarea name="plan" rows={20} defaultValue={String(item?.plan ?? '')} required /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={createState.isLoading || updateState.isLoading || isLoading || !!conceptsError}>Zapisz</Button>
  </form>
}
