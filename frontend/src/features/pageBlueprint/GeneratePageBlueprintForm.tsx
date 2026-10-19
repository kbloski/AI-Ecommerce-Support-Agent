import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useGeneratePageBlueprintMutation, type PageBlueprintPageType } from './pageBlueprintApi'

export function GeneratePageBlueprintForm({ offerProfileId, onSaved }: { offerProfileId: number; onSaved: () => void }) {
  const [generate, state] = useGeneratePageBlueprintMutation()
  const [error, setError] = useState('')
  const [countNotProvided, setCountNotProvided] = useState(false)
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const pageType: PageBlueprintPageType = form.get('page_type') === 'product_page' ? 'product_page' : null
    const sectionCount = countNotProvided ? null : Number(form.get('section_count'))
    if (sectionCount !== null && (!Number.isInteger(sectionCount) || sectionCount < 1 || sectionCount > 50)) {
      setError('Podaj liczbę sekcji od 1 do 50.')
      return
    }
    setError('')
    try {
      await generate({ offerProfileId, pageType, sectionCount, generationInstructions: String(form.get('generation_instructions') ?? '').trim() }).unwrap()
      onSaved()
    } catch {
      setError('Nie udało się wygenerować blueprintu. Spróbuj ponownie.')
    }
  }
  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Typ strony</span>
      <select name="page_type" defaultValue="" className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm">
        <option value="">Nie podano</option>
        <option value="product_page">Strona produktu</option>
      </select>
    </label>
    <fieldset className="space-y-2">
      <legend className="text-sm font-medium">Liczba sekcji</legend>
      <label className="flex items-center gap-2 text-sm">
        <input type="radio" name="section_count_mode" checked={!countNotProvided} onChange={() => setCountNotProvided(false)} />
        Podaj liczbę
      </label>
      <Input name="section_count" type="number" min={1} max={50} step={1} defaultValue={8} required={!countNotProvided} disabled={countNotProvided} aria-label="Liczba sekcji od 1 do 50" />
      <label className="flex items-center gap-2 text-sm">
        <input type="radio" name="section_count_mode" checked={countNotProvided} onChange={() => setCountNotProvided(true)} />
        Nie podano — AI dobierze liczbę sekcji
      </label>
    </fieldset>
    <label className="block space-y-2"><span className="text-sm font-medium">Wskazówki dla AI (opcjonalnie)</span>
      <Textarea name="generation_instructions" rows={5} maxLength={4000} placeholder="Np. krótka strona z naciskiem na zastosowania produktu i odpowiedzi na obiekcje." />
    </label>
    <p className="text-sm text-muted-foreground">Powstanie jeden blueprint. Katalog sekcji zostanie przekazany AI tylko dla strony produktu i służy jako inspiracja.</p>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={state.isLoading}>{state.isLoading ? 'Generowanie…' : 'Generuj blueprint'}</Button>
  </form>
}
