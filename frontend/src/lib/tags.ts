export const TAG_TYPES = [
  'Offer',
  'OfferProfile',
  'OfferProfileElement',
  'TargetAudience',
  'Analysis',
  'AnalysisQuestion',
  'Checklist',
  'BrandMarketing',
  'MarketingStrategy',
  'OfferStrategy',
  'MessageStrategy',
  'AdStrategy',
  'CreativeStrategy',
  'AdSetup',
  'CreativeExecutionSetup',
  'GenerateAd',
  'UgcCreative',
  'PageStrategy',
  'PageRequirements',
  'PageBlueprint',
  'PageContentPlan',
  'PageCopy',
  'OllamaSettings',
  'OutputPrompt',
] as const

export type Tag = (typeof TAG_TYPES)[number]

/** Tag for a parent-scoped list query — invalidated when a child is generated for that parent. */
export const listTag = (type: Tag, parentId: string | number) =>
  ({ type, id: `LIST_${parentId}` }) as const

/** Tag for a single entity's detail query. */
export const itemTag = (type: Tag, id: string | number) => ({ type, id }) as const
