import { Button } from '@/components/ui/button'
import { EntityList } from '@/components/EntityList'
import { EditOfferForm, OfferForm } from '@/features/offers/OfferForm'
import {
  useCreateOfferMutation,
  useDeleteOfferMutation,
  useListOffersQuery,
} from '@/features/offers/offersApi'
import { useSidePanel } from '@/lib/sidePanel'

export default function OffersPage() {
  const { data, isLoading, error } = useListOffersQuery()
  const [deleteOffer] = useDeleteOfferMutation()
  const { openPanel, closePanel } = useSidePanel()

  return (
    <div className="w-full space-y-8 p-6 lg:p-10">
      <EntityList
        title="Oferty"
        items={data?.items}
        isLoading={isLoading}
        error={error}
        linkTo={(offer) => `/offers/${offer.id}`}
        itemLabel={(offer) => (offer.name as string) ?? `Oferta #${offer.id}`}
        emptyTitle="Brak ofert"
        emptyDescription="Utwórz pierwszą ofertę, aby rozpocząć pracę."
        onEdit={(offer) => openPanel({
          title: 'Edytuj ofertę',
          content: <EditOfferForm
            offerId={offer.id}
            initialValues={{
              name: String(offer.name ?? ''),
              description: String(offer.description ?? ''),
            }}
            onSaved={closePanel}
          />,
        })}
        onDelete={(offer) => deleteOffer(offer.id as number)}
        actions={
          <Button
            className="h-10 rounded-none px-4"
            onClick={() => openPanel({
              title: 'Nowa oferta',
              content: <CreateOfferForm onCreated={closePanel} />,
            })}
          >
            Nowa oferta
          </Button>
        }
      />
    </div>
  )
}

function CreateOfferForm({ onCreated }: { onCreated: () => void }) {
  const [createOffer, { isLoading: isCreating }] = useCreateOfferMutation()

  return (
    <OfferForm
      onSubmit={(values) => createOffer(values).unwrap()}
      onSuccess={onCreated}
      isSubmitting={isCreating}
      submitLabel="Utwórz ofertę"
      submittingLabel="Tworzenie…"
    />
  )
}
