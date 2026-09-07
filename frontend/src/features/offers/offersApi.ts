import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

interface OffersResponse {
  items: Entity[]
  page: number
  page_size: number
  total_items: number
}

interface CreateOfferArgs {
  name: string
  buying_price: number
  selling_price?: number
  details?: string
}

interface CreateOfferItemArgs {
  offerId: number
  name: string
  quantity: number
  details?: string
}

export const offersApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listOffers: builder.query<OffersResponse, { page?: number } | void>({
      query: (params) => ({
        url: '/offers',
        params: { page: params?.page ?? 1 },
      }),
      providesTags: (result) => [
        ...(result?.items ?? []).map((item) => itemTag('Offer', item.id)),
        listTag('Offer', 'root'),
      ],
    }),
    getOffer: builder.query<Entity, number>({
      query: (id) => `/offers/${id}`,
      providesTags: (_result, _err, id) => [itemTag('Offer', id)],
    }),
    updateOffer: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/offers/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('Offer', id)],
    }),
    createOffer: builder.mutation<Entity, CreateOfferArgs>({
      query: (params) => ({ url: '/offers/create', method: 'POST', params }),
      invalidatesTags: [listTag('Offer', 'root')],
    }),
    deleteOffer: builder.mutation<void, number>({
      query: (id) => ({ url: `/offers/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, id) => [listTag('Offer', 'root'), itemTag('Offer', id)],
    }),
    deleteOfferItem: builder.mutation<void, { id: number; offerId: number }>({
      query: ({ id }) => ({ url: `/offer-items/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { offerId }) => [itemTag('Offer', offerId)],
    }),
    createOfferItem: builder.mutation<Entity, CreateOfferItemArgs>({
      query: ({ offerId, ...body }) => ({
        url: `/offers/${offerId}/items`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_result, _err, { offerId }) => [itemTag('Offer', offerId)],
    }),
    getOfferItem: builder.query<Entity, number>({
      query: (id) => `/offer-items/${id}`,
      providesTags: (_result, _err, id) => [itemTag('OfferItem', id)],
    }),
    updateOfferItem: builder.mutation<
      Entity,
      { id: number; offerId: number; fields: Record<string, unknown> }
    >({
      query: ({ id, fields }) => ({
        url: `/offer-items/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id, offerId }) => [
        itemTag('Offer', offerId),
        itemTag('OfferItem', id),
      ],
    }),
    deleteOfferInsight: builder.mutation<void, { id: number; offerId: number }>({
      query: ({ id }) => ({ url: `/offer-insights/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { offerId }) => [itemTag('Offer', offerId)],
    }),
    getOfferInsight: builder.query<Entity, number>({
      query: (id) => `/offer-insights/${id}`,
      providesTags: (_result, _err, id) => [itemTag('OfferInsight', id)],
    }),
    updateOfferInsight: builder.mutation<Entity, { id: number; offerId: number; fact_status?: string; review_status?: string }>({
      query: ({ id, offerId: _offerId, ...body }) => ({
        url: `/offer-insights/${id}/update`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_result, _err, { id, offerId }) => [
        itemTag('Offer', offerId),
        itemTag('OfferInsight', id),
      ],
    }),
    generateOfferInsights: builder.mutation<Entity, { id: number; types: string[] }>({
      query: ({ id, types }) => ({
        url: `/offers/${id}/insights/generate`,
        method: 'POST',
        body: { types },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('Offer', id)],
    }),
  }),
})

export const {
  useListOffersQuery,
  useGetOfferQuery,
  useCreateOfferMutation,
  useDeleteOfferMutation,
  useDeleteOfferItemMutation,
  useCreateOfferItemMutation,
  useDeleteOfferInsightMutation,
  useGenerateOfferInsightsMutation,
  useGetOfferInsightQuery,
  useUpdateOfferInsightMutation,
  useUpdateOfferMutation,
  useGetOfferItemQuery,
  useUpdateOfferItemMutation,
} = offersApi
