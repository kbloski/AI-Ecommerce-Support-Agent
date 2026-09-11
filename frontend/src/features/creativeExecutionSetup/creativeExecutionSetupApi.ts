import { api } from '@/store/api'
import { itemTag, listTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const creativeExecutionSetupApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listCreativeExecutionSetupsForAdSetup: builder.query<Entity[], number>({
      query: (adSetupId) => `/ad-setup/${adSetupId}/creative-execution-setups`,
      providesTags: (result, _error, adSetupId) => [
        ...(result ?? []).map((item) => itemTag('CreativeExecutionSetup', item.id)),
        listTag('CreativeExecutionSetup', adSetupId),
      ],
    }),
    getCreativeExecutionSetup: builder.query<Entity, number>({
      query: (id) => `/creative-execution-setups/${id}`,
      providesTags: (_result, _error, id) => [itemTag('CreativeExecutionSetup', id)],
    }),
    createCreativeExecutionSetup: builder.mutation<Entity, { adSetupId: number; fields: Record<string, unknown> }>({
      query: ({ adSetupId, fields }) => ({
        url: `/ad-setup/${adSetupId}/creative-execution-setups/create`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _error, { adSetupId }) => [listTag('CreativeExecutionSetup', adSetupId)],
    }),
    updateCreativeExecutionSetup: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/creative-execution-setups/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _error, { id }) => [itemTag('CreativeExecutionSetup', id)],
    }),
    deleteCreativeExecutionSetup: builder.mutation<void, { id: number; adSetupId: number }>({
      query: ({ id }) => ({ url: `/creative-execution-setups/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { id, adSetupId }) => [
        itemTag('CreativeExecutionSetup', id),
        listTag('CreativeExecutionSetup', adSetupId),
      ],
    }),
  }),
})

export const {
  useListCreativeExecutionSetupsForAdSetupQuery,
  useGetCreativeExecutionSetupQuery,
  useCreateCreativeExecutionSetupMutation,
  useUpdateCreativeExecutionSetupMutation,
  useDeleteCreativeExecutionSetupMutation,
} = creativeExecutionSetupApi
