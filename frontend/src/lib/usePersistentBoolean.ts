import { useCallback, useSyncExternalStore, type SetStateAction } from 'react'

const changeEvent = 'ai-ec-agent:preferences-changed'
const memoryValues = new Map<string, boolean>()

function readValue(key: string, defaultValue: boolean): boolean {
  if (memoryValues.has(key)) return memoryValues.get(key)!
  try {
    const value = window.localStorage.getItem(key)
    if (value === 'true') return true
    if (value === 'false') return false
  } catch {
    return memoryValues.get(key) ?? defaultValue
  }
  return defaultValue
}

function subscribe(onChange: () => void) {
  window.addEventListener('storage', onChange)
  window.addEventListener(changeEvent, onChange)
  return () => {
    window.removeEventListener('storage', onChange)
    window.removeEventListener(changeEvent, onChange)
  }
}

/** Persists a boolean preference and synchronizes all mounted consumers and tabs. */
export function usePersistentBoolean(key: string, defaultValue: boolean) {
  const getSnapshot = useCallback(() => readValue(key, defaultValue), [key, defaultValue])
  const getServerSnapshot = useCallback(() => defaultValue, [defaultValue])
  const value = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
  const setValue = useCallback((next: SetStateAction<boolean>) => {
    const resolved = typeof next === 'function' ? next(readValue(key, defaultValue)) : next
    try {
      window.localStorage.setItem(key, String(resolved))
      memoryValues.delete(key)
    } catch {
      // Keep the preference usable for this session when storage is unavailable.
      memoryValues.set(key, resolved)
    }
    window.dispatchEvent(new Event(changeEvent))
  }, [key, defaultValue])

  return [value, setValue] as const
}
