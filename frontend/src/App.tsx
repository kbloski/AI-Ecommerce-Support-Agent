import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '@/components/AppShell'
import DashboardPage from '@/pages/DashboardPage'
import OffersPage from '@/pages/OffersPage'
import OfferDetailPage from '@/pages/OfferDetailPage'
import OfferProfilesPage from '@/pages/OfferProfilesPage'
import OfferProfileDetailPage from '@/pages/OfferProfileDetailPage'
import TargetAudienceDetailPage from '@/pages/TargetAudienceDetailPage'
import TargetAudienceEditPage from '@/pages/TargetAudienceEditPage'
import AnalysisDetailPage from '@/pages/AnalysisDetailPage'
import ChecklistDetailPage from '@/pages/ChecklistDetailPage'
import BrandMarketingDetailPage from '@/pages/BrandMarketingDetailPage'
import MarketingStrategyDetailPage from '@/pages/MarketingStrategyDetailPage'
import OfferStrategyDetailPage from '@/pages/OfferStrategyDetailPage'
import MessageStrategyDetailPage from '@/pages/MessageStrategyDetailPage'
import AdStrategyDetailPage from '@/pages/AdStrategyDetailPage'
import CreativeStrategyDetailPage from '@/pages/CreativeStrategyDetailPage'
import AdExecutionDetailPage from '@/pages/AdExecutionDetailPage'
import CreativeExecutionDetailPage from '@/pages/CreativeExecutionDetailPage'
import UgcCreativeDetailPage from '@/pages/UgcCreativeDetailPage'
import PageStrategyDetailPage from '@/pages/PageStrategyDetailPage'
import PageRequirementsDetailPage from '@/pages/PageRequirementsDetailPage'
import PageBlueprintDetailPage from '@/pages/PageBlueprintDetailPage'
import PageContentPlanDetailPage from '@/pages/PageContentPlanDetailPage'
import PageCopyDetailPage from '@/pages/PageCopyDetailPage'
import SettingsPage from '@/pages/SettingsPage'
import { OfferProfileElementsPage, OfferProfileTargetAudiencesPage } from '@/pages/EntityRelationPages'
import {
  AdCreativeExecutionsPage, AdCreativeStrategiesPage, AnalysisChecklistsPage, AnalysisQuestionsPage,
  BrandMarketingStrategiesPage, ChecklistItemsPage, OfferProfileAnalysesPage,
  OfferProfileBrandMarketingPage, MarketingOfferStrategiesPage, MessageAdStrategiesPage,
  MessagePageStrategiesPage, MessageUgcCreativesPage, OfferMessageStrategiesPage,
  PageRequirementsPage, PageBlueprintsPage, PageContentPlansPage, PageCopiesPage, CreativeAdExecutionsPage,
} from '@/pages/ResourcePages'

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/offers" element={<OffersPage />} />
        <Route path="/offers/:offerId" element={<OfferDetailPage />} />
        <Route path="/offers/:offerId/offer-profiles" element={<OfferProfilesPage />} />
        <Route path="/offers/:offerId/offer_profiles" element={<OfferProfilesPage />} />
        <Route path="/offer-profiles/:offerProfileId" element={<OfferProfileDetailPage />} />
        <Route path="/offer-profiles/:offerProfileId/target-audiences" element={<OfferProfileTargetAudiencesPage />} />
        <Route path="/offer-profiles/:offerProfileId/elements" element={<OfferProfileElementsPage />} />
        <Route path="/offer-profiles/:offerProfileId/analyses" element={<OfferProfileAnalysesPage />} />
        <Route path="/offer-profiles/:offerProfileId/brand-marketing" element={<OfferProfileBrandMarketingPage />} />
        <Route path="/target-audiences/:id" element={<TargetAudienceDetailPage />} />
        <Route path="/target-audiences/:id/edit" element={<TargetAudienceEditPage />} />
        <Route path="/offer-profiles/:offerProfileId/analysis/:analysisId" element={<AnalysisDetailPage />} />
        <Route path="/offer-profiles/:offerProfileId/analysis/:analysisId/checklists" element={<AnalysisChecklistsPage />} />
        <Route path="/offer-profiles/:offerProfileId/analysis/:analysisId/questions" element={<AnalysisQuestionsPage />} />
        <Route
          path="/offer-profiles/:offerProfileId/analysis/:analysisId/checklists/:checklistId"
          element={<ChecklistDetailPage />}
        />
        <Route path="/offer-profiles/:offerProfileId/analysis/:analysisId/checklists/:checklistId/items" element={<ChecklistItemsPage />} />
        <Route path="/brand-marketing/:id" element={<BrandMarketingDetailPage />} />
        <Route path="/brand-marketing/:id/marketing-strategies" element={<BrandMarketingStrategiesPage />} />
        <Route path="/marketing-strategy/:id" element={<MarketingStrategyDetailPage />} />
        <Route path="/marketing-strategy/:id/offer-strategies" element={<MarketingOfferStrategiesPage />} />
        <Route path="/offer-strategy/:id" element={<OfferStrategyDetailPage />} />
        <Route path="/offer-strategy/:id/message-strategies" element={<OfferMessageStrategiesPage />} />
        <Route path="/message-strategy/:id" element={<MessageStrategyDetailPage />} />
        <Route path="/message-strategy/:id/ad-strategies" element={<MessageAdStrategiesPage />} />
        <Route path="/message-strategy/:id/ugc-creatives" element={<MessageUgcCreativesPage />} />
        <Route path="/message-strategy/:id/page-strategies" element={<MessagePageStrategiesPage />} />
        <Route path="/ad-strategy/:id" element={<AdStrategyDetailPage />} />
        <Route path="/ad-strategy/:id/creative-strategies" element={<AdCreativeStrategiesPage />} />
        <Route path="/creative-strategy/:id" element={<CreativeStrategyDetailPage />} />
        <Route path="/creative-strategy/:id/ad-executions" element={<CreativeAdExecutionsPage />} />
        <Route path="/ad-execution/:id" element={<AdExecutionDetailPage />} />
        <Route path="/ad-execution/:id/creative-executions" element={<AdCreativeExecutionsPage />} />
        <Route path="/creative-execution/:id" element={<CreativeExecutionDetailPage />} />
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
