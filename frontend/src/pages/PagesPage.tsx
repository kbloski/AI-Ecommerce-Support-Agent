import { useParams } from 'react-router-dom'
import { ResourceList } from '@/components/ResourceList'
import { GeneratePageForm } from '@/features/pages/GeneratePageForm'
import { useDeletePageMutation, useListPagesQuery } from '@/features/pages/pagesApi'
import { useSidePanel } from '@/lib/sidePanel'

export default function PagesPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const list = useListPagesQuery(offerProfileId)
  const [remove] = useDeletePageMutation()
  const { openPanel, closePanel } = useSidePanel()

  return <div className="w-full p-6 lg:p-10">
    <ResourceList
      title="Pages"
      items={list.data}
      isLoading={list.isLoading}
      error={list.error}
      linkTo={(page) => `/pages/${page.id}`}
      itemLabel={(page) => String(page.name ?? `#${page.id}`)}
      itemDescription={(page) => String(page.description ?? '')}
      onGenerate={() => openPanel({ title: 'Generuj page', content: <GeneratePageForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}
      generateLabel="Generuj page"
      onDelete={(page) => remove({ id: Number(page.id), offerProfileId })}
    />
  </div>
}
