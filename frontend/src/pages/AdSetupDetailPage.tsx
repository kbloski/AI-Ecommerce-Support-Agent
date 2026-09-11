import { useState, type FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { Button } from '@/components/ui/button'
import { useGetAdSetupQuery, useListCreativeTypesQuery, useUpdateAdSetupMutation } from '@/features/adSetup/adSetupApi'
import { useListPlatformsQuery, type Platform } from '@/features/platforms/platformsApi'
import type { Entity } from '@/types'

export default function AdSetupDetailPage() {
  const id = Number(useParams().id)
  const { data, isLoading, error } = useGetAdSetupQuery(id)

  const [updateAdSetup, updateState] = useUpdateAdSetupMutation()
  const displayData = data
    ? {
        ...data,
        format:
          typeof data.format === 'string'
            ? data.format.replace(/\bvideo\b\s*/i, '').trim()
            : data.format,
      }
    : undefined

  return (
    <DetailShell
      title={(data?.name as string) ?? 'Ad Setup'}
      backTo={data ? `/creative-strategy/${data.creative_strategy_id}` : undefined}
      backLabel="← Creative strategy"
      data={displayData}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updateAdSetup({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
        content: data ? (onSaved) => <AdSetupEditForm data={data} onSaved={onSaved} /> : undefined,
      }}
    />
  )
}

function AdSetupEditForm({ data, onSaved }: { data: Entity; onSaved: () => void }) {
  const [update, updateState] = useUpdateAdSetupMutation()
  const { data: platforms = [] } = useListPlatformsQuery()
  const { data: creativeTypes = [] } = useListCreativeTypesQuery()
  const [error, setError] = useState<string | null>(null)

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setError(null)
    try {
      await update({
        id: data.id as number,
        fields: {
          name: String(form.get('name') || ''),
          creative_type: String(form.get('creative_type') || ''),
          platform: String(form.get('platform') || ''),
          format: String(form.get('format') || ''),
        },
      }).unwrap()
      onSaved()
    } catch {
      setError('Nie udało się zapisać Ad Setup.')
    }
  }

  return <form onSubmit={(event) => void submit(event)} className="space-y-5">
    <label className="block space-y-2"><span className="text-sm font-medium">Nazwa</span><input name="name" defaultValue={data.name as string | undefined} className="h-9 w-full rounded-md border px-2.5 text-sm" /></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Typ kreacji</span><select name="creative_type" defaultValue={data.creative_type as string | undefined} className="h-9 w-full rounded-md border px-2.5 text-sm">{creativeTypes.map((creativeType) => <option key={creativeType.id} value={creativeType.id}>{creativeType.name}</option>)}</select></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Platforma</span><select name="platform" defaultValue={data.platform as string | undefined} className="h-9 w-full rounded-md border px-2.5 text-sm">{platforms.map((platform: Platform) => <option key={platform.id} value={platform.id}>{platform.name}</option>)}</select></label>
    <label className="block space-y-2"><span className="text-sm font-medium">Format</span><input name="format" defaultValue={data.format as string | undefined} className="h-9 w-full rounded-md border px-2.5 text-sm" /></label>
    {error && <p className="text-sm text-destructive">{error}</p>}
    <Button type="submit" disabled={updateState.isLoading}>{updateState.isLoading ? 'Zapisywanie…' : 'Zapisz'}</Button>
  </form>
}
