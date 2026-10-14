import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const brandMarketingApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listBrandMarketingForOfferSource: builder.query<Entity[], number>({
      query: (offerSourceId) => `/offer-sources/${offerSourceId}/brand-marketing`,
      providesTags: (result, _err, offerSourceId) => [
        ...(result ?? []).map((item) => itemTag('BrandMarketing', item.id)),
        listTag('BrandMarketing', offerSourceId),
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
    generateBrandMarketing: builder.mutation<Entity, { offerSourceId: number }>({
      query: ({ offerSourceId }) => ({ url: `/offer-sources/${offerSourceId}/brand-marketing/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, { offerSourceId }) => [listTag('BrandMarketing', offerSourceId)],
    }),
    deleteBrandMarketing: builder.mutation<void, { id: number; offerSourceId: number }>({
      query: ({ id }) => ({ url: `/brand-marketing/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerSourceId }) => [
        listTag('BrandMarketing', offerSourceId),
        itemTag('BrandMarketing', id),
      ],
    }),
  }),
})

export const {
  useListBrandMarketingForOfferSourceQuery,
  useGetBrandMarketingQuery,
  useGenerateBrandMarketingMutation,
  useDeleteBrandMarketingMutation,
  useUpdateBrandMarketingMutation,
} = brandMarketingApi
