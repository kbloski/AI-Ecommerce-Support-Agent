import { useState, type FormEvent } from 'react'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { useUpdateOfferMutation } from '@/features/offers/offersApi'

const offerFormSchema = z.object({
  name: z.string().trim().min(1, 'Nazwa jest wymagana'),
  description: z.string().trim().optional(),
})

export type OfferFormValues = z.infer<typeof offerFormSchema>

interface OfferFormProps {
  initialValues?: Partial<OfferFormValues>
  onSubmit: (values: OfferFormValues) => Promise<unknown>
  onSuccess?: () => void
  isSubmitting?: boolean
  submitLabel?: string
  submittingLabel?: string
}

export function OfferForm({
  initialValues,
  onSubmit,
  onSuccess,
  isSubmitting = false,
  submitLabel = 'Zapisz',
  submittingLabel = 'Zapisywanie…',
}: OfferFormProps) {
  const [formError, setFormError] = useState<string | null>(null)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setFormError(null)

    const formData = new FormData(event.currentTarget)
    const parsed = offerFormSchema.safeParse({
      name: formData.get('name'),
      description: formData.get('description'),
    })

    if (!parsed.success) {
      setFormError(parsed.error.issues[0]?.message ?? 'Nieprawidłowe dane')
      return
    }

    try {
      await onSubmit(parsed.data)
      onSuccess?.()
    } catch {
      setFormError('Nie udało się zapisać oferty.')
    }
  }

  return (
    <form onSubmit={(event) => void handleSubmit(event)} className="space-y-5">
      <label className="block space-y-2">
        <span className="text-sm font-medium">Nazwa</span>
        <Input
          name="name"
          required
          defaultValue={initialValues?.name ?? ''}
          placeholder="Nazwa oferty"
        />
      </label>
      <label className="block space-y-2">
        <span className="text-sm font-medium">Opis</span>
        <Textarea
          name="description"
          defaultValue={initialValues?.description ?? ''}
          placeholder="Opis (opcjonalnie)"
        />
      </label>
      {formError && <p className="text-sm text-destructive">{formError}</p>}
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? submittingLabel : submitLabel}
      </Button>
    </form>
  )
}

/** Shared "edit offer" form used both on the offer's detail page and from the offers list. */
export function EditOfferForm({
  offerId,
  initialValues,
  onSaved,
}: {
  offerId: number
  initialValues: { name: string; description: string }
  onSaved: () => void
}) {
  const [updateOffer, updateOfferState] = useUpdateOfferMutation()

  return (
    <OfferForm
      initialValues={initialValues}
      onSubmit={(fields) => updateOffer({ id: offerId, fields }).unwrap()}
      onSuccess={onSaved}
      isSubmitting={updateOfferState.isLoading}
    />
  )
}
