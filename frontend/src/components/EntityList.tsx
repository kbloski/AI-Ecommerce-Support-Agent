import { useMemo, type ReactNode } from 'react'
import { ArrowUpRight, Eye, Pencil, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { EntityViewer } from '@/components/EntityViewer'
import { useSidePanel } from '@/lib/sidePanel'
import type { Entity } from '@/types'

interface EntityListProps {
  title: string
  eyebrow?: string
  items: Entity[] | undefined
  isLoading?: boolean
  error?: unknown
  actions?: ReactNode
  contentBeforeList?: ReactNode
  footer?: ReactNode
  totalItems?: number
  linkTo?: (item: Entity) => string
  itemLabel?: (item: Entity) => string
  itemMeta?: (item: Entity) => ReactNode
  itemBadges?: (item: Entity) => ReactNode
  itemDescription?: (item: Entity) => ReactNode
  itemDetails?: (item: Entity) => ReactNode
  itemActions?: (item: Entity) => ReactNode
  onEdit?: (item: Entity) => void
  onDelete?: (item: Entity) => void
  emptyTitle?: string
  emptyDescription?: string
}

function defaultItemBadges(item: Entity): ReactNode {
  const badges = [item.type, item.status, item.fact_status]
    .filter((value, index, values) => value != null && value !== '' && values.indexOf(value) === index)
    .map(String)

  if (typeof item.is_reviewed === 'boolean') badges.push(item.is_reviewed ? 'Sprawdzony' : 'Wymaga sprawdzenia')
  if (badges.length === 0) return null

  return badges.map((badge) => (
    <span key={badge} className="inline-flex items-center rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[10px] font-medium text-slate-600">
      {badge.replaceAll('_', ' ')}
    </span>
  ))
}

/** Shared monochrome card list used across entity and resource pages. */
export function EntityList({
  title,
  eyebrow,
  items,
  isLoading,
  error,
  actions,
  contentBeforeList,
  footer,
  totalItems,
  linkTo,
  itemLabel = (item) => (item.name as string) ?? `#${item.id}`,
  itemMeta = (item) => `Identyfikator ${String(item.id)}`,
  itemBadges = defaultItemBadges,
  itemDescription,
  itemDetails,
  itemActions,
  onEdit,
  onDelete,
  emptyTitle = 'Brak elementów',
  emptyDescription = 'Dodaj pierwszy element, aby rozpocząć pracę.',
}: EntityListProps) {
  const entries = useMemo(() => items ?? [], [items])
  const { openPanel } = useSidePanel()

  return (
    <section className="w-full max-w-5xl space-y-7">
      <header className="flex flex-wrap items-center justify-between gap-4 pb-1">
        <div>
          {eyebrow && <p className="mb-1 text-xs font-semibold tracking-[0.16em] text-slate-500 uppercase">{eyebrow}</p>}
          <div className="flex items-baseline gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-slate-950">{title}</h1>
            <span className="font-mono text-xs text-slate-400">{totalItems ?? entries.length}</span>
          </div>
        </div>
        {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
      </header>

      {contentBeforeList}
      {isLoading && <p className="rounded-lg border border-slate-200 bg-white px-6 py-8 text-sm text-slate-500 shadow-sm">Ładowanie…</p>}
      {Boolean(error) && <p className="rounded-lg border border-slate-300 bg-slate-50 px-6 py-8 text-sm text-slate-800">Nie udało się pobrać danych.</p>}
      {!isLoading && !error && entries.length === 0 && (
        <div className="rounded-lg border border-slate-200 bg-white py-12 text-center shadow-sm">
          <p className="font-medium text-slate-900">{emptyTitle}</p>
          <p className="mt-1 text-sm text-slate-500">{emptyDescription}</p>
        </div>
      )}

      {entries.length > 0 && (
        <div className="space-y-3.5">
          {entries.map((item, index) => {
            const badges = itemBadges(item)
            return (
              <article key={item.id} className="group rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition-all hover:border-slate-400">
                <div className="flex items-start gap-8">
                  <span className="w-5 shrink-0 select-none pt-0.5 font-mono text-xs text-slate-400">{String(index + 1).padStart(2, '0')}</span>
                  <div className="min-w-0 flex-1 space-y-2">
                    <div className="flex flex-wrap items-start justify-between gap-3">
                      {linkTo ? (
                        <Link to={linkTo(item)} className="line-clamp-2 text-sm font-semibold leading-5 text-slate-950 hover:underline">{itemLabel(item)}</Link>
                      ) : (
                        <h2 className="line-clamp-2 text-sm font-semibold leading-5 text-slate-950">{itemLabel(item)}</h2>
                      )}
                      <span className="font-mono text-[11px] text-slate-400">{itemMeta(item)}</span>
                    </div>

                    {badges && <div className="flex flex-wrap items-center gap-2 pt-0.5">{badges}</div>}
                    {itemDescription?.(item) && <p className="max-w-3xl pt-1 text-xs leading-relaxed whitespace-pre-wrap text-slate-600">{itemDescription(item)}</p>}
                    {itemDetails?.(item) && <div className="mt-3 rounded-md bg-slate-50 px-3 py-2 text-xs leading-5 text-slate-600">{itemDetails(item)}</div>}

                    {(itemActions || linkTo || onEdit || onDelete) && (
                      <div className="mt-3 flex items-center gap-1 border-t border-slate-100 pt-3">
                        {itemActions?.(item)}
                        <Button
                          variant="ghost"
                          size="icon-sm"
                          className="rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-950"
                          aria-label={`Podgląd ${title}`}
                          onClick={() => openPanel({
                            title: `Podgląd: ${itemLabel(item)}`,
                            content: <EntityViewer data={item} />,
                          })}
                        >
                          <Eye />
                        </Button>
                        {linkTo && (
                          <Button nativeButton={false} render={<Link to={linkTo(item)} aria-label={`Otwórz ${title}`} />} variant="ghost" size="icon-sm" className="rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-950"><ArrowUpRight /></Button>
                        )}
                        {onEdit && (
                          <Button variant="ghost" size="icon-sm" className="rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-950" aria-label={`Edytuj ${title}`} onClick={() => onEdit(item)}><Pencil /></Button>
                        )}
                        {onDelete && (
                          <Button variant="ghost" size="icon-sm" className="rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-950" aria-label={`Usuń ${title}`} onClick={() => { if (window.confirm('Czy na pewno usunąć ten element?')) onDelete(item) }}><Trash2 /></Button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </article>
            )
          })}
        </div>
      )}

      {footer}
    </section>
  )
}
