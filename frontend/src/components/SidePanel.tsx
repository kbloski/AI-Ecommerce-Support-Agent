import { useCallback, useEffect, useMemo, useRef, useState, type PointerEvent, type ReactNode } from 'react'
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
  const [panelWidth, setPanelWidth] = useState(544)
  const isResizing = useRef(false)
  const { pathname } = useLocation()

  const openPanel = useCallback((options: SidePanelOptions) => setPanel(options), [])
  const closePanel = useCallback(() => setPanel(null), [])

  useEffect(() => {
    closePanel()
  }, [closePanel, pathname])

  const startResize = (event: PointerEvent<HTMLDivElement>) => {
    event.preventDefault()
    event.stopPropagation()
    isResizing.current = true
    event.currentTarget.setPointerCapture(event.pointerId)
  }

  const resize = (event: PointerEvent<HTMLDivElement>) => {
    if (!isResizing.current) return

    const minWidth = 320
    const maxWidth = Math.min(960, window.innerWidth - 32)
    setPanelWidth(Math.min(maxWidth, Math.max(minWidth, window.innerWidth - event.clientX)))
  }

  const stopResize = (event: PointerEvent<HTMLDivElement>) => {
    isResizing.current = false
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId)
    }
  }

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
          style={{ width: panelWidth, maxWidth: 'calc(100vw - 2rem)' }}
          aria-label={typeof panel?.title === 'string' ? panel.title : 'Panel boczny'}
        >
          <div
            role="separator"
            aria-orientation="vertical"
            aria-label="Zmień szerokość panelu"
            className="absolute inset-y-0 -left-1 z-10 hidden w-3 cursor-col-resize touch-none sm:block"
            onPointerDown={startResize}
            onPointerMove={resize}
            onPointerUp={stopResize}
            onPointerCancel={stopResize}
            onDoubleClick={() => setPanelWidth(544)}
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
