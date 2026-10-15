import { useEffect, useMemo, type ReactNode } from 'react'
import { EntityViewer } from '@/components/EntityViewer'
import { useSidePanel } from '@/lib/sidePanel'

interface JsonPanelRegistrationProps {
  data: unknown
  title: string
  content?: ReactNode
}

/** Registers JSON for the current view in the contextual Tools menu. */
export function JsonPanelRegistration({ data, title, content }: JsonPanelRegistrationProps) {
  const { setContextualPanel } = useSidePanel()
  const panel = useMemo(
    () => ({ title, content: content ?? <EntityViewer data={data} /> }),
    [data, title, content],
  )

  useEffect(() => {
    setContextualPanel(panel)
    return () => setContextualPanel(null)
  }, [panel, setContextualPanel])

  return null
}
