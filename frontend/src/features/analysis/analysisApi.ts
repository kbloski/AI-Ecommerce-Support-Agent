import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export const analysisApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAnalysisForOfferProfile: builder.query<Entity[], number>({
      query: (offerProfileId) => `/offer-profiles/${offerProfileId}/analysis`,
      providesTags: (result, _err, offerProfileId) => [
        ...(result ?? []).map((item) => itemTag('Analysis', item.id)),
        listTag('Analysis', offerProfileId),
      ],
    }),
    getAnalysis: builder.query<Entity, number>({
      query: (id) => `/analysis/${id}`,
      providesTags: (_result, _err, id) => [itemTag('Analysis', id)],
    }),
    createAnalysis: builder.mutation<Entity, { offerProfileId: number }>({
      query: ({ offerProfileId }) => ({ url: `/offer-profiles/${offerProfileId}/analysis/create`, method: 'POST' }),
      invalidatesTags: (_result, _err, { offerProfileId }) => [listTag('Analysis', offerProfileId)],
    }),
    generateAnalysisAnswers: builder.mutation<Entity, { offerProfileId: number; analysisId: number }>({
      query: ({ offerProfileId, analysisId }) =>
        ({ url: `/offer-profiles/${offerProfileId}/analysis/${analysisId}/answers/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, { analysisId }) => [itemTag('Analysis', analysisId)],
    }),
    deleteAnalysis: builder.mutation<void, { id: number; offerProfileId: number }>({
      query: ({ id }) => ({ url: `/analysis/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerProfileId }) => [
        listTag('Analysis', offerProfileId),
        itemTag('Analysis', id),
      ],
    }),
    deleteAnalysisQuestion: builder.mutation<void, { id: number; analysisId: number }>({
      query: ({ id }) => ({ url: `/analysis-questions/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { analysisId }) => [itemTag('Analysis', analysisId)],
    }),
  }),
})

export const {
  useListAnalysisForOfferProfileQuery,
  useGetAnalysisQuery,
  useCreateAnalysisMutation,
  useGenerateAnalysisAnswersMutation,
  useDeleteAnalysisMutation,
  useDeleteAnalysisQuestionMutation,
} = analysisApi
