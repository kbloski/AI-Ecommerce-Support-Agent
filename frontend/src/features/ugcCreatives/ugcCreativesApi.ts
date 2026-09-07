import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const ugcCreativesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listUgcCreativesForMessageStrategy: builder.query<Entity[], number>({
      query: (messageStrategyId) => `/message-strategy/${messageStrategyId}/ugc-creatives`,
      providesTags: (result, _err, messageStrategyId) => [
        ...(result ?? []).map((item) => itemTag('UgcCreative', item.id)),
        listTag('UgcCreative', messageStrategyId),
      ],
    }),
    getUgcCreative: builder.query<Entity, number>({
      query: (id) => `/ugc-creatives/${id}`,
      providesTags: (_result, _err, id) => [itemTag('UgcCreative', id)],
    }),
    /** ctx: the parent MessageStrategy entity. */
    generateUgcCreatives: builder.mutation<Entity[], Entity>({
      query: (ms) => ({ url: `/message-strategy/${ms.id}/ugc-creatives/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, ms) => [listTag('UgcCreative', ms.id)],
    }),
    deleteUgcCreative: builder.mutation<void, { id: number; messageStrategyId: number }>({
      query: ({ id }) => ({ url: `/ugc-creatives/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, messageStrategyId }) => [
        listTag('UgcCreative', messageStrategyId),
        itemTag('UgcCreative', id),
      ],
    }),
  }),
})

export const {
  useListUgcCreativesForMessageStrategyQuery,
  useGetUgcCreativeQuery,
  useGenerateUgcCreativesMutation,
  useDeleteUgcCreativeMutation,
} = ugcCreativesApi
