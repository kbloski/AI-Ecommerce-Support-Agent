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
  description?: string
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
  }),
})

export const {
  useListOffersQuery,
  useGetOfferQuery,
  useCreateOfferMutation,
  useDeleteOfferMutation,
  useUpdateOfferMutation,
} = offersApi
