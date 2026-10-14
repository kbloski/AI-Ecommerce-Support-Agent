import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

interface PaginatedAnalysisQuestions {
  items: Entity[]
  page: number
  page_size: number
  total_items: number
  total_pages: number
}

export const analysisApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listAnalysisForOfferSource: builder.query<Entity[], number>({
      query: (offerSourceId) => `/offer-sources/${offerSourceId}/analysis`,
      providesTags: (result, _err, offerSourceId) => [
        ...(result ?? []).map((item) => itemTag('Analysis', item.id)),
        listTag('Analysis', offerSourceId),
      ],
    }),
    getAnalysis: builder.query<Entity, number>({
      query: (id) => `/analysis/${id}`,
      providesTags: (_result, _err, id) => [itemTag('Analysis', id)],
    }),
    listAnalysisQuestions: builder.query<PaginatedAnalysisQuestions, { analysisId: number; page?: number; pageSize?: number; isReviewed?: boolean; sort?: 'unreviewed_first' | 'reviewed_first' }>({
      query: ({ analysisId, page = 1, pageSize = 20, isReviewed, sort = 'unreviewed_first' }) => ({ url: `/analysis/${analysisId}/questions`, params: { page, page_size: pageSize, is_reviewed: isReviewed, sort } }),
      providesTags: (result, _err, { analysisId }) => [...(result?.items ?? []).map((item) => itemTag('AnalysisQuestion', item.id)), listTag('AnalysisQuestion', analysisId)],
    }),
    createAnalysis: builder.mutation<Entity, { offerSourceId: number }>({
      query: ({ offerSourceId }) => ({ url: `/offer-sources/${offerSourceId}/analysis/create`, method: 'POST' }),
      invalidatesTags: (_result, _err, { offerSourceId }) => [listTag('Analysis', offerSourceId)],
    }),
    generateAnalysisAnswers: builder.mutation<Entity, { offerSourceId: number; analysisId: number }>({
      query: ({ offerSourceId, analysisId }) =>
        ({ url: `/offer-sources/${offerSourceId}/analysis/${analysisId}/answers/generate`, method: 'POST' }),
      invalidatesTags: (_result, _err, { analysisId }) => [itemTag('Analysis', analysisId)],
    }),
    deleteAnalysis: builder.mutation<void, { id: number; offerSourceId: number }>({
      query: ({ id }) => ({ url: `/analysis/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, offerSourceId }) => [
        listTag('Analysis', offerSourceId),
        itemTag('Analysis', id),
      ],
    }),
    deleteAnalysisQuestion: builder.mutation<void, { id: number; analysisId: number }>({
      query: ({ id }) => ({ url: `/analysis-questions/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { analysisId }) => [itemTag('Analysis', analysisId)],
    }),
    updateAnalysisQuestion: builder.mutation<Entity, { id: number; analysisId: number; fields: Record<string, unknown> }>({
      query: ({ id, fields }) => ({ url: `/analysis-questions/${id}/update`, method: 'POST', body: { fields } }),
      invalidatesTags: (_result, _err, { analysisId }) => [itemTag('Analysis', analysisId)],
    }),
  }),
})

export const {
  useListAnalysisForOfferSourceQuery,
  useGetAnalysisQuery,
  useListAnalysisQuestionsQuery,
  useCreateAnalysisMutation,
  useGenerateAnalysisAnswersMutation,
  useDeleteAnalysisMutation,
  useDeleteAnalysisQuestionMutation,
  useUpdateAnalysisQuestionMutation,
} = analysisApi
