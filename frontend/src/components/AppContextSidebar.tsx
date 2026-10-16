import { useId, type ReactNode } from 'react'
import { ArrowLeft, ChevronDown, CodeXml } from 'lucide-react'
import { Link, NavLink, matchPath, useLocation, useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { DownloadPipelinePathButton } from '@/components/DownloadPipelinePathButton'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useSidePanel } from '@/lib/sidePanel'
import { usePersistentBoolean } from '@/lib/usePersistentBoolean'
import type { useResizablePanel } from '@/lib/useResizablePanel'
import { useListProfileContextsQuery } from '@/features/additionalContexts/additionalContextsApi'
import { useListOfferProfilesQuery } from '@/features/offerProfiles/offerProfilesApi'
import { useListOfferFactsQuery } from '@/features/offerFacts/offerFactsApi'
import { useListOfferSourceForOfferQuery } from '@/features/offerSources/offerSourceApi'
import { useListTargetAudiencesForOfferProfileQuery } from '@/features/targetAudiences/targetAudiencesApi'
import { useListMarketingAnglesQuery } from '@/features/marketingAngles/marketingAnglesApi'
import { useListAdConceptsQuery } from '@/features/adConcepts/adConceptsApi'
import { useListCreativePlansQuery } from '@/features/creativePlans/creativePlansApi'
import { useGetAnalysisQuery, useListAnalysisForOfferProfileQuery } from '@/features/analysis/analysisApi'
import { useListBrandMarketingForOfferSourceQuery } from '@/features/brandMarketing/brandMarketingApi'
import { useGetChecklistQuery, useListChecklistsForOfferProfileQuery } from '@/features/checklists/checklistsApi'
import { useListMarketingStrategyForBrandMarketingQuery } from '@/features/marketingStrategy/marketingStrategyApi'
import { useListOfferStrategyForMarketingStrategyQuery } from '@/features/offerStrategy/offerStrategyApi'
import { useListMessageStrategyForOfferStrategyQuery } from '@/features/messageStrategy/messageStrategyApi'
import { useListAdStrategyForMessageStrategyQuery } from '@/features/adStrategy/adStrategyApi'
import { useListUgcCreativesForMessageStrategyQuery } from '@/features/ugcCreatives/ugcCreativesApi'
import { useListPageStrategyForMessageStrategyQuery } from '@/features/pageStrategy/pageStrategyApi'
import { useListCreativeStrategyForAdStrategyQuery } from '@/features/creativeStrategy/creativeStrategyApi'
import { useListAdSetupForCreativeStrategyQuery } from '@/features/adSetup/adSetupApi'
import { useListCreativeExecutionSetupsForAdSetupQuery } from '@/features/creativeExecutionSetup/creativeExecutionSetupApi'
import { useListGenerateAdsForSetupQuery } from '@/features/generateAd/generateAdApi'
import { useListPageRequirementsForPageStrategyQuery } from '@/features/pageRequirements/pageRequirementsApi'
import { useListPageBlueprintForPageRequirementsQuery } from '@/features/pageBlueprint/pageBlueprintApi'
import { useListPageContentPlanForPageBlueprintQuery } from '@/features/pageContentPlan/pageContentPlanApi'
import { useListPageCopyForPageContentPlanQuery } from '@/features/pageCopy/pageCopyApi'

const navLinkClassName = ({ isActive }: { isActive: boolean }) =>
  cn(
    'flex min-w-0 items-start gap-2 rounded-md px-3 py-2 text-sm whitespace-normal break-words',
    isActive
      ? 'bg-accent text-accent-foreground'
      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
  )

const sidebarActionClassName = 'h-auto min-h-7 w-full min-w-0 max-w-full shrink justify-start py-1.5 text-left leading-snug whitespace-normal'

function SidebarGroup({ title, children, className }: { title: string; children: ReactNode; className?: string }) {
  const [expanded, setExpanded] = usePersistentBoolean(`ai-ec-agent:sidebar-group:${title}`, true)
  const contentId = useId()

  return <section className={className}>
    <button type="button" aria-expanded={expanded} aria-controls={contentId} onClick={() => setExpanded((value) => !value)}
      className="mb-2 flex w-full items-center justify-between border-b border-foreground/30 px-2 pb-2 text-left text-xs font-semibold tracking-wide text-foreground uppercase hover:text-primary">
      <span>{title}</span>
      <ChevronDown className={cn('size-3.5 shrink-0 transition-transform', !expanded && '-rotate-90')} />
    </button>
    <div id={contentId} hidden={!expanded}>{children}</div>
  </section>
}

interface AppContextSidebarProps {
  variant?: 'sidebar' | 'mobile'
  width?: number
  resize?: ReturnType<typeof useResizablePanel>
}

/** Secondary, contextual navigation shown next to the primary sidebar. Its content depends on which section of the app is active. */
export function AppContextSidebar({ variant = 'sidebar', width = 224, resize }: AppContextSidebarProps) {
  const asideClassName = cn(
    variant === 'sidebar'
      ? 'relative hidden shrink-0 flex-col border-r p-4 md:flex'
      : 'flex w-full flex-col p-2',
  )
  const renderSidebar = (content: React.ReactNode) => (
    <aside className={asideClassName} style={variant === 'sidebar' ? { width } : undefined}>
      {content}
      {variant === 'sidebar' && resize && (
        <div
          role="separator"
          tabIndex={0}
          aria-orientation="vertical"
          aria-label="Zmień szerokość nawigacji kontekstowej"
          aria-valuemin={resize.minWidth}
          aria-valuemax={resize.maxWidth}
          aria-valuenow={resize.width}
          className="absolute inset-y-0 -right-1 z-10 w-3 cursor-col-resize touch-none outline-none focus-visible:bg-primary/10"
          onPointerDown={resize.startResize}
          onPointerMove={resize.resize}
          onPointerUp={resize.stopResize}
          onPointerCancel={resize.stopResize}
          onDoubleClick={resize.resetWidth}
          onKeyDown={resize.resizeWithKeyboard}
        >
          <div className="mx-auto h-full w-px bg-border opacity-70 transition-all hover:w-0.5 hover:bg-primary hover:opacity-100" />
        </div>
      )}
    </aside>
  )
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { contextualPanel, openPanel } = useSidePanel()
  const showBackButton = pathname !== '/' && pathname !== '/offers'
  const sections = [
    { pattern: '/offers/:id/*', current: 'Oferta', entityType: 'offer', process: [['offer-sources', 'Źródła oferty']], resources: [] },
    { pattern: '/offer-sources/:id/*', current: 'Offer source', entityType: 'offer_source', attached: [['facts', 'Fakty o produkcie']], process: [['profiles', 'Profile oferty'], ['brand-marketing', 'Marketing marki (przestarzały)']], resources: [] },
    { pattern: '/offer-profiles/:offerProfileId/analysis/:id/*', current: 'Analiza', process: [], resources: [['questions', 'Pytania']] },
    { pattern: '/offer-profiles/:offerProfileId/checklists/:id/*', current: 'Checklista', process: [], resources: [['items', 'Zadania']] },
    { pattern: '/offer-profiles/:id/*', current: 'Profil oferty', attached: [['additional-contexts', 'Dodatkowe informacje']], process: [], resources: [] },
    { pattern: '/brand-marketing/:id/*', current: 'Brand marketing', entityType: 'brand_marketing', process: [['marketing-strategies', 'Marketing strategy']], resources: [] },
    { pattern: '/marketing-strategy/:id/*', current: 'Marketing strategy', entityType: 'marketing_strategy', process: [['offer-strategies', 'Offer strategy']], resources: [] },
    { pattern: '/offer-strategy/:id/*', current: 'Offer strategy', entityType: 'offer_strategy', process: [['message-strategies', 'Message strategy']], resources: [] },
    { pattern: '/message-strategy/:id/*', current: 'Message strategy', entityType: 'message_strategy', process: [['ad-strategies', 'Ad strategy'], ['ugc-creatives', 'UGC creatives'], ['page-strategies', 'Page strategy']], resources: [] },
    { pattern: '/ad-strategy/:id/*', current: 'Ad strategy', entityType: 'ad_strategy', process: [['creative-strategies', 'Creative strategy']], resources: [] },
    { pattern: '/creative-strategy/:id/*', current: 'Creative strategy', entityType: 'creative_strategy', process: [['ad-setups', 'Ad Setup']], resources: [] },
    { pattern: '/ad-setup/:id/*', current: 'Ad Setup', entityType: 'ad_setup', process: [['creative-execution-setups', 'Creative Execution Setup']], resources: [] },
    { pattern: '/creative-execution-setup/:id/*', current: 'Creative Execution Setup', entityType: 'creative_execution_setup', process: [['generate-ads', 'Generate Ad']], resources: [] },
    { pattern: '/page-strategy/:id/*', current: 'Page strategy', entityType: 'page_strategy', process: [['page-requirements', 'Page requirements']], resources: [] },
    { pattern: '/page-requirements/:id/*', current: 'Page requirements', entityType: 'page_requirements', process: [['page-blueprints', 'Page blueprint']], resources: [] },
    { pattern: '/page-blueprint/:id/*', current: 'Page blueprint', entityType: 'page_blueprint', process: [['content-plans', 'Content plan']], resources: [] },
    { pattern: '/page-content-plan/:id/*', current: 'Content plan', entityType: 'page_content_plan', process: [['page-copies', 'Page copy']], resources: [] },
    { pattern: '/generate-ad/:id/*', current: 'Generate Ad', entityType: 'generate_ad', process: [], resources: [] },
    { pattern: '/ugc-creatives/:id/*', current: 'UGC creative', entityType: 'ugc_creative', process: [], resources: [] },
    { pattern: '/page-copy/:id/*', current: 'Page copy', entityType: 'page_copy', process: [], resources: [] },
  ] as const
  // Prefer the most specific route, otherwise an analysis URL would match OfferSource first.
  const section = [...sections].sort((a, b) => b.pattern.length - a.pattern.length)
    .map((config) => ({ config, match: matchPath(config.pattern, pathname) }))
    .find(({ match }) => match)
  const isOfferSourceSection = section?.config.current === 'Offer source'
  const offerSourceId = Number(section?.match?.params.id)
  const skipOfferSourceResources = !isOfferSourceSection || !Number.isInteger(offerSourceId)
  const currentEntityId = Number(section?.match?.params.id)
  const isAnalysisSection = section?.config.current === 'Analiza'
  const isChecklistSection = section?.config.current === 'Checklista'
  const isCurrentStage = (stage: string) => section?.config.current === stage && Number.isInteger(currentEntityId)
  const targetAudiences = useListTargetAudiencesForOfferProfileQuery(
    { offerProfileId: currentEntityId, pageSize: 1 },
    { skip: !isCurrentStage('Profil oferty') },
  )
  const unreviewedTargetAudiences = useListTargetAudiencesForOfferProfileQuery(
    { offerProfileId: currentEntityId, pageSize: 1, isReviewed: false },
    { skip: !isCurrentStage('Profil oferty') },
  )
  const marketingAngles = useListMarketingAnglesQuery(currentEntityId, { skip: !isCurrentStage('Profil oferty') })
  const adConcepts = useListAdConceptsQuery(currentEntityId, { skip: !isCurrentStage('Profil oferty') })
  const creativePlans = useListCreativePlansQuery(currentEntityId, { skip: !isCurrentStage('Profil oferty') })
  const brandMarketing = useListBrandMarketingForOfferSourceQuery(offerSourceId, { skip: skipOfferSourceResources })
  const analyses = useListAnalysisForOfferProfileQuery(currentEntityId, { skip: !isCurrentStage('Profil oferty') })
  const analysis = useGetAnalysisQuery(currentEntityId, { skip: !isAnalysisSection || !Number.isInteger(currentEntityId) })
  const checklist = useGetChecklistQuery(currentEntityId, { skip: !isChecklistSection || !Number.isInteger(currentEntityId) })
  const offerSources = useListOfferSourceForOfferQuery(currentEntityId, { skip: !isCurrentStage('Oferta') })
  const checklists = useListChecklistsForOfferProfileQuery(currentEntityId, { skip: !isCurrentStage('Profil oferty') })
  const marketingStrategies = useListMarketingStrategyForBrandMarketingQuery(currentEntityId, { skip: !isCurrentStage('Brand marketing') })
  const offerStrategies = useListOfferStrategyForMarketingStrategyQuery(currentEntityId, { skip: !isCurrentStage('Marketing strategy') })
  const messageStrategies = useListMessageStrategyForOfferStrategyQuery(currentEntityId, { skip: !isCurrentStage('Offer strategy') })
  const adStrategies = useListAdStrategyForMessageStrategyQuery(currentEntityId, { skip: !isCurrentStage('Message strategy') })
  const ugcCreatives = useListUgcCreativesForMessageStrategyQuery(currentEntityId, { skip: !isCurrentStage('Message strategy') })
  const pageStrategies = useListPageStrategyForMessageStrategyQuery(currentEntityId, { skip: !isCurrentStage('Message strategy') })
  const creativeStrategies = useListCreativeStrategyForAdStrategyQuery(currentEntityId, { skip: !isCurrentStage('Ad strategy') })
  const adSetups = useListAdSetupForCreativeStrategyQuery(currentEntityId, { skip: !isCurrentStage('Creative strategy') })
  const creativeExecutionSetups = useListCreativeExecutionSetupsForAdSetupQuery(currentEntityId, { skip: !isCurrentStage('Ad Setup') })
  const generateAds = useListGenerateAdsForSetupQuery(currentEntityId, { skip: !isCurrentStage('Creative Execution Setup') })
  const pageRequirements = useListPageRequirementsForPageStrategyQuery(currentEntityId, { skip: !isCurrentStage('Page strategy') })
  const pageBlueprints = useListPageBlueprintForPageRequirementsQuery(currentEntityId, { skip: !isCurrentStage('Page requirements') })
  const pageContentPlans = useListPageContentPlanForPageBlueprintQuery(currentEntityId, { skip: !isCurrentStage('Page blueprint') })
  const pageCopies = useListPageCopyForPageContentPlanQuery(currentEntityId, { skip: !isCurrentStage('Content plan') })
  const offerFacts = useListOfferFactsQuery({ offerSourceId: currentEntityId, pageSize: 1 }, { skip: !isOfferSourceSection })
  const offerProfiles = useListOfferProfilesQuery(currentEntityId, { skip: !isOfferSourceSection })
  const profileContexts = useListProfileContextsQuery(currentEntityId, { skip: !isCurrentStage('Profil oferty') })
  const resourceCounts: Record<string, number | undefined> = {
    'offer-sources': offerSources.data?.length,
    'target-audiences': targetAudiences.data?.total_items,
    'marketing-angles': marketingAngles.data?.length,
    'ad-concepts': adConcepts.data?.length,
    'creative-plans': creativePlans.data?.length,
    'additional-contexts': profileContexts.data?.length,
    profiles: offerProfiles.data?.length,
    facts: offerFacts.data?.total_items,
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
    'ad-setups': adSetups.data?.length,
    'creative-execution-setups': creativeExecutionSetups.data?.length,
    'generate-ads': generateAds.data?.length,
    'page-requirements': pageRequirements.data?.length,
    'page-blueprints': pageBlueprints.data?.length,
    'content-plans': pageContentPlans.data?.length,
    'page-copies': pageCopies.data?.length,
  }
  const attentionCounts: Record<string, number | undefined> = {
    'target-audiences': unreviewedTargetAudiences.data?.total_items,
    'marketing-angles': marketingAngles.data?.filter((angle) => !angle.is_reviewed).length,
    'ad-concepts': adConcepts.data?.filter((concept) => !concept.is_reviewed).length,
    'creative-plans': creativePlans.data?.filter((plan) => !plan.is_reviewed).length,
    questions: (analysis.data?.analysis_questions as Array<{ is_reviewed?: unknown }> | undefined)
      ?.filter((item) => item.is_reviewed !== true).length,
    items: (checklist.data?.checklist_items as Array<{ is_reviewed?: unknown }> | undefined)
      ?.filter((item) => item.is_reviewed !== true).length,
    'ugc-creatives': ugcCreatives.data
      ?.filter((item) => item.is_reviewed !== true).length,
  }

  const navigationLink = (slug: string, label: string, to: string) => (
    <NavLink key={slug} to={to} className={navLinkClassName}>
      <span className="min-w-0 flex-1">{label}</span>
      <span className="ml-auto flex shrink-0 items-center gap-1.5">
        {attentionCounts[slug] !== undefined && attentionCounts[slug] > 0 && (
          <Badge variant="danger" className="font-mono" title={`Wymaga sprawdzenia: ${attentionCounts[slug]}`}><strong>!</strong>{attentionCounts[slug]}</Badge>
        )}
        {resourceCounts[slug] !== undefined && <Badge variant="default" className="border-0 bg-transparent font-mono text-slate-500">{resourceCounts[slug]}</Badge>}
      </span>
    </NavLink>
  )

  if (pathname.startsWith('/settings')) {
    return renderSidebar(
      <>
        <SidebarGroup title="Ustawienia">
          <nav className="ml-2 space-y-1 border-l pl-2">
            <NavLink to="/settings/general" className={navLinkClassName}>
              General
            </NavLink>
          </nav>
        </SidebarGroup>
        {contextualPanel && (
          <SidebarGroup title="Akcje" className="mt-6">
            <nav className="ml-2 space-y-1 border-l pl-2">
              <Button type="button" variant="ghost" size="sm" className={sidebarActionClassName} onClick={() => openPanel(contextualPanel)}>
                <CodeXml />
                Zobacz JSON obiektu
              </Button>
            </nav>
          </SidebarGroup>
        )}
      </>,
    )
  }

  if (section) {
    const detailPath = section.match?.pathnameBase ?? pathname
    const currentPath = detailPath

    return renderSidebar(
      <>
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
            Aktualny zasób
          </p>
          <p className="mt-1 text-sm font-semibold text-foreground">{section.config.current}</p>
        </Link>
        {'attached' in section.config && section.config.attached.length > 0 && (
          <SidebarGroup title="Powiązane dane z zasobem" className="mb-6">
            <nav className="ml-2 space-y-1 border-l pl-2">
              {section.config.attached.map(([slug, label]) => (
                navigationLink(slug, label, `${detailPath}/${slug}`)
              ))}
            </nav>
          </SidebarGroup>
        )}
        {section.config.process.length > 0 && (
          <SidebarGroup title="Proces">
            <nav className="ml-2 space-y-1 border-l pl-2">
              {section.config.process.map(([slug, label]) => (
                navigationLink(slug, label, `${detailPath}/${slug}`)
              ))}
            </nav>
          </SidebarGroup>
        )}

        {section.config.resources.length > 0 && (
          <SidebarGroup title="Zasoby" className={section.config.process.length > 0 ? 'mt-6' : undefined}>
            <nav className="ml-2 space-y-1 border-l pl-2">
              {section.config.resources.map(([slug, label]) => (
                navigationLink(slug, label, `${detailPath}/${slug}`)
              ))}
            </nav>
          </SidebarGroup>
        )}
        {section.config.current === 'Profil oferty' && (
          <SidebarGroup title="Research" className="mb-6">
            <nav className="ml-2 space-y-1 border-l pl-2">
              {navigationLink('analyses', 'Analizy produktu (na razie nie działa poprawnie)', `${detailPath}/analyses`)}
              {navigationLink('checklists', 'Checklisty (na razie nie działa poprawnie)', `${detailPath}/checklists`)}
            </nav>
          </SidebarGroup>
        )}
        {section.config.current === 'Profil oferty' && (
          <SidebarGroup title="Targets">
            <nav className="ml-2 space-y-1 border-l pl-2">
              {navigationLink('target-audiences', 'Target audiences', `${detailPath}/target-audiences`)}
              <span aria-disabled="true" className="flex min-w-0 cursor-not-allowed rounded-md px-3 py-2 text-sm text-muted-foreground/50">Buyer personas</span>
            </nav>
          </SidebarGroup>
        )}
        {section.config.current === 'Profil oferty' && (
          <SidebarGroup title="Marketing" className="mt-6">
            <nav className="ml-2 space-y-1 border-l pl-2">
              {navigationLink('marketing-angles', 'Marketing angles', `${detailPath}/marketing-angles`)}
              {navigationLink('ad-concepts', 'Ad concepts', `${detailPath}/ad-concepts`)}
              {navigationLink('creative-plans', 'Creative plans', `${detailPath}/creative-plans`)}
            </nav>
          </SidebarGroup>
        )}
        {section.config.current === 'Profil oferty' && (
          <SidebarGroup title="Pages" className="mt-6">
            <div className="ml-2 border-l pl-2">
              <span aria-disabled="true" className="flex min-w-0 cursor-not-allowed rounded-md px-3 py-2 text-sm text-muted-foreground/50">Landing pages</span>
              <span aria-disabled="true" className="flex min-w-0 cursor-not-allowed rounded-md px-3 py-2 text-sm text-muted-foreground/50">Sales pages</span>
            </div>
          </SidebarGroup>
        )}
        {section.config.current === 'Profil oferty' && (
          <SidebarGroup title="Social" className="mt-6">
            <div className="ml-2 border-l pl-2">
              <span aria-disabled="true" className="flex min-w-0 cursor-not-allowed rounded-md px-3 py-2 text-sm text-muted-foreground/50">UGC</span>
              <span aria-disabled="true" className="flex min-w-0 cursor-not-allowed rounded-md px-3 py-2 text-sm text-muted-foreground/50">Social posts</span>
            </div>
          </SidebarGroup>
        )}
        {section.config.current === 'Profil oferty' && (
          <SidebarGroup title="Ads" className="mt-6">
            <div className="ml-2 border-l pl-2">
              <span aria-disabled="true" className="flex min-w-0 cursor-not-allowed rounded-md px-3 py-2 text-sm text-muted-foreground/50">Ad creatives</span>
              <span aria-disabled="true" className="flex min-w-0 cursor-not-allowed rounded-md px-3 py-2 text-sm text-muted-foreground/50">Ad copy</span>
            </div>
          </SidebarGroup>
        )}
        {('entityType' in section.config || contextualPanel) && (
          <SidebarGroup title="Akcje" className={section.config.process.length > 0 || section.config.resources.length > 0 || section.config.current === 'Profil oferty' ? 'mt-6' : undefined}>
            <nav className="ml-2 space-y-1 border-l pl-2">
              {'entityType' in section.config && (
                <DownloadPipelinePathButton className={sidebarActionClassName} entityType={section.config.entityType} entityId={Number(section.match?.params.id)} />
              )}
              {contextualPanel && (
                <Button type="button" variant="ghost" size="sm" className={sidebarActionClassName} onClick={() => openPanel(contextualPanel)}>
                  <CodeXml />
                  Zobacz JSON obiektu
                </Button>
              )}
            </nav>
          </SidebarGroup>
        )}
      </>,
    )
  }

  return renderSidebar(
    showBackButton ? (
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 rounded-md px-2 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        >
          <ArrowLeft className="size-4" />
          Wstecz
        </button>
      ) : null,
  )
}
