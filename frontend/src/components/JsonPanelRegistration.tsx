import { useEffect, useMemo } from 'react'
import { EntityViewer } from '@/components/EntityViewer'
import { useSidePanel } from '@/lib/sidePanel'

interface JsonPanelRegistrationProps {
  data: unknown
  title: string
}

/** Registers JSON for the current view in the contextual Tools menu. */
export function JsonPanelRegistration({ data, title }: JsonPanelRegistrationProps) {
  const { setContextualPanel } = useSidePanel()
  const panel = useMemo(
    () => ({ title, content: <EntityViewer data={data} /> }),
    [data, title],
  )

  useEffect(() => {
    setContextualPanel(panel)
    return () => setContextualPanel(null)
  }, [panel, setContextualPanel])

  return null
}
