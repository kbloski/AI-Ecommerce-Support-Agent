import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const pageContentPlanApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listPageContentPlanForPageBlueprint: builder.query<Entity[], number>({
      query: (pageBlueprintId) => `/page-blueprint/${pageBlueprintId}/page-content-plan`,
      providesTags: (result, _err, pageBlueprintId) => [
        ...(result ?? []).map((item) => itemTag('PageContentPlan', item.id)),
        listTag('PageContentPlan', pageBlueprintId),
      ],
    }),
    getPageContentPlan: builder.query<Entity, number>({
      query: (id) => `/page-content-plan/${id}`,
      providesTags: (_result, _err, id) => [itemTag('PageContentPlan', id)],
    }),
    updatePageContentPlan: builder.mutation<
      Entity,
      { id: number; fields: Record<string, unknown> }
    >({
      query: ({ id, fields }) => ({
        url: `/page-content-plan/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('PageContentPlan', id)],
    }),
    generatePageContentPlan: builder.mutation<Entity, number>({
      query: (pageBlueprintId) => ({ url: `/page-blueprint/${pageBlueprintId}/page-content-plan/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, pageBlueprintId) => [
        listTag('PageContentPlan', pageBlueprintId),
      ],
    }),
    deletePageContentPlan: builder.mutation<void, { id: number; pageBlueprintId: number }>({
      query: ({ id }) => ({ url: `/page-content-plan/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, pageBlueprintId }) => [
        listTag('PageContentPlan', pageBlueprintId),
        itemTag('PageContentPlan', id),
      ],
    }),
  }),
})

export const {
  useListPageContentPlanForPageBlueprintQuery,
  useGetPageContentPlanQuery,
  useGeneratePageContentPlanMutation,
  useDeletePageContentPlanMutation,
  useUpdatePageContentPlanMutation,
} = pageContentPlanApi
