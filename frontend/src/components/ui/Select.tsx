import type { SelectHTMLAttributes } from 'react'
import { cn } from './utils'

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  helperText?: string
}

export function Select({ className, label, helperText, children, ...props }: SelectProps) {
  return (
    <label className='block'>
      {label && <span className='mb-2 block text-sm font-semibold text-neutral-ink'>{label}</span>}
      <select
        className={cn(
          'h-11 w-full rounded-card border border-neutral-line bg-white px-3 text-sm text-neutral-ink outline-none transition focus:border-brand-sky focus:ring-2 focus:ring-brand-sky/20 disabled:cursor-not-allowed disabled:bg-neutral-line/40',
          className,
        )}
        {...props}
      >
        {children}
      </select>
      {helperText && <span className='mt-1 block text-xs text-neutral-text'>{helperText}</span>}
    </label>
  )
}
