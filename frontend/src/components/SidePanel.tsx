import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { Sheet, SheetContent } from '@/components/ui/sheet'
import { SidePanelContext, type SidePanelOptions } from '@/lib/sidePanel'
import { useResizablePanel } from '@/lib/useResizablePanel'

/**
 * A reusable right-side panel. Its content is supplied by the calling view,
 * so it can host JSON, forms, history, previews, or any other React content.
 */
export function SidePanelProvider({ children }: { children: ReactNode }) {
  const [panel, setPanel] = useState<SidePanelOptions | null>(null)
  const [contextualPanel, setContextualPanel] = useState<SidePanelOptions | null>(null)
  const { pathname } = useLocation()
  const getPanelMaxWidth = useCallback(() => Math.min(960, window.innerWidth - 32), [])
  const panelSize = useResizablePanel({
    defaultWidth: 544,
    minWidth: 320,
    getMaxWidth: getPanelMaxWidth,
    resizeEdge: 'right',
  })

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
          className="w-full max-w-none gap-4 p-6 sm:max-w-[90vw]"
          style={{ width: panelSize.width, maxWidth: 'calc(100vw - 2rem)' }}
          aria-label={typeof panel?.title === 'string' ? panel.title : 'Panel boczny'}
        >
          <div
            role="separator"
            tabIndex={0}
            aria-orientation="vertical"
            aria-label="Zmień szerokość panelu"
            aria-valuemin={panelSize.minWidth}
            aria-valuemax={panelSize.maxWidth}
            aria-valuenow={panelSize.width}
            className="absolute inset-y-0 -left-1 z-10 hidden w-3 cursor-col-resize touch-none sm:block"
            onPointerDown={panelSize.startResize}
            onPointerMove={panelSize.resize}
            onPointerUp={panelSize.stopResize}
            onPointerCancel={panelSize.stopResize}
            onDoubleClick={panelSize.resetWidth}
            onKeyDown={panelSize.resizeWithKeyboard}
          >
            <div className="mx-auto h-full w-px bg-border opacity-70 transition-all hover:w-0.5 hover:bg-primary hover:opacity-100" />
          </div>
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
