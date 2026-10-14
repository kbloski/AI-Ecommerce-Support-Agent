import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const checklistsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listChecklistsForOfferSource: builder.query<Entity[], number>({
      query: (offerSourceId) => `/offer-sources/${offerSourceId}/checklists`,
      providesTags: (result, _err, offerSourceId) => [
        ...(result ?? []).map((item) => itemTag('Checklist', item.id)),
        listTag('Checklist', offerSourceId),
      ],
    }),
    getChecklist: builder.query<Entity, number>({
      query: (id) => `/checklists/${id}`,
      providesTags: (_result, _err, id) => [itemTag('Checklist', id)],
    }),
    createChecklist: builder.mutation<Entity, { offerSourceId: number }>({
      query: ({ offerSourceId }) => ({
        url: `/offer-sources/${offerSourceId}/checklists/create`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _err, { offerSourceId }) => [listTag('Checklist', offerSourceId)],
    }),
    generateChecklist: builder.mutation<
      Entity,
      { offerSourceId: number; checklistId: number }
    >({
      query: ({ offerSourceId, checklistId }) => ({
        url: `/offer-sources/${offerSourceId}/checklists/${checklistId}/generate`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _err, { checklistId }) => [itemTag('Checklist', checklistId)],
    }),
    deleteChecklistItem: builder.mutation<void, { id: number; checklistId: number }>({
      query: ({ id }) => ({ url: `/checklist-items/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { checklistId }) => [itemTag('Checklist', checklistId)],
    }),
    updateChecklistItem: builder.mutation<Entity, { id: number; checklistId: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({ url: `/checklist-items/${id}/update`, method: 'POST', body: { fields } }),
      invalidatesTags: (_result, _err, { checklistId }) => [itemTag('Checklist', checklistId)],
    }),
    deleteChecklist: builder.mutation<void, { id: number; offerSourceId: number }>({
      query: ({ id }) => ({ url: `/checklists/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerSourceId }) => [
        listTag('Checklist', offerSourceId),
        itemTag('Checklist', id),
      ],
    }),
  }),
})

export const {
  useListChecklistsForOfferSourceQuery,
  useGetChecklistQuery,
  useCreateChecklistMutation,
  useGenerateChecklistMutation,
  useDeleteChecklistItemMutation,
  useUpdateChecklistItemMutation,
  useDeleteChecklistMutation,
} = checklistsApi
