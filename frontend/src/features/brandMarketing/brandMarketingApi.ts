import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const brandMarketingApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listBrandMarketingForOfferProfile: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/brand-marketing`,
      providesTags: (result, _err, offerProfileId) => [
        ...(result ?? []).map((item) => itemTag('BrandMarketing', item.id)),
        listTag('BrandMarketing', offerProfileId),
      ],
    }),
    getBrandMarketing: builder.query<Entity, number>({
      query: (id) => `/brand-marketing/${id}`,
      providesTags: (_result, _err, id) => [itemTag('BrandMarketing', id)],
    }),
    updateBrandMarketing: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/brand-marketing/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('BrandMarketing', id)],
    }),
    generateBrandMarketing: builder.mutation<Entity, { offerProfileId: number }>({
      query: ({ offerProfileId }) => ({ url: `/offer-profiles/${offerProfileId}/brand-marketing/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, { offerProfileId }) => [listTag('BrandMarketing', offerProfileId)],
    }),
    deleteBrandMarketing: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/brand-marketing/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        listTag('BrandMarketing', offerProfileId),
        itemTag('BrandMarketing', id),
      ],
    }),
  }),
})

export const {
  useListBrandMarketingForOfferProfileQuery,
  useGetBrandMarketingQuery,
  useGenerateBrandMarketingMutation,
  useDeleteBrandMarketingMutation,
  useUpdateBrandMarketingMutation,
} = brandMarketingApi
