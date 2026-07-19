import type { HTMLAttributes } from 'react'
import { cn } from './utils'

type BadgeVariant = 'category' | 'status' | 'availability' | 'muted' | 'warning'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
}

const variants: Record<BadgeVariant, string> = {
  category: 'bg-brand-mist text-brand-deep',
  status: 'bg-heritage-cream text-heritage-brick',
  availability: 'bg-nature-green/15 text-nature-green',
  muted: 'bg-neutral-line text-neutral-text',
  warning: 'bg-heritage-brick/10 text-heritage-brick',
}

export function Badge({ className, variant = 'muted', ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold',
        variants[variant],
        className,
      )}
      {...props}
    />
  )
}
