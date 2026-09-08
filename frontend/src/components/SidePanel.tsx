import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { Sheet, SheetContent } from '@/components/ui/sheet'
import { SidePanelContext, type SidePanelOptions } from '@/lib/sidePanel'

/**
 * A reusable right-side panel. Its content is supplied by the calling view,
 * so it can host JSON, forms, history, previews, or any other React content.
 */
export function SidePanelProvider({ children }: { children: ReactNode }) {
  const [panel, setPanel] = useState<SidePanelOptions | null>(null)
  const [contextualPanel, setContextualPanel] = useState<SidePanelOptions | null>(null)
  const { pathname } = useLocation()

  const openPanel = useCallback((options: SidePanelOptions) => setPanel(options), [])
  const closePanel = useCallback(() => setPanel(null), [])

  useEffect(() => {
    closePanel()
  }, [closePanel, pathname])

  const value = useMemo(
    () => ({ openPanel, closePanel, isOpen: panel !== null, contextualPanel, setContextualPanel }),
    [closePanel, contextualPanel, openPanel, panel],
  )

  return (
    <SidePanelContext.Provider value={value}>
      {children}
      <Sheet open={panel !== null} onOpenChange={(open) => !open && closePanel()}>
        <SheetContent
          side="right"
          className="w-full max-w-none gap-4 p-6 sm:w-[34rem] sm:max-w-[90vw]"
          aria-label={typeof panel?.title === 'string' ? panel.title : 'Panel boczny'}
        >
          {panel && (
            <>
              <div className="min-w-0 pr-8 text-lg font-semibold">{panel.title}</div>
              <div className="min-h-0 flex-1 overflow-auto">{panel.content}</div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </SidePanelContext.Provider>
  )
}
