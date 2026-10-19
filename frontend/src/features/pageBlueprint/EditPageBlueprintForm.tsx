import { useId, useState, type FormEvent } from 'react'
import { ArrowDown, ArrowUp, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useListPageSectionsQuery } from '@/features/pageSections/pageSectionsApi'
import { useCreatePageBlueprintMutation, useUpdatePageBlueprintMutation } from './pageBlueprintApi'
import type { PageBlueprintSection } from './pageBlueprintFields'
import type { Entity } from '@/types'

type SectionDraft = PageBlueprintSection & { key: string }

export function EditPageBlueprintForm({ pageBlueprint, offerProfileId, onSaved }: {
  pageBlueprint?: Entity
  offerProfileId?: number
  onSaved: () => void
}) {
  const catalogId = useId()
  const { data: catalog = [] } = useListPageSectionsQuery()
  const [name, setName] = useState(String(pageBlueprint?.name ?? ''))
  const [description, setDescription] = useState(String(pageBlueprint?.description ?? ''))
  const [sections, setSections] = useState<SectionDraft[]>(() =>
    ((pageBlueprint?.sections as PageBlueprintSection[] | undefined) ?? [])
      .slice().sort((a, b) => a.position - b.position)
      .map((section) => ({ ...section, key: crypto.randomUUID() })),
  )
  const [create, createState] = useCreatePageBlueprintMutation()
  const [update, updateState] = useUpdatePageBlueprintMutation()
  const [error, setError] = useState('')
  const isSaving = createState.isLoading || updateState.isLoading

  const changeSection = (key: string, patch: Partial<PageBlueprintSection>) =>
    setSections((previous) => previous.map((section) => section.key === key ? { ...section, ...patch } : section))

  const moveSection = (index: number, offset: number) => setSections((previous) => {
    const next = [...previous]
    const destination = index + offset
    if (destination < 0 || destination >= next.length) return previous
    ;[next[index], next[destination]] = [next[destination], next[index]]
    return next
  })

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!name.trim() || sections.length === 0 || sections.some((section) => !section.type.trim() || !section.name.trim() || !section.purpose.trim())) {
      setError('Podaj nazwę blueprintu i uzupełnij co najmniej jedną sekcję.')
      return
    }
    const fields = {
      name: name.trim(), description: description.trim(),
      sections: sections.map((section, index) => ({
        ...(section.id == null ? {} : { id: section.id }),
        type: section.type.trim(), name: section.name.trim(), purpose: section.purpose.trim(),
        position: index + 1, is_optional: section.is_optional,
      })),
    }
    setError('')
    try {
      if (pageBlueprint) {
        await update({ id: Number(pageBlueprint.id), offerProfileId: Number(pageBlueprint.offer_profile_id), fields }).unwrap()
      } else if (offerProfileId != null) {
        await create({ offerProfileId, fields }).unwrap()
      } else {
        setError('Brak profilu oferty.')
        return
      }
      onSaved()
    } catch {
      setError('Nie udało się zapisać blueprintu. Spróbuj ponownie.')
    }
  }

  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Nazwa blueprintu</span>
      <Input value={name} onChange={(event) => setName(event.target.value)} maxLength={255} required />
    </label>
    <label className="block space-y-2"><span className="text-sm font-medium">Opis</span>
      <Textarea value={description} onChange={(event) => setDescription(event.target.value)} maxLength={4000} rows={3} />
    </label>
    <div className="space-y-3">
      <h3 className="font-medium">Sekcje ({sections.length})</h3>
      <p className="text-sm text-muted-foreground">Wybierz sugerowany typ lub wpisz własny. Ten sam typ możesz dodać wielokrotnie.</p>
      <datalist id={catalogId}>{catalog.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}</datalist>
      {sections.map((section, index) => <fieldset key={section.key} className="min-w-0 space-y-3 rounded-md border p-3">
        <legend className="px-1 text-sm font-medium">Sekcja {index + 1}</legend>
        <div className="flex justify-end gap-1">
          <Button type="button" variant="ghost" size="sm" aria-label={`Przesuń sekcję ${index + 1} w górę`} disabled={index === 0 || isSaving} onClick={() => moveSection(index, -1)}><ArrowUp /></Button>
          <Button type="button" variant="ghost" size="sm" aria-label={`Przesuń sekcję ${index + 1} w dół`} disabled={index === sections.length - 1 || isSaving} onClick={() => moveSection(index, 1)}><ArrowDown /></Button>
          <Button type="button" variant="ghost" size="sm" aria-label={`Usuń sekcję ${index + 1}`} disabled={isSaving} onClick={() => setSections((previous) => previous.filter((item) => item.key !== section.key))}><Trash2 /></Button>
        </div>
        <label className="block space-y-2"><span className="text-sm">Typ</span>
          <Input list={catalogId} value={section.type} maxLength={100} required placeholder="Np. hero lub własny typ" onChange={(event) => {
            const reference = catalog.find((item) => item.id === event.target.value)
            changeSection(section.key, { type: event.target.value,
              ...(!section.name && reference ? { name: reference.name } : {}),
              ...(!section.purpose && reference ? { purpose: reference.description } : {}),
            })
          }} />
        </label>
        <label className="block space-y-2"><span className="text-sm">Nazwa sekcji</span>
          <Input value={section.name} onChange={(event) => changeSection(section.key, { name: event.target.value })} maxLength={255} required />
        </label>
        <label className="block space-y-2"><span className="text-sm">Cel sekcji</span>
          <Textarea value={section.purpose} onChange={(event) => changeSection(section.key, { purpose: event.target.value })} maxLength={4000} rows={3} required />
        </label>
        <label className="flex items-center gap-2 text-sm"><input type="checkbox" checked={section.is_optional} onChange={(event) => changeSection(section.key, { is_optional: event.target.checked })} />Sekcja opcjonalna</label>
      </fieldset>)}
      <Button type="button" variant="outline" className="w-full" disabled={sections.length >= 50 || isSaving} onClick={() => setSections((previous) => [
        ...previous, { key: crypto.randomUUID(), type: '', name: '', purpose: '', position: previous.length + 1, is_optional: false },
      ])}><Plus />Dodaj sekcję</Button>
    </div>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={isSaving}>{isSaving ? 'Zapisywanie…' : 'Zapisz blueprint'}</Button>
  </form>
}
