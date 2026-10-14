import { useState, type FormEvent } from 'react'
import { EntityList } from '@/components/EntityList'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import type { Entity } from '@/types'
import { useListAdditionalContextsQuery, useListProfileContextsQuery, useCreateAdditionalContextMutation, useUpdateAdditionalContextMutation, useAttachAdditionalContextMutation, useDetachAdditionalContextMutation } from './additionalContextsApi'

export function ProfileAdditionalContexts({ offerProfileId }: { offerProfileId: number }) {
  const { data, isLoading, error } = useListProfileContextsQuery(offerProfileId)
  const [detach, state] = useDetachAdditionalContextMutation()
  const [actionError, setActionError] = useState('')
  const { openPanel, closePanel } = useSidePanel()
  const unlink = async (contextId: number) => {
    if (!window.confirm('Odłączyć kontekst od tego profilu?')) return
    setActionError('')
    try { await detach({ offerProfileId, contextId }).unwrap() }
    catch { setActionError('Nie udało się odłączyć kontekstu.') }
  }
  return <EntityList title="Dodatkowe informacje" items={data} totalItems={data?.length} isLoading={isLoading} error={error}
    emptyTitle="Brak dodatkowych informacji" emptyDescription="Dodaj nowy kontekst lub dołącz istniejący."
    itemDescription={(context) => <p className="whitespace-pre-wrap">{String(context.content)}</p>}
    onEdit={(context) => openPanel({ title: 'Edytuj kontekst', content: <ContextForm offerProfileId={offerProfileId} context={context} onSaved={closePanel} /> })}
    itemActions={(context) => <Button variant="ghost" size="sm" disabled={state.isLoading} onClick={() => unlink(context.id as number)}>Odłącz</Button>}
    contentBeforeList={actionError ? <p role="alert" className="text-sm text-destructive">{actionError}</p> : undefined}
    actions={<><Button variant="outline" onClick={() => openPanel({ title: 'Dołącz istniejący kontekst', content: <AttachContextForm offerProfileId={offerProfileId} attached={data ?? []} onSaved={closePanel} /> })}>Dołącz istniejący</Button><Button onClick={() => openPanel({ title: 'Dodaj kontekst', content: <ContextForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}>Dodaj kontekst</Button></>}
  />
}

function ContextForm({ offerProfileId, context, onSaved }: { offerProfileId: number; context?: Entity; onSaved: () => void }) {
  const [create, createState] = useCreateAdditionalContextMutation()
  const [update, updateState] = useUpdateAdditionalContextMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError('')
    const data = new FormData(event.currentTarget)
    const fields = { name: String(data.get('name') ?? '').trim(), content: String(data.get('content') ?? '').trim() }
    if (!fields.name || !fields.content) { setError('Podaj nazwę i treść kontekstu.'); return }
    try {
      if (context) await update({ id: context.id as number, ...fields }).unwrap()
      else await create({ offerProfileId, ...fields }).unwrap()
      onSaved()
    } catch { setError('Nie udało się zapisać kontekstu.') }
  }
  return <form className="space-y-4" onSubmit={submit}>
    <label className="block space-y-2"><span>Nazwa</span><Input name="name" required maxLength={255} autoFocus defaultValue={String(context?.name ?? '')} /></label>
    <label className="block space-y-2"><span>Treść</span><Textarea name="content" required rows={12} defaultValue={String(context?.content ?? '')} /></label>
    {context && <p className="text-sm text-muted-foreground">Zmiany będą widoczne we wszystkich profilach korzystających z tego kontekstu.</p>}
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={createState.isLoading || updateState.isLoading}>Zapisz kontekst</Button>
  </form>
}

function AttachContextForm({ offerProfileId, attached, onSaved }: { offerProfileId: number; attached: Entity[]; onSaved: () => void }) {
  const { data, isLoading, error: loadError } = useListAdditionalContextsQuery()
  const [attach, state] = useAttachAdditionalContextMutation()
  const [error, setError] = useState('')
  const available = (data ?? []).filter((context) => !attached.some((item) => item.id === context.id))
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError('')
    const id = Number(new FormData(event.currentTarget).get('contextId'))
    if (!id) return
    try { await attach({ offerProfileId, contextId: id }).unwrap(); onSaved() }
    catch { setError('Nie udało się dołączyć kontekstu.') }
  }
  return <form onSubmit={submit} className="space-y-4">
    {isLoading ? <p>Wczytywanie...</p> : loadError ? <p role="alert">Nie udało się pobrać kontekstów.</p> : !available.length ? <p>Brak dostępnych kontekstów do dołączenia.</p> : <label className="block space-y-2"><span>Kontekst</span><select name="contextId" required className="w-full rounded-md border p-2" defaultValue=""><option value="" disabled>Wybierz kontekst</option>{available.map((context) => <option key={context.id} value={context.id}>{String(context.name)}</option>)}</select></label>}
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={state.isLoading || isLoading || !!loadError || !available.length}>Dołącz kontekst</Button>
  </form>
}
