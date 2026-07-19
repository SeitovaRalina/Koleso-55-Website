import type { InputHTMLAttributes } from 'react'
import { cn } from './utils'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  helperText?: string
  error?: string
}

export function Input({ className, label, helperText, error, id, ...props }: InputProps) {
  const inputId = id || props.name

  return (
    <label className='block' htmlFor={inputId}>
      {label && <span className='mb-2 block text-sm font-semibold text-neutral-ink'>{label}</span>}
      <input
        id={inputId}
        className={cn(
          'h-11 w-full rounded-card border border-neutral-line bg-white px-3 text-sm text-neutral-ink outline-none transition focus:border-brand-sky focus:ring-2 focus:ring-brand-sky/20 disabled:cursor-not-allowed disabled:bg-neutral-line/40',
          error && 'border-heritage-brick focus:border-heritage-brick focus:ring-heritage-brick/20',
          className,
        )}
        {...props}
      />
      {(helperText || error) && (
        <span className={cn('mt-1 block text-xs', error ? 'text-heritage-brick' : 'text-neutral-text')}>
          {error || helperText}
        </span>
      )}
    </label>
  )
}
