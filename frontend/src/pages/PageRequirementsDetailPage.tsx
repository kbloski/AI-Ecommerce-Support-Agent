import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { Button } from '@/components/ui/button'
import { EditPageRequirementsForm } from '@/features/pageRequirements/EditPageRequirementsForm'
import {
  PAGE_REQUIREMENT_LABELS,
  type PageSectionRequirement,
} from '@/features/pageRequirements/pageRequirementsFields'
import { useGetPageRequirementsQuery } from '@/features/pageRequirements/pageRequirementsApi'
import { useListPageSectionsQuery } from '@/features/pageSections/pageSectionsApi'
import { useSidePanel } from '@/lib/sidePanel'

export default function PageRequirementsDetailPage() {
  const id = Number(useParams().id)
  const { data: pageRequirements, isLoading, error } = useGetPageRequirementsQuery(id)
  const { data: sectionTypes } = useListPageSectionsQuery()
  const { openPanel, closePanel } = useSidePanel()
  const sectionRequirements =
    (pageRequirements?.page_section_requirements as PageSectionRequirement[] | undefined) ?? []

  return (
    <DetailShell
      title=""
      backTo={pageRequirements ? `/page-strategy/${pageRequirements.page_strategy_id}` : undefined}
      backLabel="← Page strategy"
      data={pageRequirements}
      isLoading={isLoading}
      error={error}
      actions={pageRequirements ? (
        <Button onClick={() => openPanel({
          title: 'Edytuj wymagania dotyczące sekcji',
          content: (
            <EditPageRequirementsForm
              pageRequirements={pageRequirements}
              onSaved={closePanel}
            />
          ),
        })}>
          Edytuj
        </Button>
      ) : undefined}
    >
      <div className="space-y-4">
        <h2 className="text-lg font-semibold">Wymagania dotyczące sekcji</h2>

        {sectionRequirements.length === 0 && (
          <p className="text-sm text-muted-foreground">Brak skonfigurowanych wymagań.</p>
        )}

        <div className="space-y-2">
          {sectionRequirements.map((item) => {
            const section = sectionTypes?.find((candidate) => candidate.id === item.page_section_type_id)

            return (
              <div
                key={item.page_section_type_id}
                className="grid grid-cols-1 items-start gap-3 bg-muted/25 p-3 sm:grid-cols-[1fr_10rem_6rem]"
              >
                <div>
                  <p className="text-sm font-medium">{section?.name ?? item.page_section_type_id}</p>
                  {section?.description && (
                    <p className="text-xs text-muted-foreground">{section.description}</p>
                  )}
                </div>
                <p className="text-sm">
                  {PAGE_REQUIREMENT_LABELS[item.requirement_type] ?? item.requirement_type}
                </p>
                <p className="text-sm text-muted-foreground">{item.position ?? '—'}</p>
              </div>
            )
          })}
        </div>
      </div>
    </DetailShell>
  )
}
