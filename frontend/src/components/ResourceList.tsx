import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { EntityList } from '@/components/EntityList'
import type { ReactNode } from 'react'
import type { Entity } from '@/types'

interface ResourceListProps {
  title: string
  items: Entity[] | undefined
  isLoading: boolean
  error?: unknown
  linkTo?: (item: Entity) => string
  itemLabel?: (item: Entity) => string
  eyebrow?: string
  itemMeta?: (item: Entity) => ReactNode
  itemDescription?: (item: Entity) => ReactNode
  itemDetails?: (item: Entity) => ReactNode
  onGenerate?: () => void
  isGenerating?: boolean
  generateLabel?: string
  onEdit?: (item: Entity) => void
  onDelete?: (item: Entity) => void
}

/** Generic "list of children + generate new one" block reused by every pipeline stage page. */
export function ResourceList({
  title,
  items,
  isLoading,
  error,
  linkTo,
  itemLabel = (item) => (item.name as string) ?? `#${item.id}`,
  eyebrow,
  itemMeta,
  itemDescription,
  itemDetails,
  onGenerate,
  isGenerating,
  generateLabel = 'Generuj',
  onEdit,
  onDelete,
}: ResourceListProps) {
  return (
    <EntityList
      title={title}
      eyebrow={eyebrow}
      items={items}
      isLoading={isLoading}
      error={error}
      linkTo={linkTo}
      itemLabel={itemLabel}
      itemMeta={itemMeta}
      itemDescription={itemDescription}
      itemDetails={itemDetails}
      onEdit={onEdit}
      onDelete={onDelete}
      emptyDescription="Wygeneruj lub dodaj pierwszy element, aby rozpocząć pracę."
      actions={onGenerate ? (
          <Button onClick={onGenerate} disabled={isGenerating} className="h-10 rounded-none px-4">
            <Plus />
            {isGenerating ? 'Generowanie…' : generateLabel}
          </Button>
      ) : undefined}
    />
  )
}
