import { api } from '@/store/api'

interface OutputPrompt {
  content: string
}

export interface OllamaSettingField {
  value: string | number
  default: string | number
  is_override: boolean
}

export interface OllamaSettings {
  ollama_url: OllamaSettingField
  ollama_model: OllamaSettingField
  ollama_timeout: OllamaSettingField
  ollama_context_length: OllamaSettingField
  ollama_temperature: OllamaSettingField
}

export type OllamaSettingsFields = Partial<{
  ollama_url: string | null
  ollama_model: string | null
  ollama_timeout: number | null
  ollama_context_length: number | null
  ollama_temperature: number | null
}>

interface OllamaModelsResponse {
  models: string[]
}

export const settingsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getOutputPrompt: builder.query<OutputPrompt, void>({
      query: () => '/settings/output-prompt',
      providesTags: ['OutputPrompt'],
    }),
    saveOutputPrompt: builder.mutation<OutputPrompt, string>({
      query: (content) => ({
        url: '/settings/output-prompt',
        method: 'POST',
        body: { content },
      }),
      invalidatesTags: ['OutputPrompt'],
    }),
    getOllamaSettings: builder.query<OllamaSettings, void>({
      query: () => '/settings/ollama',
      providesTags: ['OllamaSettings'],
    }),
    saveOllamaSettings: builder.mutation<OllamaSettings, OllamaSettingsFields>({
      query: (fields) => ({
        url: '/settings/ollama',
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: ['OllamaSettings'],
    }),
    listOllamaModels: builder.query<OllamaModelsResponse, string | undefined>({
      query: (url) => ({
        url: '/settings/ollama/models',
        params: url ? { url } : undefined,
      }),
    }),
  }),
})

export const {
  useGetOutputPromptQuery,
  useSaveOutputPromptMutation,
  useGetOllamaSettingsQuery,
  useSaveOllamaSettingsMutation,
  useListOllamaModelsQuery,
} = settingsApi
