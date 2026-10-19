import { useCallback, useRef, useState, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'

export interface ConfirmOptions {
  title: ReactNode
  description?: ReactNode
  confirmLabel?: string
  cancelLabel?: string
  destructive?: boolean
}

/**
 * In-app replacement for window.confirm: `const [confirm, confirmDialog] = useConfirm()`,
 * render `confirmDialog` once and `if (await confirm({ title })) …`.
 */
export function useConfirm() {
  const [options, setOptions] = useState<ConfirmOptions | null>(null)
  const resolver = useRef<((confirmed: boolean) => void) | null>(null)

  const confirm = useCallback((next: ConfirmOptions) => new Promise<boolean>((resolve) => {
    resolver.current?.(false)
    resolver.current = resolve
    setOptions(next)
  }), [])

  const close = (confirmed: boolean) => {
    resolver.current?.(confirmed)
    resolver.current = null
    setOptions(null)
  }

  const dialog = <Dialog open={options !== null} onOpenChange={(open) => { if (!open) close(false) }}>
    {/* Above the side panel (z-50), from which confirmations are usually opened. */}
    <DialogContent className="z-[60] sm:max-w-md" overlayProps={{ forceRender: true, className: 'z-[60] bg-black/40' }} showCloseButton={false}>
      <DialogHeader>
        <DialogTitle>{options?.title}</DialogTitle>
        {options?.description && <DialogDescription>{options.description}</DialogDescription>}
      </DialogHeader>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={() => close(false)}>{options?.cancelLabel ?? 'Anuluj'}</Button>
        <Button type="button" variant={options?.destructive ? 'destructive' : 'default'} autoFocus onClick={() => close(true)}>{options?.confirmLabel ?? 'Potwierdź'}</Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>

  return [confirm, dialog] as const
}
