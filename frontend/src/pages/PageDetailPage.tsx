import { Link, useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetPageQuery } from '@/features/pages/pagesApi'

type PageSection = { id: number; type: string; name: string; content: string; position: number }

export default function PageDetailPage() {
  const id = Number(useParams().id)
  const { data, isLoading, error } = useGetPageQuery(id)
  const sections = ((data?.sections as PageSection[] | undefined) ?? []).slice().sort((a, b) => a.position - b.position)
  const blueprintId = data?.page_blueprint_id

  return <DetailShell
    title={String(data?.name ?? 'Page')}
    data={data}
    isLoading={isLoading}
    error={error}
    exclude={['sections']}
  >
    {data && <div className="space-y-5">
      <Link className="inline-block text-sm underline" to={`/offer-profiles/${data.offer_profile_id}/pages`}>← Pages</Link>
      {typeof blueprintId === 'number' && <p className="text-sm text-muted-foreground">Blueprint: <Link className="underline" to={`/page-blueprints/${blueprintId}`}>#{blueprintId}</Link></p>}
      <h2 className="text-lg font-semibold">Sekcje ({sections.length})</h2>
      {sections.map((section) => <article key={section.id} className="space-y-3 rounded-md border p-5">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{section.position}. {section.type}</p>
        <h3 className="text-xl font-semibold">{section.name}</h3>
        <p className="whitespace-pre-wrap leading-relaxed">{section.content}</p>
      </article>)}
    </div>}
  </DetailShell>
}
