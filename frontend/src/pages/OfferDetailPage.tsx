import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import {
  useGetOfferQuery,
  useUpdateOfferMutation,
} from '@/features/offers/offersApi'

export default function OfferDetailPage() {
  const offerId = Number(useParams().offerId)
  const { data: offer, isLoading, error } = useGetOfferQuery(offerId)
  const [updateOffer, updateOfferState] = useUpdateOfferMutation()

  return (
    <DetailShell
      title={offer?.name as string}
      backTo="/offers"
      backLabel="← Oferty"
      data={offer}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updateOffer({ id: offerId, fields }).unwrap(),
        isSaving: updateOfferState.isLoading,
      }}
    />
  )
}
