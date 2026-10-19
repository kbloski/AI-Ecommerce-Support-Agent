import { api } from '@/store/api'
import { itemTag } from '@/lib/tags'
import type { ResourceContextInclude, ResourceContextRequest, ResourceContextType } from '@/features/resources/resourceContextApi'

export interface ChatContext {
  type: ResourceContextType
  id: number
  include: ResourceContextInclude[]
  target_audience_ids: number[]
  marketing_angle_ids: number[]
  ad_concept_ids: number[]
  creative_plan_ids: number[]
  ugc_creative_ids: number[]
  ad_copy_ids: number[]
  brand_style_ids: number[]
  include_offer_facts: boolean
  include_additional_contexts: boolean
}

export interface ChatMessage {
  id: number
  conversation_id: number
  role: 'user' | 'assistant'
  content: string
  prompt_tokens: number | null
  completion_tokens: number | null
  created_at: string
}

export interface ChatConversation {
  id: number
  title: string
  context: ChatContext
  created_at: string
  updated_at: string
  messages?: ChatMessage[]
}

export interface ChatUsage {
  context_tokens: number
  history_tokens: number
  used_tokens: number
  limit_tokens: number
  answer_reserve_tokens: number
  messages_in_context: number
  messages_total: number
  too_large: boolean
  last_prompt_tokens: number | null
  last_completion_tokens: number | null
}

export const toChatContext =(request: ResourceContextRequest): ChatContext => ({
  type: request.type,
  id: request.id,
  include: request.include ?? [],
  target_audience_ids: request.targetAudienceIds ?? [],
  marketing_angle_ids: request.marketingAngleIds ?? [],
  ad_concept_ids: request.adConceptIds ?? [],
  creative_plan_ids: request.creativePlanIds ?? [],
  ugc_creative_ids: request.ugcCreativeIds ?? [],
  ad_copy_ids: request.adCopyIds ?? [],
  brand_style_ids: request.brandStyleIds ?? [],
  include_offer_facts: request.includeOfferFacts ?? true,
  include_additional_contexts: request.includeAdditionalContexts ?? true,
})

export const toResourceRequest = (context: ChatContext): ResourceContextRequest => ({
  type: context.type,
  id: context.id,
  include: context.include,
  targetAudienceIds: context.target_audience_ids,
  marketingAngleIds: context.marketing_angle_ids,
  adConceptIds: context.ad_concept_ids,
  creativePlanIds: context.creative_plan_ids,
  ugcCreativeIds: context.ugc_creative_ids,
  adCopyIds: context.ad_copy_ids,
  brandStyleIds: context.brand_style_ids ?? [],
  includeOfferFacts: context.include_offer_facts,
  includeAdditionalContexts: context.include_additional_contexts,
})

export const chatApi = api.injectEndpoints({
  endpoints: (builder) => ({
    listConversations: builder.query<ChatConversation[], void>({
      query: () => '/chat/conversations',
      providesTags: ['ChatConversation'],
    }),
    getConversation: builder.query<ChatConversation, number>({
      query: (id) => `/chat/conversations/${id}`,
      providesTags: (_result, _error, id) => [itemTag('ChatConversation', id)],
    }),
    getConversationUsage: builder.query<ChatUsage, number>({
      query: (id) => `/chat/conversations/${id}/usage`,
      providesTags: (_result, _error, id) => [itemTag('ChatConversation', id)],
    }),
    createConversation: builder.mutation<ChatConversation, { title?: string; context: ChatContext }>({
      query: (body) => ({ url: '/chat/conversations', method: 'POST', body }),
      invalidatesTags: ['ChatConversation'],
    }),
    updateConversation: builder.mutation<ChatConversation, { id: number; title?: string; context?: ChatContext }>({
      query: ({ id, ...body }) => ({ url: `/chat/conversations/${id}/update`, method: 'POST', body }),
      invalidatesTags: (_result, _error, { id }) => ['ChatConversation', itemTag('ChatConversation', id)],
    }),
    deleteConversation: builder.mutation<{ deleted: boolean }, number>({
      query: (id) => ({ url: `/chat/conversations/${id}/delete`, method: 'DELETE' }),
      invalidatesTags: ['ChatConversation'],
    }),
    sendMessage: builder.mutation<{ conversation: ChatConversation; messages: ChatMessage[] }, { id: number; content: string }>({
      query: ({ id, content }) => ({ url: `/chat/conversations/${id}/messages`, method: 'POST', body: { content } }),
      invalidatesTags: (_result, _error, { id }) => ['ChatConversation', itemTag('ChatConversation', id)],
    }),
    forkFromMessage: builder.mutation<ChatConversation, { messageId: number }>({
      query: ({ messageId }) => ({ url: `/chat/messages/${messageId}/fork`, method: 'POST' }),
      invalidatesTags: ['ChatConversation'],
    }),
    deleteMessage: builder.mutation<ChatConversation, { messageId: number; conversationId: number }>({
      query: ({ messageId }) => ({ url: `/chat/messages/${messageId}/delete`, method: 'DELETE' }),
      invalidatesTags: (_result, _error, { conversationId }) => ['ChatConversation', itemTag('ChatConversation', conversationId)],
    }),
    regenerateMessage: builder.mutation<ChatConversation, { messageId: number; conversationId: number }>({
      query: ({ messageId }) => ({ url: `/chat/messages/${messageId}/regenerate`, method: 'POST' }),
      invalidatesTags: (_result, _error, { conversationId }) => ['ChatConversation', itemTag('ChatConversation', conversationId)],
    }),
    editMessage: builder.mutation<ChatConversation, { messageId: number; conversationId: number; content: string }>({
      query: ({ messageId, content }) => ({ url: `/chat/messages/${messageId}/edit`, method: 'POST', body: { content } }),
      invalidatesTags: (_result, _error, { conversationId }) => ['ChatConversation', itemTag('ChatConversation', conversationId)],
    }),
  }),
})

export const {
  useListConversationsQuery, useGetConversationQuery, useGetConversationUsageQuery, useCreateConversationMutation,
  useUpdateConversationMutation, useDeleteConversationMutation, useSendMessageMutation,
  useForkFromMessageMutation, useDeleteMessageMutation, useRegenerateMessageMutation, useEditMessageMutation,
} = chatApi
