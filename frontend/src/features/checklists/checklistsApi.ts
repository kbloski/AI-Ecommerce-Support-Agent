import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const checklistsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listChecklistsForAnalysis: builder.query<Entity[], number>({
      query: (analysisId) => `/analysis/${analysisId}/checklists`,
      providesTags: (result, _err, analysisId) => [
        ...(result ?? []).map((item) => itemTag('Checklist', item.id)),
        listTag('Checklist', analysisId),
      ],
    }),
    getChecklist: builder.query<Entity, number>({
      query: (id) => `/checklists/${id}`,
      providesTags: (_result, _err, id) => [itemTag('Checklist', id)],
    }),
    createChecklist: builder.mutation<Entity, { offerProfileId: number; analysisId: number }>({
      query: ({ offerProfileId, analysisId }) => ({
        url: `/offer-profiles/${offerProfileId}/analysis/${analysisId}/checklists/create`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _err, { analysisId }) => [listTag('Checklist', analysisId)],
    }),
    generateChecklist: builder.mutation<
      Entity,
      { offerProfileId: number; analysisId: number; checklistId: number }
    >({
      query: ({ offerProfileId, analysisId, checklistId }) => ({
        url: `/offer-profiles/${offerProfileId}/analysis/${analysisId}/checklists/${checklistId}/generate`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _err, { checklistId }) => [itemTag('Checklist', checklistId)],
    }),
    deleteChecklistItem: builder.mutation<void, { id: number; checklistId: number }>({
      query: ({ id }) => ({ url: `/checklist-items/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { checklistId }) => [itemTag('Checklist', checklistId)],
    }),
    deleteChecklist: builder.mutation<void, { id: number; analysisId: number }>({
      query: ({ id }) => ({ url: `/checklists/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, analysisId }) => [
        listTag('Checklist', analysisId),
        itemTag('Checklist', id),
      ],
    }),
  }),
})

export const {
  useListChecklistsForAnalysisQuery,
  useGetChecklistQuery,
  useCreateChecklistMutation,
  useGenerateChecklistMutation,
  useDeleteChecklistItemMutation,
  useDeleteChecklistMutation,
} = checklistsApi
