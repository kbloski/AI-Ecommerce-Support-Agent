import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const brandMarketingApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listBrandMarketingForKnowledge: builder.query<Entity[], number>({
      query: (knowledgeId) => `/knowledges/${knowledgeId}/brand-marketing`,
      providesTags: (result, _err, knowledgeId) => [
        ...(result ?? []).map((item) => itemTag('BrandMarketing', item.id)),
        listTag('BrandMarketing', knowledgeId),
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
    generateBrandMarketing: builder.mutation<Entity, { knowledgeId: number }>({
      query: ({ knowledgeId }) => ({ url: `/knowledges/${knowledgeId}/brand-marketing/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, { knowledgeId }) => [listTag('BrandMarketing', knowledgeId)],
    }),
    deleteBrandMarketing: builder.mutation<void, { id: number; knowledgeId: number }>({
      query: ({ id }) => ({ url: `/brand-marketing/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, knowledgeId }) => [
        listTag('BrandMarketing', knowledgeId),
        itemTag('BrandMarketing', id),
      ],
    }),
  }),
})

export const {
  useListBrandMarketingForKnowledgeQuery,
  useGetBrandMarketingQuery,
  useGenerateBrandMarketingMutation,
  useDeleteBrandMarketingMutation,
  useUpdateBrandMarketingMutation,
} = brandMarketingApi
