import { useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { EntityList } from '@/components/EntityList'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import { useListTargetAudiencesForOfferProfileQuery } from '@/features/targetAudiences/targetAudiencesApi'
import {
  useListMarketingAnglesQuery, useGenerateMarketingAnglesMutation, useCreateMarketingAngleMutation,
  useUpdateMarketingAngleMutation, useDeleteMarketingAngleMutation,
} from '@/features/marketingAngles/marketingAnglesApi'
import type { Entity } from '@/types'
import type { MarketingAngleFields } from '@/features/marketingAngles/marketingAnglesApi'

const stringList = (value: unknown): string[] => Array.isArray(value) ? value.map(String) : []
const lines = (value: string): string[] => value.split('\n').map((part) => part.trim()).filter(Boolean)
const angleFields = (angle: Entity): MarketingAngleFields => ({
  name: String(angle.name ?? ''),
  description: String(angle.description ?? ''),
  core_message: String(angle.core_message ?? ''),
  value_proposition: String(angle.value_proposition ?? ''),
  pain_point: String(angle.pain_point ?? ''),
  desire: String(angle.desire ?? ''),
  emotional_driver: String(angle.emotional_driver ?? ''),
  supporting_arguments: stringList(angle.supporting_arguments),
  proof_points: stringList(angle.proof_points),
})

export default function MarketingAnglesPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data, isLoading, error } = useListMarketingAnglesQuery(offerProfileId)
  const [remove] = useDeleteMarketingAngleMutation()
  const [update] = useUpdateMarketingAngleMutation()
  const { openPanel, closePanel } = useSidePanel()
  const [actionError, setActionError] = useState('')

  return <div className="w-full p-6 lg:p-10"><EntityList
    title="Marketing angle"
    items={data}
    totalItems={data?.length}
    attentionItems={data?.filter((angle) => !angle.is_reviewed).length}
    isLoading={isLoading}
    error={error}
    itemDescription={(angle) => String(angle.description)}
    itemDetails={(angle) => <div className="space-y-1 text-sm text-muted-foreground">
      <p><strong>Główny przekaz:</strong> {String(angle.core_message ?? '')}</p>
      <p><strong>Propozycja wartości:</strong> {String(angle.value_proposition ?? '')}</p>
      <p><strong>Problem:</strong> {String(angle.pain_point ?? '')}</p>
      <p><strong>Pragnienie:</strong> {String(angle.desire ?? '')}</p>
      <p><strong>Motywacja emocjonalna:</strong> {String(angle.emotional_driver ?? '')}</p>
      {stringList(angle.supporting_arguments).length > 0 && <p><strong>Argumenty:</strong> {stringList(angle.supporting_arguments).join(' · ')}</p>}
      {stringList(angle.proof_points).length > 0 && <p><strong>Dowody:</strong> {stringList(angle.proof_points).join(' · ')}</p>}
    </div>}
    contentBeforeList={actionError ? <p role="alert" className="text-sm text-destructive">{actionError}</p> : undefined}
    actions={<>
      <Button variant="outline" onClick={() => openPanel({ title: 'Dodaj marketing angle', content: <AngleForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Dodaj ręcznie</Button>
      <Button onClick={() => openPanel({ title: 'Generuj marketing angles', content: <GenerateAnglesForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Generuj</Button>
    </>}
    onEdit={(angle) => openPanel({ title: 'Edytuj marketing angle', content: <AngleForm offerProfileId={offerProfileId} angle={angle} onSaved={closePanel} /> })}
    onDelete={(angle) => { void remove({ id: Number(angle.id), offerProfileId }).unwrap().catch(() => setActionError('Nie udało się usunąć kierunku.')) }}
    itemActions={(angle) => <Button size="sm" variant={angle.is_reviewed ? 'ghost' : 'default'} onClick={() => {
      void update({ id: Number(angle.id), offerProfileId, fields: angleFields(angle), isReviewed: !angle.is_reviewed }).unwrap().catch(() => setActionError('Nie udało się zmienić stanu.'))
    }}>{angle.is_reviewed ? 'Oznacz jako niesprawdzone' : 'Zatwierdź'}</Button>}
  /></div>
}

function GenerateAnglesForm({ offerProfileId, onSaved }: { offerProfileId: number; onSaved: () => void }) {
  const { data: audiences, isLoading: audiencesLoading, error: audiencesError } = useListTargetAudiencesForOfferProfileQuery({ offerProfileId, pageSize: 100 })
  const [generate, state] = useGenerateMarketingAnglesMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const count = Number(form.get('count'))
    const targetAudienceIds = form.getAll('target_audience_ids').map(Number)
    const generationInstructions = String(form.get('generation_instructions') ?? '').trim()
    if (!Number.isInteger(count) || count < 1 || count > 10) { setError('Podaj liczbę od 1 do 10.'); return }
    setError('')
    try { await generate({ offerProfileId, count, targetAudienceIds, generationInstructions }).unwrap(); onSaved() }
    catch { setError('Nie udało się wygenerować kierunków. Sprawdź odpowiedź modelu i spróbuj ponownie.') }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Liczba marketing angles</span><Input name="count" type="number" min={1} max={10} step={1} defaultValue={3} required /></label>
    <fieldset className="space-y-2"><legend className="text-sm font-medium">Grupy docelowe do uwzględnienia</legend>
      {audiencesLoading && <p className="text-sm text-muted-foreground">Ładowanie grup…</p>}
      {audiencesError && <p role="alert" className="text-sm text-destructive">Nie udało się pobrać grup docelowych.</p>}
      {audiences?.items.length === 0 && <p className="text-sm text-muted-foreground">Brak grup docelowych. Generowanie oprze się na profilu.</p>}
      {audiences?.items.map((audience) => <label key={String(audience.id)} className="flex items-center gap-2 text-sm"><input name="target_audience_ids" type="checkbox" value={Number(audience.id)} className="size-4" /><span>{String(audience.name)}</span></label>)}
      {(audiences?.total_items ?? 0) > 100 && <p className="text-xs text-muted-foreground">Wyświetlono pierwsze 100 grup.</p>}
    </fieldset>
    <label className="block space-y-2"><span className="text-sm font-medium">Wskazówki do generowania (opcjonalnie)</span><Textarea name="generation_instructions" maxLength={4000} rows={5} placeholder="Np. skup się na wygodzie i oszczędności czasu." /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={state.isLoading || audiencesLoading || !!audiencesError}>{state.isLoading ? 'Generowanie…' : 'Generuj marketing angles'}</Button>
  </form>
}

function AngleForm({ offerProfileId, angle, onSaved }: { offerProfileId: number; angle?: Entity; onSaved: () => void }) {
  const [create, createState] = useCreateMarketingAngleMutation()
  const [update, updateState] = useUpdateMarketingAngleMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const fields: MarketingAngleFields = {
      name: String(form.get('name') ?? '').trim(),
      description: String(form.get('description') ?? '').trim(),
      core_message: String(form.get('core_message') ?? '').trim(),
      value_proposition: String(form.get('value_proposition') ?? '').trim(),
      pain_point: String(form.get('pain_point') ?? '').trim(),
      desire: String(form.get('desire') ?? '').trim(),
      emotional_driver: String(form.get('emotional_driver') ?? '').trim(),
      supporting_arguments: lines(String(form.get('supporting_arguments') ?? '')),
      proof_points: lines(String(form.get('proof_points') ?? '')),
    }
    if (!fields.name || !fields.description) { setError('Podaj nazwę i opis.'); return }
    try {
      if (angle) await update({ id: Number(angle.id), offerProfileId, fields, isReviewed: Boolean(angle.is_reviewed) }).unwrap()
      else await create({ offerProfileId, fields }).unwrap()
      onSaved()
    } catch { setError('Nie udało się zapisać kierunku.') }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-4">
    <label className="block space-y-2"><span>Nazwa</span><Input name="name" maxLength={255} defaultValue={String(angle?.name ?? '')} required /></label>
    <label className="block space-y-2"><span>Opis</span><Textarea name="description" defaultValue={String(angle?.description ?? '')} required /></label>
    <label className="block space-y-2"><span>Główny przekaz</span><Textarea name="core_message" defaultValue={String(angle?.core_message ?? '')} /></label>
    <label className="block space-y-2"><span>Propozycja wartości</span><Textarea name="value_proposition" defaultValue={String(angle?.value_proposition ?? '')} /></label>
    <label className="block space-y-2"><span>Problem odbiorcy</span><Textarea name="pain_point" defaultValue={String(angle?.pain_point ?? '')} /></label>
    <label className="block space-y-2"><span>Pragnienie odbiorcy</span><Textarea name="desire" defaultValue={String(angle?.desire ?? '')} /></label>
    <label className="block space-y-2"><span>Motywacja emocjonalna</span><Textarea name="emotional_driver" defaultValue={String(angle?.emotional_driver ?? '')} /></label>
    <label className="block space-y-2"><span>Argumenty wspierające (jeden w wierszu)</span><Textarea name="supporting_arguments" rows={4} defaultValue={stringList(angle?.supporting_arguments).join('\n')} /></label>
    <label className="block space-y-2"><span>Punkty dowodowe (jeden w wierszu)</span><Textarea name="proof_points" rows={4} defaultValue={stringList(angle?.proof_points).join('\n')} /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={createState.isLoading || updateState.isLoading}>Zapisz</Button>
  </form>
}
