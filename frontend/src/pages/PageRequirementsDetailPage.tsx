import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  useGetPageRequirementsQuery,
  useUpdatePageRequirementsMutation,
} from '@/features/pageRequirements/pageRequirementsApi'
import { useListPageSectionsQuery } from '@/features/pageSections/pageSectionsApi'
import { useSidePanel } from '@/lib/sidePanel'
import type { Entity } from '@/types'

const REQUIREMENT_OPTIONS = [
  { value: 'required', label: 'Wymagana' },
  { value: 'optional', label: 'Opcjonalna' },
  { value: 'excluded', label: 'Wykluczona' },
]

const REQUIREMENT_LABELS: Record<string, string> = Object.fromEntries(
  REQUIREMENT_OPTIONS.map((option) => [option.value, option.label]),
)

interface SectionState {
  requirement_type?: string
  position?: string
}

interface PageSectionRequirement {
  page_section_type_id: string
  requirement_type: string
  position: number | null
}

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
            <EditSectionRequirementsForm
              id={id}
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
            const section = sectionTypes?.find((s) => s.id === item.page_section_type_id)

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
                  {REQUIREMENT_LABELS[item.requirement_type] ?? item.requirement_type}
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

function EditSectionRequirementsForm({
  id,
  pageRequirements,
  onSaved,
}: {
  id: number
  pageRequirements: Entity
  onSaved: () => void
}) {
  const { data: sectionTypes, isLoading: sectionsLoading } = useListPageSectionsQuery()
  const [updatePageRequirements, updateState] = useUpdatePageRequirementsMutation()

  const [values, setValues] = useState<Record<string, SectionState>>(() => {
    const sectionRequirements =
      (pageRequirements.page_section_requirements as PageSectionRequirement[] | undefined) ?? []

    return Object.fromEntries(
      sectionRequirements.map((item) => [
        item.page_section_type_id,
        {
          requirement_type: item.requirement_type,
          position: item.position == null ? '' : String(item.position),
        },
      ]),
    )
  })

  const setSectionValue = (sectionType: string, patch: Partial<SectionState>) =>
    setValues((prev) => ({ ...prev, [sectionType]: { ...prev[sectionType], ...patch } }))

  const handleSave = async () => {
    const sectionRequirements = Object.entries(values)
      .filter(([, value]) => value.requirement_type)
      .map(([page_section_type_id, value]) => ({
        page_section_type_id,
        requirement_type: value.requirement_type as 'required' | 'optional' | 'excluded',
        position: value.position ? Number(value.position) : null,
      }))

    await updatePageRequirements({ id, sectionRequirements }).unwrap()
    onSaved()
  }

  return (
    <div className="space-y-4">
      {sectionsLoading && <p className="text-sm text-muted-foreground">Ładowanie…</p>}

      <div className="space-y-3">
        {sectionTypes?.map((section) => {
          const value = values[section.id] ?? {}

          return (
            <div key={section.id} className="space-y-2 bg-muted/25 p-3">
              <div>
                <p className="text-sm font-medium">{section.name}</p>
                <p className="text-xs text-muted-foreground">{section.description}</p>
              </div>

              <div className="flex gap-2">
                <div className="flex-1">
                  <Label className="sr-only" htmlFor={`requirement-${section.id}`}>
                    Status sekcji {section.name}
                  </Label>
                  <Select
                    value={value.requirement_type}
                    onValueChange={(next) => next && setSectionValue(section.id, { requirement_type: next })}
                  >
                    <SelectTrigger id={`requirement-${section.id}`}>
                      <SelectValue placeholder="— (brak)" />
                    </SelectTrigger>
                    <SelectContent>
                      {REQUIREMENT_OPTIONS.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                          {option.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="w-24">
                  <Label className="sr-only" htmlFor={`position-${section.id}`}>
                    Pozycja sekcji {section.name}
                  </Label>
                  <Input
                    id={`position-${section.id}`}
                    type="number"
                    placeholder="pozycja"
                    value={value.position ?? ''}
                    disabled={!value.requirement_type}
                    onChange={(e) => setSectionValue(section.id, { position: e.target.value })}
                  />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <Button onClick={() => void handleSave()} disabled={updateState.isLoading}>
        {updateState.isLoading ? 'Zapisywanie…' : 'Zapisz'}
      </Button>
    </div>
  )
}
