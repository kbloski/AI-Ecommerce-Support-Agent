import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/AppShell'
import DashboardPage from '@/pages/DashboardPage'
import OffersPage from '@/pages/OffersPage'
import NotesPage from '@/pages/NotesPage'
import OfferDetailPage from '@/pages/OfferDetailPage'
import OfferProfileAdditionalContextsPage from '@/pages/OfferProfileAdditionalContextsPage'
import OfferProfileDetailPage from '@/pages/OfferProfileDetailPage'
import OfferProfilesPage from '@/pages/OfferProfilesPage'
import ExistingOfferProfilesPage from '@/pages/ExistingOfferProfilesPage'
import OfferFactsPage from '@/pages/OfferFactsPage'
import MarketingAnglesPage from '@/pages/MarketingAnglesPage'
import AdConceptsPage from '@/pages/AdConceptsPage'
import AdCopyPage from '@/pages/AdCopyPage'
import CreativePlansPage from '@/pages/CreativePlansPage'
import BrandStylesPage from '@/pages/BrandStylesPage'
import OfferSourcesPage from '@/pages/OfferSourcesPage'
import OfferSourceDetailPage from '@/pages/OfferSourceDetailPage'
import AnalysisDetailPage from '@/pages/AnalysisDetailPage'
import ChecklistDetailPage from '@/pages/ChecklistDetailPage'
import BrandMarketingDetailPage from '@/pages/BrandMarketingDetailPage'
import MarketingStrategyDetailPage from '@/pages/MarketingStrategyDetailPage'
import OfferStrategyDetailPage from '@/pages/OfferStrategyDetailPage'
import MessageStrategyDetailPage from '@/pages/MessageStrategyDetailPage'
import UgcCreativeDetailPage from '@/pages/UgcCreativeDetailPage'
import PageStrategyDetailPage from '@/pages/PageStrategyDetailPage'
import PageRequirementsDetailPage from '@/pages/PageRequirementsDetailPage'
import PageBlueprintDetailPage from '@/pages/PageBlueprintDetailPage'
import PageContentPlanDetailPage from '@/pages/PageContentPlanDetailPage'
import PageCopyDetailPage from '@/pages/PageCopyDetailPage'
import SettingsPage from '@/pages/SettingsPage'
import { OfferProfileTargetAudiencesPage } from '@/pages/EntityRelationPages'
import {
  AnalysisQuestionsPage,
  BrandMarketingStrategiesPage, ChecklistItemsPage, OfferProfileAnalysesPage,
  OfferSourceBrandMarketingPage, MarketingOfferStrategiesPage,
  MessagePageStrategiesPage, OfferProfileUgcCreativesPage, OfferMessageStrategiesPage,
  PageRequirementsPage, PageBlueprintsPage, PageContentPlansPage, PageCopiesPage, OfferProfileChecklistsPage,
} from '@/pages/ResourcePages'

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/offers" element={<OffersPage />} />
        <Route path="/offer-profiles" element={<ExistingOfferProfilesPage />} />
        <Route path="/notes" element={<NotesPage />} />
        <Route path="/offers/:offerId" element={<OfferDetailPage />} />
        <Route path="/offers/:offerId/offer-sources" element={<OfferSourcesPage />} />
        <Route path="/offers/:offerId/offer_sources" element={<OfferSourcesPage />} />
        <Route path="/offer-sources/:offerSourceId" element={<OfferSourceDetailPage />} />
        <Route path="/offer-profiles/:offerProfileId/target-audiences" element={<OfferProfileTargetAudiencesPage />} />
        <Route path="/offer-profiles/:offerProfileId/marketing-angles" element={<MarketingAnglesPage />} />
        <Route path="/offer-profiles/:offerProfileId/ad-concepts" element={<AdConceptsPage />} />
        <Route path="/offer-profiles/:offerProfileId/ad-copy" element={<AdCopyPage />} />
        <Route path="/offer-profiles/:offerProfileId/creative-plans" element={<CreativePlansPage />} />
        <Route path="/offer-profiles/:offerProfileId/brand-styles" element={<BrandStylesPage />} />
        <Route path="/offer-profiles/:offerProfileId/additional-contexts" element={<OfferProfileAdditionalContextsPage />} />
        <Route path="/offer-profiles/:offerProfileId" element={<OfferProfileDetailPage />} />
        <Route path="/offer-sources/:offerSourceId/profiles" element={<OfferProfilesPage />} />
        <Route path="/offer-sources/:offerSourceId/facts" element={<OfferFactsPage />} />
        <Route path="/offer-profiles/:offerProfileId/analyses" element={<OfferProfileAnalysesPage />} />
        <Route path="/offer-profiles/:offerProfileId/checklists" element={<OfferProfileChecklistsPage />} />
        <Route path="/offer-sources/:offerSourceId/brand-marketing" element={<OfferSourceBrandMarketingPage />} />
        <Route path="/offer-profiles/:offerProfileId/analysis/:analysisId" element={<AnalysisDetailPage />} />
        <Route path="/offer-profiles/:offerProfileId/analysis/:analysisId/questions" element={<AnalysisQuestionsPage />} />
        <Route
          path="/offer-profiles/:offerProfileId/checklists/:checklistId"
          element={<ChecklistDetailPage />}
        />
        <Route path="/offer-profiles/:offerProfileId/checklists/:checklistId/items" element={<ChecklistItemsPage />} />
        <Route path="/brand-marketing/:id" element={<BrandMarketingDetailPage />} />
        <Route path="/brand-marketing/:id/marketing-strategies" element={<BrandMarketingStrategiesPage />} />
        <Route path="/marketing-strategy/:id" element={<MarketingStrategyDetailPage />} />
        <Route path="/marketing-strategy/:id/offer-strategies" element={<MarketingOfferStrategiesPage />} />
        <Route path="/offer-strategy/:id" element={<OfferStrategyDetailPage />} />
        <Route path="/offer-strategy/:id/message-strategies" element={<OfferMessageStrategiesPage />} />
        <Route path="/message-strategy/:id" element={<MessageStrategyDetailPage />} />
        <Route path="/offer-profiles/:offerProfileId/ugc-creatives" element={<OfferProfileUgcCreativesPage />} />
        <Route path="/message-strategy/:id/page-strategies" element={<MessagePageStrategiesPage />} />
        <Route path="/ugc-creatives/:id" element={<UgcCreativeDetailPage />} />
        <Route path="/page-strategy/:id" element={<PageStrategyDetailPage />} />
        <Route path="/page-strategy/:id/page-requirements" element={<PageRequirementsPage />} />
        <Route path="/page-requirements/:id" element={<PageRequirementsDetailPage />} />
        <Route path="/page-requirements/:id/page-blueprints" element={<PageBlueprintsPage />} />
        <Route path="/page-blueprint/:id" element={<PageBlueprintDetailPage />} />
        <Route path="/page-blueprint/:id/content-plans" element={<PageContentPlansPage />} />
        <Route path="/page-content-plan/:id" element={<PageContentPlanDetailPage />} />
        <Route path="/page-content-plan/:id/page-copies" element={<PageCopiesPage />} />
        <Route path="/page-copy/:id" element={<PageCopyDetailPage />} />
        <Route path="/settings" element={<Navigate to="/settings/general" replace />} />
        <Route path="/settings/general" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}

export default App
