import type { HTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex shrink-0 items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] font-medium leading-none',
  {
    variants: {
      variant: {
        default: 'border-slate-200 bg-slate-50 text-slate-600',
        success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
        danger: 'border-rose-200 bg-rose-50 text-rose-700',
      },
    },
    defaultVariants: { variant: 'default' },
  },
)

function Badge({ className, variant, ...props }: HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badgeVariants>) {
  return <span data-slot="badge" className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge }
