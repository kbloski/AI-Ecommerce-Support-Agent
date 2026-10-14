import { useParams } from 'react-router-dom'
import { ProfileAdditionalContexts } from '@/features/additionalContexts/ProfileAdditionalContexts'

export default function OfferProfileAdditionalContextsPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  return <div className="w-full p-6 lg:p-10"><ProfileAdditionalContexts offerProfileId={offerProfileId} /></div>
}
