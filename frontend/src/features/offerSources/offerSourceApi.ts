import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export interface PaginatedResult<T> {
  items: T[]
  page: number
  page_size: number
  total_items: number
  total_pages: number
}


export const offerSourceApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listOfferSourceForOffer: builder.query<Entity[], number>({
      query: (offerId) => `/offers/${offerId}/offer-sources`,
      providesTags: (result, _err, offerId) => [
        ...(result ?? []).map((item) => itemTag('OfferSource', item.id)),
        listTag('OfferSource', offerId),
      ],
    }),
    getOfferSource: builder.query<Entity, number>({
      query: (id) => `/offer-sources/${id}`,
      providesTags: (_result, _err, id) => [itemTag('OfferSource', id)],
    }),
    updateOfferSource: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/offer-sources/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('OfferSource', id)],
    }),
    generateOfferSource: builder.mutation<Entity, { offerId: number; generationInstructions?: string }>({
      query: ({ offerId, generationInstructions }) => ({
        url: `/offers/${offerId}/offer-sources/generate`,
        method: 'POST',
        body: { generation_instructions: generationInstructions },
      }),
      invalidatesTags: (_result, _err, { offerId }) => [listTag('OfferSource', offerId)],
    }),
    deleteOfferSource: builder.mutation<void, { id: number; offerId: number }>({
      query: ({ id }) => ({ url: `/offer-sources/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerId }) => [
        listTag('OfferSource', offerId),
        itemTag('OfferSource', id),
      ],
    }),
  }),
})

export const {
  useListOfferSourceForOfferQuery,
  useGetOfferSourceQuery,
  useGenerateOfferSourceMutation,
  useDeleteOfferSourceMutation,
  useUpdateOfferSourceMutation,
} = offerSourceApi
