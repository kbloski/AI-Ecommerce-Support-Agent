import { useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { EntityList } from '@/components/EntityList'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import {
  useListBrandStylesQuery, useGenerateBrandStyleMutation, useCreateBrandStyleMutation,
  useUpdateBrandStyleMutation, useDeleteBrandStyleMutation,
  type BrandStyleFields,
} from '@/features/brandStyles/brandStylesApi'
import type { Entity } from '@/types'

const HEX_COLOR = /^#[0-9A-Fa-f]{6}$/

export default function BrandStylesPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const { data, isLoading, error } = useListBrandStylesQuery(offerProfileId)
  const [remove] = useDeleteBrandStyleMutation()
  const { openPanel, closePanel } = useSidePanel()
  const [actionError, setActionError] = useState('')

  return <div className="w-full p-6 lg:p-10"><EntityList
    title="Brand styles" items={data} totalItems={data?.length}
    isLoading={isLoading} error={error}
    emptyTitle="Brak brand styles" emptyDescription="Wygeneruj styl marki lub dodaj font i kolory ręcznie."
    itemLabel={(item) => String(item.font_family ?? `#${item.id}`)}
    itemDetails={(item) => <div className="space-y-2 text-sm">
      <ColorRow label="Kolor marki" value={String(item.brand_color)} />
      <ColorRow label="Kolor tekstu" value={String(item.text_color)} />
      <ColorRow label="Kolor tła" value={String(item.background_color)} />
    </div>}
    contentBeforeList={actionError ? <p role="alert" className="text-sm text-destructive">{actionError}</p> : undefined}
    actions={<>
      <Button variant="outline" onClick={() => openPanel({ title: 'Dodaj brand style', content: <BrandStyleForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Dodaj ręcznie</Button>
      <Button onClick={() => openPanel({ title: 'Generuj brand style', content: <GenerateBrandStyleForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Generuj</Button>
    </>}
    onEdit={(item) => openPanel({ title: 'Edytuj brand style', content: <BrandStyleForm offerProfileId={offerProfileId} item={item} onSaved={closePanel} /> })}
    onDelete={(item) => { void remove({ id: Number(item.id), offerProfileId }).unwrap().catch(() => setActionError('Nie udało się usunąć brand style.')) }}
  /></div>
}

function GenerateBrandStyleForm({ offerProfileId, onSaved }: { offerProfileId: number; onSaved: () => void }) {
  const [generate, state] = useGenerateBrandStyleMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setError('')
    try {
      await generate({ offerProfileId, generationInstructions: String(form.get('generation_instructions') ?? '').trim() }).unwrap()
      onSaved()
    } catch { setError('Nie udało się wygenerować brand style. Spróbuj ponownie.') }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Wskazówki dla AI (opcjonalnie)</span><Textarea name="generation_instructions" rows={5} maxLength={4000} placeholder="Np. minimalistyczny, premium, ciemne tło i złoty akcent." /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={state.isLoading}>{state.isLoading ? 'Generowanie…' : 'Generuj brand style'}</Button>
  </form>
}

function ColorRow({ label, value }: { label: string; value: string }) {
  return <p className="flex items-center gap-2">
    <span className="inline-block size-4 rounded border" style={{ backgroundColor: value }} />
    <strong>{label}:</strong> {value}
  </p>
}

function ColorField({ name, label, defaultValue }: { name: keyof BrandStyleFields; label: string; defaultValue: string }) {
  const [value, setValue] = useState(defaultValue)
  return <label className="block space-y-2"><span>{label}</span>
    <div className="flex gap-2">
      <input type="color" aria-label={`${label} — wybór`} value={HEX_COLOR.test(value) ? value : '#000000'} onChange={(event) => setValue(event.target.value.toUpperCase())} className="h-10 w-14 cursor-pointer rounded-md border" />
      <Input name={name} value={value} onChange={(event) => setValue(event.target.value)} pattern="#[0-9A-Fa-f]{6}" placeholder="#RRGGBB" required />
    </div>
  </label>
}

function BrandStyleForm({ offerProfileId, item, onSaved }: { offerProfileId: number; item?: Entity; onSaved: () => void }) {
  const [create, createState] = useCreateBrandStyleMutation()
  const [update, updateState] = useUpdateBrandStyleMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const fields: BrandStyleFields = {
      font_family: String(form.get('font_family') ?? '').trim(),
      brand_color: String(form.get('brand_color') ?? '').trim(),
      text_color: String(form.get('text_color') ?? '').trim(),
      background_color: String(form.get('background_color') ?? '').trim(),
    }
    if (!fields.font_family) { setError('Podaj font.'); return }
    if (!HEX_COLOR.test(fields.brand_color) || !HEX_COLOR.test(fields.text_color) || !HEX_COLOR.test(fields.background_color)) { setError('Kolory podaj w formacie #RRGGBB.'); return }
    setError('')
    try {
      if (item) await update({ id: Number(item.id), offerProfileId, fields }).unwrap()
      else await create({ offerProfileId, fields }).unwrap()
      onSaved()
    } catch { setError('Nie udało się zapisać brand style.') }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-4">
    <label className="block space-y-2"><span>Font family</span><Input name="font_family" maxLength={255} defaultValue={String(item?.font_family ?? '')} placeholder="Np. Inter, sans-serif" required /></label>
    <ColorField name="brand_color" label="Kolor marki" defaultValue={String(item?.brand_color ?? '#000000')} />
    <ColorField name="text_color" label="Kolor tekstu" defaultValue={String(item?.text_color ?? '#000000')} />
    <ColorField name="background_color" label="Kolor tła" defaultValue={String(item?.background_color ?? '#FFFFFF')} />
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={createState.isLoading || updateState.isLoading}>Zapisz</Button>
  </form>
}
