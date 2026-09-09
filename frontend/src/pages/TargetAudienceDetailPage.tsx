import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { Button } from '@/components/ui/button'
import { EditTargetAudienceForm } from '@/features/targetAudiences/TargetAudienceForm'
import { useGetTargetAudienceQuery } from '@/features/targetAudiences/targetAudiencesApi'
import { useSidePanel } from '@/lib/sidePanel'

export default function TargetAudienceDetailPage() {
  const id = Number(useParams().id)
  const { data, isLoading, error } = useGetTargetAudienceQuery(id)
  const { openPanel, closePanel } = useSidePanel()

  return (
    <DetailShell
      title={(data?.name as string) ?? 'Grupa docelowa'}
      backTo={data ? `/offer-profiles/${data.offer_profile_id}` : undefined}
      backLabel="← OfferProfile"
      data={data}
      isLoading={isLoading}
      error={error}
      actions={data ? (
        <Button onClick={() => openPanel({
          title: 'Edytuj grupę docelową',
          content: <EditTargetAudienceForm id={id} data={data} onSaved={closePanel} />,
        })}>
          Edytuj
        </Button>
      ) : undefined}
    />
  )
}
