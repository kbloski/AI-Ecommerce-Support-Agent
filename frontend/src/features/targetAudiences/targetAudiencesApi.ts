import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export interface PaginatedTargetAudiencesResult {
  items: Entity[]
  page: number
  page_size: number
  total_items: number
  total_pages: number
}

export type TargetAudienceSort = 'unreviewed_first' | 'reviewed_first'

export interface UpdateTargetAudienceArgs {
  id: number
  offerSourceId?: number
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
    listTargetAudiencesForOfferSource: builder.query<PaginatedTargetAudiencesResult, {
      offerSourceId: number
      page?: number
      pageSize?: number
      isReviewed?: boolean
      sort?: TargetAudienceSort
    }>({
      query: ({ offerSourceId, page = 1, pageSize = 20, isReviewed, sort = 'unreviewed_first' }) => ({
        url: `/offer-sources/${offerSourceId}/target-audiences`,
        params: { page, page_size: pageSize, is_reviewed: isReviewed, sort },
      }),
      providesTags: (result, _err, { offerSourceId }) => [
        ...(result?.items ?? []).map((item) => itemTag('TargetAudience', item.id)),
        listTag('TargetAudience', offerSourceId),
      ],
    }),
    generateTargetAudiences: builder.mutation<Entity[], { offerSourceId: number }>({
      query: ({ offerSourceId }) => ({ url: `/offer-sources/${offerSourceId}/target-audiences/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, { offerSourceId }) => [
        listTag('TargetAudience', offerSourceId),
        itemTag('OfferSource', offerSourceId),
      ],
    }),
    deleteTargetAudience: builder.mutation<void, { id: number; offerSourceId: number }>({
      query: ({ id }) => ({ url: `/target-audiences/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerSourceId }) => [
        listTag('TargetAudience', offerSourceId),
        itemTag('TargetAudience', id),
        itemTag('OfferSource', offerSourceId),
      ],
    }),
    updateTargetAudience: builder.mutation<Entity, UpdateTargetAudienceArgs>({
      query: ({ id, offerSourceId: _offerSourceId, ...body }) => ({
        url: `/target-audiences/${id}/update`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_result, _err, { id, offerSourceId }) => [
        itemTag('TargetAudience', id),
        ...(offerSourceId === undefined ? [] : [listTag('TargetAudience', offerSourceId)]),
        ...(offerSourceId === undefined ? [] : [itemTag('OfferSource', offerSourceId)]),
      ],
    }),
  }),
})

export const {
  useListTargetAudiencesForOfferSourceQuery,
  useGenerateTargetAudiencesMutation,
  useDeleteTargetAudienceMutation,
  useUpdateTargetAudienceMutation,
} = targetAudiencesApi
