import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const checklistsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listChecklistsForOfferProfile: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/checklists`,
      providesTags: (result, _err, offerProfileId) => [
        ...(result ?? []).map((item) => itemTag('Checklist', item.id)),
        listTag('Checklist', offerProfileId),
      ],
    }),
    getChecklist: builder.query<Entity, number>({
      query: (id) => `/checklists/${id}`,
      providesTags: (_result, _err, id) => [itemTag('Checklist', id)],
    }),
    createChecklist: builder.mutation<Entity, { offerProfileId: number }>({
      query: ({ offerProfileId }) => ({
        url: `/offer-profiles/${offerProfileId}/checklists/create`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _err, { offerProfileId }) => [listTag('Checklist', offerProfileId)],
    }),
    generateChecklist: builder.mutation<
      Entity,
      { offerProfileId: number; checklistId: number }
    >({
      query: ({ offerProfileId, checklistId }) => ({
        url: `/offer-profiles/${offerProfileId}/checklists/${checklistId}/generate`,
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
    deleteChecklist: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/checklists/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        listTag('Checklist', offerProfileId),
        itemTag('Checklist', id),
      ],
    }),
  }),
})

export const {
  useListChecklistsForOfferProfileQuery,
  useGetChecklistQuery,
  useCreateChecklistMutation,
  useGenerateChecklistMutation,
  useDeleteChecklistItemMutation,
  useUpdateChecklistItemMutation,
  useDeleteChecklistMutation,
} = checklistsApi
