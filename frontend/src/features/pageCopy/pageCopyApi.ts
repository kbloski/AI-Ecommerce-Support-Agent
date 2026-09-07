import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const pageCopyApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listPageCopyForPageContentPlan: builder.query<Entity[], number>({
      query: (pageContentPlanId) => `/page-content-plan/${pageContentPlanId}/page-copy`,
      providesTags: (result, _err, pageContentPlanId) => [
        ...(result ?? []).map((item) => itemTag('PageCopy', item.id)),
        listTag('PageCopy', pageContentPlanId),
      ],
    }),
    getPageCopy: builder.query<Entity, number>({
      query: (id) => `/page-copy/${id}`,
      providesTags: (_result, _err, id) => [itemTag('PageCopy', id)],
    }),
    updatePageCopy: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/page-copy/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('PageCopy', id)],
    }),
    generatePageCopy: builder.mutation<Entity, number>({
      query: (pageContentPlanId) => ({ url: `/page-content-plan/${pageContentPlanId}/page-copy/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, pageContentPlanId) => [
        listTag('PageCopy', pageContentPlanId),
      ],
    }),
    deletePageCopy: builder.mutation<void, { id: number; pageContentPlanId: number }>({
      query: ({ id }) => ({ url: `/page-copy/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, pageContentPlanId }) => [
        listTag('PageCopy', pageContentPlanId),
        itemTag('PageCopy', id),
      ],
    }),
  }),
})

export const {
  useListPageCopyForPageContentPlanQuery,
  useGetPageCopyQuery,
  useGeneratePageCopyMutation,
  useDeletePageCopyMutation,
  useUpdatePageCopyMutation,
} = pageCopyApi
