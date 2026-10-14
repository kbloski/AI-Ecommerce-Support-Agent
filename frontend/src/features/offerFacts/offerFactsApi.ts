import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'
import type { PaginatedResult } from '@/features/offerSources/offerSourceApi'

export interface FactFields { name: string; description: string; evidence?: string | null; is_reviewed: boolean }
export type FactSort = 'created_at_desc' | 'created_at_asc' | 'name_asc' | 'name_desc'
const invalidates = (offerSourceId: number) => [listTag('OfferFact', offerSourceId), itemTag('OfferSource', offerSourceId)]
export const offerFactsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listOfferFacts: builder.query<PaginatedResult<Entity>, { offerSourceId: number; page?: number; pageSize?: number; search?: string; isReviewed?: boolean; sort?: FactSort }>({
      query: ({ offerSourceId, page = 1, pageSize = 20, search, isReviewed, sort }) => ({ url: `/offer-sources/${offerSourceId}/facts`, params: { page, page_size: pageSize, search, is_reviewed: isReviewed, sort } }),
      providesTags: (_result, _error, { offerSourceId }) => [listTag('OfferFact', offerSourceId)],
    }),
    generateOfferFacts: builder.mutation<{ items: Entity[]; created_count: number; skipped_count: number }, number>({
      query: (id) => ({ url: `/offer-sources/${id}/facts/generate`, method: 'POST' }),
      invalidatesTags: (_result, _error, id) => invalidates(id),
    }),
    createOfferFact: builder.mutation<Entity, { offerSourceId: number; fields: FactFields }>({
      query: ({ offerSourceId, fields }) => ({ url: `/offer-sources/${offerSourceId}/facts`, method: 'POST', body: fields }),
      invalidatesTags: (_result, _error, { offerSourceId }) => invalidates(offerSourceId),
    }),
    updateOfferFact: builder.mutation<Entity, { offerSourceId: number; id: number; fields: Partial<FactFields> }>({
      query: ({ id, fields }) => ({ url: `/offer-facts/${id}/update`, method: 'POST', body: { fields } }),
      invalidatesTags: (_result, _error, { offerSourceId }) => invalidates(offerSourceId),
    }),
    deleteOfferFact: builder.mutation<{ deleted: boolean }, { offerSourceId: number; id: number }>({
      query: ({ id }) => ({ url: `/offer-facts/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { offerSourceId }) => invalidates(offerSourceId),
    }),
  }),
})
export const { useListOfferFactsQuery, useGenerateOfferFactsMutation, useCreateOfferFactMutation, useUpdateOfferFactMutation, useDeleteOfferFactMutation } = offerFactsApi
