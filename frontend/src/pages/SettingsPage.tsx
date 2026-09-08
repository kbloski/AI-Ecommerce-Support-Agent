import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { JsonPanelRegistration } from '@/components/JsonPanelRegistration'
import {
  useGetOutputPromptQuery,
  useSaveOutputPromptMutation,
  useGetOllamaSettingsQuery,
  useSaveOllamaSettingsMutation,
  useListOllamaModelsQuery,
  type OllamaSettingsFields,
} from '@/features/settings/settingsApi'

const CONTEXT_LENGTH_PRESETS = [
  { label: '4k', value: 4_096 },
  { label: '8k', value: 8_192 },
  { label: '16k', value: 16_384 },
  { label: '32k', value: 32_768 },
  { label: '64k', value: 65_536 },
  { label: '128k', value: 131_072 },
  { label: '256k', value: 262_144 },
  { label: '512k', value: 524_288 },
  { label: '1M', value: 1_048_576 },
]
const CUSTOM_CONTEXT_LENGTH = 'custom'

function OllamaSettingsSection() {
  const { data, isLoading, error } = useGetOllamaSettingsQuery()
  const [saveOllamaSettings, saveState] = useSaveOllamaSettingsMutation()

  const [urlValue, setUrlValue] = useState('')
  const [modelValue, setModelValue] = useState('')
  const [timeoutValue, setTimeoutValue] = useState('')
  const [contextLengthValue, setContextLengthValue] = useState('')
  const [isCustomContextLength, setIsCustomContextLength] = useState(false)
  const [temperatureValue, setTemperatureValue] = useState('')

  useEffect(() => {
    if (!data) return
    setUrlValue(String(data.ollama_url.value))
    setModelValue(String(data.ollama_model.value))
    setTimeoutValue(String(data.ollama_timeout.value))
    const loadedContextLength = String(data.ollama_context_length.value)
    setContextLengthValue(loadedContextLength)
    setIsCustomContextLength(!CONTEXT_LENGTH_PRESETS.some((preset) => String(preset.value) === loadedContextLength))
    setTemperatureValue(String(data.ollama_temperature.value))
  }, [data])

  const {
    data: modelsData,
    isFetching: isLoadingModels,
    error: modelsError,
  } = useListOllamaModelsQuery(urlValue || undefined, { skip: !urlValue })

  const buildChangedFields = (): OllamaSettingsFields => {
    if (!data) return {}
    const fields: OllamaSettingsFields = {}
    if (urlValue !== String(data.ollama_url.value)) fields.ollama_url = urlValue || null
    if (modelValue !== String(data.ollama_model.value)) fields.ollama_model = modelValue || null
    if (timeoutValue !== String(data.ollama_timeout.value)) {
      fields.ollama_timeout = timeoutValue === '' ? null : Number(timeoutValue)
    }
    if (contextLengthValue !== String(data.ollama_context_length.value)) {
      fields.ollama_context_length = contextLengthValue === '' ? null : Number(contextLengthValue)
    }
    if (temperatureValue !== String(data.ollama_temperature.value)) {
      fields.ollama_temperature = temperatureValue === '' ? null : Number(temperatureValue)
    }
    return fields
  }

  const changedFields = buildChangedFields()
  const hasChanges = Object.keys(changedFields).length > 0

  const handleSave = () => {
    if (!hasChanges) return
    saveOllamaSettings(changedFields)
  }

  const handleResetField = (field: keyof OllamaSettingsFields) => {
    saveOllamaSettings({ [field]: null })
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">Ollama</h2>
        <p className="text-sm text-muted-foreground">
          Nadpisania obowiązują tylko dla tej instancji aplikacji. Puste pole = wartość domyślna z konfiguracji backendu.
        </p>
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Ładowanie…</p>}
      {Boolean(error) && <p className="text-sm text-destructive">Nie udało się pobrać ustawień Ollama.</p>}

      {data && (
        <div className="max-w-lg space-y-4">
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Label htmlFor="ollama_url">Ollama URL</Label>
              {data.ollama_url.is_override && (
                <ResetFieldButton onClick={() => handleResetField('ollama_url')} />
              )}
            </div>
            <Input
              id="ollama_url"
              value={urlValue}
              onChange={(e) => setUrlValue(e.target.value)}
              placeholder={String(data.ollama_url.default)}
            />
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Label htmlFor="ollama_model">Model</Label>
              {data.ollama_model.is_override && (
                <ResetFieldButton onClick={() => handleResetField('ollama_model')} />
              )}
            </div>
            <Select value={modelValue || undefined} onValueChange={(value) => value && setModelValue(value)}>
              <SelectTrigger id="ollama_model" className="w-full">
                <SelectValue placeholder={String(data.ollama_model.default)} />
              </SelectTrigger>
              <SelectContent>
                {(modelsData?.models ?? []).map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {isLoadingModels && <p className="text-xs text-muted-foreground">Pobieranie listy modeli…</p>}
            {Boolean(modelsError) && (
              <p className="text-xs text-destructive">
                Nie udało się pobrać listy modeli z podanego adresu Ollama.
              </p>
            )}
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="ollama_timeout">Timeout (s)</Label>
                {data.ollama_timeout.is_override && (
                  <ResetFieldButton onClick={() => handleResetField('ollama_timeout')} />
                )}
              </div>
              <Input
                id="ollama_timeout"
                type="number"
                value={timeoutValue}
                onChange={(e) => setTimeoutValue(e.target.value)}
                placeholder={String(data.ollama_timeout.default)}
              />
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="ollama_context_length">Context length</Label>
                {data.ollama_context_length.is_override && (
                  <ResetFieldButton onClick={() => handleResetField('ollama_context_length')} />
                )}
              </div>
              <Select
                value={isCustomContextLength ? CUSTOM_CONTEXT_LENGTH : contextLengthValue}
                onValueChange={(value) => {
                  if (!value) return
                  if (value === CUSTOM_CONTEXT_LENGTH) {
                    setIsCustomContextLength(true)
                  } else {
                    setIsCustomContextLength(false)
                    setContextLengthValue(value)
                  }
                }}
              >
                <SelectTrigger id="ollama_context_length" className="w-full">
                  <SelectValue placeholder={String(data.ollama_context_length.default)} />
                </SelectTrigger>
                <SelectContent>
                  {CONTEXT_LENGTH_PRESETS.map((preset) => (
                    <SelectItem key={preset.value} value={String(preset.value)}>
                      {preset.label} ({preset.value.toLocaleString('pl-PL')})
                    </SelectItem>
                  ))}
                  <SelectItem value={CUSTOM_CONTEXT_LENGTH}>Inna…</SelectItem>
                </SelectContent>
              </Select>
              {isCustomContextLength && (
                <Input
                  id="ollama_context_length_custom"
                  type="number"
                  value={contextLengthValue}
                  onChange={(e) => setContextLengthValue(e.target.value)}
                  placeholder={String(data.ollama_context_length.default)}
                />
              )}
            </div>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label htmlFor="ollama_temperature">Temperature</Label>
                {data.ollama_temperature.is_override && (
                  <ResetFieldButton onClick={() => handleResetField('ollama_temperature')} />
                )}
              </div>
              <Input
                id="ollama_temperature"
                type="number"
                step="0.1"
                value={temperatureValue}
                onChange={(e) => setTemperatureValue(e.target.value)}
                placeholder={String(data.ollama_temperature.default)}
              />
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button onClick={handleSave} disabled={!hasChanges || saveState.isLoading}>
              {saveState.isLoading ? 'Zapisywanie…' : 'Zapisz'}
            </Button>
            {saveState.isSuccess && !hasChanges && (
              <span className="text-sm text-muted-foreground">Zapisano.</span>
            )}
            {saveState.isError && <span className="text-sm text-destructive">Nie udało się zapisać.</span>}
          </div>
        </div>
      )}
    </div>
  )
}

function ResetFieldButton({ onClick }: { onClick: () => void }) {
  return (
    <Button type="button" variant="ghost" size="xs" onClick={onClick}>
      Przywróć domyślne
    </Button>
  )
}

export default function SettingsPage() {
  const { data, isLoading, error } = useGetOutputPromptQuery()
  const [saveOutputPrompt, saveState] = useSaveOutputPromptMutation()

  const [content, setContent] = useState('')

  useEffect(() => {
    if (data) setContent(data.content)
  }, [data])

  return (
    <div className="w-full space-y-10 p-6 lg:p-10">
      <div>
        <p className="text-xs font-semibold tracking-[0.14em] text-muted-foreground uppercase">Ustawienia</p>
        <h1 className="mt-1 text-3xl font-semibold tracking-tight">General</h1>
      </div>

      <OllamaSettingsSection />

      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Base output prompt</h2>
        <p className="text-sm text-muted-foreground">
          Treść instrukcji formatowania odpowiedzi dołączana do każdego zapytania do modelu LLM.
        </p>
        <p className="text-sm font-medium text-muted-foreground">
          To ustawienie jest obecnie wyłączone.
        </p>

        {isLoading && <p className="text-sm text-muted-foreground">Ładowanie…</p>}
        {Boolean(error) && <p className="text-sm text-destructive">Nie udało się pobrać danych.</p>}

        {!isLoading && (
          <>
            {data && (
              <JsonPanelRegistration data={data} title="JSON ustawień output promptu" />
            )}

            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              disabled
              rows={20}
              className="w-full rounded-lg border border-border bg-background p-3 font-mono text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
            />

            <div className="flex items-center gap-3">
              <Button onClick={() => saveOutputPrompt(content)} disabled>
                {saveState.isLoading ? 'Zapisywanie…' : 'Zapisz'}
              </Button>
              {saveState.isSuccess && <span className="text-sm text-muted-foreground">Zapisano.</span>}
              {saveState.isError && <span className="text-sm text-destructive">Nie udało się zapisać.</span>}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
