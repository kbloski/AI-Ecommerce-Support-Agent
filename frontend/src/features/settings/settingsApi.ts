import { api } from '@/store/api'

export type RuleSet = 'json_output' | 'english_output'

interface RuleSetContent {
  rule_set: RuleSet
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
    getRuleSet: builder.query<RuleSetContent, RuleSet>({
      query: (ruleSet) => `/settings/rules/${ruleSet}`,
      providesTags: (_result, _error, ruleSet) => [{ type: 'RuleSet', id: ruleSet }],
    }),
    saveRuleSet: builder.mutation<RuleSetContent, { ruleSet: RuleSet; content: string }>({
      query: ({ ruleSet, content }) => ({
        url: `/settings/rules/${ruleSet}`,
        method: 'POST',
        body: { content },
      }),
      invalidatesTags: (_result, _error, { ruleSet }) => [{ type: 'RuleSet', id: ruleSet }],
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
  useGetRuleSetQuery,
  useSaveRuleSetMutation,
  useGetOllamaSettingsQuery,
  useSaveOllamaSettingsMutation,
  useListOllamaModelsQuery,
} = settingsApi
