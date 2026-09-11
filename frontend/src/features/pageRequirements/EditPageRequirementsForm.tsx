import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useListPageSectionsQuery } from '@/features/pageSections/pageSectionsApi'
import { useUpdatePageRequirementsMutation } from './pageRequirementsApi'
import { PAGE_REQUIREMENT_OPTIONS, type PageSectionRequirement } from './pageRequirementsFields'
import type { Entity } from '@/types'

interface SectionState {
  requirement_type?: string
  position?: string
}

export function EditPageRequirementsForm({
  pageRequirements,
  onSaved,
}: {
  pageRequirements: Entity
  onSaved: () => void
}) {
  const { data: sectionTypes, isLoading: sectionsLoading } = useListPageSectionsQuery()
  const [updatePageRequirements, updateState] = useUpdatePageRequirementsMutation()
  const [error, setError] = useState<string | null>(null)
  const [values, setValues] = useState<Record<string, SectionState>>(() => {
    const requirements =
      (pageRequirements.page_section_requirements as PageSectionRequirement[] | undefined) ?? []

    return Object.fromEntries(
      requirements.map((item) => [
        item.page_section_type_id,
        {
          requirement_type: item.requirement_type,
          position: item.position == null ? '' : String(item.position),
        },
      ]),
    )
  })

  const setSectionValue = (sectionType: string, patch: Partial<SectionState>) =>
    setValues((previous) => ({
      ...previous,
      [sectionType]: { ...previous[sectionType], ...patch },
    }))

  const handleSave = async () => {
    const sectionRequirements = Object.entries(values)
      .filter(([, value]) => value.requirement_type)
      .map(([page_section_type_id, value]) => ({
        page_section_type_id,
        requirement_type: value.requirement_type as 'required' | 'optional' | 'excluded',
        position: value.position ? Number(value.position) : null,
      }))

    setError(null)
    try {
      await updatePageRequirements({
        id: pageRequirements.id as number,
        pageStrategyId: pageRequirements.page_strategy_id as number,
        sectionRequirements,
      }).unwrap()
      onSaved()
    } catch {
      setError('Nie udało się zapisać wymagań strony.')
    }
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
                    onValueChange={(next) =>
                      next && setSectionValue(section.id, { requirement_type: next })
                    }
                  >
                    <SelectTrigger id={`requirement-${section.id}`}>
                      <SelectValue placeholder="— (brak)" />
                    </SelectTrigger>
                    <SelectContent>
                      {PAGE_REQUIREMENT_OPTIONS.map((option) => (
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
                    onChange={(event) => setSectionValue(section.id, { position: event.target.value })}
                  />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}
      <Button onClick={() => void handleSave()} disabled={updateState.isLoading || sectionsLoading}>
        {updateState.isLoading ? 'Zapisywanie…' : 'Zapisz'}
      </Button>
    </div>
  )
}
