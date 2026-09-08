import { useState } from 'react'
import { Check, Copy } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface EntityViewerProps {
  data: unknown
  className?: string
}

/** Uniwersalny podgląd dowolnej encji w postaci sformatowanego JSON-a. */
export function EntityViewer({ data, className }: EntityViewerProps) {
  const [copied, setCopied] = useState(false)

  const json = JSON.stringify(data, null, 2)

  async function handleCopy() {
    await navigator.clipboard.writeText(json)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className={cn('bg-card text-card-foreground shadow-sm', className)}>
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground">JSON</h3>
        <Button variant="outline" size="sm" onClick={handleCopy}>
          {copied ? (
            <>
              <Check /> Copied!
            </>
          ) : (
            <>
              <Copy /> Copy JSON
            </>
          )}
        </Button>
      </div>
      <pre className="h-96 min-h-48 max-h-[calc(100svh-12rem)] resize-y overflow-auto rounded-md bg-muted p-3 text-xs whitespace-pre-wrap break-words">{json}</pre>
    </div>
  )
}
