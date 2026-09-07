import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const pageBlueprintApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listPageBlueprintForPageRequirements: builder.query<Entity[], number>({
      query: (pageRequirementsId) => `/page-requirements/${pageRequirementsId}/page-blueprint`,
      providesTags: (result, _err, pageRequirementsId) => [
        ...(result ?? []).map((item) => itemTag('PageBlueprint', item.id)),
        listTag('PageBlueprint', pageRequirementsId),
      ],
    }),
    getPageBlueprint: builder.query<Entity, number>({
      query: (id) => `/page-blueprint/${id}`,
      providesTags: (_result, _err, id) => [itemTag('PageBlueprint', id)],
    }),
    updatePageBlueprint: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/page-blueprint/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('PageBlueprint', id)],
    }),
    generatePageBlueprint: builder.mutation<Entity, number>({
      query: (pageRequirementsId) => ({ url: `/page-requirements/${pageRequirementsId}/page-blueprint/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, pageRequirementsId) => [listTag('PageBlueprint', pageRequirementsId)],
    }),
    deletePageBlueprint: builder.mutation<void, { id: number; pageRequirementsId: number }>({
      query: ({ id }) => ({ url: `/page-blueprint/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, pageRequirementsId }) => [
        listTag('PageBlueprint', pageRequirementsId),
        itemTag('PageBlueprint', id),
      ],
    }),
  }),
})

export const {
  useListPageBlueprintForPageRequirementsQuery,
  useGetPageBlueprintQuery,
  useGeneratePageBlueprintMutation,
  useDeletePageBlueprintMutation,
  useUpdatePageBlueprintMutation,
} = pageBlueprintApi
