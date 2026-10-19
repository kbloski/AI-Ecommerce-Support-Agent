import { useState } from 'react'
import { ResourceContextExportPanel } from '@/features/resources/ResourceContextExportPanel'
import { ResourcePathPicker } from '@/features/resources/ResourcePathPicker'
import type { ResourceContextRequest } from '@/features/resources/resourceContextApi'

export function ResourceExportPanel() {
  const [request, setRequest] = useState<ResourceContextRequest | null>(null)

  return <div className="w-full min-w-0 space-y-5 pb-4">
    <div>
      <p className="text-sm text-muted-foreground">Wybierz ścieżkę zasobów, zdecyduj co dołączyć, a następnie sprawdź i pobierz kontekst jako plik TXT.</p>
    </div>
    <ResourcePathPicker onChange={setRequest} />
    {request ? <div className="rounded-md border p-4">
      <h2 className="mb-4 font-semibold">Zawartość eksportu</h2>
      <ResourceContextExportPanel key={`${request.type}:${request.id}`} initialRequest={request} />
    </div> : <p className="rounded-md border border-dashed p-6 text-sm text-muted-foreground">Wybierz surową ofertę, aby rozpocząć składanie kontekstu.</p>}
  </div>
}
