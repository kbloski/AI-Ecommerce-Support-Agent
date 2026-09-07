import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

interface CreateAdExecutionArgs {
  creativeStrategyId: number
  creative_type: string
  platform: string
  format: string
  name?: string
}

export const adExecutionApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAdExecutionForCreativeStrategy: builder.query<Entity[], number>({
      query: (creativeStrategyId) => `/creative-strategy/${creativeStrategyId}/ad-execution`,
      providesTags: (result, _err, creativeStrategyId) => [
        ...(result ?? []).map((item) => itemTag('AdExecution', item.id)),
        listTag('AdExecution', creativeStrategyId),
      ],
    }),
    getAdExecution: builder.query<Entity, number>({
      query: (id) => `/ad-execution/${id}`,
      providesTags: (_result, _err, id) => [itemTag('AdExecution', id)],
    }),
    updateAdExecution: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/ad-execution/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('AdExecution', id)],
    }),
    createAdExecution: builder.mutation<Entity, CreateAdExecutionArgs>({
      query: ({ creativeStrategyId, ...params }) => ({
        url: `/creative-strategy/${creativeStrategyId}/ad-execution/create`,
        method: 'POST',
        params,
      }),
      invalidatesTags: (_result, _err, { creativeStrategyId }) => [
        listTag('AdExecution', creativeStrategyId),
      ],
    }),
    deleteAdExecution: builder.mutation<void, { id: number; creativeStrategyId: number }>({
      query: ({ id }) => ({ url: `/ad-execution/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, creativeStrategyId }) => [
        listTag('AdExecution', creativeStrategyId),
        itemTag('AdExecution', id),
      ],
    }),
  }),
})

export const {
  useListAdExecutionForCreativeStrategyQuery,
  useGetAdExecutionQuery,
  useCreateAdExecutionMutation,
  useDeleteAdExecutionMutation,
  useUpdateAdExecutionMutation,
} = adExecutionApi
