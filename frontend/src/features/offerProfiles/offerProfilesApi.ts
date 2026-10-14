import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const offerProfilesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getOfferProfile: builder.query<Entity, number>({
      query: (id) => `/offer-profiles/${id}`,
      providesTags: (_result, _error, id) => [itemTag('OfferProfile', id)],
    }),
    updateOfferProfile: builder.mutation<Entity, { id: number; offerSourceId: number; name: string }>({
      query: ({ id, name }) => ({ url: `/offer-profiles/${id}/update`, method: 'POST', body: { name } }),
      invalidatesTags: (_result, _error, { id, offerSourceId }) => [itemTag('OfferProfile', id), listTag('OfferProfile', offerSourceId)],
    }),
    deleteOfferProfile: builder.mutation<{ deleted: boolean }, { id: number; offerSourceId: number }>({
      query: ({ id }) => ({ url: `/offer-profiles/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { id, offerSourceId }) => [itemTag('OfferProfile', id), listTag('OfferProfile', offerSourceId)],
    }),
    listOfferProfiles: builder.query<Entity[], number>({
      query: (id) => `/offer-sources/${id}/profiles`,
      providesTags: (_result, _error, id) => [listTag('OfferProfile', id)],
    }),
    createOfferProfile: builder.mutation<Entity, { offerSourceId: number; name: string }>({
      query: ({ offerSourceId, name }) => ({ url: `/offer-sources/${offerSourceId}/profiles`, method: 'POST', body: { name } }),
      invalidatesTags: (_result, _error, { offerSourceId }) => [listTag('OfferProfile', offerSourceId)],
    }),
  }),
})
export const { useListOfferProfilesQuery, useCreateOfferProfileMutation, useGetOfferProfileQuery, useUpdateOfferProfileMutation, useDeleteOfferProfileMutation } = offerProfilesApi
