import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export interface AdConceptFields {
  name: string
  description: string
  format: 'video' | 'image'
  core_idea: string
  key_message: string
  generation_mode: 'standard' | 'experimental'
  marketing_angle_ids: number[]
}

export type AdConceptContentFields = Omit<AdConceptFields, 'generation_mode' | 'marketing_angle_ids'>

export const adConceptsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAdConcepts: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/ad-concepts`,
      providesTags: (_result, _error, offerProfileId) => [listTag('AdConcept', offerProfileId)],
    }),
    generateAdConcepts: builder.mutation<Entity[], { offerProfileId: number; count: number; generationMode: 'standard' | 'experimental'; marketingAngleIds: number[]; preferredFormat: 'image' | 'video' | null; generationInstructions: string }>({
      query: ({ offerProfileId, count, generationMode, marketingAngleIds, preferredFormat, generationInstructions }) => ({
        url: `/offer-profiles/${offerProfileId}/ad-concepts/generate`, method: 'POST',
        body: { count, generation_mode: generationMode, marketing_angle_ids: marketingAngleIds, preferred_format: preferredFormat, generation_instructions: generationInstructions },
      }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('AdConcept', offerProfileId)],
    }),
    createAdConcept: builder.mutation<Entity, { offerProfileId: number; fields: AdConceptFields }>({
      query: ({ offerProfileId, fields }) => ({ url: `/offer-profiles/${offerProfileId}/ad-concepts`, method: 'POST', body: fields }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('AdConcept', offerProfileId)],
    }),
    updateAdConcept: builder.mutation<Entity, { id: number; offerProfileId: number; fields: AdConceptFields | AdConceptContentFields; isReviewed: boolean }>({
      query: ({ id, fields, isReviewed }) => ({ url: `/ad-concepts/${id}/update`, method: 'POST', body: { ...fields, is_reviewed: isReviewed } }),
      invalidatesTags: (_result, _error, { offerProfileId, id }) => [listTag('AdConcept', offerProfileId), itemTag('AdConcept', id)],
    }),
    deleteAdConcept: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/ad-concepts/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('AdConcept', offerProfileId)],
    }),
  }),
})

export const { useListAdConceptsQuery, useGenerateAdConceptsMutation, useCreateAdConceptMutation, useUpdateAdConceptMutation, useDeleteAdConceptMutation } = adConceptsApi
