import { api } from '@/store/api'

export type ResourceContextType = 'offer_raw' | 'offer_source' | 'offer_profile'
export type ResourceContextInclude = 'offer_raw' | 'offer_source' | 'target_audiences' | 'marketing_angle' | 'ad_concept'

export interface ResourceContextRequest {
  type: ResourceContextType
  id: number
  include?: ResourceContextInclude[]
  marketingAngleIds?: number[]
  adConceptIds?: number[]
  includeOfferFacts?: boolean
  includeAdditionalContexts?: boolean
}

function contextUrl({ type, id, include = [], marketingAngleIds = [], adConceptIds = [], includeOfferFacts, includeAdditionalContexts }: ResourceContextRequest, download = false) {
  const params = new URLSearchParams()
  include.forEach((item) => params.append('include', item))
  marketingAngleIds.forEach((angleId) => params.append('marketing_angle_ids', String(angleId)))
  adConceptIds.forEach((conceptId) => params.append('ad_concept_ids', String(conceptId)))
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

export const { useLazyGetResourceContextQuery, useLazyDownloadResourceContextQuery } = resourceContextApi
