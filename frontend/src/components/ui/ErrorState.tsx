import { Button } from './Button'

interface ErrorStateProps {
  title?: string
  description?: string
  actionLabel?: string
  onAction?: () => void
}

export function ErrorState({
  title = 'Не удалось загрузить данные',
  description = 'Проверьте соединение или повторите попытку позже.',
  actionLabel = 'Повторить',
  onAction,
}: ErrorStateProps) {
  return (
    <div className='rounded-card border border-heritage-brick/25 bg-heritage-brick/10 px-5 py-8 text-center'>
      <h3 className='text-lg font-semibold text-heritage-brick'>{title}</h3>
      <p className='mx-auto mt-2 max-w-md text-sm text-neutral-text'>{description}</p>
      {onAction && (
        <Button className='mt-5' variant='danger' onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
