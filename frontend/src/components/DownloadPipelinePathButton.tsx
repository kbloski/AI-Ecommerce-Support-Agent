import { Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useGetPipelinePathMutation, type PipelinePathResponse } from '@/features/pipeline/pipelineApi'
import { cn } from '@/lib/utils'

function formatPipelinePathAsText(response: PipelinePathResponse): string {
  return response.path
    .map((stage) => {
      const header = `===== ${stage.stage.toUpperCase()} (id=${stage.id}) =====`
      const body = stage.llm_context ?? JSON.stringify(stage.data, null, 2)
      return `${header}\n${body}`
    })
    .join('\n\n')
}

function downloadTextFile(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

export function DownloadPipelinePathButton({
  entityType,
  entityId,
  className,
}: {
  entityType: string
  entityId: number
  className?: string
}) {
  const [getPipelinePath, { isLoading }] = useGetPipelinePathMutation()

  const handleClick = async () => {
    const response = await getPipelinePath({ entity_type: entityType, entity_id: entityId }).unwrap()
    downloadTextFile(`pipeline-path_${entityType}-${entityId}.txt`, formatPipelinePathAsText(response))
  }

  return (
    <Button
      type="button"
      variant="ghost"
      size="sm"
      className={cn('w-full justify-start', className)}
      onClick={handleClick}
      disabled={isLoading}
    >
      <Download />
      {isLoading ? 'Pobieranie…' : 'Pobierz dane ścieżki (.txt)'}
    </Button>
  )
}
