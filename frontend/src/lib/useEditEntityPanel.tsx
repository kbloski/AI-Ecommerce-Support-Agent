import { EditableFields } from '@/components/EditableFields'
import { useSidePanel } from '@/lib/sidePanel'
import type { Entity } from '@/types'

/** Opens the shared side panel with a generic editable-fields form for `item`, closing the panel once `onSave` resolves. */
export function useEditEntityPanel() {
  const { openPanel, closePanel } = useSidePanel()

  return (title: string, item: Entity, onSave: (fields: Record<string, unknown>) => Promise<unknown>) => {
    openPanel({
      title: `Edytuj: ${title}`,
      content: (
        <EditableFields
          key={String(item.id)}
          data={item}
          onSave={async (fields) => {
            const result = await onSave(fields)
            closePanel()
            return result
          }}
        />
      ),
    })
  }
}
