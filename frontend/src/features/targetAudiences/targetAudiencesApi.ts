import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export interface UpdateTargetAudienceArgs {
  id: number
  offerProfileId?: number
  fact_status?: string
  is_reviewed?: boolean
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
    listTargetAudiencesForOfferProfile: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/target-audiences`,
      providesTags: (result, _err, offerProfileId) => [
        ...(result ?? []).map((item) => itemTag('TargetAudience', item.id)),
        listTag('TargetAudience', offerProfileId),
      ],
    }),
    generateTargetAudiences: builder.mutation<Entity[], { offerProfileId: number }>({
      query: ({ offerProfileId }) => ({ url: `/offer-profiles/${offerProfileId}/target-audiences/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, { offerProfileId }) => [
        listTag('TargetAudience', offerProfileId),
        itemTag('OfferProfile', offerProfileId),
      ],
    }),
    deleteTargetAudience: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/target-audiences/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        listTag('TargetAudience', offerProfileId),
        itemTag('TargetAudience', id),
        itemTag('OfferProfile', offerProfileId),
      ],
    }),
    updateTargetAudience: builder.mutation<Entity, UpdateTargetAudienceArgs>({
      query: ({ id, offerProfileId: _offerProfileId, ...body }) => ({
        url: `/target-audiences/${id}/update`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        itemTag('TargetAudience', id),
        ...(offerProfileId === undefined ? [] : [itemTag('OfferProfile', offerProfileId)]),
      ],
    }),
  }),
})

export const {
  useListTargetAudiencesForOfferProfileQuery,
  useGenerateTargetAudiencesMutation,
  useDeleteTargetAudienceMutation,
  useUpdateTargetAudienceMutation,
} = targetAudiencesApi
