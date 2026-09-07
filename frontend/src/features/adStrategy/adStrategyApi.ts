import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const adStrategyApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAdStrategyForMessageStrategy: builder.query<Entity[], number>({
      query: (messageStrategyId) => `/message-strategy/${messageStrategyId}/ad-strategy`,
      providesTags: (result, _err, messageStrategyId) => [
        ...(result ?? []).map((item) => itemTag('AdStrategy', item.id)),
        listTag('AdStrategy', messageStrategyId),
      ],
    }),
    getAdStrategy: builder.query<Entity, number>({
      query: (id) => `/ad-strategy/${id}`,
      providesTags: (_result, _err, id) => [itemTag('AdStrategy', id)],
    }),
    updateAdStrategy: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/ad-strategy/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('AdStrategy', id)],
    }),
    /** ctx: the parent MessageStrategy entity. */
    generateAdStrategy: builder.mutation<Entity, Entity>({
      query: (ms) => ({ url: `/message-strategy/${ms.id}/ad-strategy/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, ms) => [listTag('AdStrategy', ms.id)],
    }),
    deleteAdStrategy: builder.mutation<void, { id: number; messageStrategyId: number }>({
      query: ({ id }) => ({ url: `/ad-strategy/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, messageStrategyId }) => [
        listTag('AdStrategy', messageStrategyId),
        itemTag('AdStrategy', id),
      ],
    }),
  }),
})

export const {
  useListAdStrategyForMessageStrategyQuery,
  useGetAdStrategyQuery,
  useGenerateAdStrategyMutation,
  useDeleteAdStrategyMutation,
  useUpdateAdStrategyMutation,
} = adStrategyApi
