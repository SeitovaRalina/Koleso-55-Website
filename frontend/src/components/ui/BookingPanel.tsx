import { Alert } from './Alert'
import { Badge } from './Badge'
import { Button } from './Button'

type BookingState = 'available' | 'pending' | 'paid' | 'manager' | 'closed'

interface BookingPanelProps {
  title: string
  date: string
  seatsLabel: string
  priceLabel: string
  state?: BookingState
  onAction?: () => void
}

const stateCopy: Record<BookingState, { badge: string; action: string; alert: string }> = {
  available: {
    badge: 'Есть места',
    action: 'Забронировать',
    alert: 'Слот будет занят только после успешной оплаты.',
  },
  pending: {
    badge: 'Ожидает оплаты',
    action: 'Перейти к оплате',
    alert: 'YooKassa test mode будет основным шагом после бронирования.',
  },
  paid: {
    badge: 'Оплачено',
    action: 'Заказ оплачен',
    alert: 'Отмена оплаченного заказа доступна больше чем за 48 часов до события.',
  },
  manager: {
    badge: 'Цена по запросу',
    action: 'Связаться с менеджером',
    alert: 'Для договорной цены менеджер подтвердит условия вручную.',
  },
  closed: {
    badge: 'Мест нет',
    action: 'Недоступно',
    alert: 'Выберите другой слот или оставьте запрос менеджеру.',
  },
}

export function BookingPanel({
  title,
  date,
  seatsLabel,
  priceLabel,
  state = 'available',
  onAction,
}: BookingPanelProps) {
  const copy = stateCopy[state]
  const isDisabled = state === 'paid' || state === 'closed'

  return (
    <aside className='rounded-card border border-neutral-line bg-white p-5 shadow-sm'>
      <div className='flex items-start justify-between gap-3'>
        <div>
          <h3 className='text-lg font-semibold text-neutral-ink'>{title}</h3>
          <p className='mt-1 text-sm text-neutral-text'>{date}</p>
        </div>
        <Badge variant={state === 'available' ? 'availability' : state === 'manager' ? 'warning' : 'status'}>
          {copy.badge}
        </Badge>
      </div>

      <dl className='mt-5 grid grid-cols-2 gap-3 text-sm'>
        <div className='rounded-card bg-brand-mist/60 p-3'>
          <dt className='text-neutral-text'>Места</dt>
          <dd className='mt-1 font-semibold text-neutral-ink'>{seatsLabel}</dd>
        </div>
        <div className='rounded-card bg-heritage-cream p-3'>
          <dt className='text-neutral-text'>Стоимость</dt>
          <dd className='mt-1 font-semibold text-neutral-ink'>{priceLabel}</dd>
        </div>
      </dl>

      <Alert className='mt-5' variant={state === 'available' ? 'info' : state === 'closed' ? 'danger' : 'warning'}>
        {copy.alert}
      </Alert>

      <Button className='mt-5 w-full' disabled={isDisabled} onClick={onAction}>
        {copy.action}
      </Button>
    </aside>
  )
}
