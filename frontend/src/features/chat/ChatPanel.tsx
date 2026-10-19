import { useCallback, useEffect, useLayoutEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import { ArrowLeft, ArrowUp, Check, ChevronDown, ChevronRight, Copy, GitBranch, NotebookPen, Pencil, Plus, RefreshCw, Trash2, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { useConfirm } from '@/components/ConfirmDialog'
import { ResourceContextSelector } from '@/features/resources/ResourceContextSelector'
import { ResourcePathPicker } from '@/features/resources/ResourcePathPicker'
import type { ResourceContextRequest } from '@/features/resources/resourceContextApi'
import { useCreateNoteMutation } from '@/features/notes/notesApi'
import {
  toChatContext, toResourceRequest,
  useCreateConversationMutation, useDeleteConversationMutation, useGetConversationQuery,
  useGetConversationContextQuery,
  useListConversationsQuery, useSendMessageMutation, useUpdateConversationMutation,
  useDeleteMessageMutation, useEditMessageMutation, useForkFromMessageMutation, useRegenerateMessageMutation,
  useUpdateMessageMutation, type ChatContext, type ChatConversation, type ChatMessage,
} from './chatApi'
import { useActiveChatConversation } from './ChatPanelTitle'

type View = { kind: 'list' } | { kind: 'new' } | { kind: 'conversation'; id: number }

const rootNames: Record<ChatContext['type'], string> = {
  offer_raw: 'Surowa oferta',
  offer_source: 'Źródło oferty',
  offer_profile: 'Profil oferty',
}

const conversationTitle = (conversation: Pick<ChatConversation, 'title'>) => conversation.title || 'Nowa rozmowa'

/** Rough estimate, the same ratio the backend uses to fit the history. */
const CHARS_PER_TOKEN = 3
const COMPOSER_MAX_HEIGHT = 200

const includeNames: Record<ChatContext['include'][number], string> = {
  offer_raw: 'Surowa oferta',
  offer_source: 'Źródło oferty',
  target_audiences: 'Grupy docelowe',
  marketing_angle: 'Marketing angles',
  ad_concept: 'Ad concepts',
  creative_plan: 'Creative plans',
  ugc_creative: 'UGC',
  ad_copy: 'Ad copy',
  brand_style: 'Brand styles',
  analysis: 'Analizy',
  checklist: 'Checklisty',
  page_blueprint: 'Page blueprints',
  page: 'Pages',
  note: 'Notatki',
}

function contextItems(context: ChatContext) {
  const counts: Partial<Record<ChatContext['include'][number], number>> = {
    target_audiences: context.target_audience_ids.length,
    marketing_angle: context.marketing_angle_ids.length,
    ad_concept: context.ad_concept_ids.length,
    creative_plan: context.creative_plan_ids.length,
    ugc_creative: context.ugc_creative_ids.length,
    ad_copy: context.ad_copy_ids.length,
    brand_style: context.brand_style_ids?.length ?? 0,
    analysis: context.analysis_ids?.length ?? 0,
    checklist: context.checklist_ids?.length ?? 0,
    page_blueprint: context.page_blueprint_ids?.length ?? 0,
    page: context.page_ids?.length ?? 0,
    note: context.note_ids?.length ?? 0,
  }
  const sourceIncluded = context.type === 'offer_source' || context.include.includes('offer_source')
  return [
    `${rootNames[context.type]} #${context.id}`,
    ...context.include.map((item) => counts[item] ? `${includeNames[item]} (${counts[item]})` : includeNames[item]),
    ...(sourceIncluded && context.include_offer_facts ? ['Zatwierdzone fakty'] : []),
    ...(context.type === 'offer_profile' && context.include_additional_contexts ? ['Dodatkowe informacje'] : []),
  ]
}

function contextSummary(context: ChatContext) {
  const items = contextItems(context)
  return items.length > 1 ? `${items[0]} · ${items.length - 1} powiązanych` : items[0]
}

export function ChatPanel() {
  const [view, setView] = useState<View>({ kind: 'list' })
  if (view.kind === 'new') return <NewConversation onBack={() => setView({ kind: 'list' })} onCreated={(id) => setView({ kind: 'conversation', id })} />
  if (view.kind === 'conversation') return <Conversation key={view.id} id={view.id} onBack={() => setView({ kind: 'list' })} onOpen={(id) => setView({ kind: 'conversation', id })} />
  return <ConversationList onNew={() => setView({ kind: 'new' })} onOpen={(id) => setView({ kind: 'conversation', id })} />
}

/** Inline title editing: Enter saves, Escape cancels. */
function TitleEditor({ conversation, onDone, className }: { conversation: ChatConversation; onDone: () => void; className?: string }) {
  const [title, setTitle] = useState(conversation.title)
  const [update, updateState] = useUpdateConversationMutation()
  const [error, setError] = useState(false)
  const save = async () => {
    const next = title.trim()
    if (!next || next === conversation.title) { onDone(); return }
    try { await update({ id: conversation.id, title: next }).unwrap(); onDone() }
    catch { setError(true) }
  }
  return <form className={cn('flex min-w-0 flex-1 items-center gap-1', className)} onSubmit={(event) => { event.preventDefault(); void save() }} onClick={(event) => event.stopPropagation()}>
    <Input autoFocus value={title} maxLength={255} placeholder="Nazwa rozmowy" aria-invalid={error || undefined}
      className="h-8" onChange={(event) => { setTitle(event.target.value); setError(false) }}
      onKeyDown={(event) => { if (event.key === 'Escape') { event.preventDefault(); onDone() } }} />
    <Button type="submit" variant="ghost" size="icon-sm" disabled={updateState.isLoading} aria-label="Zapisz nazwę" title="Zapisz nazwę"><Check /></Button>
    <Button type="button" variant="ghost" size="icon-sm" onClick={onDone} aria-label="Anuluj" title="Anuluj"><X /></Button>
  </form>
}

function ConversationList({ onNew, onOpen }: { onNew: () => void; onOpen: (id: number) => void }) {
  const { data, isLoading, error } = useListConversationsQuery()
  const [remove, removeState] = useDeleteConversationMutation()
  const [renamingId, setRenamingId] = useState<number | null>(null)
  const [actionError, setActionError] = useState('')
  const [confirm, confirmDialog] = useConfirm()
  const deleteConversation = async (conversation: ChatConversation) => {
    if (!await confirm({ title: 'Usunąć rozmowę?', description: `Rozmowa „${conversationTitle(conversation)}” zostanie trwale usunięta razem z wiadomościami.`, confirmLabel: 'Usuń', destructive: true })) return
    setActionError('')
    try { await remove(conversation.id).unwrap() }
    catch { setActionError('Nie udało się usunąć rozmowy.') }
  }
  return <div className="space-y-4 text-sm">
    {confirmDialog}
    <Button type="button" variant="outline" className="w-full justify-start" onClick={onNew}><Plus />Nowa rozmowa</Button>
    {actionError && <p role="alert" className="text-destructive">{actionError}</p>}
    {isLoading ? <p className="text-muted-foreground">Wczytywanie rozmów…</p>
      : error ? <p role="alert" className="text-destructive">Nie udało się pobrać rozmów.</p>
        : !data?.length ? <p className="rounded-md border border-dashed p-6 text-muted-foreground">Brak rozmów. Zacznij nową, wybierając zasoby.</p>
          : <ul className="space-y-1">{data.map((conversation) => <li key={conversation.id}
            className="group flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 hover:bg-accent"
            onClick={() => renamingId !== conversation.id && onOpen(conversation.id)}>
            {renamingId === conversation.id ? <TitleEditor conversation={conversation} onDone={() => setRenamingId(null)} /> : <>
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{conversationTitle(conversation)}</p>
                <p className="truncate text-xs text-muted-foreground">{contextSummary(conversation.context)} · {new Date(conversation.updated_at).toLocaleString()}</p>
              </div>
              <div className="flex shrink-0 gap-1 opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100" onClick={(event) => event.stopPropagation()}>
                <Button type="button" variant="ghost" size="icon-sm" onClick={() => setRenamingId(conversation.id)} aria-label="Zmień nazwę" title="Zmień nazwę"><Pencil /></Button>
                <Button type="button" variant="ghost" size="icon-sm" disabled={removeState.isLoading} onClick={() => void deleteConversation(conversation)} aria-label="Usuń rozmowę" title="Usuń rozmowę"><Trash2 /></Button>
              </div>
            </>}
          </li>)}</ul>}
  </div>
}

function NewConversation({ onBack, onCreated }: { onBack: () => void; onCreated: (id: number) => void }) {
  const [root, setRoot] = useState<ResourceContextRequest | null>(null)
  const [request, setRequest] = useState<ResourceContextRequest | null>(null)
  const [isReady, setIsReady] = useState(false)
  const [create, createState] = useCreateConversationMutation()
  const [error, setError] = useState('')
  const onSelectionChange = useCallback((next: ResourceContextRequest, ready: boolean) => { setRequest(next); setIsReady(ready) }, [])
  const onRootChange = useCallback((next: ResourceContextRequest | null) => { setRoot(next); setRequest(next) }, [])
  const start = async () => {
    if (!request) return
    setError('')
    try { onCreated((await create({ context: toChatContext(request) }).unwrap()).id) }
    catch { setError('Nie udało się utworzyć rozmowy. Sprawdź wybrane zasoby.') }
  }
  return <div className="space-y-5 pb-4 text-sm">
    <Button type="button" variant="ghost" size="sm" onClick={onBack}><ArrowLeft />Rozmowy</Button>
    <ResourcePathPicker onChange={onRootChange} />
    {root ? <div className="rounded-md border p-4">
      <h2 className="mb-4 font-semibold">Dane dla AI</h2>
      <ResourceContextSelector key={`${root.type}:${root.id}`} initialRequest={root} onChange={onSelectionChange} />
    </div> : <p className="rounded-md border border-dashed p-6 text-muted-foreground">Wybierz surową ofertę, aby wskazać dane do rozmowy.</p>}
    {error && <p role="alert" className="text-destructive">{error}</p>}
    <Button type="button" disabled={!request || !isReady || createState.isLoading} onClick={() => void start()}>{createState.isLoading ? 'Tworzenie…' : 'Rozpocznij rozmowę'}</Button>
  </div>
}

type Busy = { kind: 'regenerate'; messageId: number } | { kind: 'edit'; messageId: number; content: string } | { kind: 'update'; messageId: number }
type MessageEdit = { messageId: number; content: string; mode: 'update' | 'regenerate' }

const bubbleClass = 'max-w-[85%] whitespace-pre-wrap break-words border bg-muted px-3 py-2'
const actionsClass = 'mt-1 flex gap-1 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100 focus-within:opacity-100'

function Conversation({ id, onBack, onOpen }: { id: number; onBack: () => void; onOpen: (id: number) => void }) {
  const { data: conversation, isLoading, error } = useGetConversationQuery(id)
  const [send, sendState] = useSendMessageMutation()
  const [regenerate] = useRegenerateMessageMutation()
  const [editMessage] = useEditMessageMutation()
  const [updateMessage] = useUpdateMessageMutation()
  const [deleteMessage] = useDeleteMessageMutation()
  const [fork, forkState] = useForkFromMessageMutation()
  const [createNote] = useCreateNoteMutation()
  const [draft, setDraft] = useState('')
  const [pending, setPending] = useState<string | null>(null)
  const [busy, setBusy] = useState<Busy | null>(null)
  const [editing, setEditing] = useState<MessageEdit | null>(null)
  const [sendError, setSendError] = useState('')
  const [notice, setNotice] = useState('')
  const [renaming, setRenaming] = useState(false)
  const [confirm, confirmDialog] = useConfirm()
  const bottomRef = useRef<HTMLDivElement>(null)
  const composerRef = useRef<HTMLTextAreaElement>(null)
  const messages = conversation?.messages ?? []
  const isWorking = sendState.isLoading || busy !== null
  // While regenerating or editing, hide what will be replaced so the view matches the result.
  const visibleMessages = busy && busy.kind !== 'update' ? messages.filter((message) => message.id < busy.messageId) : messages
  useActiveChatConversation(id)

  useEffect(() => { bottomRef.current?.scrollIntoView({ block: 'end' }) }, [visibleMessages.length, pending, busy])
  useLayoutEffect(() => {
    const element = composerRef.current
    if (!element) return
    element.style.height = 'auto'
    element.style.height = `${Math.min(element.scrollHeight, COMPOSER_MAX_HEIGHT)}px`
  }, [draft])
  useEffect(() => {
    if (!notice) return
    const timeout = window.setTimeout(() => setNotice(''), 2500)
    return () => window.clearTimeout(timeout)
  }, [notice])

  const submit = async (event?: FormEvent) => {
    event?.preventDefault()
    const content = draft.trim()
    if (!content || isWorking) return
    setSendError('')
    setPending(content)
    setDraft('')
    try { await send({ id, content }).unwrap() }
    catch {
      setDraft(content)
      setSendError('Nie udało się uzyskać odpowiedzi. Wiadomość nie została zapisana — spróbuj ponownie.')
    } finally { setPending(null) }
  }
  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void submit() }
  }
  const runBusy = async (next: Busy, action: () => Promise<unknown>, failure: string) => {
    setSendError('')
    setBusy(next)
    try { await action() }
    catch { setSendError(failure) }
    finally { setBusy(null) }
  }
  const regenerateAnswer = (messageId: number) => void runBusy(
    { kind: 'regenerate', messageId },
    () => regenerate({ messageId, conversationId: id }).unwrap(),
    'Nie udało się wygenerować nowej odpowiedzi. Poprzednia odpowiedź została zachowana.',
  )
  const saveEdit = async () => {
    if (!editing) return
    const content = editing.content.trim()
    if (!content) return
    if (editing.mode === 'update') {
      setSendError('')
      setBusy({ kind: 'update', messageId: editing.messageId })
      try {
        await updateMessage({ messageId: editing.messageId, conversationId: id, content }).unwrap()
        setEditing(null)
      } catch { setSendError('Nie udało się zapisać zmiany wiadomości.') }
      finally { setBusy(null) }
    } else {
      setEditing(null)
      void runBusy(
        { kind: 'edit', messageId: editing.messageId, content },
        () => editMessage({ messageId: editing.messageId, conversationId: id, content }).unwrap(),
        'Nie udało się wysłać zmienionej wiadomości. Rozmowa pozostała bez zmian.',
      )
    }
  }
  const removeMessage = async (messageId: number) => {
    if (!await confirm({ title: 'Usunąć wiadomość?', description: 'Wiadomość zostanie trwale usunięta z tej rozmowy.', confirmLabel: 'Usuń', destructive: true })) return
    try { await deleteMessage({ messageId, conversationId: id }).unwrap() }
    catch { setNotice('Nie udało się usunąć wiadomości.') }
  }
  const forkFrom = async (messageId: number) => {
    let created
    try { created = await fork({ messageId }).unwrap() }
    catch { setNotice('Nie udało się utworzyć forka rozmowy.'); return }
    const go = await confirm({
      title: 'Utworzono fork rozmowy',
      description: `Nowa rozmowa „${conversationTitle(created)}” zawiera historię do wybranej wiadomości. Przejść do niej teraz?`,
      confirmLabel: 'Przejdź do forka', cancelLabel: 'Zostań tutaj',
    })
    if (go) onOpen(created.id)
    else setNotice('Fork zapisano na liście rozmów.')
  }
  const copy = async (content: string) => {
    try { await navigator.clipboard.writeText(content); setNotice('Skopiowano.') }
    catch { setNotice('Nie udało się skopiować.') }
  }
  const saveAsNote = async (content: string) => {
    try { await createNote({ title: `${conversationTitle(conversation ?? { title: '' })} — odpowiedź AI`.slice(0, 255), content }).unwrap(); setNotice('Zapisano jako notatkę.') }
    catch { setNotice('Nie udało się zapisać notatki.') }
  }
  const commonActions = (messageId: number, content: string) => <>
    <Button type="button" variant="ghost" size="icon-sm" onClick={() => void copy(content)} aria-label="Kopiuj" title="Kopiuj"><Copy /></Button>
    <Button type="button" variant="ghost" size="icon-sm" disabled={forkState.isLoading} onClick={() => void forkFrom(messageId)} aria-label="Fork od tej wiadomości" title="Fork — nowa rozmowa z historią do tej wiadomości"><GitBranch /></Button>
    <Button type="button" variant="ghost" size="icon-sm" disabled={isWorking} onClick={() => void removeMessage(messageId)} aria-label="Usuń wiadomość" title="Usuń wiadomość"><Trash2 /></Button>
  </>

  const messageEditor = (message: ChatMessage) => editing && <div className="w-full space-y-2 border border-input bg-muted/40 p-3">
    <textarea autoFocus value={editing.content} rows={3} maxLength={20000} aria-label="Edytuj wiadomość"
      onChange={(event) => setEditing({ ...editing, content: event.target.value })}
      onKeyDown={(event) => {
        if (event.key === 'Escape') setEditing(null)
        if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); void saveEdit() }
      }}
      className="w-full resize-y bg-transparent px-1 outline-none" />
    <div className="flex justify-end gap-2">
      <Button type="button" variant="ghost" size="sm" onClick={() => setEditing(null)}>Anuluj</Button>
      <Button type="button" size="sm" disabled={!editing.content.trim() || isWorking} onClick={() => void saveEdit()}>{editing.mode === 'update' ? 'Zapisz' : 'Wyślij'}</Button>
    </div>
    {editing.mode === 'regenerate' && message.role === 'user' && <p className="px-1 text-xs text-muted-foreground">Wiadomości po tej zostaną zastąpione nową odpowiedzią.</p>}
  </div>

  if (isLoading) return <p className="text-sm text-muted-foreground">Wczytywanie rozmowy…</p>
  if (error || !conversation) return <div className="space-y-3 text-sm">
    <Button type="button" variant="ghost" size="sm" onClick={onBack}><ArrowLeft />Rozmowy</Button>
    <p role="alert" className="text-destructive">Nie udało się wczytać rozmowy.</p>
  </div>

  return <div className="flex h-full min-h-0 flex-col text-sm">
    {confirmDialog}
    <div className="flex shrink-0 items-center gap-1 border-b pb-2">
      <Button type="button" variant="ghost" size="icon-sm" onClick={onBack} aria-label="Wróć do rozmów" title="Wróć do rozmów"><ArrowLeft /></Button>
      {renaming ? <TitleEditor conversation={conversation} onDone={() => setRenaming(false)} /> : <>
        <p className="min-w-0 flex-1 truncate font-medium">{conversationTitle(conversation)}</p>
        <Button type="button" variant="ghost" size="icon-sm" onClick={() => setRenaming(true)} aria-label="Zmień nazwę" title="Zmień nazwę"><Pencil /></Button>
      </>}
    </div>
    <div className="mx-auto w-full max-w-3xl shrink-0 border-b py-2">
      <ContextInfo conversation={conversation} />
    </div>

    <div className="min-h-0 flex-1 overflow-y-auto">
      <div className="mx-auto max-w-3xl space-y-5 py-4">
        {!visibleMessages.length && !pending && !busy && <div className="py-16 text-center">
          <p className="text-lg font-medium">W czym mogę pomóc?</p>
          <p className="mt-1 text-muted-foreground">AI odpowie na podstawie załadowanego kontekstu.</p>
        </div>}
        {visibleMessages.map((message) => message.role === 'user'
          ? <div key={message.id} className="group flex flex-col items-end">
            {editing?.messageId === message.id ? messageEditor(message) : <>
              <p className={bubbleClass}>{message.content}</p>
              <div className={actionsClass}>
                <Button type="button" variant="ghost" size="icon-sm" disabled={isWorking} onClick={() => setEditing({ messageId: message.id, content: message.content, mode: 'update' })} aria-label="Edytuj wiadomość" title="Edytuj wiadomość"><Pencil /></Button>
                <Button type="button" variant="ghost" size="icon-sm" disabled={isWorking} onClick={() => setEditing({ messageId: message.id, content: message.content, mode: 'regenerate' })} aria-label="Edytuj i wygeneruj odpowiedź ponownie" title="Edytuj i wygeneruj odpowiedź ponownie"><RefreshCw /></Button>
                {commonActions(message.id, message.content)}
              </div>
            </>}
          </div>
          : <div key={message.id} className="group">
            {editing?.messageId === message.id ? messageEditor(message) : <p className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</p>}
            {editing?.messageId !== message.id && <div className={actionsClass}>
              <Button type="button" variant="ghost" size="icon-sm" disabled={isWorking} onClick={() => setEditing({ messageId: message.id, content: message.content, mode: 'update' })} aria-label="Edytuj odpowiedź AI" title="Edytuj odpowiedź AI"><Pencil /></Button>
              <Button type="button" variant="ghost" size="icon-sm" onClick={() => void saveAsNote(message.content)} aria-label="Zapisz jako notatkę" title="Zapisz jako notatkę"><NotebookPen /></Button>
              <Button type="button" variant="ghost" size="icon-sm" disabled={isWorking} onClick={() => regenerateAnswer(message.id)} aria-label="Wygeneruj ponownie" title="Wygeneruj odpowiedź ponownie"><RefreshCw /></Button>
              {commonActions(message.id, message.content)}
              {message.prompt_tokens != null && <span className="self-center pl-1 text-xs tabular-nums" title="Dokładna liczba tokenów podana przez model: prompt → odpowiedź">{message.prompt_tokens.toLocaleString('pl-PL')} → {(message.completion_tokens ?? 0).toLocaleString('pl-PL')} tok.</span>}
            </div>}
          </div>)}
        {busy?.kind === 'edit' && <div className="flex justify-end"><p className={bubbleClass}>{busy.content}</p></div>}
        {pending && <div className="flex justify-end"><p className={bubbleClass}>{pending}</p></div>}
        {(pending || (busy && busy.kind !== 'update')) && <p className="animate-pulse text-muted-foreground">AI pisze…</p>}
        <div ref={bottomRef} />
      </div>
    </div>

    <div className="mx-auto w-full max-w-3xl shrink-0 space-y-2 pt-2">
      {notice && <p className="text-center text-xs text-muted-foreground" role="status">{notice}</p>}
      {sendError && <p role="alert" className="text-destructive">{sendError}</p>}
      {/* The border sits on the inner div: index.css removes borders from every form. */}
      <form onSubmit={(event) => void submit(event)}>
        <div className="flex items-end gap-2 border border-foreground/25 bg-background px-3 py-2 shadow-sm focus-within:border-foreground/50">
        <textarea ref={composerRef} value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={onKeyDown}
          rows={1} maxLength={20000} placeholder="Napisz wiadomość…" disabled={isWorking} aria-label="Wiadomość"
          className="max-h-[200px] min-h-6 flex-1 resize-none bg-transparent py-1.5 outline-none placeholder:text-muted-foreground" />
        <Button type="submit" size="icon-sm" className="mb-0.5" disabled={!draft.trim() || isWorking} aria-label="Wyślij" title="Wyślij"><ArrowUp /></Button>
        </div>
      </form>
      <p className="text-center text-xs text-muted-foreground">Enter — wyślij · Shift+Enter — nowa linia</p>
    </div>
  </div>
}

/** What the model currently receives: the selected resources and, on demand, the exact composed text. */
function ContextInfo({ conversation }: { conversation: ChatConversation }) {
  const { context } = conversation
  const [open, setOpen] = useState(false)
  const [mode, setMode] = useState<'text' | 'edit'>('text')
  const { data: text, isFetching, error } = useGetConversationContextQuery(conversation.id, { skip: !open || mode !== 'text', refetchOnMountOrArgChange: true })
  return <div className="border text-xs">
    <button type="button" className="flex w-full cursor-pointer items-center gap-2 px-3 py-2 text-left" onClick={() => setOpen((value) => !value)} aria-expanded={open}>
      {open ? <ChevronDown className="size-4 shrink-0" /> : <ChevronRight className="size-4 shrink-0" />}
      <span className="font-medium">Załadowany kontekst</span>
      <span className="min-w-0 flex-1 truncate text-muted-foreground">{contextSummary(context)}</span>
    </button>
    {open && <div className="max-h-[35vh] space-y-3 overflow-y-auto border-t px-3 py-3">
      <div className="flex flex-wrap gap-1">
        {contextItems(context).map((item) => <span key={item} className="border bg-muted/40 px-2 py-0.5">{item}</span>)}
      </div>
      <div className="flex gap-1">
        <Button type="button" size="sm" variant={mode === 'text' ? 'secondary' : 'ghost'} onClick={() => setMode('text')}>Treść</Button>
        <Button type="button" size="sm" variant={mode === 'edit' ? 'secondary' : 'ghost'} onClick={() => setMode('edit')}>Zmień dane</Button>
      </div>
      {mode === 'edit' ? <ContextEditor conversation={conversation} onSaved={() => setMode('text')} />
        : isFetching ? <p className="text-muted-foreground">Składanie kontekstu…</p>
          : error || text === undefined ? <p role="alert" className="text-destructive">Nie udało się złożyć kontekstu.</p>
            : <>
              <p className="text-muted-foreground">{text.length.toLocaleString()} znaków · ok. {Math.ceil(text.length / CHARS_PER_TOKEN).toLocaleString()} tokenów — dokładnie to otrzymuje AI przy następnej wiadomości.</p>
              <pre className="whitespace-pre-wrap break-words rounded-md bg-muted/40 p-2">{text}</pre>
            </>}
    </div>}
  </div>
}

function ContextEditor({ conversation, onSaved }: { conversation: ChatConversation; onSaved: () => void }) {
  const initialRequest = toResourceRequest(conversation.context)
  const [request, setRequest] = useState<ResourceContextRequest>(initialRequest)
  const [isReady, setIsReady] = useState(false)
  const [update, updateState] = useUpdateConversationMutation()
  const [error, setError] = useState('')
  const onSelectionChange = useCallback((next: ResourceContextRequest, ready: boolean) => { setRequest(next); setIsReady(ready) }, [])
  const save = async () => {
    setError('')
    try { await update({ id: conversation.id, context: toChatContext(request) }).unwrap(); onSaved() }
    catch { setError('Nie udało się zapisać wyboru danych.') }
  }
  return <div className="space-y-3">
    <p className="text-muted-foreground">Zmiana danych obowiązuje od następnej wiadomości.</p>
    <ResourceContextSelector initialRequest={initialRequest} onChange={onSelectionChange} />
    {error && <p role="alert" className="text-destructive">{error}</p>}
    <Button type="button" size="sm" disabled={!isReady || updateState.isLoading} onClick={() => void save()}>Zapisz wybór danych</Button>
  </div>
}
