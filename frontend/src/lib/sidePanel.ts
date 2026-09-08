import { createContext, useContext, type ReactNode } from 'react'

export interface SidePanelOptions {
  title: ReactNode
  content: ReactNode
}

export interface SidePanelContextValue {
  openPanel: (options: SidePanelOptions) => void
  closePanel: () => void
  isOpen: boolean
  contextualPanel: SidePanelOptions | null
  setContextualPanel: (options: SidePanelOptions | null) => void
}

export const SidePanelContext = createContext<SidePanelContextValue | null>(null)

export function useSidePanel() {
  const context = useContext(SidePanelContext)

  if (!context) {
    throw new Error('useSidePanel must be used within SidePanelProvider')
  }

  return context
}
