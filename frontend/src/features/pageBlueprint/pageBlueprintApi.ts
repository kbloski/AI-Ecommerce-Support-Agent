import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

import type { PageBlueprintFields } from './pageBlueprintFields'

export type PageBlueprintPageType = 'product_page' | null

export const pageBlueprintApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listPageBlueprintForOfferProfile: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/page-blueprints`,
      providesTags: (result, _err, offerProfileId) => [
        ...(result ?? []).map((item) => itemTag('PageBlueprint', item.id)),
        listTag('PageBlueprint', offerProfileId),
      ],
    }),
    getPageBlueprint: builder.query<Entity, number>({
      query: (id) => `/page-blueprints/${id}`,
      providesTags: (_result, _err, id) => [itemTag('PageBlueprint', id)],
    }),
    createPageBlueprint: builder.mutation<
      Entity,
      { offerProfileId: number; fields: PageBlueprintFields }
    >({
      query: ({ offerProfileId, fields }) => ({
        url: `/offer-profiles/${offerProfileId}/page-blueprints/create`,
        method: 'POST',
        body: fields,
      }),
      invalidatesTags: (_result, _err, { offerProfileId }) => [
        listTag('PageBlueprint', offerProfileId),
      ],
    }),
    generatePageBlueprint: builder.mutation<Entity, { offerProfileId: number; pageType: PageBlueprintPageType; sectionCount: number | null; generationInstructions: string }>({
      query: ({ offerProfileId, pageType, sectionCount, generationInstructions }) => ({
        url: `/offer-profiles/${offerProfileId}/page-blueprints/generate`,
        method: 'POST',
        body: { page_type: pageType, section_count: sectionCount, generation_instructions: generationInstructions },
      }),
      invalidatesTags: (_result, _err, { offerProfileId }) => [
        listTag('PageBlueprint', offerProfileId),
      ],
    }),
    updatePageBlueprint: builder.mutation<
      Entity,
      { id: number; offerProfileId: number; fields: PageBlueprintFields }
    >({
      query: ({ id, fields }) => ({
        url: `/page-blueprints/${id}/update`,
        method: 'POST',
        body: fields,
      }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        itemTag('PageBlueprint', id),
        listTag('PageBlueprint', offerProfileId),
      ],
    }),
    deletePageBlueprint: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/page-blueprints/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        listTag('PageBlueprint', offerProfileId),
        itemTag('PageBlueprint', id),
      ],
    }),
  }),
})

export const {
  useListPageBlueprintForOfferProfileQuery,
  useGetPageBlueprintQuery,
  useCreatePageBlueprintMutation,
  useGeneratePageBlueprintMutation,
  useUpdatePageBlueprintMutation,
  useDeletePageBlueprintMutation,
} = pageBlueprintApi
