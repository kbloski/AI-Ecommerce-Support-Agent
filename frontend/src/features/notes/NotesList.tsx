import { useState, type FormEvent } from 'react'
import { EntityList } from '@/components/EntityList'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  useCreateNoteMutation, useDeleteNoteMutation, useListNotesQuery, useUpdateNoteMutation,
  type Note,
} from './notesApi'

type NoteDialog = { mode: 'create' } | { mode: 'edit'; note: Note }

export function NotesList() {
  const { data: notes, isLoading, error } = useListNotesQuery()
  const [dialog, setDialog] = useState<NoteDialog | null>(null)
  const [create, createState] = useCreateNoteMutation()
  const [update, updateState] = useUpdateNoteMutation()
  const [remove, removeState] = useDeleteNoteMutation()
  const [actionError, setActionError] = useState('')
  const [dialogError, setDialogError] = useState('')

  const openDialog = (next: NoteDialog) => { setDialogError(''); setDialog(next) }
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!dialog) return
    setDialogError('')
    const form = new FormData(event.currentTarget)
    const title = String(form.get('title') ?? '').trim()
    const content = String(form.get('content') ?? '').trim()
    if (!title || !content) { setDialogError('Podaj tytuł i treść notatki.'); return }
    try {
      if (dialog.mode === 'edit') await update({ id: dialog.note.id, title, content }).unwrap()
      else await create({ title, content }).unwrap()
      setDialog(null)
    } catch { setDialogError('Nie udało się zapisać notatki.') }
  }

  const deleteNote = async (note: Note) => {
    if (!window.confirm(`Usunąć notatkę „${note.title}”?`)) return
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
      itemActions={(item) => <Button variant="ghost" size="sm" disabled={removeState.isLoading} onClick={() => void deleteNote(item as Note)}>Usuń</Button>}
      emptyTitle="Brak notatek"
      emptyDescription="Dodaj pierwszą notatkę."
      contentBeforeList={actionError ? <p role="alert" className="text-sm text-destructive">{actionError}</p> : undefined}
      actions={<Button onClick={() => openDialog({ mode: 'create' })}>Dodaj notatkę</Button>}
    />
    <Dialog open={dialog !== null} onOpenChange={(open) => { if (!open) setDialog(null) }}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{dialog?.mode === 'edit' ? 'Edytuj notatkę' : 'Dodaj notatkę'}</DialogTitle>
        </DialogHeader>
        {dialog && <form key={dialog.mode === 'edit' ? `edit-${dialog.note.id}` : dialog.mode} className="space-y-4" onSubmit={(event) => void submit(event)}>
          <label className="block space-y-2"><span>Tytuł</span><Input name="title" required maxLength={255} autoFocus defaultValue={dialog.mode === 'edit' ? dialog.note.title : ''} /></label>
          <label className="block space-y-2"><span>Treść</span><Textarea name="content" required rows={10} defaultValue={dialog.mode === 'edit' ? dialog.note.content : ''} /></label>
          {dialogError && <p role="alert" className="text-sm text-destructive">{dialogError}</p>}
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setDialog(null)}>Anuluj</Button>
            <Button type="submit" disabled={createState.isLoading || updateState.isLoading}>Zapisz notatkę</Button>
          </DialogFooter>
        </form>}
      </DialogContent>
    </Dialog>
  </>
}
