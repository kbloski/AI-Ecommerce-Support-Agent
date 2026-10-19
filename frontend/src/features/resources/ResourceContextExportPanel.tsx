import { useCallback, useState } from 'react'
import { Button } from '@/components/ui/button'
import { useLazyDownloadResourceContextQuery, useLazyGetResourceContextQuery } from './resourceContextApi'
import type { ResourceContextRequest } from './resourceContextApi'
import { ResourceContextSelector } from './ResourceContextSelector'
import { downloadTextFile } from '@/lib/downloadTextFile'

export function ResourceContextExportPanel({ initialRequest }: { initialRequest: ResourceContextRequest }) {
  const [request, setRequest] = useState<ResourceContextRequest>(initialRequest)
  const [isReady, setIsReady] = useState(false)
  const [step, setStep] = useState<'select' | 'preview'>('select')
  const [preview, setPreview] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [getContext, { isFetching: isPreviewing }] = useLazyGetResourceContextQuery()
  const [downloadContext, { isFetching: isDownloading }] = useLazyDownloadResourceContextQuery()
  const onSelectionChange = useCallback((next: ResourceContextRequest, ready: boolean) => {
    setRequest(next)
    setIsReady(ready)
  }, [])

  const showPreview = async () => {
    setError(null)
    try {
      const content = await getContext(request).unwrap()
      setPreview(content)
      setStep('preview')
    } catch {
      setError('Nie udało się złożyć kontekstu. Sprawdź wybrane dane i spróbuj ponownie.')
    }
  }

  const download = async () => {
    setError(null)
    try {
      const content = await downloadContext(request).unwrap()
      downloadTextFile(`${initialRequest.type}_${initialRequest.id}_context.txt`, content)
    } catch {
      setError('Nie udało się pobrać kontekstu.')
    }
  }

  return <div className="flex h-full min-h-0 flex-col gap-4 text-sm">
    <p className="text-muted-foreground">{step === 'select' ? 'Wybierz dane, które mają znaleźć się w kontekście. Następnie sprawdź wynik przed pobraniem.' : 'Sprawdź złożony kontekst, a następnie pobierz go jako plik TXT.'}</p>
    <div className={step === 'select' ? 'min-h-0 flex-1 overflow-auto' : 'hidden'}>
      <ResourceContextSelector initialRequest={initialRequest} onChange={onSelectionChange} />
    </div>
    {step === 'preview' && <pre className="min-h-0 flex-1 overflow-auto whitespace-pre-wrap break-words rounded-md border bg-muted/30 p-3 text-xs">{preview}</pre>}
    {error && <p role="alert" className="text-destructive">{error}</p>}
    <div className="flex flex-wrap gap-2 border-t pt-4">
      {step === 'select' ? <Button type="button" onClick={() => void showPreview()} disabled={isPreviewing || !isReady}>{isPreviewing ? 'Składanie kontekstu…' : 'Złóż i zobacz kontekst'}</Button> : <>
        <Button type="button" variant="outline" onClick={() => { setStep('select'); setError(null) }}>Zmień wybór</Button>
        <Button type="button" onClick={() => void download()} disabled={isDownloading}>{isDownloading ? 'Pobieranie…' : 'Pobierz TXT'}</Button>
      </>}
    </div>
  </div>
}
