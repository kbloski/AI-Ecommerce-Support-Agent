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
  offerProfileId?: number
  fact_status?: string
  is_reviewed?: boolean
  name?: string
  age_min?: number
  age_max?: number
  gender?: string
  lifestyles?: unknown[]
  values?: unknown[]
  pain_points?: unknown[]
  motivations?: unknown[]
  buying_triggers?: unknown[]
  desires?: unknown[]
}

export const targetAudiencesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAllTargetAudiencesForOfferProfile: builder.query<Entity[], number>({
      async queryFn(offerProfileId, _api, _extraOptions, baseQuery) {
        const items: Entity[] = []
        let page = 1
        let totalPages = 1
        while (page <= totalPages) {
          const result = await baseQuery({
            url: `/offer-profiles/${offerProfileId}/target-audiences`,
            params: { page, page_size: 100 },
          })
          if (result.error) return { error: result.error }
          const data = result.data as PaginatedTargetAudiencesResult
          items.push(...data.items)
          totalPages = data.total_pages
          page += 1
        }
        return { data: items }
      },
      providesTags: (result, _err, offerProfileId) => [
        ...(result ?? []).map((item) => itemTag('TargetAudience', item.id)),
        listTag('TargetAudience', offerProfileId),
      ],
    }),
    listTargetAudiencesForOfferProfile: builder.query<PaginatedTargetAudiencesResult, {
      offerProfileId: number
      page?: number
      pageSize?: number
      isReviewed?: boolean
      sort?: TargetAudienceSort
    }>({
      query: ({ offerProfileId, page = 1, pageSize = 20, isReviewed, sort = 'unreviewed_first' }) => ({
        url: `/offer-profiles/${offerProfileId}/target-audiences`,
        params: { page, page_size: pageSize, is_reviewed: isReviewed, sort },
      }),
      providesTags: (result, _err, { offerProfileId }) => [
        ...(result?.items ?? []).map((item) => itemTag('TargetAudience', item.id)),
        listTag('TargetAudience', offerProfileId),
      ],
    }),
    generateTargetAudiences: builder.mutation<Entity[], { offerProfileId: number; count: number; generationInstructions: string }>({
      query: ({ offerProfileId, count, generationInstructions }) => ({ url: `/offer-profiles/${offerProfileId}/target-audiences/generate`, method: 'POST', body: { count, generation_instructions: generationInstructions } }),
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
        ...(offerProfileId === undefined ? [] : [listTag('TargetAudience', offerProfileId)]),
        ...(offerProfileId === undefined ? [] : [itemTag('OfferProfile', offerProfileId)]),
      ],
    }),
  }),
})

export const {
  useListAllTargetAudiencesForOfferProfileQuery,
  useListTargetAudiencesForOfferProfileQuery,
  useGenerateTargetAudiencesMutation,
  useDeleteTargetAudienceMutation,
  useUpdateTargetAudienceMutation,
} = targetAudiencesApi
