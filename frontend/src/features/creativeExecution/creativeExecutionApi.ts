import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const creativeExecutionApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listCreativeExecutionForAdExecution: builder.query<Entity[], number>({
      query: (adExecutionId) => `/ad-execution/${adExecutionId}/creative-execution`,
      providesTags: (result, _err, adExecutionId) => [
        ...(result ?? []).map((item) => itemTag('CreativeExecution', item.id)),
        listTag('CreativeExecution', adExecutionId),
      ],
    }),
    getCreativeExecution: builder.query<Entity, number>({
      query: (id) => `/creative-execution/${id}`,
      providesTags: (_result, _err, id) => [itemTag('CreativeExecution', id)],
    }),
    updateCreativeExecution: builder.mutation<
      Entity,
      { id: number; fields: Record<string, unknown> }
    >({
      query: ({ id, fields }) => ({
        url: `/creative-execution/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('CreativeExecution', id)],
    }),
    generateCreativeExecution: builder.mutation<
      Entity,
      {
        adExecutionId: number
        duration_seconds?: number
        number_of_slides?: number
        ad_framework_id?: string
        creative_angle_id?: string
        execution_style_id?: string
      }
    >({
      query: ({ adExecutionId, ...params }) => ({
        url: `/ad-execution/${adExecutionId}/creative-execution/generate`,
        method: 'POST',
        params,
      }),
      invalidatesTags: (_result, _err, { adExecutionId }) => [
        listTag('CreativeExecution', adExecutionId),
      ],
    }),
    deleteCreativeExecution: builder.mutation<void, { id: number; adExecutionId: number }>({
      query: ({ id }) => ({ url: `/creative-execution/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, adExecutionId }) => [
        listTag('CreativeExecution', adExecutionId),
        itemTag('CreativeExecution', id),
      ],
    }),
  }),
})

export const {
  useListCreativeExecutionForAdExecutionQuery,
  useGetCreativeExecutionQuery,
  useGenerateCreativeExecutionMutation,
  useDeleteCreativeExecutionMutation,
  useUpdateCreativeExecutionMutation,
} = creativeExecutionApi
