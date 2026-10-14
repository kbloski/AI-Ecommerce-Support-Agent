import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export interface PaginatedResult<T> {
  items: T[]
  page: number
  page_size: number
  total_items: number
  total_pages: number
}

export type OfferSourceElementSort = 'created_at_desc' | 'created_at_asc' | 'name_asc' | 'name_desc'

export const offerSourceApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listOfferSourceForOffer: builder.query<Entity[], number>({
      query: (offerId) => `/offers/${offerId}/offer-sources`,
      providesTags: (result, _err, offerId) => [
        ...(result ?? []).map((item) => itemTag('OfferSource', item.id)),
        listTag('OfferSource', offerId),
      ],
    }),
    getOfferSource: builder.query<Entity, number>({
      query: (id) => `/offer-sources/${id}`,
      providesTags: (_result, _err, id) => [itemTag('OfferSource', id)],
    }),
    listOfferSourceElements: builder.query<PaginatedResult<Entity>, {
      offerSourceId: number
      page?: number
      pageSize?: number
      search?: string
      elementType?: string
      isReviewed?: boolean
      sort?: OfferSourceElementSort
    }>({
      query: ({ offerSourceId, page = 1, pageSize = 20, search, elementType, isReviewed, sort = 'created_at_desc' }) => ({
        url: `/offer-sources/${offerSourceId}/elements`,
        params: {
          page,
          page_size: pageSize,
          search: search || undefined,
          element_type: elementType || undefined,
          is_reviewed: isReviewed,
          sort,
        },
      }),
      providesTags: (result, _err, { offerSourceId }) => [
        ...(result?.items ?? []).map((item) => itemTag('OfferSourceElement', item.id)),
        listTag('OfferSourceElement', offerSourceId),
      ],
    }),
    listOfferSourceElementTypes: builder.query<string[], void>({
      query: () => '/offer-source-elements/types',
    }),
    createOfferSourceElement: builder.mutation<Entity, {
      offerSourceId: number
      type: string
      name: string
      description?: string
      is_reviewed: boolean
    }>({
      query: ({ offerSourceId, ...body }) => ({
        url: `/offer-sources/${offerSourceId}/elements`,
        method: 'POST',
        body,
      }),
      invalidatesTags: (_result, _err, { offerSourceId }) => [
        listTag('OfferSourceElement', offerSourceId),
      ],
    }),
    updateOfferSourceElement: builder.mutation<Entity, {
      id: number
      offerSourceId: number
      fields: Record<string, unknown>
    }>({
      query: ({ id, fields }) => ({
        url: `/offer-source-elements/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id, offerSourceId }) => [
        itemTag('OfferSourceElement', id),
        listTag('OfferSourceElement', offerSourceId),
      ],
    }),
    deleteOfferSourceElement: builder.mutation<void, { id: number; offerSourceId: number }>({
      query: ({ id }) => ({ url: `/offer-source-elements/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerSourceId }) => [
        itemTag('OfferSourceElement', id),
        listTag('OfferSourceElement', offerSourceId),
      ],
    }),
    generateOfferSourceElements: builder.mutation<Entity[], {
      offerSourceId: number
      element_types: string[]
      examples_per_type: number
    }>({
      query: ({ offerSourceId, element_types, examples_per_type }) => ({
        url: `/offer-sources/${offerSourceId}/elements/generate`,
        method: 'POST',
        body: { element_types, examples_per_type },
      }),
      invalidatesTags: (_result, _err, { offerSourceId }) => [
        listTag('OfferSourceElement', offerSourceId),
      ],
    }),
    updateOfferSource: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/offer-sources/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('OfferSource', id)],
    }),
    generateOfferSource: builder.mutation<Entity, { offerId: number }>({
      query: ({ offerId }) => ({ url: `/offers/${offerId}/offer-sources/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, { offerId }) => [listTag('OfferSource', offerId)],
    }),
    deleteOfferSource: builder.mutation<void, { id: number; offerId: number }>({
      query: ({ id }) => ({ url: `/offer-sources/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerId }) => [
        listTag('OfferSource', offerId),
        itemTag('OfferSource', id),
      ],
    }),
  }),
})

export const {
  useListOfferSourceForOfferQuery,
  useGetOfferSourceQuery,
  useListOfferSourceElementsQuery,
  useListOfferSourceElementTypesQuery,
  useCreateOfferSourceElementMutation,
  useUpdateOfferSourceElementMutation,
  useDeleteOfferSourceElementMutation,
  useGenerateOfferSourceElementsMutation,
  useGenerateOfferSourceMutation,
  useDeleteOfferSourceMutation,
  useUpdateOfferSourceMutation,
} = offerSourceApi
