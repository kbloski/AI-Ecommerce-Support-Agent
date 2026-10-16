import { useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { EntityList } from '@/components/EntityList'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import {
  useListAdCopiesQuery, useGenerateAdCopiesMutation, useCreateAdCopyMutation,
  useUpdateAdCopyMutation, useDeleteAdCopyMutation, useListAdCopyStructuresQuery, type AdCopyFields,
} from '@/features/adCopy/adCopyApi'
import type { Entity } from '@/types'

const copyFields = (item: Entity): AdCopyFields => ({
  name: String(item.name ?? ''),
  primary_text: String(item.primary_text ?? ''),
  headline: String(item.headline ?? ''),
  description: String(item.description ?? ''),
  cta: item.cta == null ? null : String(item.cta),
})

export default function AdCopyPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data, isLoading, error } = useListAdCopiesQuery(offerProfileId)
  const [remove] = useDeleteAdCopyMutation()
  const [update] = useUpdateAdCopyMutation()
  const { openPanel, closePanel } = useSidePanel()
  const [actionError, setActionError] = useState('')

  return <div className="w-full p-6 lg:p-10"><EntityList
    title="Ad copy" items={data} totalItems={data?.length}
    attentionItems={data?.filter((item) => !item.is_reviewed).length}
    isLoading={isLoading} error={error}
    emptyTitle="Brak ad copy" emptyDescription="Wygeneruj tekst reklamy lub dodaj go ręcznie."
    itemDetails={(item) => <div className="space-y-4 text-sm">
      <div><p className="mb-1 font-medium">Tekst główny</p><p className="whitespace-pre-wrap break-words">{String(item.primary_text ?? '')}</p></div>
      <div><p className="mb-1 font-medium">Nagłówek</p><p className="whitespace-pre-wrap break-words">{String(item.headline ?? '')}</p></div>
      <div><p className="mb-1 font-medium">Opis</p><p className="whitespace-pre-wrap break-words">{String(item.description ?? '')}</p></div>
      {Boolean(item.cta) && <div><p className="mb-1 font-medium">CTA</p><p className="whitespace-pre-wrap break-words">{String(item.cta)}</p></div>}
    </div>}
    contentBeforeList={actionError ? <p role="alert" className="text-sm text-destructive">{actionError}</p> : undefined}
    actions={<>
      <Button variant="outline" onClick={() => openPanel({ title: 'Dodaj ad copy', content: <CopyForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Dodaj ręcznie</Button>
      <Button onClick={() => openPanel({ title: 'Generuj ad copy', content: <GenerateCopyForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Generuj</Button>
    </>}
    onEdit={(item) => openPanel({ title: 'Edytuj ad copy', content: <CopyForm offerProfileId={offerProfileId} item={item} onSaved={closePanel} /> })}
    onDelete={(item) => { void remove({ id: Number(item.id), offerProfileId }).unwrap().catch(() => setActionError('Nie udało się usunąć tekstu reklamy.')) }}
    itemActions={(item) => <Button size="sm" variant={item.is_reviewed ? 'ghost' : 'default'} onClick={() => {
      void update({ id: Number(item.id), offerProfileId, fields: copyFields(item), isReviewed: !item.is_reviewed }).unwrap().catch(() => setActionError('Nie udało się zmienić stanu ad copy.'))
    }}>{item.is_reviewed ? 'Oznacz jako niesprawdzone' : 'Zatwierdź'}</Button>}
  /></div>
}

function GenerateCopyForm({ offerProfileId, onSaved }: { offerProfileId: number; onSaved: () => void }) {
  const [generate, { isLoading }] = useGenerateAdCopiesMutation()
  const { data: structures, isLoading: structuresLoading, error: structuresError } = useListAdCopyStructuresQuery()
  const [structureId, setStructureId] = useState('')
  const selectedStructure = structures?.find((structure) => structure.id === structureId)
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const count = Number(form.get('count'))
    if (!Number.isInteger(count) || count < 1 || count > 10) { setError('Podaj liczbę od 1 do 10.'); return }
    setError('')
    try {
      await generate({ offerProfileId, count, structureId: structureId || null, generationInstructions: String(form.get('generation_instructions') ?? '').trim() }).unwrap()
      onSaved()
    } catch { setError('Nie udało się wygenerować ad copy. Spróbuj ponownie.') }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Liczba ad copy</span><Input name="count" type="number" min={1} max={10} step={1} defaultValue={3} required /></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Struktura ad copy</span>
      <select className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm" value={structureId} onChange={(event) => setStructureId(event.target.value)} disabled={structuresLoading || !!structuresError}>
        <option value="">Brak — według wskazówek dla AI</option>
        {structures?.map((structure) => <option key={structure.id} value={structure.id}>{structure.name}</option>)}
      </select>
    </label>
    {selectedStructure && <p className="text-sm text-muted-foreground">{selectedStructure.description} {selectedStructure.structure.map((step) => step.name).join(' → ')}</p>}
    {!structureId && <p className="text-sm text-muted-foreground">AI dobierze strukturę ze wskazówek, a jeśli ich nie podasz — z danych oferty.</p>}
    {structuresError && <p role="alert" className="text-sm text-destructive">Nie udało się pobrać struktur ad copy.</p>}
    <label className="block space-y-2"><span className="text-sm font-medium">Wskazówki dla AI (opcjonalnie)</span><Textarea name="generation_instructions" rows={5} maxLength={4000} placeholder="Np. krótki tekst skupiony na wygodzie, bez CTA." /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={isLoading || (!!structureId && (structuresLoading || !!structuresError || !selectedStructure))}>{isLoading ? 'Generowanie…' : 'Generuj ad copy'}</Button>
  </form>
}

function CopyForm({ offerProfileId, item, onSaved }: { offerProfileId: number; item?: Entity; onSaved: () => void }) {
  const [create, createState] = useCreateAdCopyMutation()
  const [update, updateState] = useUpdateAdCopyMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const fields: AdCopyFields = {
      name: String(form.get('name') ?? '').trim(), primary_text: String(form.get('primary_text') ?? '').trim(),
      headline: String(form.get('headline') ?? '').trim(), description: String(form.get('description') ?? '').trim(),
      cta: String(form.get('cta') ?? '').trim() || null,
    }
    if (!fields.name || !fields.primary_text || !fields.headline || !fields.description) { setError('Uzupełnij nazwę, tekst główny, nagłówek i opis.'); return }
    setError('')
    try {
      if (item) await update({ id: Number(item.id), offerProfileId, fields, isReviewed: Boolean(item.is_reviewed) }).unwrap()
      else await create({ offerProfileId, fields }).unwrap()
      onSaved()
    } catch { setError('Nie udało się zapisać ad copy.') }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-4">
    <label className="block space-y-2"><span>Nazwa</span><Input name="name" maxLength={255} defaultValue={String(item?.name ?? '')} required /></label>
    <label className="block space-y-2"><span>Tekst główny</span><Textarea name="primary_text" rows={8} defaultValue={String(item?.primary_text ?? '')} required /></label>
    <label className="block space-y-2"><span>Nagłówek</span><Textarea name="headline" rows={2} defaultValue={String(item?.headline ?? '')} required /></label>
    <label className="block space-y-2"><span>Opis</span><Textarea name="description" rows={3} defaultValue={String(item?.description ?? '')} required /></label>
    <label className="block space-y-2"><span>CTA (opcjonalnie)</span><Input name="cta" defaultValue={String(item?.cta ?? '')} /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={createState.isLoading || updateState.isLoading}>Zapisz</Button>
  </form>
}
