import { useCallback, useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Menu } from 'lucide-react'
import { AppSidebar } from '@/components/AppSidebar'
import { AppContextSidebar } from '@/components/AppContextSidebar'
import { Toaster } from '@/components/ui/sonner'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { SidePanelProvider } from '@/components/SidePanel'
import { useResizablePanel } from '@/lib/useResizablePanel'

const PRIMARY_SIDEBAR_STORAGE_KEY = 'aiec:layout:primary-sidebar-collapsed'
const CONTEXT_SIDEBAR_STORAGE_KEY = 'aiec:layout:context-sidebar-width'

/** Root layout: primary sidebar, contextual sidebar, routed page content. */
export function AppShell() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const [primarySidebarCollapsed, setPrimarySidebarCollapsed] = useState(() =>
    window.localStorage.getItem(PRIMARY_SIDEBAR_STORAGE_KEY) !== 'false',
  )
  const { pathname } = useLocation()
  const getContextSidebarMaxWidth = useCallback(
    () => Math.min(420, Math.max(200, window.innerWidth - (primarySidebarCollapsed ? 64 : 224) - 480)),
    [primarySidebarCollapsed],
  )
  const contextSidebar = useResizablePanel({
    defaultWidth: 224,
    minWidth: 200,
    getMaxWidth: getContextSidebarMaxWidth,
    resizeEdge: 'left',
    storageKey: CONTEXT_SIDEBAR_STORAGE_KEY,
  })

  useEffect(() => {
    setMobileNavOpen(false)
  }, [pathname])

  useEffect(() => {
    window.localStorage.setItem(PRIMARY_SIDEBAR_STORAGE_KEY, String(primarySidebarCollapsed))
  }, [primarySidebarCollapsed])

  return (
    <SidePanelProvider>
      <div className="flex min-h-svh flex-col md:flex-row">
        <header className="flex items-center border-b p-2 md:hidden">
          <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
            <SheetTrigger
              render={<Button variant="ghost" size="icon" aria-label="Otwórz menu" />}
            >
              <Menu className="size-5" />
            </SheetTrigger>
            <SheetContent>
              <AppSidebar variant="mobile" />
              <div className="my-2 border-t" />
              <AppContextSidebar variant="mobile" />
            </SheetContent>
          </Sheet>
          <span className="ml-2 text-sm font-semibold">AIEC SASS</span>
        </header>

        <AppSidebar
          collapsed={primarySidebarCollapsed}
          onToggle={() => setPrimarySidebarCollapsed((collapsed) => !collapsed)}
        />
        <AppContextSidebar width={contextSidebar.width} resize={contextSidebar} />
        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
        <Toaster position="bottom-right" richColors closeButton />
      </div>
    </SidePanelProvider>
  )
}
