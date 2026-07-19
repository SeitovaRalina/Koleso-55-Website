import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { cn } from './utils'

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'icon'
type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  icon?: ReactNode
}

const variants: Record<ButtonVariant, string> = {
  primary: 'border-brand-sky bg-brand-sky text-white hover:bg-brand-deep',
  secondary: 'border-neutral-line bg-white text-neutral-ink hover:border-brand-sky hover:text-brand-deep',
  ghost: 'border-transparent bg-transparent text-neutral-ink hover:bg-brand-mist',
  danger: 'border-heritage-brick bg-heritage-brick text-white hover:bg-heritage-brick/90',
  icon: 'border-neutral-line bg-white text-neutral-ink hover:border-brand-sky hover:text-brand-deep',
}

const sizes: Record<ButtonSize, string> = {
  sm: 'h-9 px-3 text-sm',
  md: 'h-11 px-5 text-sm',
  lg: 'h-12 px-6 text-base',
}

export function Button({
  children,
  className,
  variant = 'primary',
  size = 'md',
  icon,
  type = 'button',
  ...props
}: ButtonProps) {
  const isIcon = variant === 'icon'

  return (
    <button
      type={type}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-card border font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-sky focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-55',
        variants[variant],
        isIcon ? 'h-11 w-11 p-0' : sizes[size],
        className,
      )}
      {...props}
    >
      {icon}
      {isIcon ? <span className='sr-only'>{children}</span> : children}
    </button>
  )
}
