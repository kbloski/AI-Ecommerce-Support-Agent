import { useParams } from 'react-router-dom'
import { DetailShell } from '@/components/DetailShell'
import { useGetPageBlueprintQuery, useUpdatePageBlueprintMutation } from '@/features/pageBlueprint/pageBlueprintApi'

export default function PageBlueprintDetailPage() {
  const id = Number(useParams().id)
  const { data: pageBlueprint, isLoading, error } = useGetPageBlueprintQuery(id)

  const [updatePageBlueprint, updateState] = useUpdatePageBlueprintMutation()

  return (
    <DetailShell
      title={(pageBlueprint?.page_type as string) ?? 'Page blueprint'}
      backTo={pageBlueprint ? `/page-requirements/${pageBlueprint.page_requirements_id}` : undefined}
      backLabel="← Page requirements"
      data={pageBlueprint}
      isLoading={isLoading}
      error={error}
      editable={{
        onSave: (fields) => updatePageBlueprint({ id, fields }).unwrap(),
        isSaving: updateState.isLoading,
      }}
    />
  )
}
