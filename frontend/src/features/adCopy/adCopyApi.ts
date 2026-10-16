import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export interface AdCopyFields {
  name: string
  primary_text: string
  headline: string
  description: string
  cta: string | null
}

export const adCopyApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAdCopies: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/ad-copies`,
      providesTags: (result, _error, offerProfileId) => [
        listTag('AdCopy', offerProfileId), ...(result ?? []).map((item) => itemTag('AdCopy', item.id)),
      ],
    }),
    generateAdCopies: builder.mutation<Entity[], { offerProfileId: number; count: number; generationInstructions: string }>({
      query: ({ offerProfileId, count, generationInstructions }) => ({
        url: `/offer-profiles/${offerProfileId}/ad-copies/generate`, method: 'POST',
        body: { count, generation_instructions: generationInstructions },
      }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('AdCopy', offerProfileId)],
    }),
    createAdCopy: builder.mutation<Entity, { offerProfileId: number; fields: AdCopyFields }>({
      query: ({ offerProfileId, fields }) => ({ url: `/offer-profiles/${offerProfileId}/ad-copies`, method: 'POST', body: fields }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('AdCopy', offerProfileId)],
    }),
    updateAdCopy: builder.mutation<Entity, { id: number; offerProfileId: number; fields: AdCopyFields }>({
      query: ({ id, fields }) => ({ url: `/ad-copies/${id}/update`, method: 'POST', body: fields }),
      invalidatesTags: (_result, _error, { id, offerProfileId }) => [itemTag('AdCopy', id), listTag('AdCopy', offerProfileId)],
    }),
    deleteAdCopy: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/ad-copies/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { id, offerProfileId }) => [itemTag('AdCopy', id), listTag('AdCopy', offerProfileId)],
    }),
  }),
})

export const {
  useListAdCopiesQuery, useGenerateAdCopiesMutation, useCreateAdCopyMutation,
  useUpdateAdCopyMutation, useDeleteAdCopyMutation,
} = adCopyApi
