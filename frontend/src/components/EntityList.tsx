import { useMemo, type ReactNode } from 'react'
import { ArrowUpRight, Pencil, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import type { Entity } from '@/types'

interface EntityListProps {
  title: string
  eyebrow?: string
  items: Entity[] | undefined
  isLoading?: boolean
  error?: unknown
  actions?: ReactNode
  contentBeforeList?: ReactNode
  linkTo?: (item: Entity) => string
  itemLabel?: (item: Entity) => string
  itemMeta?: (item: Entity) => ReactNode
  itemDescription?: (item: Entity) => ReactNode
  itemDetails?: (item: Entity) => ReactNode
  onEdit?: (item: Entity) => void
  onDelete?: (item: Entity) => void
  emptyTitle?: string
  emptyDescription?: string
}

/** Full-width, flat entity list with a count and an optional header action area. */
export function EntityList({
  title,
  eyebrow,
  items,
  isLoading,
  error,
  actions,
  contentBeforeList,
  linkTo,
  itemLabel = (item) => (item.name as string) ?? `#${item.id}`,
  itemMeta = (item) => `ID ${String(item.id)}`,
  itemDescription,
  itemDetails,
  onEdit,
  onDelete,
  emptyTitle = 'Brak elementów',
  emptyDescription = 'Dodaj pierwszy element, aby rozpocząć pracę.',
}: EntityListProps) {
  const entries = useMemo(() => items ?? [], [items])

  return (
    <section className="w-full space-y-8">
      <header className="flex flex-wrap items-end justify-between gap-4 pb-2">
        <div>
          {eyebrow && (
            <p className="mb-1 text-xs font-semibold tracking-[0.16em] text-muted-foreground uppercase">
              {eyebrow}
            </p>
          )}
          <div className="flex items-baseline gap-3">
            <h1 className="text-3xl font-semibold tracking-tight">{title}</h1>
            <span className="font-mono text-sm text-muted-foreground">{entries.length}</span>
          </div>
        </div>
        {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
      </header>

      {contentBeforeList}

      {isLoading && <p className="bg-muted/30 px-4 py-6 text-sm text-muted-foreground">Ładowanie…</p>}
      {Boolean(error) && (
        <p className="bg-destructive/5 px-4 py-6 text-sm text-destructive">
          Nie udało się pobrać danych.
        </p>
      )}
      {!isLoading && !error && entries.length === 0 && (
        <div className="bg-muted/25 py-12 text-center">
          <p className="font-medium">{emptyTitle}</p>
          <p className="mt-1 text-sm text-muted-foreground">{emptyDescription}</p>
        </div>
      )}

      {entries.length > 0 && (
        <div className="space-y-2">
          {entries.map((item, index) => (
            <article
              key={item.id}
              className="group grid grid-cols-[3.5rem_minmax(0,1fr)_auto] items-center gap-4 bg-muted/25 px-4 py-5 transition-colors hover:bg-muted/55"
            >
              <span className="font-mono text-xs text-muted-foreground">
                {String(index + 1).padStart(2, '0')}
              </span>
              {linkTo ? <Link to={linkTo(item)} className="min-w-0 py-1">
                <span className="line-clamp-2 text-base font-medium leading-6 group-hover:underline">
                  {itemLabel(item)}
                </span>
                {itemDescription?.(item) && (
                  <p className="mt-2 text-sm leading-6 whitespace-pre-wrap text-muted-foreground">
                    {itemDescription(item)}
                  </p>
                )}
                {itemDetails?.(item) && (
                  <div className="mt-3 bg-background/70 px-3 py-2 text-sm leading-6">
                    {itemDetails(item)}
                  </div>
                )}
                <span className="mt-1 block font-mono text-xs text-muted-foreground">
                  {itemMeta(item)}
                </span>
              </Link> : <div className="min-w-0 py-1">
                <span className="line-clamp-2 text-base font-medium leading-6">{itemLabel(item)}</span>
                {itemDescription?.(item) && (
                  <p className="mt-2 text-sm leading-6 whitespace-pre-wrap text-muted-foreground">
                    {itemDescription(item)}
                  </p>
                )}
                {itemDetails?.(item) && (
                  <div className="mt-3 bg-background/70 px-3 py-2 text-sm leading-6">
                    {itemDetails(item)}
                  </div>
                )}
                <span className="mt-1 block font-mono text-xs text-muted-foreground">{itemMeta(item)}</span>
              </div>}
              <div className="flex items-center gap-1">
                {linkTo && (
                  <Button nativeButton={false} render={<Link to={linkTo(item)} aria-label={`Otwórz ${title}`} />} variant="ghost" size="icon" className="rounded-none">
                    <ArrowUpRight />
                  </Button>
                )}
                {onEdit && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="rounded-none text-muted-foreground hover:text-foreground"
                    aria-label={`Edytuj ${title}`}
                    onClick={() => onEdit(item)}
                  >
                    <Pencil />
                  </Button>
                )}
                {onDelete && (
                  <Button
                    variant="ghost"
                    size="icon"
                    className="rounded-none text-muted-foreground hover:text-destructive"
                    aria-label={`Usuń ${title}`}
                    onClick={() => {
                      if (window.confirm('Czy na pewno usunąć ten element?')) onDelete(item)
                    }}
                  >
                    <Trash2 />
                  </Button>
                )}
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  )
}
