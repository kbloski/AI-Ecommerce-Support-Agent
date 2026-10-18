import { useState, type FormEvent } from 'react'
import { EntityList } from '@/components/EntityList'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  useAttachNoteMutation, useCreateNoteMutation, useCreateProfileNoteMutation, useDeleteNoteMutation,
  useDetachNoteMutation, useListNotesQuery, useListProfileNotesQuery, useUpdateNoteMutation,
  type Note,
} from './notesApi'

type NoteDialog = { mode: 'create' } | { mode: 'attach' } | { mode: 'edit'; note: Note }

export function ProfileNotes({ offerProfileId }: { offerProfileId?: number }) {
  const profileQuery = useListProfileNotesQuery(offerProfileId ?? 0, { skip: offerProfileId === undefined })
  const allQuery = useListNotesQuery(undefined, { skip: offerProfileId !== undefined })
  const { data: notes, isLoading, error } = offerProfileId === undefined ? allQuery : profileQuery
  const [dialog, setDialog] = useState<NoteDialog | null>(null)
  const { data: allNotes, isLoading: allNotesLoading, error: allNotesError } = useListNotesQuery(undefined, { skip: dialog?.mode !== 'attach' })
  const [create, createState] = useCreateNoteMutation()
  const [createProfile, createProfileState] = useCreateProfileNoteMutation()
  const [update, updateState] = useUpdateNoteMutation()
  const [attach, attachState] = useAttachNoteMutation()
  const [detach, detachState] = useDetachNoteMutation()
  const [remove, removeState] = useDeleteNoteMutation()
  const [actionError, setActionError] = useState('')
  const [dialogError, setDialogError] = useState('')
  const available = (allNotes ?? []).filter((note) => !notes?.some((attached) => attached.id === note.id))

  const openDialog = (next: NoteDialog) => { setDialogError(''); setDialog(next) }
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!dialog) return
    setDialogError('')
    const form = new FormData(event.currentTarget)
    try {
      if (dialog.mode === 'attach') {
        const noteId = Number(form.get('noteId'))
        if (!noteId || offerProfileId === undefined) { setDialogError('Wybierz notatkę.'); return }
        await attach({ offerProfileId, noteId }).unwrap()
      } else {
        const title = String(form.get('title') ?? '').trim()
        const content = String(form.get('content') ?? '').trim()
        if (!title || !content) { setDialogError('Podaj tytuł i treść notatki.'); return }
        if (dialog.mode === 'edit') await update({ id: dialog.note.id, title, content }).unwrap()
        else if (offerProfileId === undefined) await create({ title, content }).unwrap()
        else await createProfile({ offerProfileId, title, content }).unwrap()
      }
      setDialog(null)
    } catch { setDialogError('Nie udało się zapisać notatki.') }
  }

  const unlink = async (note: Note) => {
    if (offerProfileId === undefined) return
    if (!window.confirm(`Odpiąć notatkę „${note.title}” od tego profilu?`)) return
    setActionError('')
    try { await detach({ offerProfileId, noteId: note.id }).unwrap() }
    catch { setActionError('Nie udało się odpiąć notatki.') }
  }

  const deleteEverywhere = async (note: Note) => {
    if (!window.confirm(offerProfileId === undefined
      ? `Usunąć notatkę „${note.title}”? Zniknie też ze wszystkich profili, do których jest przypięta.`
      : `Usunąć notatkę „${note.title}” ze wszystkich profili?`)) return
    setActionError('')
    try { await remove(note.id).unwrap() }
    catch { setActionError('Nie udało się usunąć notatki.') }
  }

  return <>
    <EntityList
      title="Notatki"
      items={notes}
      isLoading={isLoading}
      error={error}
      totalItems={notes?.length}
      itemLabel={(item) => String(item.title)}
      itemDescription={(item) => String(item.content)}
      onEdit={(item) => openDialog({ mode: 'edit', note: item as Note })}
      itemActions={(item) => <>
        {offerProfileId !== undefined && <Button variant="ghost" size="sm" disabled={detachState.isLoading} onClick={() => void unlink(item as Note)}>Odepnij</Button>}
        <Button variant="ghost" size="sm" disabled={removeState.isLoading} onClick={() => void deleteEverywhere(item as Note)}>{offerProfileId === undefined ? 'Usuń' : 'Usuń wszędzie'}</Button>
      </>}
      emptyTitle="Brak notatek"
      emptyDescription={offerProfileId === undefined ? 'Dodaj pierwszą notatkę.' : 'Dodaj notatkę lub przypnij istniejącą.'}
      contentBeforeList={actionError ? <p role="alert" className="text-sm text-destructive">{actionError}</p> : undefined}
      actions={<>
        {offerProfileId !== undefined && <Button variant="outline" onClick={() => openDialog({ mode: 'attach' })}>Przypnij istniejącą</Button>}
        <Button onClick={() => openDialog({ mode: 'create' })}>Dodaj notatkę</Button>
      </>}
    />
    <Dialog open={dialog !== null} onOpenChange={(open) => { if (!open) setDialog(null) }}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{dialog?.mode === 'edit' ? 'Edytuj notatkę' : dialog?.mode === 'attach' ? 'Przypnij notatkę' : 'Dodaj notatkę'}</DialogTitle>
        </DialogHeader>
        {dialog && <form key={dialog.mode === 'edit' ? `edit-${dialog.note.id}` : dialog.mode} className="space-y-4" onSubmit={(event) => void submit(event)}>
          {dialog.mode === 'attach' ? <>
            {allNotesLoading ? <p>Wczytywanie notatek…</p> : allNotesError ? <p role="alert">Nie udało się pobrać notatek.</p> : !available.length ? <p>Brak notatek do przypięcia.</p> :
              <label className="block space-y-2"><span>Notatka</span><select name="noteId" required defaultValue="" className="w-full rounded-md border p-2"><option value="" disabled>Wybierz notatkę</option>{available.map((note) => <option key={note.id} value={note.id}>{note.title}</option>)}</select></label>}
          </> : <>
            <label className="block space-y-2"><span>Tytuł</span><Input name="title" required maxLength={255} autoFocus defaultValue={dialog.mode === 'edit' ? dialog.note.title : ''} /></label>
            <label className="block space-y-2"><span>Treść</span><Textarea name="content" required rows={10} defaultValue={dialog.mode === 'edit' ? dialog.note.content : ''} /></label>
            {dialog.mode === 'edit' && <p className="text-sm text-muted-foreground">Zmiany będą widoczne we wszystkich profilach, do których przypięto tę notatkę.</p>}
          </>}
          {dialogError && <p role="alert" className="text-sm text-destructive">{dialogError}</p>}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setDialog(null)}>Anuluj</Button>
            <Button type="submit" disabled={createState.isLoading || createProfileState.isLoading || updateState.isLoading || attachState.isLoading || (dialog.mode === 'attach' && (allNotesLoading || !!allNotesError || !available.length))}>
              {dialog.mode === 'attach' ? 'Przypnij' : 'Zapisz notatkę'}
            </Button>
          </DialogFooter>
        </form>}
      </DialogContent>
    </Dialog>
  </>
}
