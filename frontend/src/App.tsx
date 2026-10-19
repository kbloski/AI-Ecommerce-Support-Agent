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
import UgcCreativeDetailPage from '@/pages/UgcCreativeDetailPage'
import PageBlueprintDetailPage from '@/pages/PageBlueprintDetailPage'
import PagesPage from '@/pages/PagesPage'
import PageDetailPage from '@/pages/PageDetailPage'
import SettingsPage from '@/pages/SettingsPage'
import { OfferProfileTargetAudiencesPage } from '@/pages/EntityRelationPages'
import {
  AnalysisQuestionsPage,
  ChecklistItemsPage, OfferProfileAnalysesPage,
  OfferProfileUgcCreativesPage,
  OfferProfilePageBlueprintsPage, OfferProfileChecklistsPage,
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
        <Route path="/offer-profiles/:offerProfileId/analysis/:analysisId" element={<AnalysisDetailPage />} />
        <Route path="/offer-profiles/:offerProfileId/analysis/:analysisId/questions" element={<AnalysisQuestionsPage />} />
        <Route
          path="/offer-profiles/:offerProfileId/checklists/:checklistId"
          element={<ChecklistDetailPage />}
        />
        <Route path="/offer-profiles/:offerProfileId/checklists/:checklistId/items" element={<ChecklistItemsPage />} />
        <Route path="/offer-profiles/:offerProfileId/ugc-creatives" element={<OfferProfileUgcCreativesPage />} />
        <Route path="/ugc-creatives/:id" element={<UgcCreativeDetailPage />} />
        <Route path="/offer-profiles/:offerProfileId/page-blueprints" element={<OfferProfilePageBlueprintsPage />} />
        <Route path="/offer-profiles/:offerProfileId/pages" element={<PagesPage />} />
        <Route path="/page-blueprints/:id" element={<PageBlueprintDetailPage />} />
        <Route path="/pages/:id" element={<PageDetailPage />} />
        <Route path="/settings" element={<Navigate to="/settings/general" replace />} />
        <Route path="/settings/general" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}

export default App
