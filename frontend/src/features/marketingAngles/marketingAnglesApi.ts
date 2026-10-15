import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export interface MarketingAngleFields {
  name: string
  description: string
  core_message: string
  value_proposition: string
  pain_point: string
  desire: string
  emotional_driver: string
  supporting_arguments: string[]
  proof_points: string[]
}

export const marketingAnglesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listMarketingAngles: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/marketing-angles`,
      providesTags: (_result, _error, offerProfileId) => [listTag('MarketingAngle', offerProfileId)],
    }),
    generateMarketingAngles: builder.mutation<Entity[], { offerProfileId: number; count: number; targetAudienceIds: number[]; generationInstructions: string }>({
      query: ({ offerProfileId, count, targetAudienceIds, generationInstructions }) => ({
        url: `/offer-profiles/${offerProfileId}/marketing-angles/generate`, method: 'POST',
        body: { count, target_audience_ids: targetAudienceIds, generation_instructions: generationInstructions },
      }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('MarketingAngle', offerProfileId)],
    }),
    createMarketingAngle: builder.mutation<Entity, { offerProfileId: number; fields: MarketingAngleFields }>({
      query: ({ offerProfileId, fields }) => ({ url: `/offer-profiles/${offerProfileId}/marketing-angles`, method: 'POST', body: fields }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('MarketingAngle', offerProfileId)],
    }),
    updateMarketingAngle: builder.mutation<Entity, { id: number; offerProfileId: number; fields: MarketingAngleFields; isReviewed: boolean }>({
      query: ({ id, fields, isReviewed }) => ({ url: `/marketing-angles/${id}/update`, method: 'POST', body: { ...fields, is_reviewed: isReviewed } }),
      invalidatesTags: (_result, _error, { offerProfileId, id }) => [listTag('MarketingAngle', offerProfileId), itemTag('MarketingAngle', id)],
    }),
    deleteMarketingAngle: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/marketing-angles/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('MarketingAngle', offerProfileId)],
    }),
  }),
})

export const { useListMarketingAnglesQuery, useGenerateMarketingAnglesMutation, useCreateMarketingAngleMutation, useUpdateMarketingAngleMutation, useDeleteMarketingAngleMutation } = marketingAnglesApi
