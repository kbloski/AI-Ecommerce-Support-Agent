import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const pageStrategyApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listPageStrategyForMessageStrategy: builder.query<Entity[], number>({
      query: (messageStrategyId) => `/message-strategy/${messageStrategyId}/page-strategy`,
      providesTags: (result, _err, messageStrategyId) => [
        ...(result ?? []).map((item) => itemTag('PageStrategy', item.id)),
        listTag('PageStrategy', messageStrategyId),
      ],
    }),
    getPageStrategy: builder.query<Entity, number>({
      query: (id) => `/page-strategy/${id}`,
      providesTags: (_result, _err, id) => [itemTag('PageStrategy', id)],
    }),
    updatePageStrategy: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/page-strategy/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('PageStrategy', id)],
    }),
    /** ctx: the parent MessageStrategy entity. */
    generatePageStrategy: builder.mutation<Entity, Entity>({
      query: (ms) => ({ url: `/message-strategy/${ms.id}/page-strategy/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, ms) => [listTag('PageStrategy', ms.id)],
    }),
    deletePageStrategy: builder.mutation<void, { id: number; messageStrategyId: number }>({
      query: ({ id }) => ({ url: `/page-strategy/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, messageStrategyId }) => [
        listTag('PageStrategy', messageStrategyId),
        itemTag('PageStrategy', id),
      ],
    }),
  }),
})

export const {
  useListPageStrategyForMessageStrategyQuery,
  useGetPageStrategyQuery,
  useGeneratePageStrategyMutation,
  useDeletePageStrategyMutation,
  useUpdatePageStrategyMutation,
} = pageStrategyApi
