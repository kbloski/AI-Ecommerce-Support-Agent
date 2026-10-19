import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export interface BrandStyleFields {
  font_family: string
  background_color: string
  brand_color: string
}

export const brandStylesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listBrandStyles: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/brand-styles`,
      providesTags: (result, _error, offerProfileId) => [
        listTag('BrandStyle', offerProfileId),
        ...(result ?? []).map((item) => itemTag('BrandStyle', item.id)),
      ],
    }),
    generateBrandStyle: builder.mutation<Entity, { offerProfileId: number; generationInstructions: string }>({
      query: ({ offerProfileId, generationInstructions }) => ({
        url: `/offer-profiles/${offerProfileId}/brand-styles/generate`, method: 'POST',
        body: { generation_instructions: generationInstructions },
      }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('BrandStyle', offerProfileId)],
    }),
    createBrandStyle: builder.mutation<Entity, { offerProfileId: number; fields: BrandStyleFields }>({
      query: ({ offerProfileId, fields }) => ({ url: `/offer-profiles/${offerProfileId}/brand-styles`, method: 'POST', body: fields }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('BrandStyle', offerProfileId)],
    }),
    updateBrandStyle: builder.mutation<Entity, { id: number; offerProfileId: number; fields: BrandStyleFields }>({
      query: ({ id, fields }) => ({ url: `/brand-styles/${id}/update`, method: 'POST', body: fields }),
      invalidatesTags: (_result, _error, { id, offerProfileId }) => [itemTag('BrandStyle', id), listTag('BrandStyle', offerProfileId)],
    }),
    deleteBrandStyle: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/brand-styles/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { id, offerProfileId }) => [itemTag('BrandStyle', id), listTag('BrandStyle', offerProfileId)],
    }),
  }),
})

export const {
  useListBrandStylesQuery, useGenerateBrandStyleMutation, useCreateBrandStyleMutation,
  useUpdateBrandStyleMutation, useDeleteBrandStyleMutation,
} = brandStylesApi
