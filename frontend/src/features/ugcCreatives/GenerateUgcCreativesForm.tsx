import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useGenerateUgcCreativesMutation } from './ugcCreativesApi'

export function GenerateUgcCreativesForm({ offerProfileId, onSaved }: { offerProfileId: number; onSaved: () => void }) {
  const [generate, { isLoading }] = useGenerateUgcCreativesMutation()
  const [error, setError] = useState('')

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const count = Number(form.get('count'))
    if (!Number.isInteger(count) || count < 1 || count > 10) {
      setError('Podaj liczbę od 1 do 10.')
      return
    }
    setError('')
    try {
      await generate({
        offerProfileId,
        count,
        generationInstructions: String(form.get('generation_instructions') ?? '').trim(),
      }).unwrap()
      onSaved()
    } catch {
      setError('Nie udało się wygenerować UGC creatives. Spróbuj ponownie.')
    }
  }

  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2">
      <span className="text-sm font-medium">Liczba UGC creatives</span>
      <Input name="count" type="number" min={1} max={10} step={1} defaultValue={3} required />
    </label>
    <label className="block space-y-2">
      <span className="text-sm font-medium">Wskazówki dla AI (opcjonalnie)</span>
      <Textarea name="generation_instructions" rows={5} maxLength={4000} placeholder="Np. naturalne nagranie telefonem, pokazujące użycie oferty krok po kroku." />
    </label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={isLoading}>{isLoading ? 'Generowanie…' : 'Generuj UGC creatives'}</Button>
  </form>
}
