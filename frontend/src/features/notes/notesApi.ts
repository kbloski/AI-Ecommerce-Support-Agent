import { api } from '@/store/api'
import type { Entity } from '@/types'

export interface Note extends Entity {
  title: string
  content: string
  created_at: string
  updated_at: string
}

export const notesApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listNotes: builder.query<Note[], void>({
      query: () => '/notes',
      providesTags: ['Note'],
    }),
    listProfileNotes: builder.query<Note[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/notes`,
      providesTags: ['Note'],
    }),
    createNote: builder.mutation<Note, { title: string; content: string }>({
      query: (body) => ({ url: '/notes', method: 'POST', body }),
      invalidatesTags: ['Note'],
    }),
    createProfileNote: builder.mutation<Note, { offerProfileId: number; title: string; content: string }>({
      query: ({ offerProfileId, ...body }) => ({ url: `/offer-profiles/${offerProfileId}/notes`, method: 'POST', body }),
      invalidatesTags: ['Note'],
    }),
    updateNote: builder.mutation<Note, { id: number; title: string; content: string }>({
      query: ({ id, ...body }) => ({ url: `/notes/${id}/update`, method: 'POST', body }),
      invalidatesTags: ['Note'],
    }),
    attachNote: builder.mutation<{ attached: boolean }, { offerProfileId: number; noteId: number }>({
      query: ({ offerProfileId, noteId }) => ({ url: `/offer-profiles/${offerProfileId}/notes/${noteId}`, method: 'POST' }),
      invalidatesTags: ['Note'],
    }),
    detachNote: builder.mutation<{ detached: boolean }, { offerProfileId: number; noteId: number }>({
      query: ({ offerProfileId, noteId }) => ({ url: `/offer-profiles/${offerProfileId}/notes/${noteId}`, method: 'DELETE' }),
      invalidatesTags: ['Note'],
    }),
    deleteNote: builder.mutation<{ deleted: boolean }, number>({
      query: (noteId) => ({ url: `/notes/${noteId}`, method: 'DELETE' }),
      invalidatesTags: ['Note'],
    }),
  }),
})

export const {
  useListNotesQuery,
  useListProfileNotesQuery,
  useCreateNoteMutation,
  useCreateProfileNoteMutation,
  useUpdateNoteMutation,
  useAttachNoteMutation,
  useDetachNoteMutation,
  useDeleteNoteMutation,
} = notesApi
