import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { ResourceList } from '@/components/ResourceList'
import { ListFilters, ReviewStatusFilter, ReviewStatusSortSelect, type ReviewStatusFilterValue, type ReviewStatusSort } from '@/components/ListFilters'
import { Button } from '@/components/ui/button'
import { useSidePanel } from '@/lib/sidePanel'
import { EditTargetAudienceForm } from '@/features/targetAudiences/TargetAudienceForm'
import { GenerateTargetAudiencesForm } from '@/features/targetAudiences/GenerateTargetAudiencesForm'
import { useDeleteTargetAudienceMutation, useListTargetAudiencesForOfferProfileQuery, useUpdateTargetAudienceMutation } from '@/features/targetAudiences/targetAudiencesApi'

export function OfferProfileTargetAudiencesPage() {
  const offerProfileId = Number(useParams().offerProfileId)
  const [page, setPage] = useState(1)
  const [isReviewedFilter, setIsReviewedFilter] = useState<ReviewStatusFilterValue>('')
  const [reviewStatusSort, setReviewStatusSort] = useState<ReviewStatusSort>('unreviewed_first')
  const { data: result, isLoading, error } = useListTargetAudiencesForOfferProfileQuery({
    offerProfileId,
    page,
    pageSize: 6,
    isReviewed: isReviewedFilter === '' ? undefined : isReviewedFilter === 'true',
    sort: reviewStatusSort,
  })
  const { data: unreviewedResult } = useListTargetAudiencesForOfferProfileQuery({
    offerProfileId,
    pageSize: 1,
    isReviewed: false,
  })
  const [remove] = useDeleteTargetAudienceMutation()
  const [updateTargetAudience] = useUpdateTargetAudienceMutation()
  const { openPanel, closePanel } = useSidePanel()
  const items = result?.items ?? []

  const updateIsReviewedFilter = (value: ReviewStatusFilterValue) => {
    setIsReviewedFilter(value)
    setPage(1)
  }

  const updateReviewStatusSort = (value: ReviewStatusSort) => {
    setReviewStatusSort(value)
    setPage(1)
  }

  return (
    <div className="w-full p-6 lg:p-10">
      <ResourceList
        title="Grupy docelowe"
        items={items}
        totalItems={result?.total_items}
        attentionItems={unreviewedResult?.total_items}
        isLoading={isLoading}
        error={error}
        itemLabel={(item) => (item.name as string) ?? `#${item.id}`}
        onGenerate={() => openPanel({ title: 'Generuj grupy docelowe', content: <GenerateTargetAudiencesForm offerProfileId={offerProfileId} onSaved={closePanel} /> })}
        generateLabel="Generuj grupy docelowe"
        contentBeforeList={
          <ListFilters>
            <ReviewStatusFilter value={isReviewedFilter} onChange={updateIsReviewedFilter} />
            <ReviewStatusSortSelect value={reviewStatusSort} onChange={updateReviewStatusSort} />
          </ListFilters>
        }
        footer={result && result.total_pages > 1 ? (
          <div className="flex items-center justify-between gap-3 border-t pt-4">
            <span className="text-sm text-muted-foreground">Strona {result.page} z {result.total_pages}</span>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={result.page <= 1} onClick={() => setPage(result.page - 1)}>Poprzednia</Button>
              <Button variant="outline" size="sm" disabled={result.page >= result.total_pages} onClick={() => setPage(result.page + 1)}>Następna</Button>
            </div>
          </div>
        ) : undefined}
        onEdit={(item) => openPanel({
          title: 'Edytuj grupę docelową',
          content: <EditTargetAudienceForm id={item.id as number} data={item} onSaved={closePanel} />,
        })}
        onDelete={(item) => remove({ id: item.id as number, offerProfileId })}
        itemActions={(item) => (
          <Button
            variant={item.is_reviewed ? 'ghost' : 'default'}
            size="sm"
            className="h-7 px-2.5 text-xs"
            onClick={() => updateTargetAudience({
              id: item.id as number,
              offerProfileId,
              is_reviewed: item.is_reviewed !== true,
            })}
          >
            {item.is_reviewed ? 'Oznacz jako niesprawdzone' : 'Zatwierdź'}
          </Button>
        )}
      />
    </div>
  )
}
