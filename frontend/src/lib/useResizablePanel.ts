import { useCallback, useEffect, useRef, useState, type KeyboardEvent, type PointerEvent } from 'react'

type ResizeEdge = 'left' | 'right'

interface UseResizablePanelOptions {
  defaultWidth: number
  minWidth: number
  getMaxWidth: () => number
  resizeEdge: ResizeEdge
  storageKey?: string
}

function readStoredWidth(storageKey: string | undefined, fallback: number) {
  if (!storageKey) return fallback

  const stored = Number(window.localStorage.getItem(storageKey))
  return Number.isFinite(stored) ? stored : fallback
}

/** Shared pointer and keyboard resizing behavior for panels anchored to either viewport edge. */
export function useResizablePanel({
  defaultWidth,
  minWidth,
  getMaxWidth,
  resizeEdge,
  storageKey,
}: UseResizablePanelOptions) {
  const [width, setWidth] = useState(() => readStoredWidth(storageKey, defaultWidth))
  const dragStart = useRef<{ clientX: number; width: number } | null>(null)
  const previousBodyStyles = useRef<{ cursor: string; userSelect: string } | null>(null)

  const clampWidth = useCallback(
    (nextWidth: number) => Math.min(Math.max(minWidth, nextWidth), Math.max(minWidth, getMaxWidth())),
    [getMaxWidth, minWidth],
  )

  const updateWidth = useCallback(
    (nextWidth: number | ((current: number) => number)) => {
      setWidth((current) => clampWidth(typeof nextWidth === 'function' ? nextWidth(current) : nextWidth))
    },
    [clampWidth],
  )

  const stopBodyResizeState = useCallback(() => {
    if (!previousBodyStyles.current) return
    document.body.style.cursor = previousBodyStyles.current.cursor
    document.body.style.userSelect = previousBodyStyles.current.userSelect
    previousBodyStyles.current = null
  }, [])

  const startResize = useCallback((event: PointerEvent<HTMLDivElement>) => {
    event.preventDefault()
    event.stopPropagation()
    dragStart.current = { clientX: event.clientX, width }
    event.currentTarget.setPointerCapture(event.pointerId)
    previousBodyStyles.current = {
      cursor: document.body.style.cursor,
      userSelect: document.body.style.userSelect,
    }
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [width])

  const resize = useCallback((event: PointerEvent<HTMLDivElement>) => {
    if (!dragStart.current) return

    const delta = event.clientX - dragStart.current.clientX
    const direction = resizeEdge === 'right' ? -1 : 1
    updateWidth(dragStart.current.width + delta * direction)
  }, [resizeEdge, updateWidth])

  const stopResize = useCallback((event: PointerEvent<HTMLDivElement>) => {
    dragStart.current = null
    stopBodyResizeState()
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId)
    }
  }, [stopBodyResizeState])

  const resetWidth = useCallback(() => updateWidth(defaultWidth), [defaultWidth, updateWidth])

  const resizeWithKeyboard = useCallback((event: KeyboardEvent<HTMLDivElement>) => {
    const step = event.shiftKey ? 32 : 8
    let nextWidth: number | undefined

    if (event.key === 'ArrowLeft') nextWidth = width + (resizeEdge === 'right' ? step : -step)
    if (event.key === 'ArrowRight') nextWidth = width + (resizeEdge === 'right' ? -step : step)
    if (event.key === 'Home') nextWidth = minWidth
    if (event.key === 'End') nextWidth = getMaxWidth()
    if (nextWidth === undefined) return

    event.preventDefault()
    updateWidth(nextWidth)
  }, [getMaxWidth, minWidth, resizeEdge, updateWidth, width])

  useEffect(() => {
    const clampToViewport = () => updateWidth((current) => current)
    clampToViewport()
    window.addEventListener('resize', clampToViewport)
    return () => window.removeEventListener('resize', clampToViewport)
  }, [updateWidth])

  useEffect(() => {
    if (storageKey) window.localStorage.setItem(storageKey, String(width))
  }, [storageKey, width])

  useEffect(() => stopBodyResizeState, [stopBodyResizeState])

  return {
    width,
    minWidth,
    maxWidth: Math.max(minWidth, getMaxWidth()),
    startResize,
    resize,
    stopResize,
    resetWidth,
    resizeWithKeyboard,
  }
}
