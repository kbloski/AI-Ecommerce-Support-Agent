import { useState, type FormEvent, type ReactNode } from 'react'
import { ChevronDown } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { RelationCards } from '@/components/RelationCards'
import { SegmentedControl } from '@/components/SegmentedControl'
import { isPrimitive, isRelationArray, label } from '@/lib/entityFields'
import { useListFactStatusesQuery } from '@/features/factStatus/factStatusApi'

const SKIP_KEYS = new Set(['id', 'created_at', 'updated_at'])

function isSkipped(key: string, includeRelationIds: string[] = []): boolean {
  return SKIP_KEYS.has(key) || (key.endsWith('_id') && !includeRelationIds.includes(key))
}

function toFormValue(value: unknown): string {
  if (value === null || value === undefined) return ''
  if (isPrimitive(value)) return String(value)
  return JSON.stringify(value, null, 2)
}

function ObjectArray({
  items,
  onDelete,
  onEditLink,
  onStatusChange,
  statuses,
}: {
  items: Record<string, unknown>[]
  onDelete?: (item: Record<string, unknown>) => void
  onEditLink?: (item: Record<string, unknown>) => string
  onStatusChange?: (item: Record<string, unknown>, status: string) => void | Promise<unknown>
  statuses?: { value: string; label: string }[]
}) {
  return (
    <div className="space-y-2">
      {items.map((item, i) => (
        <div
          key={item.id == null ? i : String(item.id)}
          className="space-y-2 bg-muted/25 p-4 transition-colors hover:bg-muted/45"
        >
          {(onDelete || onEditLink) && (
            <div className="flex justify-end gap-2">
              {onEditLink && (
                <Button
                  size="sm"
                  variant="black"
                  className="rounded-none"
                  nativeButton={false}
                  render={<Link to={onEditLink(item)} />}
                >
                  Edytuj
                </Button>
              )}
              {onDelete && (
                <Button
                  size="sm"
                  variant="black"
                  className="rounded-none"
                  onClick={() => {
                    if (window.confirm('Czy na pewno usunąć ten element?')) {
                      onDelete(item)
                    }
                  }}
                >
                  Usuń
                </Button>
              )}
            </div>
          )}
          <dl className="space-y-3">
            {Object.entries(item)
              .filter(([key]) => key !== 'id')
              .map(([key, value]) => (
                <div key={key} className="grid gap-1">
                  <dt className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
                    {label(key)}
                  </dt>
                  <dd className="text-sm whitespace-pre-wrap">
                    {key === 'fact_status' && onStatusChange ? (
                      <SegmentedControl
                        value={typeof value === 'string' ? value : undefined}
                        options={statuses}
                        onValueChange={(status) => onStatusChange(item, status)}
                        ariaLabel={`Status faktyczny elementu ${String(item.id)}`}
                      />
                    ) : value === null || value === undefined || value === '' ? (
                      <span className="text-muted-foreground italic">—</span>
                    ) : isPrimitive(value) ? (
                      String(value)
                    ) : (
                      <pre className="overflow-x-auto rounded-md border bg-muted/50 p-2 text-xs">
                        {JSON.stringify(value, null, 2)}
                      </pre>
                    )}
                  </dd>
                </div>
              ))}
          </dl>
        </div>
      ))}
    </div>
  )
}

/** Labeled, collapsible list of a relation field's items (each with its own "id"), with optional per-item "Edytuj"/"Usuń" actions. */
export function RelationList({
  fieldKey,
  items,
  onDelete,
  onEditLink,
  onStatusChange,
  statuses,
  addition,
  showHeading = true,
}: {
  fieldKey: string
  items: Record<string, unknown>[]
  onDelete?: (item: Record<string, unknown>) => void
  onEditLink?: (item: Record<string, unknown>) => string
  onStatusChange?: (item: Record<string, unknown>, status: string) => void | Promise<unknown>
  statuses?: { value: string; label: string }[]
  addition?: ReactNode
  showHeading?: boolean
}) {
  if (items.length === 0 && !addition) return null

  const content = (
    <>
      {addition && <div className="mb-3">{addition}</div>}
      {items.length > 0 && (
        <ObjectArray
          items={items}
          onDelete={onDelete}
          onEditLink={onEditLink}
          onStatusChange={onStatusChange}
          statuses={statuses}
        />
      )}
    </>
  )

  if (!showHeading) return content

  return (
    <Collapsible>
      <CollapsibleTrigger className="group flex items-center gap-1.5 text-xs font-medium tracking-wide text-muted-foreground uppercase hover:text-foreground">
        <ChevronDown className="size-3.5 shrink-0 transition-transform group-data-[panel-open]:rotate-180" />
        {label(fieldKey)} ({items.length})
      </CollapsibleTrigger>
      <CollapsibleContent className="pt-2">
        {content}
      </CollapsibleContent>
    </Collapsible>
  )
}

interface EditableFieldsProps {
  data: Record<string, unknown>
  /** When omitted, fields render as disabled/read-only inputs and no save button is shown. */
  onSave?: (fields: Record<string, unknown>) => Promise<unknown>
  isSaving?: boolean
  exclude?: string[]
  includeRelationIds?: string[]
  itemActions?: Record<string, (item: Record<string, unknown>) => void>
  itemLinks?: Record<string, (item: Record<string, unknown>) => string>
  itemStatusActions?: Record<
    string,
    (item: Record<string, unknown>, status: string) => void | Promise<unknown>
  >
  itemAdditions?: Record<string, ReactNode>
  relationLinks?: Record<string, string>
}

/** Generic view of any DTO's fields: a plain read-only label/value display when `onSave` is omitted, or an editable form when it's provided. Relation arrays (child entities with their own `id`) stay read-only, rendered via RelationList. */
export function EditableFields({
  data,
  onSave,
  isSaving,
  exclude = [],
  includeRelationIds = [],
  itemActions,
  itemLinks,
  itemStatusActions,
  itemAdditions,
  relationLinks,
}: EditableFieldsProps) {
  const { data: statuses } = useListFactStatusesQuery()

  const isRelationField = (key: string) =>
    isRelationArray(data[key]) ||
    (Array.isArray(data[key]) &&
      Boolean(
        itemActions?.[key] ||
          itemLinks?.[key] ||
          itemStatusActions?.[key] ||
          itemAdditions?.[key],
      ))

  const editableKeys = Object.keys(data).filter(
    (key) => !isSkipped(key, includeRelationIds) && !exclude.includes(key) && !isRelationField(key)
  )
  const relationKeys = Object.keys(data).filter(
    (key) => !isSkipped(key, includeRelationIds) && !exclude.includes(key) && isRelationField(key)
  )

  const [values, setValues] = useState<Record<string, string>>(() =>
    Object.fromEntries(editableKeys.map((key) => [key, toFormValue(data[key])]))
  )
  const [error, setError] = useState<string | null>(null)

  const setField = (key: string, value: string) =>
    setValues((prev) => ({ ...prev, [key]: value }))

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!onSave) return
    setError(null)

    const fields: Record<string, unknown> = {}

    for (const key of editableKeys) {
      const original = data[key]
      const raw = values[key]

      if (key === 'fact_status') {
        fields[key] = raw
      } else if (typeof original === 'number') {
        fields[key] = raw === '' ? null : Number(raw)
      } else if ((original === null || original === undefined) && raw === '') {
        fields[key] = null
      } else if (isPrimitive(original) || original === null || original === undefined) {
        fields[key] = raw
      } else {
        try {
          fields[key] = raw.trim() === '' ? null : JSON.parse(raw)
        } catch {
          setError(`Nieprawidłowy JSON w polu "${label(key)}"`)
          return
        }
      }
    }

    await onSave(fields)
  }

  const relationCards = relationKeys.length > 0 && relationLinks && (
    <RelationCards
      cards={relationKeys.flatMap((key) => {
        const to = relationLinks[key]
        return to ? [{
          id: key,
          label: label(key),
          count: (data[key] as Record<string, unknown>[]).length,
          to,
        }] : []
      })}
    />
  )

  if (!onSave) {
    return (
      <div className="space-y-4">
        <dl className="space-y-3">
          {editableKeys.map((key) => {
            const value = data[key]
            const statusLabel =
              key === 'fact_status'
                ? statuses?.find((status) => status.value === value)?.label
                : undefined

            return (
              <div key={key} className="grid gap-1">
                <dt className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
                  {label(key)}
                </dt>
                <dd className="text-sm whitespace-pre-wrap">
                  {value === null || value === undefined || value === '' ? (
                    <span className="text-muted-foreground italic">—</span>
                  ) : statusLabel ? (
                    statusLabel
                  ) : isPrimitive(value) ? (
                    String(value)
                  ) : (
                    <pre className="overflow-x-auto rounded-md border bg-muted/50 p-2 text-xs">
                      {JSON.stringify(value, null, 2)}
                    </pre>
                  )}
                </dd>
              </div>
            )
          })}
        </dl>

        {relationCards}
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <p className="text-sm text-destructive">{error}</p>}

      <div className="space-y-3">
        {editableKeys.map((key) => (
          <div key={key} className="space-y-1">
            <Label htmlFor={key}>{label(key)}</Label>
            {key === 'fact_status' ? (
              <Select
                value={values[key]}
                onValueChange={(value) => {
                  if (value !== null) setField(key, value)
                }}
              >
                <SelectTrigger id={key}>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {statuses?.map((status) => (
                    <SelectItem key={status.value} value={status.value}>
                      {status.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : typeof data[key] === 'number' ? (
              <Input
                id={key}
                type="number"
                value={values[key]}
                onChange={(e) => setField(key, e.target.value)}
              />
            ) : (
              <Textarea
                id={key}
                value={values[key]}
                onChange={(e) => setField(key, e.target.value)}
                rows={typeof data[key] === 'string' && (data[key] as string).length > 80 ? 4 : 2}
              />
            )}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <Button type="submit" disabled={isSaving}>
          {isSaving ? 'Zapisywanie…' : 'Zapisz'}
        </Button>
      </div>

      {relationCards}
    </form>
  )
}
