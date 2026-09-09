import { ArrowLeft, CodeXml } from 'lucide-react'
import { Link, NavLink, matchPath, useLocation, useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { DownloadPipelinePathButton } from '@/components/DownloadPipelinePathButton'
import { Button } from '@/components/ui/button'
import { useSidePanel } from '@/lib/sidePanel'
import { useListOfferProfileElementsQuery, useListOfferProfileForOfferQuery } from '@/features/offerProfiles/offerProfileApi'
import { useListTargetAudiencesForOfferProfileQuery } from '@/features/targetAudiences/targetAudiencesApi'
import { useGetAnalysisQuery, useListAnalysisForOfferProfileQuery } from '@/features/analysis/analysisApi'
import { useListBrandMarketingForOfferProfileQuery } from '@/features/brandMarketing/brandMarketingApi'
import { useGetChecklistQuery, useListChecklistsForAnalysisQuery } from '@/features/checklists/checklistsApi'
import { useListMarketingStrategyForBrandMarketingQuery } from '@/features/marketingStrategy/marketingStrategyApi'
import { useListOfferStrategyForMarketingStrategyQuery } from '@/features/offerStrategy/offerStrategyApi'
import { useListMessageStrategyForOfferStrategyQuery } from '@/features/messageStrategy/messageStrategyApi'
import { useListAdStrategyForMessageStrategyQuery } from '@/features/adStrategy/adStrategyApi'
import { useListUgcCreativesForMessageStrategyQuery } from '@/features/ugcCreatives/ugcCreativesApi'
import { useListPageStrategyForMessageStrategyQuery } from '@/features/pageStrategy/pageStrategyApi'
import { useListCreativeStrategyForAdStrategyQuery } from '@/features/creativeStrategy/creativeStrategyApi'
import { useListAdExecutionForCreativeStrategyQuery } from '@/features/adExecution/adExecutionApi'
import { useListCreativeExecutionForAdExecutionQuery } from '@/features/creativeExecution/creativeExecutionApi'
import { useListPageRequirementsForPageStrategyQuery } from '@/features/pageRequirements/pageRequirementsApi'
import { useListPageBlueprintForPageRequirementsQuery } from '@/features/pageBlueprint/pageBlueprintApi'
import { useListPageContentPlanForPageBlueprintQuery } from '@/features/pageContentPlan/pageContentPlanApi'
import { useListPageCopyForPageContentPlanQuery } from '@/features/pageCopy/pageCopyApi'

const navLinkClassName = ({ isActive }: { isActive: boolean }) =>
  cn(
    'flex items-center gap-2 rounded-md px-3 py-2 text-sm',
    isActive
      ? 'bg-accent text-accent-foreground'
      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
  )

/** Secondary, contextual navigation shown next to the primary sidebar. Its content depends on which section of the app is active. */
export function AppContextSidebar({ variant = 'sidebar' }: { variant?: 'sidebar' | 'mobile' }) {
  const asideClassName = cn(
    variant === 'sidebar'
      ? 'hidden w-56 shrink-0 flex-col border-r p-4 md:flex'
      : 'flex w-full flex-col p-2',
  )
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { contextualPanel, openPanel } = useSidePanel()
  const showBackButton = pathname !== '/' && pathname !== '/offers'
  const sections = [
    { pattern: '/offers/:id/*', current: 'Oferta', entityType: 'offer', process: [['offer-profiles', 'Profile oferty']], resources: [] },
    { pattern: '/offer-profiles/:id/*', current: 'Offer profile', entityType: 'offer_profile', process: [['brand-marketing', 'Brand marketing']], offer_profile: [['analyses', 'Analizy']], resources: [['target-audiences', 'Grupy docelowe'], ['elements', 'Elementy oferty']] },
    { pattern: '/offer-profiles/:offerProfileId/analysis/:id/*', current: 'Analiza', process: [['checklists', 'Checklisty']], resources: [['questions', 'Pytania']] },
    { pattern: '/offer-profiles/:offerProfileId/analysis/:analysisId/checklists/:id/*', current: 'Checklista', process: [], resources: [['items', 'Zadania']] },
    { pattern: '/brand-marketing/:id/*', current: 'Brand marketing', entityType: 'brand_marketing', process: [['marketing-strategies', 'Marketing strategy']], resources: [] },
    { pattern: '/marketing-strategy/:id/*', current: 'Marketing strategy', entityType: 'marketing_strategy', process: [['offer-strategies', 'Offer strategy']], resources: [] },
    { pattern: '/offer-strategy/:id/*', current: 'Offer strategy', entityType: 'offer_strategy', process: [['message-strategies', 'Message strategy']], resources: [] },
    { pattern: '/message-strategy/:id/*', current: 'Message strategy', entityType: 'message_strategy', process: [['ad-strategies', 'Ad strategy'], ['ugc-creatives', 'UGC creatives'], ['page-strategies', 'Page strategy']], resources: [] },
    { pattern: '/ad-strategy/:id/*', current: 'Ad strategy', entityType: 'ad_strategy', process: [['creative-strategies', 'Creative strategy']], resources: [] },
    { pattern: '/creative-strategy/:id/*', current: 'Creative strategy', entityType: 'creative_strategy', process: [['ad-executions', 'Ad execution']], resources: [] },
    { pattern: '/ad-execution/:id/*', current: 'Ad execution', entityType: 'ad_execution', process: [['creative-executions', 'Creative execution']], resources: [] },
    { pattern: '/page-strategy/:id/*', current: 'Page strategy', entityType: 'page_strategy', process: [['page-requirements', 'Page requirements']], resources: [] },
    { pattern: '/page-requirements/:id/*', current: 'Page requirements', entityType: 'page_requirements', process: [['page-blueprints', 'Page blueprint']], resources: [] },
    { pattern: '/page-blueprint/:id/*', current: 'Page blueprint', entityType: 'page_blueprint', process: [['content-plans', 'Content plan']], resources: [] },
    { pattern: '/page-content-plan/:id/*', current: 'Content plan', entityType: 'page_content_plan', process: [['page-copies', 'Page copy']], resources: [] },
    { pattern: '/creative-execution/:id/*', current: 'Creative execution', entityType: 'creative_execution', process: [], resources: [] },
    { pattern: '/ugc-creatives/:id/*', current: 'UGC creative', entityType: 'ugc_creative', process: [], resources: [] },
    { pattern: '/page-copy/:id/*', current: 'Page copy', entityType: 'page_copy', process: [], resources: [] },
    { pattern: '/target-audiences/:id/*', current: 'Grupa docelowa', process: [], resources: [] },
  ] as const
  // Prefer the most specific route, otherwise an analysis URL would match OfferProfile first.
  const section = [...sections].sort((a, b) => b.pattern.length - a.pattern.length)
    .map((config) => ({ config, match: matchPath(config.pattern, pathname) }))
    .find(({ match }) => match)
  const isOfferProfileSection = section?.config.current === 'Offer profile'
  const offerProfileId = Number(section?.match?.params.id)
  const skipOfferProfileResources = !isOfferProfileSection || !Number.isInteger(offerProfileId)
  const currentEntityId = Number(section?.match?.params.id)
  const isAnalysisSection = section?.config.current === 'Analiza'
  const isChecklistSection = section?.config.current === 'Checklista'
  const isCurrentStage = (stage: string) => section?.config.current === stage && Number.isInteger(currentEntityId)
  const targetAudiences = useListTargetAudiencesForOfferProfileQuery(offerProfileId, { skip: skipOfferProfileResources })
  const offerProfileElements = useListOfferProfileElementsQuery(offerProfileId, { skip: skipOfferProfileResources })
  const brandMarketing = useListBrandMarketingForOfferProfileQuery(offerProfileId, { skip: skipOfferProfileResources })
  const analyses = useListAnalysisForOfferProfileQuery(offerProfileId, { skip: skipOfferProfileResources })
  const analysis = useGetAnalysisQuery(currentEntityId, { skip: !isAnalysisSection || !Number.isInteger(currentEntityId) })
  const checklist = useGetChecklistQuery(currentEntityId, { skip: !isChecklistSection || !Number.isInteger(currentEntityId) })
  const offerProfiles = useListOfferProfileForOfferQuery(currentEntityId, { skip: !isCurrentStage('Oferta') })
  const checklists = useListChecklistsForAnalysisQuery(currentEntityId, { skip: !isCurrentStage('Analiza') })
  const marketingStrategies = useListMarketingStrategyForBrandMarketingQuery(currentEntityId, { skip: !isCurrentStage('Brand marketing') })
  const offerStrategies = useListOfferStrategyForMarketingStrategyQuery(currentEntityId, { skip: !isCurrentStage('Marketing strategy') })
  const messageStrategies = useListMessageStrategyForOfferStrategyQuery(currentEntityId, { skip: !isCurrentStage('Offer strategy') })
  const adStrategies = useListAdStrategyForMessageStrategyQuery(currentEntityId, { skip: !isCurrentStage('Message strategy') })
  const ugcCreatives = useListUgcCreativesForMessageStrategyQuery(currentEntityId, { skip: !isCurrentStage('Message strategy') })
  const pageStrategies = useListPageStrategyForMessageStrategyQuery(currentEntityId, { skip: !isCurrentStage('Message strategy') })
  const creativeStrategies = useListCreativeStrategyForAdStrategyQuery(currentEntityId, { skip: !isCurrentStage('Ad strategy') })
  const adExecutions = useListAdExecutionForCreativeStrategyQuery(currentEntityId, { skip: !isCurrentStage('Creative strategy') })
  const creativeExecutions = useListCreativeExecutionForAdExecutionQuery(currentEntityId, { skip: !isCurrentStage('Ad execution') })
  const pageRequirements = useListPageRequirementsForPageStrategyQuery(currentEntityId, { skip: !isCurrentStage('Page strategy') })
  const pageBlueprints = useListPageBlueprintForPageRequirementsQuery(currentEntityId, { skip: !isCurrentStage('Page requirements') })
  const pageContentPlans = useListPageContentPlanForPageBlueprintQuery(currentEntityId, { skip: !isCurrentStage('Page blueprint') })
  const pageCopies = useListPageCopyForPageContentPlanQuery(currentEntityId, { skip: !isCurrentStage('Content plan') })
  const resourceCounts: Record<string, number | undefined> = {
    'offer-profiles': offerProfiles.data?.length,
    'target-audiences': targetAudiences.data?.length,
    elements: offerProfileElements.data?.length,
    'brand-marketing': brandMarketing.data?.length,
    analyses: analyses.data?.length,
    checklists: checklists.data?.length,
    questions: (analysis.data?.analysis_questions as unknown[] | undefined)?.length,
    items: (checklist.data?.checklist_items as unknown[] | undefined)?.length,
    'marketing-strategies': marketingStrategies.data?.length,
    'offer-strategies': offerStrategies.data?.length,
    'message-strategies': messageStrategies.data?.length,
    'ad-strategies': adStrategies.data?.length,
    'ugc-creatives': ugcCreatives.data?.length,
    'page-strategies': pageStrategies.data?.length,
    'creative-strategies': creativeStrategies.data?.length,
    'ad-executions': adExecutions.data?.length,
    'creative-executions': creativeExecutions.data?.length,
    'page-requirements': pageRequirements.data?.length,
    'page-blueprints': pageBlueprints.data?.length,
    'content-plans': pageContentPlans.data?.length,
    'page-copies': pageCopies.data?.length,
  }

  const navigationLink = (slug: string, label: string, to: string) => (
    <NavLink key={slug} to={to} className={navLinkClassName}>
      <span>{label}</span>
      {resourceCounts[slug] !== undefined && (
        <span className="ml-auto rounded-full bg-muted px-1.5 py-0.5 font-mono text-[0.65rem] leading-none text-muted-foreground">
          {resourceCounts[slug]}
        </span>
      )}
    </NavLink>
  )

  if (pathname.startsWith('/settings')) {
    return (
      <aside className={asideClassName}>
        <h2 className="mb-2 border-b border-foreground/30 px-2 pb-2 text-xs font-semibold tracking-wide text-foreground uppercase">
          Ustawienia
        </h2>
        <nav className="ml-2 space-y-1 border-l pl-2">
          <NavLink to="/settings/general" className={navLinkClassName}>
            General
          </NavLink>
        </nav>
        {contextualPanel && (
          <section className="mt-6">
            <h2 className="mb-2 border-b border-foreground/30 px-2 pb-2 text-xs font-semibold tracking-wide text-foreground uppercase">
              Narzędzia
            </h2>
            <nav className="ml-2 space-y-1 border-l pl-2">
              <Button type="button" variant="ghost" size="sm" className="w-full justify-start" onClick={() => openPanel(contextualPanel)}>
                <CodeXml />
                Zobacz JSON obiektu
              </Button>
            </nav>
          </section>
        )}
      </aside>
    )
  }

  if (section) {
    const detailPath = section.match?.pathnameBase ?? pathname
    const currentPath = detailPath

    return (
      <aside className={asideClassName}>
        {showBackButton && (
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="mb-5 flex items-center gap-2 rounded-md px-2 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          >
            <ArrowLeft className="size-4" />
            Wstecz
          </button>
        )}
        <Link
          to={currentPath}
          className="mb-6 block bg-muted/35 px-3 py-3 transition-colors hover:bg-muted/65"
          aria-label={`Przejdź do: ${section.config.current}`}
        >
          <p className="text-[0.68rem] font-semibold tracking-[0.14em] text-muted-foreground uppercase">
            Aktualny etap
          </p>
          <p className="mt-1 text-sm font-semibold text-foreground">{section.config.current}</p>
        </Link>
        {section.config.process.length > 0 && (
          <section>
            <h2 className="mb-2 border-b border-foreground/30 px-2 pb-2 text-xs font-semibold tracking-wide text-foreground uppercase">
              Proces
            </h2>
            <nav className="ml-2 space-y-1 border-l pl-2">
              {section.config.process.map(([slug, label]) => (
                navigationLink(slug, label, `${detailPath}/${slug}`)
              ))}
            </nav>
          </section>
        )}

        {'offer_profile' in section.config && section.config.offer_profile.length > 0 && (
          <section className={section.config.process.length > 0 ? 'mt-6' : undefined}>
            <h2 className="mb-2 border-b border-foreground/30 px-2 pb-2 text-xs font-semibold tracking-wide text-foreground uppercase">
              Wiedza
            </h2>
            <nav className="ml-2 space-y-1 border-l pl-2">
              {section.config.offer_profile.map(([slug, label]) => (
                navigationLink(slug, label, `${detailPath}/${slug}`)
              ))}
            </nav>
          </section>
        )}

        {section.config.resources.length > 0 && (
          <section className={section.config.process.length > 0 || 'offer_profile' in section.config ? 'mt-6' : undefined}>
            <h2 className="mb-2 border-b border-foreground/30 px-2 pb-2 text-xs font-semibold tracking-wide text-foreground uppercase">
              Zasoby
            </h2>
            <nav className="ml-2 space-y-1 border-l pl-2">
              {section.config.resources.map(([slug, label]) => (
                navigationLink(slug, label, `${detailPath}/${slug}`)
              ))}
            </nav>
          </section>
        )}
        {('entityType' in section.config || contextualPanel) && (
          <section className={section.config.process.length > 0 || 'offer_profile' in section.config || section.config.resources.length > 0 ? 'mt-6' : undefined}>
            <h2 className="mb-2 border-b border-foreground/30 px-2 pb-2 text-xs font-semibold tracking-wide text-foreground uppercase">
              Narzędzia
            </h2>
            <nav className="ml-2 space-y-1 border-l pl-2">
              {'entityType' in section.config && (
                <DownloadPipelinePathButton entityType={section.config.entityType} entityId={Number(section.match?.params.id)} />
              )}
              {contextualPanel && (
                <Button type="button" variant="ghost" size="sm" className="w-full justify-start" onClick={() => openPanel(contextualPanel)}>
                  <CodeXml />
                  Zobacz JSON obiektu
                </Button>
              )}
            </nav>
          </section>
        )}
      </aside>
    )
  }

  return <aside className="hidden w-56 shrink-0 flex-col border-r p-4 md:flex">
    {showBackButton && (
      <button
        type="button"
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 rounded-md px-2 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
      >
        <ArrowLeft className="size-4" />
        Wstecz
      </button>
    )}
  </aside>
}
