import { Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { EntityList } from '@/components/EntityList'
import type { ReactNode } from 'react'
import type { Entity } from '@/types'

interface ResourceListProps {
  title: string
  items: Entity[] | undefined
  attentionItems?: number
  isLoading: boolean
  error?: unknown
  linkTo?: (item: Entity) => string
  itemLabel?: (item: Entity) => string
  eyebrow?: string
  itemMeta?: (item: Entity) => ReactNode
  itemBadges?: (item: Entity) => ReactNode
  itemDescription?: (item: Entity) => ReactNode
  itemDetails?: (item: Entity) => ReactNode
  itemActions?: (item: Entity) => ReactNode
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
  attentionItems,
  isLoading,
  error,
  linkTo,
  itemLabel = (item) => (item.name as string) ?? `#${item.id}`,
  eyebrow,
  itemMeta,
  itemBadges,
  itemDescription,
  itemDetails,
  itemActions,
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
      attentionItems={attentionItems}
      isLoading={isLoading}
      error={error}
      linkTo={linkTo}
      itemLabel={itemLabel}
      itemMeta={itemMeta}
      itemBadges={itemBadges}
      itemDescription={itemDescription}
      itemDetails={itemDetails}
      itemActions={itemActions}
      onEdit={onEdit}
      onDelete={onDelete}
      emptyDescription="Wygeneruj lub dodaj pierwszy element, aby rozpocząć pracę."
      actions={onGenerate ? (
          <Button onClick={onGenerate} disabled={isGenerating} className="h-9 rounded-md bg-[#111111] px-4 text-white shadow-sm hover:bg-black">
            <Plus />
            {isGenerating ? 'Generowanie…' : generateLabel}
          </Button>
      ) : undefined}
    />
  )
}
