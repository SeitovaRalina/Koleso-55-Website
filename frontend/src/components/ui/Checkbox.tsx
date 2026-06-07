import type { InputHTMLAttributes, ReactNode } from 'react'
import { cn } from './utils'

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: ReactNode
  description?: ReactNode
}

export function Checkbox({ className, label, description, ...props }: CheckboxProps) {
  return (
    <label className='flex gap-3 rounded-card border border-neutral-line bg-white p-3 text-sm text-neutral-ink'>
      <input
        type='checkbox'
        className={cn('mt-1 h-4 w-4 rounded border-neutral-line text-brand-sky focus:ring-brand-sky', className)}
        {...props}
      />
      <span>
        <span className='block font-semibold'>{label}</span>
        {description && <span className='mt-1 block text-neutral-text'>{description}</span>}
      </span>
    </label>
  )
}
