import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const messageStrategyApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listMessageStrategyForOfferStrategy: builder.query<Entity[], number>({
      query: (offerStrategyId) => `/offer-strategy/${offerStrategyId}/message-strategy`,
      providesTags: (result, _err, offerStrategyId) => [
        ...(result ?? []).map((item) => itemTag('MessageStrategy', item.id)),
        listTag('MessageStrategy', offerStrategyId),
      ],
    }),
    getMessageStrategy: builder.query<Entity, number>({
      query: (id) => `/message-strategy/${id}`,
      providesTags: (_result, _err, id) => [itemTag('MessageStrategy', id)],
    }),
    /** ctx: the parent OfferStrategy entity. */
    generateMessageStrategy: builder.mutation<Entity, Entity>({
      query: (os) => ({ url: `/offer-strategy/${os.id}/message-strategy/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, os) => [listTag('MessageStrategy', os.id)],
    }),
    deleteMessageStrategy: builder.mutation<void, { id: number; offerStrategyId: number }>({
      query: ({ id }) => ({ url: `/message-strategy/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerStrategyId }) => [
        listTag('MessageStrategy', offerStrategyId),
        itemTag('MessageStrategy', id),
      ],
    }),
    updateMessageStrategy: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/message-strategy/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('MessageStrategy', id)],
    }),
  }),
})

export const {
  useListMessageStrategyForOfferStrategyQuery,
  useGetMessageStrategyQuery,
  useGenerateMessageStrategyMutation,
  useDeleteMessageStrategyMutation,
  useUpdateMessageStrategyMutation,
} = messageStrategyApi
