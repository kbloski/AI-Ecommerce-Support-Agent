import { NavLink } from 'react-router-dom'
import { ChevronLeft, ChevronRight, LayoutDashboard, Package, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

interface SidebarSection {
  label: string
  to: string
  icon: typeof Package
}

/** Top-level sections the user has access to. Add new entries here as new root-level sections appear. */
const SECTIONS: SidebarSection[] = [
  { label: 'Dashboard', to: '/', icon: LayoutDashboard },
  { label: 'Oferty', to: '/offers', icon: Package },
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
}

export function AppSidebar({ variant = 'sidebar', collapsed = false, onToggle }: AppSidebarProps) {
  const isCollapsed = variant === 'sidebar' && collapsed

  return (
    <aside
      className={cn(
        variant === 'sidebar'
          ? 'relative hidden shrink-0 flex-col border-r py-4 transition-[width] duration-200 ease-in-out md:flex'
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
        {SECTIONS.map(({ label, to, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={(state) => cn(navLinkClassName(state), isCollapsed && 'justify-center px-0')}
            aria-label={isCollapsed ? label : undefined}
            title={isCollapsed ? label : undefined}
          >
            <Icon className="size-4 shrink-0" />
            {!isCollapsed && label}
          </NavLink>
        ))}
      </nav>

    </aside>
  )
}
