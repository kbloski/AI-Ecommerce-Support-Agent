import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

interface CreateAdSetupArgs {
  creativeStrategyId: number
  creative_type: string
  platform: string
  format: string
  name?: string
}

export const adSetupApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listCreativeTypes: builder.query<Array<{ id: string; name: string }>, void>({
      query: () => '/creative-types',
    }),
    listAdSetupForCreativeStrategy: builder.query<Entity[], number>({
      query: (creativeStrategyId) => `/creative-strategy/${creativeStrategyId}/ad-setup`,
      providesTags: (result, _err, creativeStrategyId) => [
        ...(result ?? []).map((item) => itemTag('AdSetup', item.id)),
        listTag('AdSetup', creativeStrategyId),
      ],
    }),
    getAdSetup: builder.query<Entity, number>({
      query: (id) => `/ad-setup/${id}`,
      providesTags: (_result, _err, id) => [itemTag('AdSetup', id)],
    }),
    updateAdSetup: builder.mutation<Entity, { id: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({
        url: `/ad-setup/${id}/update`,
        method: 'POST',
        body: { fields },
      }),
      invalidatesTags: (_result, _err, { id }) => [itemTag('AdSetup', id)],
    }),
    createAdSetup: builder.mutation<Entity, CreateAdSetupArgs>({
      query: ({ creativeStrategyId, ...params }) => ({
        url: `/creative-strategy/${creativeStrategyId}/ad-setup/create`,
        method: 'POST',
        params,
      }),
      invalidatesTags: (_result, _err, { creativeStrategyId }) => [
        listTag('AdSetup', creativeStrategyId),
      ],
    }),
    deleteAdSetup: builder.mutation<void, { id: number; creativeStrategyId: number }>({
      query: ({ id }) => ({ url: `/ad-setup/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, creativeStrategyId }) => [
        listTag('AdSetup', creativeStrategyId),
        itemTag('AdSetup', id),
      ],
    }),
  }),
})

export const {
  useListCreativeTypesQuery,
  useListAdSetupForCreativeStrategyQuery,
  useGetAdSetupQuery,
  useCreateAdSetupMutation,
  useDeleteAdSetupMutation,
  useUpdateAdSetupMutation,
} = adSetupApi
