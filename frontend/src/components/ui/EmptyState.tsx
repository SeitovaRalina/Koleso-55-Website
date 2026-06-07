import type { ReactNode } from 'react'
import { Button } from './Button'

interface EmptyStateProps {
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
  icon?: ReactNode
}

export function EmptyState({ title, description, actionLabel, onAction, icon }: EmptyStateProps) {
  return (
    <div className='rounded-card border border-dashed border-neutral-line bg-white px-5 py-10 text-center'>
      {icon && (
        <div className='mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-brand-mist text-brand-deep'>
          {icon}
        </div>
      )}
      <h3 className='text-lg font-semibold text-neutral-ink'>{title}</h3>
      <p className='mx-auto mt-2 max-w-md text-sm text-neutral-text'>{description}</p>
      {actionLabel && onAction && (
        <Button className='mt-5' onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
