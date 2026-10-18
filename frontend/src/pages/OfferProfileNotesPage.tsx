import { useParams } from 'react-router-dom'
import { ProfileNotes } from '@/features/notes/ProfileNotes'

export default function OfferProfileNotesPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  return <div className="w-full p-6 lg:p-10"><ProfileNotes offerProfileId={offerProfileId} /></div>
}
