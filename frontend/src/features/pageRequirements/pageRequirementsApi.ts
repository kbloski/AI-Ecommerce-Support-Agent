import { api } from '@/store/api'
import { listTag, itemTag } from '@/lib/tags'
import type { Entity } from '@/types'

export interface PageSectionRequirementInput {
  page_section_type_id: string
  requirement_type: 'required' | 'optional' | 'excluded'
  position?: number | null
}

export const pageRequirementsApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listPageRequirementsForPageStrategy: builder.query<Entity[], number>({
      query: (pageStrategyId) => `/page-strategy/${pageStrategyId}/page-requirements`,
      providesTags: (result, _err, pageStrategyId) => [
        ...(result ?? []).map((item) => itemTag('PageRequirements', item.id)),
        listTag('PageRequirements', pageStrategyId),
      ],
    }),
    getPageRequirements: builder.query<Entity, number>({
      query: (id) => `/page-requirements/${id}`,
      providesTags: (_result, _err, id) => [itemTag('PageRequirements', id)],
    }),
    createPageRequirements: builder.mutation<
      Entity,
      { pageStrategyId: number; name: string; sectionRequirements: PageSectionRequirementInput[] }
    >({
      query: ({ pageStrategyId, name, sectionRequirements }) => ({
        url: `/page-strategy/${pageStrategyId}/page-requirements/create`,
        method: 'POST',
        body: { name, section_requirements: sectionRequirements },
      }),
      invalidatesTags: (_result, _err, { pageStrategyId }) => [
        listTag('PageRequirements', pageStrategyId),
      ],
    }),
    generatePageRequirements: builder.mutation<Entity, number>({
      query: (pageStrategyId) => ({
        url: `/page-strategy/${pageStrategyId}/page-requirements/generate`,
        method: 'POST',
      }),
      invalidatesTags: (_result, _err, pageStrategyId) => [
        listTag('PageRequirements', pageStrategyId),
      ],
    }),
    updatePageRequirements: builder.mutation<
      Entity,
      { id: number; pageStrategyId: number; name: string; sectionRequirements: PageSectionRequirementInput[] }
    >({
      query: ({ id, name, sectionRequirements }) => ({
        url: `/page-requirements/${id}/update`,
        method: 'POST',
        body: { name, section_requirements: sectionRequirements },
      }),
      invalidatesTags: (_result, _err, { id, pageStrategyId }) => [
        itemTag('PageRequirements', id),
        listTag('PageRequirements', pageStrategyId),
      ],
    }),
    deletePageRequirements: builder.mutation<void, { id: number; pageStrategyId: number }>({
      query: ({ id }) => ({ url: `/page-requirements/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _err, { id, pageStrategyId }) => [
        listTag('PageRequirements', pageStrategyId),
        itemTag('PageRequirements', id),
      ],
    }),
  }),
})

export const {
  useListPageRequirementsForPageStrategyQuery,
  useGetPageRequirementsQuery,
  useCreatePageRequirementsMutation,
  useGeneratePageRequirementsMutation,
  useUpdatePageRequirementsMutation,
  useDeletePageRequirementsMutation,
} = pageRequirementsApi
