import { cn } from './utils'

interface ImagePlaceholderProps {
  className?: string
  label?: string
}

export function ImagePlaceholder({ className, label = 'Фото нет' }: ImagePlaceholderProps) {
  return (
    <div
      className={cn(
        'flex items-center justify-center bg-[#dfe8f3] text-neutral-text',
        className,
      )}
      role="img"
      aria-label={label}
    >
      <span className="text-sm font-medium">{label}</span>
    </div>
  )
}
