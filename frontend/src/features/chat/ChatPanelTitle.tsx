import { useEffect, useRef, useState, useSyncExternalStore } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useGetConversationUsageQuery, type ChatUsage } from './chatApi'

// The side panel renders its title outside the chat content, so the open conversation is shared here.
let activeConversationId: number | null = null
const listeners = new Set<() => void>()
const subscribe = (listener: () => void) => { listeners.add(listener); return () => { listeners.delete(listener) } }

/** Marks the conversation as open so the panel title can show its context usage. */
export function useActiveChatConversation(id: number) {
  useEffect(() => {
    activeConversationId = id
    listeners.forEach((listener) => listener())
    return () => {
      activeConversationId = null
      listeners.forEach((listener) => listener())
    }
  }, [id])
}

const compact = new Intl.NumberFormat('pl-PL', { notation: 'compact', maximumFractionDigits: 1 })
const exact = (value: number) => value.toLocaleString('pl-PL')

export function ChatPanelTitle() {
  const id = useSyncExternalStore(subscribe, () => activeConversationId)
  const [expanded, setExpanded] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!expanded) return
    const closeOutside = (event: PointerEvent) => { if (!rootRef.current?.contains(event.target as Node)) setExpanded(false) }
    const closeOnEscape = (event: KeyboardEvent) => { if (event.key === 'Escape') { event.stopPropagation(); setExpanded(false) } }
    document.addEventListener('pointerdown', closeOutside)
    document.addEventListener('keydown', closeOnEscape, true)
    return () => {
      document.removeEventListener('pointerdown', closeOutside)
      document.removeEventListener('keydown', closeOnEscape, true)
    }
  }, [expanded])
  const { data: usage, isFetching } = useGetConversationUsageQuery(id ?? 0, { skip: id === null, refetchOnMountOrArgChange: true })
  const available = usage ? usage.limit_tokens - usage.answer_reserve_tokens : 0
  const ratio = usage && available > 0 ? usage.used_tokens / available : 0
  const tone = !usage ? '' : usage.too_large || ratio >= 0.9 ? 'border-destructive/50 text-destructive'
    : ratio >= 0.75 ? 'border-amber-500/50 text-amber-600 dark:text-amber-400' : 'text-muted-foreground'

  return <div ref={rootRef} className="relative flex min-w-0 items-center gap-3">
    <span>Chat</span>
    {id !== null && usage && <button type="button" onClick={() => setExpanded((value) => !value)} aria-expanded={expanded}
      className={cn('flex cursor-pointer items-center gap-1 border px-2 py-0.5 text-xs font-normal tabular-nums hover:bg-accent', tone, isFetching && 'opacity-60')}
      title="Kliknij, aby zobaczyć dokładne liczby tokenów">
      {expanded ? <ChevronDown className="size-3" /> : <ChevronRight className="size-3" />}
      Kontekst: ~{compact.format(usage.used_tokens)} / {compact.format(available)} tokenów
    </button>}
    {id !== null && usage && expanded && <div className="absolute left-0 top-full z-50 mt-2 w-[min(30rem,calc(100vw-4rem))] shadow-lg">
      <UsageDetails usage={usage} available={available} />
    </div>}
  </div>
}

function UsageDetails({ usage, available }: { usage: ChatUsage; available: number }) {
  const rows: [string, string][] = [
    ['Dane i instrukcja', `~${exact(usage.context_tokens)}`],
    [`Historia (${usage.messages_in_context} z ${usage.messages_total} wiadomości)`, `~${exact(usage.history_tokens)}`],
    ['Razem przy następnej wiadomości', `~${exact(usage.used_tokens)}`],
    ['Wolne miejsce', `~${exact(Math.max(available - usage.used_tokens, 0))}`],
    ['Limit modelu', `${exact(usage.limit_tokens)} (w tym ${exact(usage.answer_reserve_tokens)} na odpowiedź)`],
  ]
  return <div className="space-y-2 border bg-background p-3 text-xs font-normal">
    {usage.last_prompt_tokens != null && <div>
      <p className="font-medium">Ostatnia odpowiedź — dokładnie wg modelu</p>
      <p className="tabular-nums">Prompt: <strong>{exact(usage.last_prompt_tokens)}</strong> tokenów · odpowiedź: <strong>{exact(usage.last_completion_tokens ?? 0)}</strong> tokenów</p>
    </div>}
    <div>
      <p className="font-medium">Następna wiadomość — szacunek</p>
      <dl className="mt-1 grid grid-cols-[1fr_auto] gap-x-4 gap-y-0.5 tabular-nums">
        {rows.map(([label, value]) => <div key={label} className="contents"><dt className="text-muted-foreground">{label}</dt><dd className="text-right">{value}</dd></div>)}
      </dl>
    </div>
    {usage.messages_in_context < usage.messages_total && <p className="text-amber-600 dark:text-amber-400">Najstarsze wiadomości nie mieszczą się w kontekście i są pomijane.</p>}
    {usage.too_large && <p className="text-destructive">Same dane przekraczają limit modelu — zaznacz mniej zasobów.</p>}
  </div>
}
