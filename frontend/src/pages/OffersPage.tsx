import { useState, type FormEvent } from 'react'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { EntityList } from '@/components/EntityList'
import {
  useCreateOfferMutation,
  useDeleteOfferMutation,
  useListOffersQuery,
} from '@/features/offers/offersApi'

const createOfferSchema = z.object({
  name: z.string().min(1, 'Nazwa jest wymagana'),
  description: z.string().optional(),
})

export default function OffersPage() {
  const { data, isLoading, error } = useListOffersQuery()
  const [createOffer, { isLoading: isCreating }] = useCreateOfferMutation()
  const [deleteOffer] = useDeleteOfferMutation()
  const [formError, setFormError] = useState<string | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setFormError(null)

    const form = e.currentTarget
    const formData = new FormData(form)
    const parsed = createOfferSchema.safeParse({
      name: formData.get('name'),
      description: formData.get('description'),
    })

    if (!parsed.success) {
      setFormError(parsed.error.issues[0]?.message ?? 'Nieprawidłowe dane')
      return
    }

    await createOffer(parsed.data).unwrap()
    form.reset()
    setShowCreateForm(false)
  }

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
        onDelete={(offer) => deleteOffer(offer.id as number)}
        actions={
          <Button className="h-10 rounded-none px-4" onClick={() => setShowCreateForm((value) => !value)}>
            {showCreateForm ? 'Anuluj' : 'Nowa oferta'}
          </Button>
        }
        contentBeforeList={showCreateForm ? (
          <form onSubmit={handleSubmit} className="w-full space-y-2 p-4">
            <h2 className="text-lg font-semibold">Nowa oferta</h2>
            <input name="name" placeholder="Nazwa" className="w-full rounded-none border px-3 py-2 text-sm" />
            <textarea name="description" placeholder="Opis (opcjonalnie)" className="w-full rounded-none border px-3 py-2 text-sm" />
            {formError && <p className="text-sm text-destructive">{formError}</p>}
            <Button type="submit" disabled={isCreating} className="rounded-none">
              {isCreating ? 'Tworzenie…' : 'Utwórz ofertę'}
            </Button>
          </form>
        ) : undefined}
      />
    </div>
  )
}
