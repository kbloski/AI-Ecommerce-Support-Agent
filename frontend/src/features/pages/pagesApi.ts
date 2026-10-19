import { api } from '@/store/api'
import { itemTag, listTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const pagesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listPages: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/pages`,
      providesTags: (result, _error, offerProfileId) => [
        ...(result ?? []).map((page) => itemTag('Page', page.id)),
        listTag('Page', offerProfileId),
      ],
    }),
    getPage: builder.query<Entity, number>({
      query: (id) => `/pages/${id}`,
      providesTags: (_result, _error, id) => [itemTag('Page', id)],
    }),
    generatePage: builder.mutation<Entity, { offerProfileId: number; pageBlueprintId: number | null; generationInstructions: string }>({
      query: ({ offerProfileId, pageBlueprintId, generationInstructions }) => ({
        url: `/offer-profiles/${offerProfileId}/pages/generate`,
        method: 'POST',
        body: { page_blueprint_id: pageBlueprintId, generation_instructions: generationInstructions },
      }),
      invalidatesTags: (_result, _error, { offerProfileId }) => [listTag('Page', offerProfileId)],
    }),
    deletePage: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/pages/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { id, offerProfileId }) => [itemTag('Page', id), listTag('Page', offerProfileId)],
    }),
  }),
})

export const { useListPagesQuery, useGetPageQuery, useGeneratePageMutation, useDeletePageMutation } = pagesApi
