import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const offerStrategyApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listOfferStrategyForMarketingStrategy: builder.query<Entity[], number>({
      query: (marketingStrategyId) => `/marketing-strategy/${marketingStrategyId}/offer-strategy`,
      providesTags: (result, _err, marketingStrategyId) => [
        ...(result ?? []).map((item) => itemTag('OfferStrategy', item.id)),
        listTag('OfferStrategy', marketingStrategyId),
      ],
    }),
    getOfferStrategy: builder.query<Entity, number>({
      query: (id) => `/offer-strategy/${id}`,
      providesTags: (_result, _err, id) => [itemTag('OfferStrategy', id)],
    }),
    updateOfferStrategy: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/offer-strategy/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('OfferStrategy', id)],
    }),
    /** ctx: the parent MarketingStrategy entity. */
    generateOfferStrategy: builder.mutation<Entity, Entity>({
      query: (ms) => ({ url: `/marketing-strategy/${ms.id}/offer-strategy/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, ms) => [listTag('OfferStrategy', ms.id)],
    }),
    deleteOfferStrategy: builder.mutation<void, { id: number; marketingStrategyId: number }>({
      query: ({ id }) => ({ url: `/offer-strategy/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, marketingStrategyId }) => [
        listTag('OfferStrategy', marketingStrategyId),
        itemTag('OfferStrategy', id),
      ],
    }),
  }),
})

export const {
  useListOfferStrategyForMarketingStrategyQuery,
  useGetOfferStrategyQuery,
  useGenerateOfferStrategyMutation,
  useDeleteOfferStrategyMutation,
  useUpdateOfferStrategyMutation,
} = offerStrategyApi
