import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const generateAdApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAllGenerateAds: builder.query<Entity[], void>({
      query: () => '/generate-ads',
      providesTags: (result) => [
        ...(result ?? []).map((item) => itemTag('GenerateAd', item.id)),
        listTag('GenerateAd', 'ALL'),
      ],
    }),
    listGenerateAdsForSetup: builder.query<Entity[], number>({
      query: (setupId) => `/creative-execution-setups/${setupId}/generate-ads`,
      providesTags: (result, _err, setupId) => [
        ...(result ?? []).map((item) => itemTag('GenerateAd', item.id)),
        listTag('GenerateAd', setupId),
      ],
    }),
    getGenerateAd: builder.query<Entity, number>({
      query: (id) => `/generate-ad/${id}`,
      providesTags: (_result, _err, id) => [itemTag('GenerateAd', id)],
    }),
    updateGenerateAd: builder.mutation<
      Entity,
      { id: number; fields: Record<string, unknown> }
    >({
      query: ({ id, fields }) => ({
        url: `/generate-ad/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('GenerateAd', id)],
    }),
    generateAd: builder.mutation<
      Entity,
      {
        setupId: number
      }
    >({
      query: ({ setupId }) => ({
        url: `/creative-execution-setups/${setupId}/generate-ads/generate`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _err, { setupId }) => [
        listTag('GenerateAd', setupId),
        listTag('GenerateAd', 'ALL'),
      ],
    }),
    deleteGenerateAd: builder.mutation<void, { id: number; setupId: number }>({
      query: ({ id }) => ({ url: `/generate-ad/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, setupId }) => [
        listTag('GenerateAd', setupId),
        listTag('GenerateAd', 'ALL'),
        itemTag('GenerateAd', id),
      ],
    }),
  }),
})

export const {
  useListAllGenerateAdsQuery,
  useListGenerateAdsForSetupQuery,
  useGetGenerateAdQuery,
  useGenerateAdMutation,
  useDeleteGenerateAdMutation,
  useUpdateGenerateAdMutation,
} = generateAdApi
