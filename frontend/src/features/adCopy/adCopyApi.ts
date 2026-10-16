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

export interface AdCopyStructure {
  id: string
  name: string
  description: string
  rules: string[]
  structure: { step: number; name: string; purpose: string }[]
}

export const adCopyApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAdCopyStructures: builder.query<AdCopyStructure[], void>({
      query: () => '/ad-copy-structures',
    }),
    listAdCopies: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/ad-copies`,
      providesTags: (result, _error, offerProfileId) => [
        listTag('AdCopy', offerProfileId), ...(result ?? []).map((item) => itemTag('AdCopy', item.id)),
      ],
    }),
    generateAdCopies: builder.mutation<Entity[], { offerProfileId: number; count: number; structureId: string | null; generationInstructions: string }>({
      query: ({ offerProfileId, count, structureId, generationInstructions }) => ({
        url: `/offer-profiles/${offerProfileId}/ad-copies/generate`, method: 'POST',
        body: { count, structure_id: structureId, generation_instructions: generationInstructions },
      }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('AdCopy', offerProfileId)],
    }),
    createAdCopy: builder.mutation<Entity, { offerProfileId: number; fields: AdCopyFields }>({
      query: ({ offerProfileId, fields }) => ({ url: `/offer-profiles/${offerProfileId}/ad-copies`, method: 'POST', body: fields }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('AdCopy', offerProfileId)],
    }),
    updateAdCopy: builder.mutation<Entity, { id: number; offerProfileId: number; fields: AdCopyFields; isReviewed?: boolean }>({
      query: ({ id, fields, isReviewed }) => ({ url: `/ad-copies/${id}/update`, method: 'POST', body: { ...fields, ...(isReviewed === undefined ? {} : { is_reviewed: isReviewed }) } }),
      invalidatesTags: (_result, _error, { id, offerProfileId }) => [itemTag('AdCopy', id), listTag('AdCopy', offerProfileId)],
    }),
    deleteAdCopy: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/ad-copies/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { id, offerProfileId }) => [itemTag('AdCopy', id), listTag('AdCopy', offerProfileId)],
    }),
  }),
})

export const {
  useListAdCopyStructuresQuery,
  useListAdCopiesQuery, useGenerateAdCopiesMutation, useCreateAdCopyMutation,
  useUpdateAdCopyMutation, useDeleteAdCopyMutation,
} = adCopyApi
