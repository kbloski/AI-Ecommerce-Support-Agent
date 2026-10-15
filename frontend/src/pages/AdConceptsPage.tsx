import { useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { EntityList } from '@/components/EntityList'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import {
  useListAdConceptsQuery, useGenerateAdConceptsMutation, useCreateAdConceptMutation,
  useUpdateAdConceptMutation, useDeleteAdConceptMutation,
} from '@/features/adConcepts/adConceptsApi'
import type { AdConceptFields } from '@/features/adConcepts/adConceptsApi'
import type { Entity } from '@/types'
import { useListMarketingAnglesQuery } from '@/features/marketingAngles/marketingAnglesApi'

const conceptFields = (concept: Entity): AdConceptFields => ({
  name: String(concept.name ?? ''),
  description: String(concept.description ?? ''),
  format: concept.format === 'image' ? 'image' : 'video',
  core_idea: String(concept.core_idea ?? ''),
  key_message: String(concept.key_message ?? ''),
  marketing_angle_id: concept.marketing_angle_id == null ? null : Number(concept.marketing_angle_id),
})

export default function AdConceptsPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data, isLoading, error } = useListAdConceptsQuery(offerProfileId)
  const { data: marketingAngles } = useListMarketingAnglesQuery(offerProfileId)
  const [remove] = useDeleteAdConceptMutation()
  const [update] = useUpdateAdConceptMutation()
  const { openPanel, closePanel } = useSidePanel()
  const [actionError, setActionError] = useState('')

  return <div className="w-full p-6 lg:p-10"><EntityList
    title="Ad concepts"
    items={data}
    totalItems={data?.length}
    attentionItems={data?.filter((concept) => !concept.is_reviewed).length}
    isLoading={isLoading}
    error={error}
    itemDescription={(concept) => String(concept.description)}
    itemDetails={(concept) => <div className="space-y-1 text-sm text-muted-foreground">
      <p><strong>Format:</strong> {concept.format === 'image' ? 'Obraz' : 'Wideo'}</p>
      {concept.marketing_angle_id != null && <p><strong>Marketing angle:</strong> {String(marketingAngles?.find((angle) => Number(angle.id) === Number(concept.marketing_angle_id))?.name ?? `#${concept.marketing_angle_id}`)}</p>}
      <p><strong>Główny pomysł:</strong> {String(concept.core_idea ?? '')}</p>
      <p><strong>Kluczowy komunikat:</strong> {String(concept.key_message ?? '')}</p>
    </div>}
    contentBeforeList={actionError ? <p role="alert" className="text-sm text-destructive">{actionError}</p> : undefined}
    actions={<>
      <Button variant="outline" onClick={() => openPanel({ title: 'Dodaj ad concept', content: <ConceptForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Dodaj ręcznie</Button>
      <Button onClick={() => openPanel({ title: 'Generuj ad concepts', content: <GenerateConceptsForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Generuj</Button>
    </>}
    onEdit={(concept) => openPanel({ title: 'Edytuj ad concept', content: <ConceptForm offerProfileId={offerProfileId} concept={concept} onSaved={closePanel} /> })}
    onDelete={(concept) => { void remove({ id: Number(concept.id), offerProfileId }).unwrap().catch(() => setActionError('Nie udało się usunąć koncepcji.')) }}
    itemActions={(concept) => <Button size="sm" variant={concept.is_reviewed ? 'ghost' : 'default'} onClick={() => {
      void update({ id: Number(concept.id), offerProfileId, fields: conceptFields(concept), isReviewed: !concept.is_reviewed }).unwrap().catch(() => setActionError('Nie udało się zmienić stanu.'))
    }}>{concept.is_reviewed ? 'Oznacz jako niesprawdzone' : 'Zatwierdź'}</Button>}
  /></div>
}

function GenerateConceptsForm({ offerProfileId, onSaved }: { offerProfileId: number; onSaved: () => void }) {
  const { data: marketingAngles, isLoading: anglesLoading, error: anglesError } = useListMarketingAnglesQuery(offerProfileId)
  const [generate, state] = useGenerateAdConceptsMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const count = Number(form.get('count'))
    const marketingAngleId = form.get('marketing_angle_id') ? Number(form.get('marketing_angle_id')) : null
    const generationInstructions = String(form.get('generation_instructions') ?? '').trim()
    if (!Number.isInteger(count) || count < 1 || count > 10) { setError('Podaj liczbę od 1 do 10.'); return }
    setError('')
    try { await generate({ offerProfileId, count, marketingAngleId, generationInstructions }).unwrap(); onSaved() }
    catch { setError('Nie udało się wygenerować koncepcji. Sprawdź odpowiedź modelu i spróbuj ponownie.') }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Liczba ad concepts</span><Input name="count" type="number" min={1} max={10} step={1} defaultValue={3} required /></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Marketing angle (opcjonalnie)</span><select name="marketing_angle_id" defaultValue="" className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"><option value="">Bez marketing angle</option>{marketingAngles?.map((angle) => <option key={String(angle.id)} value={Number(angle.id)}>{String(angle.name)}</option>)}</select></label>
    {anglesError && <p role="alert" className="text-sm text-destructive">Nie udało się pobrać marketing angles.</p>}
    <label className="block space-y-2"><span className="text-sm font-medium">Wskazówki do generowania (opcjonalnie)</span><Textarea name="generation_instructions" maxLength={4000} rows={5} placeholder="Np. skup się na prostym pokazaniu produktu." /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={state.isLoading || anglesLoading || !!anglesError}>{state.isLoading ? 'Generowanie…' : 'Generuj ad concepts'}</Button>
  </form>
}

function ConceptForm({ offerProfileId, concept, onSaved }: { offerProfileId: number; concept?: Entity; onSaved: () => void }) {
  const { data: marketingAngles } = useListMarketingAnglesQuery(offerProfileId)
  const [create, createState] = useCreateAdConceptMutation()
  const [update, updateState] = useUpdateAdConceptMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const fields: AdConceptFields = {
      name: String(form.get('name') ?? '').trim(),
      description: String(form.get('description') ?? '').trim(),
      format: form.get('format') === 'image' ? 'image' : 'video',
      core_idea: String(form.get('core_idea') ?? '').trim(),
      key_message: String(form.get('key_message') ?? '').trim(),
      marketing_angle_id: form.get('marketing_angle_id') ? Number(form.get('marketing_angle_id')) : null,
    }
    if (!fields.name || !fields.description || !fields.core_idea || !fields.key_message) { setError('Wypełnij wszystkie pola.'); return }
    try {
      if (concept) await update({ id: Number(concept.id), offerProfileId, fields, isReviewed: Boolean(concept.is_reviewed) }).unwrap()
      else await create({ offerProfileId, fields }).unwrap()
      onSaved()
    } catch { setError('Nie udało się zapisać koncepcji.') }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-4">
    <label className="block space-y-2"><span>Nazwa</span><Input name="name" maxLength={255} defaultValue={String(concept?.name ?? '')} required /></label>
    <label className="block space-y-2"><span>Opis</span><Textarea name="description" defaultValue={String(concept?.description ?? '')} required /></label>
    <label className="block space-y-2"><span>Format</span><select name="format" defaultValue={String(concept?.format ?? 'video')} className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"><option value="video">Wideo</option><option value="image">Obraz</option></select></label>
    <label className="block space-y-2"><span>Marketing angle (opcjonalnie)</span><select name="marketing_angle_id" defaultValue={String(concept?.marketing_angle_id ?? '')} className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"><option value="">Bez marketing angle</option>{marketingAngles?.map((angle) => <option key={String(angle.id)} value={Number(angle.id)}>{String(angle.name)}</option>)}</select></label>
    <label className="block space-y-2"><span>Główny pomysł</span><Textarea name="core_idea" defaultValue={String(concept?.core_idea ?? '')} required /></label>
    <label className="block space-y-2"><span>Kluczowy komunikat</span><Textarea name="key_message" defaultValue={String(concept?.key_message ?? '')} required /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={createState.isLoading || updateState.isLoading}>Zapisz</Button>
  </form>
}
