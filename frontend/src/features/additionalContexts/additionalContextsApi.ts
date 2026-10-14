import { api } from '@/store/api'
import type { Entity } from '@/types'

export const additionalContextsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAdditionalContexts: builder.query<Entity[], void>({
      query: () => '/additional-contexts', providesTags: ['AdditionalContext'],
    }),
    listProfileContexts: builder.query<Entity[], number>({
      query: (id) => `/offer-profiles/${id}/additional-contexts`, providesTags: ['AdditionalContext'],
    }),
    createAdditionalContext: builder.mutation<Entity, { offerProfileId: number; name: string; content: string }>({
      query: ({ offerProfileId, ...body }) => ({ url: `/offer-profiles/${offerProfileId}/additional-contexts`, method: 'POST', body }), invalidatesTags: ['AdditionalContext'],
    }),
    updateAdditionalContext: builder.mutation<Entity, { id: number; name: string; content: string }>({
      query: ({ id, ...body }) => ({ url: `/additional-contexts/${id}/update`, method: 'POST', body }), invalidatesTags: ['AdditionalContext'],
    }),
    attachAdditionalContext: builder.mutation<{ attached: boolean }, { offerProfileId: number; contextId: number }>({
      query: ({ offerProfileId, contextId }) => ({ url: `/offer-profiles/${offerProfileId}/additional-contexts/${contextId}`, method: 'POST' }), invalidatesTags: ['AdditionalContext'],
    }),
    detachAdditionalContext: builder.mutation<{ detached: boolean }, { offerProfileId: number; contextId: number }>({
      query: ({ offerProfileId, contextId }) => ({ url: `/offer-profiles/${offerProfileId}/additional-contexts/${contextId}`, method: 'DELETE' }), invalidatesTags: ['AdditionalContext'],
    }),
  }),
})
export const { useListAdditionalContextsQuery, useListProfileContextsQuery, useCreateAdditionalContextMutation, useUpdateAdditionalContextMutation, useAttachAdditionalContextMutation, useDetachAdditionalContextMutation } = additionalContextsApi
