import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

interface OfferProfileContextArgs {
  id: number
  include: Array<'offer_raw' | 'offer_source' | 'target_audiences' | 'marketing_angle' | 'ad_concept'>
  marketingAngleIds: number[]
  adConceptIds: number[]
}

export const offerProfilesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAllOfferProfiles: builder.query<Entity[], void>({
      query: () => '/offer-profiles',
      providesTags: [listTag('OfferProfile', 'root')],
    }),
    getOfferProfile: builder.query<Entity, number>({
      query: (id) => `/offer-profiles/${id}`,
      providesTags: (_result, _error, id) => [itemTag('OfferProfile', id)],
    }),
    getOfferProfileLlmContext: builder.query<{ context: string; sections: Record<string, unknown> }, OfferProfileContextArgs>({
      query: ({ id, include, marketingAngleIds, adConceptIds }) => {
        const params = new URLSearchParams()
        include.forEach((type) => params.append('include', type))
        marketingAngleIds.forEach((angleId) => params.append('marketing_angle_ids', String(angleId)))
        adConceptIds.forEach((conceptId) => params.append('ad_concept_ids', String(conceptId)))
        return `/offer-profiles/${id}/llm-context?${params.toString()}`
      },
      providesTags: (_result, _error, { id }) => [itemTag('OfferProfile', id)],
    }),
    updateOfferProfile: builder.mutation<Entity, { id: number; offerSourceId: number; name: string }>({
      query: ({ id, name }) => ({ url: `/offer-profiles/${id}/update`, method: 'POST', body: { name } }),
      invalidatesTags: (_result, _error, { id, offerSourceId }) => [itemTag('OfferProfile', id), listTag('OfferProfile', offerSourceId), listTag('OfferProfile', 'root')],
    }),
    deleteOfferProfile: builder.mutation<{ deleted: boolean }, { id: number; offerSourceId: number }>({
      query: ({ id }) => ({ url: `/offer-profiles/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { id, offerSourceId }) => [itemTag('OfferProfile', id), listTag('OfferProfile', offerSourceId), listTag('OfferProfile', 'root')],
    }),
    listOfferProfiles: builder.query<Entity[], number>({
      query: (id) => `/offer-sources/${id}/profiles`,
      providesTags: (_result, _error, id) => [listTag('OfferProfile', id)],
    }),
    createOfferProfile: builder.mutation<Entity, { offerSourceId: number; name: string }>({
      query: ({ offerSourceId, name }) => ({ url: `/offer-sources/${offerSourceId}/profiles`, method: 'POST', body: { name } }),
      invalidatesTags: (_result, _error, { offerSourceId }) => [listTag('OfferProfile', offerSourceId), listTag('OfferProfile', 'root')],
    }),
  }),
})
export const { useListAllOfferProfilesQuery, useListOfferProfilesQuery, useCreateOfferProfileMutation, useGetOfferProfileQuery, useGetOfferProfileLlmContextQuery, useUpdateOfferProfileMutation, useDeleteOfferProfileMutation } = offerProfilesApi
