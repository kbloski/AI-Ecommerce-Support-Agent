import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const ugcCreativesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listUgcCreativesForOfferProfile: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/ugc-creatives`,
      providesTags: (result, _err, offerProfileId) => [
        ...(result ?? []).map((item) => itemTag('UgcCreative', item.id)),
        listTag('UgcCreative', offerProfileId),
      ],
    }),
    getUgcCreative: builder.query<Entity, number>({
      query: (id) => `/ugc-creatives/${id}`,
      providesTags: (_result, _err, id) => [itemTag('UgcCreative', id)],
    }),
    generateUgcCreatives: builder.mutation<Entity[], { offerProfileId: number; count?: number; generationInstructions?: string }>({
      query: ({ offerProfileId, count = 3, generationInstructions = '' }) => ({
        url: `/offer-profiles/${offerProfileId}/ugc-creatives/generate`, method: 'POST',
        body: { count, generation_instructions: generationInstructions },
      }),
      invalidatesTags: (_result, _err, { offerProfileId }) => [listTag('UgcCreative', offerProfileId)],
    }),
    updateUgcCreative: builder.mutation<Entity, { id: number; offerProfileId: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({ url: `/ugc-creatives/${id}/update`, method: 'POST', body: { fields } }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        itemTag('UgcCreative', id),
        listTag('UgcCreative', offerProfileId),
      ],
    }),
    deleteUgcCreative: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/ugc-creatives/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        listTag('UgcCreative', offerProfileId),
        itemTag('UgcCreative', id),
      ],
    }),
  }),
})

export const {
  useListUgcCreativesForOfferProfileQuery,
  useGetUgcCreativeQuery,
  useGenerateUgcCreativesMutation,
  useUpdateUgcCreativeMutation,
  useDeleteUgcCreativeMutation,
} = ugcCreativesApi
