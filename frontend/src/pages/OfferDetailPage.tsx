import { useParams } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { DetailShell } from '@/components/DetailShell'
import { useGetOfferQuery } from '@/features/offers/offersApi'
import { EditOfferForm } from '@/features/offers/OfferForm'
import { useSidePanel } from '@/lib/sidePanel'

export default function OfferDetailPage() {
  const offerId = Number(useParams().offerId)
  const { data: offer, isLoading, error } = useGetOfferQuery(offerId)
  const { openPanel, closePanel } = useSidePanel()

  return (
    <DetailShell
      title={offer?.name as string}
      backTo="/offers"
      backLabel="← Oferty"
      data={offer}
      isLoading={isLoading}
      error={error}
      actions={offer ? (
        <Button onClick={() => openPanel({
          title: 'Edytuj ofertę',
          content: <EditOfferForm
            offerId={offerId}
            initialValues={{
              name: String(offer.name ?? ''),
              description: String(offer.description ?? ''),
            }}
            onSaved={closePanel}
          />,
        })}>
          Edytuj
        </Button>
      ) : undefined}
    />
  )
}
