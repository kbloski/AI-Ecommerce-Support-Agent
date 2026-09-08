import { useEffect, useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { Menu } from 'lucide-react'
import { AppSidebar } from '@/components/AppSidebar'
import { AppContextSidebar } from '@/components/AppContextSidebar'
import { Toaster } from '@/components/ui/sonner'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { SidePanelProvider } from '@/components/SidePanel'

/** Root layout: primary sidebar, contextual sidebar, routed page content. */
export function AppShell() {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const { pathname } = useLocation()

  useEffect(() => {
    setMobileNavOpen(false)
  }, [pathname])

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

        <AppSidebar />
        <AppContextSidebar />
        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
        <Toaster position="bottom-right" richColors closeButton />
      </div>
    </SidePanelProvider>
  )
}
