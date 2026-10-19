import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useSidePanel } from '@/lib/sidePanel'
import { useCreateNoteMutation } from './notesApi'

export function CreateNotePanel() {
  const [createNote, { isLoading }] = useCreateNoteMutation()
  const [error, setError] = useState('')
  const { closePanel } = useSidePanel()

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setError('')
    const form = new FormData(event.currentTarget)
    const title = String(form.get('title') ?? '').trim()
    const content = String(form.get('content') ?? '').trim()
    if (!title || !content) {
      setError('Podaj tytuł i treść notatki.')
      return
    }
    try {
      await createNote({ title, content }).unwrap()
      closePanel()
    } catch {
      setError('Nie udało się zapisać notatki.')
    }
  }

  return <form className="space-y-4" onSubmit={(event) => void submit(event)}>
    <label className="block space-y-2"><span className="text-sm font-medium">Tytuł</span><Input name="title" required maxLength={255} autoFocus /></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Treść</span><Textarea name="content" required rows={12} /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <div className="flex justify-end gap-2">
      <Button type="button" variant="outline" onClick={closePanel}>Anuluj</Button>
      <Button type="submit" disabled={isLoading}>Zapisz notatkę</Button>
    </div>
  </form>
}
