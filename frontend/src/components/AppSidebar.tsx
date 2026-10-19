import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Download, Layers, LayoutDashboard, MessageSquare, NotebookPen, Package, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { useSidePanel } from '@/lib/sidePanel'
import { ResourceExportPanel } from '@/features/resources/ResourceExportPanel'
import { ChatPanel } from '@/features/chat/ChatPanel'
import { ChatPanelTitle } from '@/features/chat/ChatPanelTitle'
import { CreateNotePanel } from '@/features/notes/CreateNotePanel'

interface SidebarSection {
  label: string
  to?: string
  icon: typeof Package
  /** Opens this content in the side panel instead of navigating. */
  panel?: () => ReactNode
  /** Custom side panel title; the label is used by default. */
  panelTitle?: () => ReactNode
}

/** Top-level sections the user has access to. Add new entries here as new root-level sections appear. */
const SECTIONS: SidebarSection[] = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Tworzenie oferty', to: '/offers', icon: Package },
  { label: 'Profile ofert', to: '/offer-profiles', icon: Layers },
  { label: 'Notatki', to: '/notes', icon: NotebookPen },
  { label: 'Chat', icon: MessageSquare, panel: () => <ChatPanel />, panelTitle: () => <ChatPanelTitle /> },
  { label: 'Export zasobów', icon: Download, panel: () => <ResourceExportPanel /> },
  { label: 'Ustawienia', to: '/settings', icon: Settings },
]

const navLinkClassName = ({ isActive }: { isActive: boolean }) =>
  cn(
    'flex items-center gap-2 rounded-md px-2 py-2 text-sm',
    isActive
      ? 'bg-accent text-accent-foreground'
      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
  )

/** Primary left-hand navigation, persistent across the whole app. */
interface AppSidebarProps {
  variant?: 'sidebar' | 'mobile'
  collapsed?: boolean
  onToggle?: () => void
  onAction?: () => void
}

export function AppSidebar({ variant = 'sidebar', collapsed = false, onToggle, onAction }: AppSidebarProps) {
  const isCollapsed = variant === 'sidebar' && collapsed
  const { openPanel } = useSidePanel()

  return (
    <aside
      className={cn(
        variant === 'sidebar'
          ? 'relative z-20 hidden shrink-0 flex-col border-r py-4 transition-[width] duration-200 ease-in-out md:flex'
          : 'flex w-full flex-col p-2',
        variant === 'sidebar' && (isCollapsed ? 'w-16 px-2' : 'w-56 px-4'),
      )}
    >
      <div className={cn('mb-4 flex h-8 items-center', isCollapsed ? 'justify-center' : 'justify-between px-2')}>
        {!isCollapsed && <div className="text-sm font-semibold">AIEC SASS</div>}
        {variant === 'sidebar' && (
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            onClick={onToggle}
            aria-label={isCollapsed ? 'Rozwiń główne menu' : 'Zwiń główne menu'}
            title={isCollapsed ? 'Rozwiń główne menu' : 'Zwiń główne menu'}
          >
            {isCollapsed ? <ChevronRight /> : <ChevronLeft />}
          </Button>
        )}
      </div>
      <nav className="space-y-1">
        {SECTIONS.map(({ label, to, icon: Icon, panel, panelTitle }) => label === 'Notatki' ? (
          <div key={label} className="group relative">
            <NavLink
              to="/notes"
              className={(state) => cn(navLinkClassName(state), isCollapsed && 'justify-center px-0')}
              aria-label={isCollapsed ? label : undefined}
              title={isCollapsed ? label : undefined}
              onClick={onAction}
            >
              <Icon className="size-4 shrink-0" />
              {!isCollapsed && label}
            </NavLink>
            <div className={cn(
              'rounded-md border bg-popover p-1 text-popover-foreground shadow-md',
              variant === 'sidebar'
                ? 'absolute top-0 left-full z-30 hidden w-44 group-hover:block group-focus-within:block'
                : 'mt-1 ml-6',
            )}>
              <button type="button" className="block w-full rounded-sm px-2 py-1.5 text-left text-sm hover:bg-accent focus-visible:bg-accent"
                onClick={() => { onAction?.(); openPanel({ title: 'Dodaj notatkę', content: <CreateNotePanel /> }) }}>
                Dodaj notatkę
              </button>
              <NavLink to="/notes" className="block rounded-sm px-2 py-1.5 text-sm hover:bg-accent focus-visible:bg-accent" onClick={onAction}>
                Zobacz wszystkie
              </NavLink>
            </div>
          </div>
        ) : to ? (
          <NavLink
            key={label}
            to={to}
            end={to === '/'}
            className={(state) => cn(navLinkClassName(state), isCollapsed && 'justify-center px-0')}
            aria-label={isCollapsed ? label : undefined}
            title={isCollapsed ? label : undefined}
          >
            <Icon className="size-4 shrink-0" />
            {!isCollapsed && label}
          </NavLink>
        ) : (
          <button key={label} type="button" className={cn(navLinkClassName({ isActive: false }), 'w-full text-left', isCollapsed && 'justify-center px-0')}
            aria-label={isCollapsed ? label : undefined} title={isCollapsed ? label : undefined}
            onClick={() => { onAction?.(); if (panel) openPanel({ title: panelTitle?.() ?? label, content: panel() }) }}>
            <Icon className="size-4 shrink-0" />
            {!isCollapsed && label}
          </button>
        ))}
      </nav>

    </aside>
  )
}
