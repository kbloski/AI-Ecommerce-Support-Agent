import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'
import type { AdConceptFields } from '@/features/adConcepts/adConceptsApi'

export type CreativePlanFormat = AdConceptFields['format']

export interface CreativePlanFields {
  name: string
  description: string
  format: CreativePlanFormat
  plan: string
  ad_concept_id: number | null
}

export const creativePlansApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listCreativePlans: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/creative-plans`,
      providesTags: (result, _error, offerProfileId) => [
        listTag('CreativePlan', offerProfileId),
        ...(result ?? []).map((item) => itemTag('CreativePlan', item.id)),
      ],
    }),
    generateCreativePlans: builder.mutation<Entity[], {
      offerProfileId: number
      count: number
      adConceptId: number | null
      preferredFormat: CreativePlanFormat | null
      adFrameworkId?: string | null
      generationInstructions: string
    }>({
      query: ({ offerProfileId, count, adConceptId, preferredFormat, adFrameworkId, generationInstructions }) => ({
        url: `/offer-profiles/${offerProfileId}/creative-plans/generate`, method: 'POST',
        body: { count, ad_concept_id: adConceptId, preferred_format: preferredFormat, ad_framework_id: adFrameworkId, generation_instructions: generationInstructions },
      }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('CreativePlan', offerProfileId)],
    }),
    createCreativePlan: builder.mutation<Entity, { offerProfileId: number; fields: CreativePlanFields }>({
      query: ({ offerProfileId, fields }) => ({ url: `/offer-profiles/${offerProfileId}/creative-plans`, method: 'POST', body: fields }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('CreativePlan', offerProfileId)],
    }),
    updateCreativePlan: builder.mutation<Entity, { id: number; offerProfileId: number; fields: CreativePlanFields; isReviewed: boolean }>({
      query: ({ id, fields, isReviewed }) => ({ url: `/creative-plans/${id}/update`, method: 'POST', body: { ...fields, is_reviewed: isReviewed } }),
      invalidatesTags: (_result, _error, { id, offerProfileId }) => [itemTag('CreativePlan', id), listTag('CreativePlan', offerProfileId)],
    }),
    deleteCreativePlan: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/creative-plans/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { id, offerProfileId }) => [itemTag('CreativePlan', id), listTag('CreativePlan', offerProfileId)],
    }),
  }),
})

export const {
  useListCreativePlansQuery, useGenerateCreativePlansMutation, useCreateCreativePlanMutation,
  useUpdateCreativePlanMutation, useDeleteCreativePlanMutation,
} = creativePlansApi
