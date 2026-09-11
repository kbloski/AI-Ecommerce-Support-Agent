import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useListPageSectionsQuery } from '@/features/pageSections/pageSectionsApi'
import {
  useCreatePageRequirementsMutation,
  useUpdatePageRequirementsMutation,
} from './pageRequirementsApi'
import { PAGE_REQUIREMENT_OPTIONS, type PageSectionRequirement } from './pageRequirementsFields'
import type { Entity } from '@/types'

interface SectionState {
  requirement_type?: string
  position?: string
}

export function EditPageRequirementsForm({
  pageRequirements,
  pageStrategyId,
  onSaved,
}: {
  pageRequirements?: Entity
  pageStrategyId?: number
  onSaved: () => void
}) {
  const { data: sectionTypes, isLoading: sectionsLoading } = useListPageSectionsQuery()
  const [updatePageRequirements, updateState] = useUpdatePageRequirementsMutation()
  const [createPageRequirements, createState] = useCreatePageRequirementsMutation()
  const [error, setError] = useState<string | null>(null)
  const [name, setName] = useState(String(pageRequirements?.name ?? ''))
  const [values, setValues] = useState<Record<string, SectionState>>(() => {
    const requirements =
      (pageRequirements?.page_section_requirements as PageSectionRequirement[] | undefined) ?? []

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
    const normalizedName = name.trim()
    if (!normalizedName) {
      setError('Nazwa jest wymagana.')
      return
    }

    const sectionRequirements = Object.entries(values)
      .filter(([, value]) => value.requirement_type)
      .map(([page_section_type_id, value]) => ({
        page_section_type_id,
        requirement_type: value.requirement_type as 'required' | 'optional' | 'excluded',
        position: value.position ? Number(value.position) : null,
      }))

    setError(null)
    try {
      if (pageRequirements) {
        await updatePageRequirements({
          id: pageRequirements.id as number,
          pageStrategyId: pageRequirements.page_strategy_id as number,
          name: normalizedName,
          sectionRequirements,
        }).unwrap()
      } else {
        if (pageStrategyId == null) {
          setError('Brak Page Strategy dla nowych wymagań.')
          return
        }
        await createPageRequirements({
          pageStrategyId,
          name: normalizedName,
          sectionRequirements,
        }).unwrap()
      }
      onSaved()
    } catch {
      setError('Nie udało się zapisać wymagań strony.')
    }
  }

  const isSaving = updateState.isLoading || createState.isLoading
  const formId = pageRequirements?.id ?? 'new'

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor={`page-requirements-name-${formId}`}>Nazwa</Label>
        <Input
          id={`page-requirements-name-${formId}`}
          value={name}
          onChange={(event) => setName(event.target.value)}
          placeholder="Np. Landing page produktu"
        />
      </div>

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
                      next && setSectionValue(section.id, {
                        requirement_type: next,
                        ...(next === 'excluded' ? { position: '' } : {}),
                      })
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
                    min={1}
                    placeholder="pozycja"
                    value={value.position ?? ''}
                    disabled={!value.requirement_type || value.requirement_type === 'excluded'}
                    onChange={(event) => setSectionValue(section.id, { position: event.target.value })}
                  />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {error && <p className="text-sm text-destructive">{error}</p>}
      <Button onClick={() => void handleSave()} disabled={isSaving || sectionsLoading}>
        {isSaving ? 'Zapisywanie…' : 'Zapisz'}
      </Button>
    </div>
  )
}
