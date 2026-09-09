import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const offerProfileApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listOfferProfileForOffer: builder.query<Entity[], number>({
      query: (offerId) => `/offers/${offerId}/offer-profiles`,
      providesTags: (result, _err, offerId) => [
        ...(result ?? []).map((item) => itemTag('OfferProfile', item.id)),
        listTag('OfferProfile', offerId),
      ],
    }),
    getOfferProfile: builder.query<Entity, number>({
      query: (id) => `/offer-profiles/${id}`,
      providesTags: (_result, _err, id) => [itemTag('OfferProfile', id)],
    }),
    updateOfferProfile: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/offer-profiles/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('OfferProfile', id)],
    }),
    generateOfferProfile: builder.mutation<Entity, { offerId: number }>({
      query: ({ offerId }) => ({ url: `/offers/${offerId}/offer-profiles/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, { offerId }) => [listTag('OfferProfile', offerId)],
    }),
    deleteOfferProfile: builder.mutation<void, { id: number; offerId: number }>({
      query: ({ id }) => ({ url: `/offer-profiles/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerId }) => [
        listTag('OfferProfile', offerId),
        itemTag('OfferProfile', id),
      ],
    }),
  }),
})

export const {
  useListOfferProfileForOfferQuery,
  useGetOfferProfileQuery,
  useGenerateOfferProfileMutation,
  useDeleteOfferProfileMutation,
  useUpdateOfferProfileMutation,
} = offerProfileApi
