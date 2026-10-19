import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { Button } from '@/components/ui/button'
import { EditPageBlueprintForm } from '@/features/pageBlueprint/EditPageBlueprintForm'
import type { PageBlueprintSection } from '@/features/pageBlueprint/pageBlueprintFields'
import { useGetPageBlueprintQuery } from '@/features/pageBlueprint/pageBlueprintApi'
import { useSidePanel } from '@/lib/sidePanel'

export default function PageBlueprintDetailPage() {
  const id = Number(useParams().id)
  const { data, isLoading, error } = useGetPageBlueprintQuery(id)
  const { openPanel, closePanel } = useSidePanel()
  const sections = ((data?.sections as PageBlueprintSection[] | undefined) ?? []).slice().sort((a, b) => a.position - b.position)
  return <DetailShell
    title={String(data?.name ?? 'Page blueprint')}
    data={data} isLoading={isLoading} error={error} exclude={['sections']}
    backTo={data ? `/offer-profiles/${data.offer_profile_id}` : undefined}
    actions={data ? <Button onClick={() => openPanel({ title: 'Edytuj page blueprint', content: <EditPageBlueprintForm pageBlueprint={data} onSaved={closePanel} /> })}>Edytuj</Button> : undefined}
  >
    {data && <div className="space-y-3">
      <h2 className="text-lg font-semibold">Sekcje ({sections.length})</h2>
      {sections.map((section) => <article key={section.id ?? section.position} className="space-y-2 rounded-md border p-4">
        <h3 className="font-medium">{section.position}. {section.name}</h3>
        <p className="text-sm text-muted-foreground">{section.type}{section.is_optional ? ' · Opcjonalna' : ''}</p>
        <p className="whitespace-pre-wrap text-sm">{section.purpose}</p>
      </article>)}
      {sections.length === 0 && <p className="text-sm text-muted-foreground">Brak sekcji. Dodaj je w edytorze blueprintu.</p>}
    </div>}
  </DetailShell>
}
