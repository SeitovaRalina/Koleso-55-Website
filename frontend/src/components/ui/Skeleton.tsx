import type { HTMLAttributes } from 'react'
import { cn } from './utils'

export function Skeleton({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('animate-pulse rounded-card bg-neutral-line/80', className)}
      aria-hidden='true'
      {...props}
    />
  )
}
