import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { useListPageBlueprintForOfferProfileQuery } from '@/features/pageBlueprint/pageBlueprintApi'
import { useGeneratePageMutation } from './pagesApi'

export function GeneratePageForm({ offerProfileId, onSaved }: { offerProfileId: number; onSaved: () => void }) {
  const { data: blueprints, isLoading: loadingBlueprints } = useListPageBlueprintForOfferProfileQuery(offerProfileId)
  const [generate, state] = useGeneratePageMutation()
  const [error, setError] = useState('')

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const selected = String(form.get('page_blueprint_id') ?? '')
    const pageBlueprintId = selected ? Number(selected) : null
    setError('')
    try {
      await generate({
        offerProfileId,
        pageBlueprintId,
        generationInstructions: String(form.get('generation_instructions') ?? '').trim(),
      }).unwrap()
      onSaved()
    } catch {
      setError('Nie udało się wygenerować strony. Sprawdź wskazówki lub spróbuj ponownie.')
    }
  }

  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Page blueprint (opcjonalnie)</span>
      <select name="page_blueprint_id" defaultValue="" className="h-10 w-full rounded-md border border-input bg-background px-3 text-sm">
        <option value="">Bez blueprintu — AI dobierze sekcje</option>
        {(blueprints ?? []).map((blueprint) => <option key={blueprint.id} value={blueprint.id}>{String(blueprint.name ?? `#${blueprint.id}`)}</option>)}
      </select>
    </label>
    <label className="block space-y-2"><span className="text-sm font-medium">Wskazówki dla AI (opcjonalnie)</span>
      <Textarea name="generation_instructions" rows={5} maxLength={4000} placeholder="Np. ton rzeczowy, krótkie akapity i jasne wezwanie do działania." />
    </label>
    <p className="text-sm text-muted-foreground">AI użyje danych profilu i źródła oferty. Dołączony blueprint określi sekcje oraz ich kolejność.</p>
    {loadingBlueprints && <p className="text-sm text-muted-foreground">Wczytywanie blueprintów…</p>}
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={state.isLoading}>{state.isLoading ? 'Generowanie…' : 'Generuj page'}</Button>
  </form>
}
