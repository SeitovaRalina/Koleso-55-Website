import type { HTMLAttributes } from 'react'
import { cn } from './utils'

type AlertVariant = 'info' | 'success' | 'warning' | 'danger'

interface AlertProps extends HTMLAttributes<HTMLDivElement> {
  variant?: AlertVariant
  title?: string
}

const variants: Record<AlertVariant, string> = {
  info: 'border-brand-sky/30 bg-brand-mist text-brand-deep',
  success: 'border-nature-green/30 bg-nature-green/10 text-nature-green',
  warning: 'border-heritage-brick/30 bg-heritage-cream text-heritage-brick',
  danger: 'border-heritage-brick/30 bg-heritage-brick/10 text-heritage-brick',
}

export function Alert({ className, variant = 'info', title, children, ...props }: AlertProps) {
  return (
    <div
      className={cn('rounded-card border p-4 text-sm', variants[variant], className)}
      role={variant === 'danger' ? 'alert' : 'status'}
      {...props}
    >
      {title && <p className='mb-1 font-semibold'>{title}</p>}
      <div>{children}</div>
    </div>
  )
}
