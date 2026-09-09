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
    listOfferProfileElements: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/elements`,
      providesTags: (result, _err, offerProfileId) => [
        ...(result ?? []).map((item) => itemTag('OfferProfileElement', item.id)),
        listTag('OfferProfileElement', offerProfileId),
      ],
    }),
    listOfferProfileElementTypes: builder.query<string[], void>({
      query: () => '/offer-profile-elements/types',
    }),
    createOfferProfileElement: builder.mutation<Entity, {
      offerProfileId: number
      type: string
      name: string
      description?: string
    }>({
      query: ({ offerProfileId, ...body }) => ({
        url: `/offer-profiles/${offerProfileId}/elements`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_result, _err, { offerProfileId }) => [
        listTag('OfferProfileElement', offerProfileId),
      ],
    }),
    updateOfferProfileElement: builder.mutation<Entity, {
      id: number
      offerProfileId: number
      fields: Record<string, unknown>
    }>({
      query: ({ id, fields }) => ({
        url: `/offer-profile-elements/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        itemTag('OfferProfileElement', id),
        listTag('OfferProfileElement', offerProfileId),
      ],
    }),
    deleteOfferProfileElement: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/offer-profile-elements/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        itemTag('OfferProfileElement', id),
        listTag('OfferProfileElement', offerProfileId),
      ],
    }),
    generateOfferProfileElements: builder.mutation<Entity[], {
      offerProfileId: number
      element_types: string[]
    }>({
      query: ({ offerProfileId, element_types }) => ({
        url: `/offer-profiles/${offerProfileId}/elements/generate`,
        method: 'POST',
        body: { element_types },
      }),
      invalidatesTags: (_result, _err, { offerProfileId }) => [
        listTag('OfferProfileElement', offerProfileId),
      ],
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
  useListOfferProfileElementsQuery,
  useListOfferProfileElementTypesQuery,
  useCreateOfferProfileElementMutation,
  useUpdateOfferProfileElementMutation,
  useDeleteOfferProfileElementMutation,
  useGenerateOfferProfileElementsMutation,
  useGenerateOfferProfileMutation,
  useDeleteOfferProfileMutation,
  useUpdateOfferProfileMutation,
} = offerProfileApi
