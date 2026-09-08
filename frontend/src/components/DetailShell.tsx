import type { ReactNode } from 'react'
import { EditableFields } from '@/components/EditableFields'
import { JsonPanelRegistration } from '@/components/JsonPanelRegistration'
import type { Entity } from '@/types'

interface DetailShellProps {
  title: string
  backTo?: string
  backLabel?: string
  data: Entity | undefined
  isLoading: boolean
  error?: unknown
  children?: ReactNode
  actions?: ReactNode
  overview?: ReactNode
  exclude?: string[]
  itemActions?: Record<string, (item: Record<string, unknown>) => void>
  itemLinks?: Record<string, (item: Record<string, unknown>) => string>
  itemStatusActions?: Record<
    string,
    (item: Record<string, unknown>, status: string) => void | Promise<unknown>
  >
  itemAdditions?: Record<string, ReactNode>
  relationLinks?: Record<string, string>
  /** When provided, the fields panel becomes an editable form that saves via this handler; otherwise fields render disabled/read-only. */
  editable?: {
    onSave: (fields: Record<string, unknown>) => Promise<unknown>
    isSaving?: boolean
  }
}

/** Shared layout for every "detail" page: title, entity fields, optional child sections. */
export function DetailShell({
  title,
  data,
  isLoading,
  error,
  actions,
  overview,
  exclude,
  itemActions,
  itemLinks,
  itemStatusActions,
  itemAdditions,
  relationLinks,
  editable,
  children,
}: DetailShellProps) {
  return (
    <div className="w-full space-y-6 p-6 lg:p-10">

      {data && (
        <JsonPanelRegistration data={data} title={`JSON: ${title}`} />
      )}

      <div className="space-y-6">

        {title && <h1 className="text-2xl font-semibold">{title}</h1>}

        {actions && <div className="flex flex-wrap gap-2">{actions}</div>}

        {isLoading && <p className="text-sm text-muted-foreground">Ładowanie…</p>}
        {Boolean(error) && <p className="text-sm text-destructive">Nie udało się pobrać danych.</p>}

        {data && (
          <div>
            <EditableFields
              key={String(data.id)}
              data={data}
              exclude={exclude}
              itemActions={itemActions}
              itemLinks={itemLinks}
              itemStatusActions={itemStatusActions}
              itemAdditions={itemAdditions}
              relationLinks={relationLinks}
              isSaving={editable?.isSaving}
              onSave={editable ? (fields) => editable.onSave(fields) : undefined}
            />
          </div>
        )}

        {data && overview}
        {data && children}
      </div>
    </div>
  )
}
