import { api } from '@/store/api'

export type ResourceContextType = 'offer_raw' | 'offer_source' | 'offer_profile'
export type ResourceContextInclude = 'offer_raw' | 'offer_source' | 'target_audiences' | 'marketing_angle' | 'ad_concept' | 'creative_plan' | 'ugc_creative' | 'ad_copy' | 'brand_style' | 'analysis' | 'checklist' | 'page_blueprint' | 'page' | 'note'

export interface ResourceContextRequest {
  type: ResourceContextType
  id: number
  include?: ResourceContextInclude[]
  targetAudienceIds?: number[]
  marketingAngleIds?: number[]
  adConceptIds?: number[]
  creativePlanIds?: number[]
  ugcCreativeIds?: number[]
  adCopyIds?: number[]
  brandStyleIds?: number[]
  analysisIds?: number[]
  checklistIds?: number[]
  pageBlueprintIds?: number[]
  pageIds?: number[]
  noteIds?: number[]
  includeOfferFacts?: boolean
  includeAdditionalContexts?: boolean
}

function contextUrl({ type, id, include = [], targetAudienceIds = [], marketingAngleIds = [], adConceptIds = [], creativePlanIds = [], ugcCreativeIds = [], adCopyIds = [], brandStyleIds = [], analysisIds = [], checklistIds = [], pageBlueprintIds = [], pageIds = [], noteIds = [], includeOfferFacts, includeAdditionalContexts }: ResourceContextRequest, download = false) {
  const params = new URLSearchParams()
  include.forEach((item) => params.append('include', item))
  targetAudienceIds.forEach((audienceId) => params.append('target_audience_ids', String(audienceId)))
  marketingAngleIds.forEach((angleId) => params.append('marketing_angle_ids', String(angleId)))
  adConceptIds.forEach((conceptId) => params.append('ad_concept_ids', String(conceptId)))
  creativePlanIds.forEach((planId) => params.append('creative_plan_ids', String(planId)))
  ugcCreativeIds.forEach((creativeId) => params.append('ugc_creative_ids', String(creativeId)))
  adCopyIds.forEach((copyId) => params.append('ad_copy_ids', String(copyId)))
  brandStyleIds.forEach((styleId) => params.append('brand_style_ids', String(styleId)))
  analysisIds.forEach((itemId) => params.append('analysis_ids', String(itemId)))
  checklistIds.forEach((itemId) => params.append('checklist_ids', String(itemId)))
  pageBlueprintIds.forEach((itemId) => params.append('page_blueprint_ids', String(itemId)))
  pageIds.forEach((itemId) => params.append('page_ids', String(itemId)))
  noteIds.forEach((itemId) => params.append('note_ids', String(itemId)))
  if (includeOfferFacts !== undefined) params.set('include_offer_facts', String(includeOfferFacts))
  if (includeAdditionalContexts !== undefined) params.set('include_additional_contexts', String(includeAdditionalContexts))
  const query = params.toString()
  return `/resources/${type}/${id}/context${download ? '/download' : ''}${query ? `?${query}` : ''}`
}

export const resourceContextApi = api.injectEndpoints({
  endpoints: (builder) => ({
    getResourceContext: builder.query<string, ResourceContextRequest>({
      query: (request) => ({ url: contextUrl(request), responseHandler: (response: Response) => response.text() }),
    }),
    downloadResourceContext: builder.query<string, ResourceContextRequest>({
      query: (request) => ({ url: contextUrl(request, true), responseHandler: (response: Response) => response.text() }),
    }),
  }),
})

export const { useGetResourceContextQuery, useLazyGetResourceContextQuery, useLazyDownloadResourceContextQuery } = resourceContextApi
