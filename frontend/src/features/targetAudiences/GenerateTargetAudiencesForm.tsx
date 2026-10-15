import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useGenerateTargetAudiencesMutation } from './targetAudiencesApi'

export function GenerateTargetAudiencesForm({ offerProfileId, onSaved }: { offerProfileId: number; onSaved: () => void }) {
  const [generate, state] = useGenerateTargetAudiencesMutation()
  const [error, setError] = useState('')

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const count = Number(form.get('count'))
    const generationInstructions = String(form.get('generation_instructions') ?? '').trim()
    if (!Number.isInteger(count) || count < 1 || count > 10) {
      setError('Podaj liczbę od 1 do 10.')
      return
    }
    if (generationInstructions.length > 4000) {
      setError('Wskazówki mogą mieć maksymalnie 4000 znaków.')
      return
    }

    setError('')
    try {
      await generate({ offerProfileId, count, generationInstructions }).unwrap()
      onSaved()
    } catch {
      setError('Nie udało się wygenerować grup docelowych. Sprawdź odpowiedź modelu i spróbuj ponownie.')
    }
  }

  return (
    <form onSubmit={(event) => void submit(event)} className="space-y-5">
      <p className="text-sm leading-6 text-muted-foreground">
        Grupy powstaną na podstawie profilu oferty i dołączonych do niego informacji.
      </p>
      <label className="block space-y-2">
        <span className="text-sm font-medium">Liczba grup docelowych</span>
        <Input name="count" type="number" min={1} max={10} step={1} defaultValue={3} required autoFocus />
        <span className="block text-xs text-muted-foreground">Możesz wygenerować od 1 do 10 różnych grup.</span>
      </label>
      <label className="block space-y-2">
        <span className="text-sm font-medium">Wskazówki do generowania (opcjonalnie)</span>
        <Textarea
          name="generation_instructions"
          maxLength={4000}
          rows={5}
          placeholder="Np. skup się na osobach kupujących prezent dla bliskich."
        />
        <span className="block text-xs text-muted-foreground">Opisz, na jakie grupy odbiorców model ma zwrócić uwagę.</span>
      </label>
      {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
      <Button type="submit" disabled={state.isLoading}>
        {state.isLoading ? 'Generowanie…' : 'Generuj grupy docelowe'}
      </Button>
    </form>
  )
}
