import { useState, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { Entity } from '@/types'
import { useCreateOfferProfileMutation, useUpdateOfferProfileMutation } from './offerProfilesApi'

export function OfferProfileForm({ offerSourceId, profile, onCreated }: { offerSourceId: number; profile?: Entity; onCreated: () => void }) {
  const [create, state] = useCreateOfferProfileMutation()
  const [update, updateState] = useUpdateOfferProfileMutation()
  const [error, setError] = useState('')
  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError('')
    const name = String(new FormData(event.currentTarget).get('name') ?? '').trim()
    if (!name) { setError('Podaj nazwę profilu.'); return }
    try {
      if (profile) await update({ id: profile.id as number, offerSourceId, name }).unwrap()
      else await create({ offerSourceId, name }).unwrap()
      onCreated()
    }
    catch { setError('Nie udało się zapisać profilu. Spróbuj ponownie.') }
  }
  return <form className="space-y-4" onSubmit={submit}><label className="block space-y-2"><span>Nazwa profilu</span><Input name="name" defaultValue={String(profile?.name ?? '')} required maxLength={255} autoFocus /></label>
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={state.isLoading || updateState.isLoading}>{state.isLoading || updateState.isLoading ? 'Zapisywanie...' : profile ? 'Zapisz' : 'Utwórz profil'}</Button>
  </form>
}
