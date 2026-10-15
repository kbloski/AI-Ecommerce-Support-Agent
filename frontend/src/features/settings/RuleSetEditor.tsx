import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { useGetRuleSetQuery, useSaveRuleSetMutation, type RuleSet } from './settingsApi'

export function RuleSetEditor({ ruleSet, title }: { ruleSet: RuleSet; title: string }) {
  const { data, isLoading, error } = useGetRuleSetQuery(ruleSet)
  const [save, state] = useSaveRuleSetMutation()
  const [content, setContent] = useState('')

  useEffect(() => {
    if (data) setContent(data.content)
  }, [data])

  return <section className="space-y-3">
    <h2 className="text-lg font-semibold">{title}</h2>
    <p className="text-sm text-muted-foreground">Ten zestaw jest dołączany tylko przez generatory, które wybiorą go jawnie.</p>
    {isLoading && <p className="text-sm text-muted-foreground">Ładowanie…</p>}
    {Boolean(error) && <p role="alert" className="text-sm text-destructive">Nie udało się pobrać reguł.</p>}
    {data && <>
      <textarea
        aria-label={title}
        value={content}
        onChange={(event) => setContent(event.target.value)}
        rows={12}
        className="w-full rounded-lg border border-border bg-background p-3 font-mono text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
      />
      <div className="flex items-center gap-3">
        <Button onClick={() => save({ ruleSet, content })} disabled={state.isLoading || content === data.content}>Zapisz</Button>
        {state.isSuccess && <span className="text-sm text-muted-foreground">Zapisano.</span>}
        {state.isError && <span role="alert" className="text-sm text-destructive">Nie udało się zapisać.</span>}
      </div>
    </>}
  </section>
}
