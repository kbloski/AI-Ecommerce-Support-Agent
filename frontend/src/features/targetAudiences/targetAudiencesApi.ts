import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export interface UpdateTargetAudienceArgs {
  id: number
  knowledgeId?: number
  fact_status?: string
  review_status?: string
  name?: string
  reason?: string
  score?: number
  confidence?: number
  age_min?: number
  age_max?: number
  gender?: string
  location?: string
  purchasing_power?: string
  lifestyles?: unknown[]
  values?: unknown[]
  awareness_level?: string
  price_sensitivity?: string
  research_level?: string
  decision_time?: string
  pain_points?: unknown[]
  motivations?: unknown[]
  buying_triggers?: unknown[]
  objections?: unknown[]
  message_angles?: unknown[]
  marketing_channels?: unknown[]
}

export const targetAudiencesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listTargetAudiencesForKnowledge: builder.query<Entity[], number>({
      query: (knowledgeId) => `/knowledges/${knowledgeId}/target-audiences`,
      providesTags: (result, _err, knowledgeId) => [
        ...(result ?? []).map((item) => itemTag('TargetAudience', item.id)),
        listTag('TargetAudience', knowledgeId),
      ],
    }),
    getTargetAudience: builder.query<Entity, number>({
      query: (id) => `/target-audiences/${id}`,
      providesTags: (_result, _err, id) => [itemTag('TargetAudience', id)],
    }),
    generateTargetAudiences: builder.mutation<Entity[], { knowledgeId: number }>({
      query: ({ knowledgeId }) => ({ url: `/knowledges/${knowledgeId}/target-audiences/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, { knowledgeId }) => [
        listTag('TargetAudience', knowledgeId),
        itemTag('Knowledge', knowledgeId),
      ],
    }),
    deleteTargetAudience: builder.mutation<void, { id: number; knowledgeId: number }>({
      query: ({ id }) => ({ url: `/target-audiences/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, knowledgeId }) => [
        listTag('TargetAudience', knowledgeId),
        itemTag('TargetAudience', id),
        itemTag('Knowledge', knowledgeId),
      ],
    }),
    updateTargetAudience: builder.mutation<Entity, UpdateTargetAudienceArgs>({
      query: ({ id, knowledgeId: _knowledgeId, ...body }) => ({
        url: `/target-audiences/${id}/update`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_result, _err, { id, knowledgeId }) => [
        itemTag('TargetAudience', id),
        ...(knowledgeId === undefined ? [] : [itemTag('Knowledge', knowledgeId)]),
      ],
    }),
  }),
})

export const {
  useListTargetAudiencesForKnowledgeQuery,
  useGetTargetAudienceQuery,
  useGenerateTargetAudiencesMutation,
  useDeleteTargetAudienceMutation,
  useUpdateTargetAudienceMutation,
} = targetAudiencesApi
