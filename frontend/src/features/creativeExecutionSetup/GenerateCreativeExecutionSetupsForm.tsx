import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { useGenerateCreativeExecutionSetupsMutation } from '@/features/creativeExecutionSetup/creativeExecutionSetupApi'

export function GenerateCreativeExecutionSetupsForm({
  adSetupId,
  onSaved,
}: {
  adSetupId: number
  onSaved: () => void
}) {
  const [generate, state] = useGenerateCreativeExecutionSetupsMutation()
  const [error, setError] = useState<string | null>(null)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const count = Number(form.get('count'))

    if (!Number.isInteger(count) || count < 1 || count > 10) {
      setError('Podaj liczbę od 1 do 10.')
      return
    }

    setError(null)
    try {
      await generate({ adSetupId, count }).unwrap()
      onSaved()
    } catch {
      setError('Nie udało się wygenerować konfiguracji. Sprawdź odpowiedź modelu i spróbuj ponownie.')
    }
  }

  return (
    <form onSubmit={(event) => void submit(event)} className="space-y-5">
      <p className="text-sm leading-6 text-muted-foreground">
        Konfiguracje zostaną dopasowane do bieżących Ad Strategy, Creative Strategy,
        medium i platformy. Istniejące konfiguracje posłużą do unikania duplikatów.
      </p>
      <label className="block space-y-2">
        <span className="text-sm font-medium">Liczba konfiguracji</span>
        <input
          name="count"
          type="number"
          min={1}
          max={10}
          step={1}
          defaultValue={3}
          required
          className="h-9 w-full rounded-md border px-2.5 text-sm"
        />
        <span className="block text-xs text-muted-foreground">Możesz wygenerować od 1 do 10 różnych wariantów.</span>
      </label>
      {error && <p className="text-sm text-destructive">{error}</p>}
      <Button type="submit" disabled={state.isLoading}>
        {state.isLoading ? 'Generowanie…' : 'Generuj konfiguracje'}
      </Button>
    </form>
  )
}
